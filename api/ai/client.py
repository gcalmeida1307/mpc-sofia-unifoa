from __future__ import annotations

import json
import re

import requests
from config.settings import settings
from core.observability import LLM_REQUESTS, LLM_TOKENS


class ReasoningProvider:
    def __init__(self):
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY.strip()
        self.anthropic_model = settings.ANTHROPIC_MODEL
        self.anthropic_max_tokens = settings.ANTHROPIC_MAX_TOKENS
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
        self.ollama_base_url = settings.OLLAMA_BASE_URL.strip().rstrip("/")
        self.ollama_model = settings.OLLAMA_MODEL.strip()
        self.ollama_fallback_model = settings.OLLAMA_FALLBACK_MODEL.strip()
        self.ollama_api_key = settings.OLLAMA_API_KEY.strip()
        self.ollama_mode = settings.OLLAMA_MODE.strip().lower()
        self.request_timeout = max(10, int(settings.REQUEST_TIMEOUT))
        self.last_anthropic_error: str | None = None
        self.last_ollama_error: str | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.anthropic_api_key) or bool(self.ollama_base_url and self.ollama_model)

    def ask(self, messages: list[dict]) -> dict | None:
        return self.reason(messages)

    def reason(self, messages: list[dict], *, max_tokens: int | None = None) -> dict | None:
        if not messages:
            return None

        result = self._ask_anthropic(messages, max_tokens=max_tokens) if max_tokens else self._ask_anthropic(messages)
        if result and result.get("text"):
            return result

        result = self._ask_ollama(messages, max_tokens=max_tokens) if max_tokens else self._ask_ollama(messages)
        if result and result.get("text"):
            return result

        return None

    def interpret(self, *, question: str, schema: dict, examples: list[dict]) -> dict | None:
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o gateway semântico da SOFIA. Converta a pergunta somente em um objeto JSON "
                    "compatível com o schema fornecido. Não inclua markdown, explicações, comandos, SQL ou campos extras. "
                    "Não invente nomes: use null e ambiguities quando a pergunta não informar algo."
                ),
            },
            {"role": "developer", "content": json.dumps({"schema": schema, "examples": examples}, ensure_ascii=False)},
            {"role": "user", "content": question},
        ]
        result = self.reason(messages, max_tokens=512)
        if not result or not result.get("text"):
            return None
        parsed = self._parse_json_object(str(result["text"]))
        return {"data": parsed, "provider": result.get("provider", "unknown"), "usage": result.get("usage", {})} if parsed else None

    def summarize(self, content: str) -> dict | None:
        return self.reason([{"role":"system","content":"Resuma objetivamente, preservando fatos e incertezas."},{"role":"user","content":content}])

    def criticize(self, content: str) -> dict | None:
        return self.reason([{"role":"system","content":"Revise precisão, evidências e riscos. Não invente fatos."},{"role":"user","content":content}])

    @staticmethod
    def _parse_json_object(text: str) -> dict | None:
        value = text.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", value, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            value = fenced.group(1)
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
        return parsed if isinstance(parsed, dict) else None

    def _ask_anthropic(self, messages: list[dict], max_tokens: int | None = None) -> dict | None:
        if not self.anthropic_api_key:
            return None
        system = "\n\n".join(str(item.get("content", "")) for item in messages if item.get("role") in {"system", "developer"})
        payload = {
            "model": self.anthropic_model,
            "max_tokens": min(self.anthropic_max_tokens, max_tokens) if max_tokens else self.anthropic_max_tokens,
            "cache_control": {"type": "ephemeral"},
            "messages": [self._normalize_message_for_ollama(item) for item in messages if item.get("role") not in {"system", "developer"}],
        }
        if system:
            payload["system"] = system
        headers = {"x-api-key": self.anthropic_api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
        try:
            response = requests.post(self.anthropic_url, headers=headers, json=payload, timeout=self.request_timeout)
            response.raise_for_status()
            self.last_anthropic_error = None
            data = response.json()
            usage = data.get("usage", {})
            LLM_REQUESTS.labels(provider="anthropic", status="success").inc()
            LLM_TOKENS.labels(provider="anthropic", direction="input").inc(int(usage.get("input_tokens", 0) or 0))
            LLM_TOKENS.labels(provider="anthropic", direction="output").inc(int(usage.get("output_tokens", 0) or 0))
            return {
                "text": "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"),
                "usage": usage,
                "model": data.get("model", self.anthropic_model),
                "provider": "anthropic",
            }
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 0
            self.last_anthropic_error = self._classify_provider_error(status)
            LLM_REQUESTS.labels(provider="anthropic", status=self.last_anthropic_error).inc()
            return None
        except requests.RequestException:
            self.last_anthropic_error = "unavailable"
            LLM_REQUESTS.labels(provider="anthropic", status="unavailable").inc()
            return None

    def _ask_ollama(self, messages: list[dict], max_tokens: int | None = None) -> dict | None:
        if not self.ollama_base_url or not self.ollama_model:
            return None

        primary_timeout = min(self.request_timeout, 10)
        fallback_timeout = min(self.request_timeout, 10)

        result = self._ask_ollama_with_model(messages=messages, model=self.ollama_model, timeout=primary_timeout, max_tokens=max_tokens)
        if result and result.get("text"):
            return result

        if self.ollama_fallback_model and self.ollama_fallback_model != self.ollama_model:
            result = self._ask_ollama_with_model(messages=messages, model=self.ollama_fallback_model, timeout=fallback_timeout, max_tokens=max_tokens)
            if result and result.get("text"):
                return result

        return None

    def _ask_ollama_with_model(self, messages: list[dict], model: str, timeout: int, max_tokens: int | None = None) -> dict | None:
        if not model:
            return None

        headers = {"Content-Type": "application/json"}
        if self.ollama_api_key:
            headers["Authorization"] = f"Bearer {self.ollama_api_key}"

        try:
            if self.ollama_mode == "openai":
                payload = {
                    "model": model,
                    "messages": [self._normalize_message_for_ollama(item) for item in messages],
                    "temperature": 0.2,
                    "max_tokens": max_tokens or 48,
                }
                response = requests.post(
                    f"{self.ollama_base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
                LLM_REQUESTS.labels(provider="ollama", status="success").inc()
                choices = data.get("choices", [])
                text = ""
                if choices and isinstance(choices[0], dict):
                    text = choices[0].get("message", {}).get("content", "")
                return {
                    "text": text,
                    "usage": data.get("usage", {}),
                    "model": data.get("model", model),
                    "provider": "ollama",
                }

            payload = {
                "model": model,
                "messages": [self._normalize_message_for_ollama(item) for item in messages],
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": max_tokens or 48,
                },
            }
            response = requests.post(
                f"{self.ollama_base_url}/api/chat",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()
            LLM_REQUESTS.labels(provider="ollama", status="success").inc()
            LLM_TOKENS.labels(provider="ollama", direction="input").inc(int(data.get("prompt_eval_count", 0) or 0))
            LLM_TOKENS.labels(provider="ollama", direction="output").inc(int(data.get("eval_count", 0) or 0))
            return {
                "text": data.get("message", {}).get("content", ""),
                "usage": {
                    "input_tokens": data.get("prompt_eval_count", 0),
                    "output_tokens": data.get("eval_count", 0),
                },
                "model": data.get("model", model),
                "provider": "ollama",
            }
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 0
            self.last_ollama_error = self._classify_provider_error(status)
            LLM_REQUESTS.labels(provider="ollama", status=self.last_ollama_error).inc()
            return None
        except requests.RequestException:
            self.last_ollama_error = "unavailable"
            LLM_REQUESTS.labels(provider="ollama", status="unavailable").inc()
            return None

    @staticmethod
    def _classify_provider_error(status: int) -> str:
        if status in {401, 403}:
            return "invalid_or_expired_key"
        if status in {402, 429}:
            return "credit_or_rate_limit"
        if status >= 500:
            return "provider_unavailable"
        return f"http_{status}" if status else "unavailable"

    @staticmethod
    def _normalize_message_for_ollama(item: dict) -> dict:
        role = str(item.get("role", "user") or "user").strip().lower()
        if role not in {"system", "user", "assistant"}:
            role = "system" if role == "developer" else "user"
        return {
            "role": role,
            "content": item.get("content", ""),
        }


# Compatibility for integrations that still import the former vendor-shaped name.
OpenAIResponsesClient = ReasoningProvider
