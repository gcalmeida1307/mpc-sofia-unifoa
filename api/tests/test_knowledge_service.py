import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from services.knowledge import search_knowledge


class KnowledgeServiceTestCase(unittest.TestCase):
    def test_search_knowledge_reads_docs_for_zabbix_context(self):
        result = search_knowledge("severity average zabbix group hosts")
        self.assertGreater(len(result["results"]), 0)
        self.assertTrue(any("severity" in item["snippet"].lower() for item in result["results"]))

    def test_ingest_source_can_crawl_external_docs_into_local_store(self):
        html_pages = {
            "https://docs.example.test/manual/index.html": (
                "<html><head><title>Zabbix Manual</title></head><body>"
                "<main>Trigger expressions explain how severity is calculated."
                "<a href='/manual/triggers.html'>Triggers</a></main></body></html>"
            ),
            "https://docs.example.test/manual/triggers.html": (
                "<html><head><title>Triggers</title></head><body>"
                "<main>Severity average changes when triggers stay active."
                "<a href='/manual/index.html'>Back</a></main></body></html>"
            ),
        }

        def fake_get(url, timeout=None, headers=None):
            response = Mock()
            response.text = html_pages[url]
            response.headers = {"content-type": "text/html; charset=utf-8"}
            response.raise_for_status = Mock()
            return response

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            with patch("services.knowledge.DOCS_ROOT", temp_root), patch("services.knowledge.requests.get", side_effect=fake_get):
                from services.knowledge import ingest_source

                result = ingest_source(
                    {
                        "source": "zabbix-docs",
                        "source_type": "documentation_site",
                        "url": "https://docs.example.test/manual/index.html",
                        "max_pages": 3,
                        "max_depth": 1,
                        "metadata": {"site": "zabbix"},
                    }
                )

                self.assertEqual(result["status"], "indexed")
                self.assertGreaterEqual(result["pages_indexed"], 2)

                saved_docs = list((temp_root / "_external").rglob("*.md"))
                self.assertGreaterEqual(len(saved_docs), 2)

                search_result = search_knowledge("severity average trigger expressions")
                self.assertTrue(any("zabbix-docs" in item["source"] or "Triggers" in item["source"] for item in search_result["results"]))
                self.assertTrue(any("severity" in item["snippet"].lower() for item in search_result["results"]))


if __name__ == "__main__":
    unittest.main()
