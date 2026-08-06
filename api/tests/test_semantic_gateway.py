from ai.agent_runtime import agent_runtime
from ai.planner import build_plan
from semantic.fallback import deterministic_interpret
from semantic.interpreter import SemanticGateway


class FakeProvider:
    def __init__(self, result=None):
        self.result = result

    def interpret(self, **kwargs):
        return self.result


def test_equivalent_natural_questions_produce_same_logical_plan():
    questions = [
        "Quantos switches tiveram triggers nos últimos 7 dias?",
        "Na última semana, quantos switches apresentaram alertas?",
        "Qual foi a quantidade de switches com trigger nos últimos sete dias?",
    ]
    semantics = [deterministic_interpret(question) for question in questions]
    assert len({item.logical_signature() for item in semantics}) == 1

    plans = [build_plan(question, semantic) for question, semantic in zip(questions, semantics)]
    signatures = {(plan["intent"], tuple(plan["capabilities"]), tuple(plan["tools"]), plan["domain"]) for plan in plans}
    assert len(signatures) == 1


def test_invalid_provider_json_uses_safe_deterministic_fallback():
    gateway = SemanticGateway(FakeProvider(None))
    query = gateway.interpret("Quantos switches tiveram triggers nos últimos 3 dias?")
    assert query.intent == "historical_trigger_summary"
    assert query.entity_name == "Switches"
    assert query.time_range.days == 3
    assert query.interpretation_source == "deterministic"


def test_unknown_and_extra_provider_fields_are_not_executed():
    result = {"provider":"anthropic","data":{"intent":"historical_trigger_summary","domain":"network","source":"zabbix","entity_type":"switch","time_range":{"days":7},"metric":"trigger_count","state":"historical","group_by":"host","confidence":0.9,"command":"DROP TABLE users"}}
    query = SemanticGateway(FakeProvider(result)).interpret("Quantos switches tiveram triggers nos últimos 7 dias?")
    assert query.interpretation_source == "deterministic"
    assert "command" not in query.model_dump()


def test_agent_selection_uses_semantic_domain_not_raw_keyword():
    semantic = deterministic_interpret("Quantos switches tiveram triggers nos últimos 7 dias?")
    plan = build_plan("texto sem palavras de rede", semantic)
    assert agent_runtime.resolve("texto sem palavras de rede", plan)["key"] == "network"


def test_resolution_request_routes_to_read_only_investigator():
    from core.bootstrap import bootstrap_registry
    bootstrap_registry()
    semantic=deterministic_interpret("Como resolvo um enlace indisponível?")
    plan=build_plan("Como resolvo um enlace indisponível?",semantic)
    assert semantic.intent=="incident_analysis" and semantic.domain=="network"
    assert "zabbix.investigate" in plan["tools"]
