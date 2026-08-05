from unittest.mock import Mock

from routes import ai


def test_ai_ask_persists_question_and_answer_for_training(monkeypatch):
    store = Mock()
    service = Mock()
    service.answer.return_value = {
        "answer": "Resposta reutilizável",
        "learning": {"signature": "learning-123", "knowledge_updated": True},
    }
    monkeypatch.setattr(ai, "postgres_store", store)
    monkeypatch.setattr(ai, "openai_service", service)

    response = ai.ask(ai.AIAskRequest(question="Como está o ambiente?"))

    assert response["answer"] == "Resposta reutilizável"
    assert response["learning"]["knowledge_updated"] is True
    assert store.add_message.call_count == 2
    store.add_message.assert_any_call(
        "user",
        "Como está o ambiente?",
        {"channel": "ai", "purpose": "training"},
    )
    store.add_message.assert_any_call(
        "assistant",
        "Resposta reutilizável",
        {"channel": "ai", "purpose": "training", "learning_signature": "learning-123"},
    )
