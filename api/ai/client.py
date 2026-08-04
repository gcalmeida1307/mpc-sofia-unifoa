from __future__ import annotations

import requests
from config.settings import settings


class OpenAIResponsesClient:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY.strip()
        self.openai_model = settings.OPENAI_MODEL
        self.openai_url = "https://api.openai.com/v1/responses"
        self.ollama_base_url = settings.OLLAMA_BASE_URL.strip().rstrip("/")
        self.ollama_model = settings.OLLAMA_MODEL.strip()
        self.ollama_fallback_model = settings.OLLAMA_FALLBACK_MODEL.strip()
        self.ollama_api_key = settings.OLLAMA_API_KEY.strip()
        self.ollama_mode = settings.OLLAMA_MODE.strip().lower()
        self.request_timeout = max(10, int(settings.REQUEST_TIMEOUT))

    @property
    def enabled(self) -> bool:
        return bool(self.openai_api_key) or bool(self.ollama_base_url and self.ollama_model)

    def ask(self, messages: list[dict]) -> dict | None:
        if not messages:
            return None

        # Prefer local provider first for operational latency and resilience.
        result = self._ask_ollama(messages)
        if result and result.get("text"):
            return result

        result = self._ask_openai(messages)
        if result and result.get("text"):
            return result

        return None

    def _ask_openai(self, messages: list[dict]) -> dict | None:
        if not self.openai_api_key:
            return None

        payload = {
            "model": self.openai_model,
            "input": messages,
        }

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }

        try:
            # OpenAI is secondary in this stack; fail fast if unavailable/quota-limited.
            response = requests.post(self.openai_url, headers=headers, json=payload, timeout=min(self.request_timeout, 12))
            response.raise_for_status()
            data = response.json()
            return {
                "text": data.get("output_text"),
                "usage": data.get("usage", {}),
                "model": data.get("model", self.openai_model),
                "provider": "openai",
            }
        except Exception:
            return None

    def _ask_ollama(self, messages: list[dict]) -> dict | None:
        if not self.ollama_base_url or not self.ollama_model:
            return None

        primary_timeout = min(self.request_timeout, 10)
        fallback_timeout = min(self.request_timeout, 10)

        result = self._ask_ollama_with_model(messages=messages, model=self.ollama_model, timeout=primary_timeout)
        if result and result.get("text"):
            return result

        if self.ollama_fallback_model and self.ollama_fallback_model != self.ollama_model:
            result = self._ask_ollama_with_model(messages=messages, model=self.ollama_fallback_model, timeout=fallback_timeout)
            if result and result.get("text"):
                return result

        return None

    def _ask_ollama_with_model(self, messages: list[dict], model: str, timeout: int) -> dict | None:
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
                    "max_tokens": 48,
                }
                response = requests.post(
                    f"{self.ollama_base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                data = response.json()
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
                    "num_predict": 48,
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
            return {
                "text": data.get("message", {}).get("content", ""),
                "usage": {
                    "input_tokens": data.get("prompt_eval_count", 0),
                    "output_tokens": data.get("eval_count", 0),
                },
                "model": data.get("model", model),
                "provider": "ollama",
            }
        except Exception:
            return None

    @staticmethod
    def _normalize_message_for_ollama(item: dict) -> dict:
        role = str(item.get("role", "user") or "user").strip().lower()
        if role not in {"system", "user", "assistant"}:
            role = "system" if role == "developer" else "user"
        return {
            "role": role,
            "content": item.get("content", ""),
        }
