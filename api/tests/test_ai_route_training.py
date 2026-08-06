from unittest.mock import Mock

from routes import ai
from semantic.fallback import deterministic_interpret


def test_ai_ask_persists_question_and_answer_for_training(monkeypatch):
    store = Mock()
    service = Mock()
    service.answer.return_value = {
        "answer": "Resposta reutilizável",
        "learning": {"signature": "learning-123", "knowledge_updated": True},
    }
    monkeypatch.setattr(ai, "postgres_store", store)
    monkeypatch.setattr(ai, "openai_service", service)
    monkeypatch.setattr(ai.semantic_gateway, "interpret", lambda question: deterministic_interpret("O que é virtualização?"))

    response = ai.ask(ai.AIAskRequest(question="O que é virtualização?"))

    assert response["answer"] == "Resposta reutilizável"
    assert response["learning"]["knowledge_updated"] is True
    assert store.add_message.call_count == 2
    store.add_message.assert_any_call(
        "user",
        "O que é virtualização?",
        {"channel": "ai", "purpose": "training"},
    )
    store.add_message.assert_any_call(
        "assistant",
        "Resposta reutilizável",
        {"channel": "ai", "purpose": "training", "learning_signature": "learning-123"},
    )
