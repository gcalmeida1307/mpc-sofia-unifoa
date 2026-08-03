import unittest

from services.knowledge import search_knowledge


class KnowledgeServiceTestCase(unittest.TestCase):
    def test_search_knowledge_reads_docs_for_zabbix_context(self):
        result = search_knowledge("severity average zabbix group hosts")
        self.assertGreater(len(result["results"]), 0)
        self.assertTrue(any("severity" in item["snippet"].lower() for item in result["results"]))


if __name__ == "__main__":
    unittest.main()
