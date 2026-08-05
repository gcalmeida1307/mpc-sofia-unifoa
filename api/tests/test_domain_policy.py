from unittest.mock import Mock

from ai.domain_policy import OUT_OF_SCOPE_MESSAGE, is_it_question
from routes import ai


def test_domain_policy_accepts_information_technology_topics():
    for question in [
        "Como configurar DNS?",
        "Explique banco de dados PostgreSQL",
        "Qual a diferença entre IA e aprendizado de máquina?",
        "O Zabbix detectou perda de pacotes na VLAN",
        "Quais normas de segurança da informação devo usar?",
    ]:
        assert is_it_question(question)


def test_domain_policy_rejects_unrelated_topics():
    assert not is_it_question("Qual é a melhor receita de bolo de chocolate?")
    assert not is_it_question("Quem venceu o campeonato de futebol?")


def test_out_of_scope_does_not_call_claude_or_train(monkeypatch):
    service = Mock(); store = Mock()
    monkeypatch.setattr(ai, "openai_service", service)
    monkeypatch.setattr(ai, "postgres_store", store)
    response = ai.ask(ai.AIAskRequest(question="Qual a melhor receita de bolo?"))
    assert response["answer"] == OUT_OF_SCOPE_MESSAGE
    assert response["llm_used"] is False
    assert response["learning"]["stored"] is False
    service.answer.assert_not_called(); store.add_message.assert_not_called()


def test_similar_offline_fragment_does_not_short_circuit_chat(monkeypatch):
    service=Mock();store=Mock()
    service.answer.return_value={'answer':'DNS traduz nomes para enderecos IP.','learning':{},'plan':{},'reasoning':{},'critic':{},'confidence':0.8,'explainability':{},'context':{},'llm_used':True}
    monkeypatch.setattr(ai,'openai_service',service)
    monkeypatch.setattr(ai,'postgres_store',store)
    response=ai.ask(ai.AIAskRequest(question='Como funciona o DNS?'))
    assert response['source']=='claude-learning-pipeline'
    assert 'DNS traduz' in response['answer']
    service.answer.assert_called_once()


def test_common_infrastructure_terms_are_in_scope():
    assert is_it_question('O que é host?')
    assert is_it_question('Quais switches não respondem ao ping ICMP?')
