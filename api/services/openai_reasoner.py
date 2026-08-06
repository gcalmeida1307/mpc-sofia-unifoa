from __future__ import annotations

from ai.client import OpenAIResponsesClient
from config.settings import settings


def has_openai_enabled() -> bool:
    return bool(settings.ANTHROPIC_API_KEY.strip())


def has_llm_enabled() -> bool:
    return bool(settings.ANTHROPIC_API_KEY.strip()) or bool(settings.OLLAMA_BASE_URL.strip() and settings.OLLAMA_MODEL.strip())


def generate_answer(question: str, evidence: str) -> str | None:
    if not has_llm_enabled():
        return None

    system_prompt = (
        "Voce e o SOFIA, assistente de operacoes NOC. "
        "Responda de forma objetiva em portugues do Brasil, usando somente as evidencias fornecidas. "
        "Se faltar dado para concluir, diga claramente o que falta e qual proximo passo tecnico executar."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Pergunta: {question}\n\n"
                f"Evidencias:\n{evidence}\n\n"
                "Gere uma resposta curta, util e acionavel."
            ),
        },
    ]

    try:
        result = OpenAIResponsesClient().ask(messages)
        if not result:
            return None
        return str(result.get("text", "")).strip() or None
    except Exception:
        return None
