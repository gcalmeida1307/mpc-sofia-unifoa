from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any

from anthropic import Anthropic
from google import genai
from ollama import Client as OllamaClient
from openai import OpenAI

from .privacy import external_data_allowed


@dataclass(frozen=True)
class Generation:
    answer: str
    provider: str
    model: str


def _configured(provider: str) -> bool:
    if provider == "auto":
        return True
    if provider in {"gemini", "claude", "openai"} and not external_data_allowed():
        return False
    keys = {
        "gemini": "GEMINI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
    }
    return provider == "ollama" or bool(os.getenv(keys.get(provider, "")))


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on", "sim"}


def _timeout_seconds(override: float | None = None) -> float:
    if override is not None:
        return max(1.5, min(180.0, float(override)))
    try:
        return max(5.0, min(180.0, float(os.getenv("SOFIA_PROVIDER_TIMEOUT_SECONDS", "25"))))
    except ValueError:
        return 25.0


def _generate_gemini(model: str, system: str, prompt: str, max_output_tokens: int) -> str:
    """Create and close one Gemini client inside the worker thread."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "system_instruction": system,
                "max_output_tokens": max_output_tokens,
                "temperature": 0.2,
            },
        )
        return response.text or ""
    finally:
        client.close()


def _generate_openai(model: str, system: str, prompt: str, history: list[dict[str, str]], max_output_tokens: int) -> str:
    """Call the Responses API from a worker thread; credentials stay server-side."""
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    input_items = [
        {"role": item["role"], "content": item["content"]}
        for item in history
        if item.get("role") in {"user", "assistant"} and item.get("content", "").strip()
    ]
    input_items.append({"role": "user", "content": prompt})
    try:
        response = client.responses.create(
            model=model,
            instructions=system,
            input=input_items,
            max_output_tokens=max_output_tokens,
            store=_env_bool("OPENAI_STORE_RESPONSES", False),
        )
        return response.output_text or ""
    finally:
        close = getattr(client, "close", None)
        if close:
            close()


async def generate(provider: str, system: str, prompt: str, history: list[dict[str, str]], max_output_tokens: int = 280, timeout_seconds: float | None = None) -> Generation:
    timeout = _timeout_seconds(timeout_seconds)
    if provider == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        answer = await asyncio.wait_for(asyncio.to_thread(_generate_gemini, model, system, prompt, max_output_tokens), timeout=timeout)
        return Generation(answer, provider, model)
    if provider == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-5.5")
        answer = await asyncio.wait_for(asyncio.to_thread(_generate_openai, model, system, prompt, history, max_output_tokens), timeout=timeout)
        return Generation(answer, provider, model)
    if provider == "claude":
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        response = await asyncio.wait_for(asyncio.to_thread(Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]).messages.create, model=model, max_tokens=max_output_tokens, system=system, messages=history + [{"role": "user", "content": prompt}]), timeout=timeout)
        return Generation("".join(block.text for block in response.content if hasattr(block, "text")), provider, model)
    model = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
    try:
        num_predict = max(128, min(768, int(os.getenv("OLLAMA_NUM_PREDICT", str(max_output_tokens)))))
    except ValueError:
        num_predict = 256
    response: Any = await asyncio.wait_for(asyncio.to_thread(
        OllamaClient(host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"), timeout=timeout).chat,
        model=model,
        messages=[{"role": "system", "content": system}, *history, {"role": "user", "content": prompt}],
        think=False,
        options={"temperature": 0.2, "num_predict": num_predict},
    ), timeout=timeout)
    return Generation(response["message"]["content"], provider, model)


async def generate_with_fallback(preferred: str, system: str, prompt: str, history: list[dict[str, str]], max_output_tokens: int = 280, timeout_seconds: float | None = None, external_allowed: bool | None = None) -> Generation:
    allow_external = external_data_allowed() if external_allowed is None else external_allowed
    if preferred == "auto":
        # Cloud providers só entram no circuito quando a implantação local
        # recebeu opt-in explícito. Sem isso, o automático fica integralmente
        # local e continua usando o RAG/MCP antes de gerar a resposta.
        cloud_first = ("openai", "gemini", "claude") if allow_external else ()
        providers = [*cloud_first, "ollama"]
    else:
        providers = [preferred] + [candidate for candidate in ("openai", "gemini", "claude", "ollama") if candidate != preferred and (candidate == "ollama" or allow_external) and _configured(candidate)]
    providers = list(dict.fromkeys(providers))
    errors: list[str] = []
    for provider in providers:
        if not _configured(provider):
            errors.append(f"{provider}: chave não configurada")
            continue
        try:
            result = await generate(provider, system, prompt, history, max_output_tokens, timeout_seconds)
            if result.answer.strip():
                return result
            errors.append(f"{provider}: resposta vazia")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{provider}: {exc}")
    raise RuntimeError("Nenhum provider respondeu. " + " | ".join(errors))
