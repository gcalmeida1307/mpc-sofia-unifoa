import unittest

from ai.planner import build_plan
from ai.reasoning import reasoning_engine


class ReasoningEngineTests(unittest.TestCase):
    def test_calculates_simple_expression(self):
        result = reasoning_engine.build("quanto e 2+2?", {}, {})
        self.assertEqual(result["deterministic_answer"], "O resultado de 2+2 e 4.")

    def test_routes_group_pronoun_to_host_count(self):
        plan = build_plan("quantos estao no grupo PRD01-ANTIGA MEDICINA?")
        self.assertEqual(plan["intent"], "host_count")

    def test_routes_short_trigger_question_to_zabbix_tools(self):
        plan = build_plan("E quantos deles esta com triggers?")

        self.assertEqual(plan["intent"], "active_trigger_summary")
        self.assertIn("mcp_zabbix_summary", plan["capabilities"])

    def test_answers_affected_hosts_for_trigger_question(self):
        result = reasoning_engine.build(
            "E quantos deles esta com triggers?",
            {"tools": ["zabbix.list_problems"]},
            {
                "summary": {"hosts": 234, "problems": 200},
                "snapshot": {
                    "zabbix": {
                        "problem_summary": {
                            "affected_hosts": 55,
                            "total_problems": 200,
                        }
                    }
                },
            },
        )

        answer = result["deterministic_answer"]
        self.assertIn("55 host(s)", answer)
        self.assertIn("200 evento(s)", answer)
        self.assertIn("nao do total de triggers configurados", answer)


if __name__ == "__main__":
    unittest.main()
