from __future__ import annotations

import requests
from config.settings import settings


class OpenAIResponsesClient:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY.strip()
        self.model = settings.OPENAI_MODEL
        self.url = "https://api.openai.com/v1/responses"

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def ask(self, messages: list[dict]) -> str | None:
        if not self.enabled:
            return None

        payload = {
            "model": self.model,
            "input": messages,
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=25)
            response.raise_for_status()
            data = response.json()
            return data.get("output_text")
        except Exception:
            return None
