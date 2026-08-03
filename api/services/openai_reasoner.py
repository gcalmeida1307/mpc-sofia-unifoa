from __future__ import annotations

import requests

from config.settings import settings


OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def has_openai_enabled() -> bool:
    return bool(settings.OPENAI_API_KEY.strip())


def generate_answer(question: str, evidence: str) -> str | None:
    if not has_openai_enabled():
        return None

    system_prompt = (
        "Você é o SOFIA, assistente de operações NOC. "
        "Responda de forma objetiva em português do Brasil, usando somente as evidências fornecidas. "
        "Se faltar dado para concluir, diga claramente o que falta e qual próximo passo técnico executar."
    )

    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Pergunta: {question}\n\n"
                    f"Evidências:\n{evidence}\n\n"
                    "Gere uma resposta curta, útil e acionável."
                ),
            },
        ],
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
