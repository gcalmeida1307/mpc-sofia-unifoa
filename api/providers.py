from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic
from google import genai
from ollama import Client as OllamaClient


@dataclass(frozen=True)
class Generation:
    answer: str
    provider: str
    model: str


def _configured(provider: str) -> bool:
    return provider == "ollama" or bool(os.getenv("GEMINI_API_KEY" if provider == "gemini" else "ANTHROPIC_API_KEY"))


async def generate(provider: str, system: str, prompt: str, history: list[dict[str, str]]) -> Generation:
    if provider == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        response = await asyncio.to_thread(genai.Client(api_key=os.environ["GEMINI_API_KEY"]).models.generate_content, model=model, contents=prompt, config={"system_instruction": system})
        return Generation(response.text or "", provider, model)
    if provider == "claude":
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        response = await asyncio.to_thread(Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]).messages.create, model=model, max_tokens=2048, system=system, messages=history + [{"role": "user", "content": prompt}])
        return Generation("".join(block.text for block in response.content if hasattr(block, "text")), provider, model)
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    response: Any = await asyncio.to_thread(OllamaClient(host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")).chat, model=model, messages=[{"role": "system", "content": system}, *history, {"role": "user", "content": prompt}])
    return Generation(response["message"]["content"], provider, model)


async def generate_with_fallback(preferred: str, system: str, prompt: str, history: list[dict[str, str]]) -> Generation:
    providers = [preferred] + [candidate for candidate in ("gemini", "claude", "ollama") if candidate != preferred and _configured(candidate)]
    errors: list[str] = []
    for provider in providers:
        if not _configured(provider):
            errors.append(f"{provider}: chave não configurada")
            continue
        try:
            result = await generate(provider, system, prompt, history)
            if result.answer.strip():
                return result
            errors.append(f"{provider}: resposta vazia")
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
    raise RuntimeError("Nenhum provider respondeu. " + " | ".join(errors))
