import unittest

from routes.assistant import AssistantRequest, ask


class AssistantRouteTestCase(unittest.TestCase):
    def test_assistant_uses_zabbix_and_knowledge_for_severity_questions(self):
        response = ask(AssistantRequest(question="qual grupo de hosts possuem a severity average?"))
        self.assertIn("severity", response["answer"].lower())
        self.assertIn("knowledge", response["answer"].lower())


if __name__ == "__main__":
    unittest.main()
