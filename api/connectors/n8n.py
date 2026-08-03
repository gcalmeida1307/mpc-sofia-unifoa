from __future__ import annotations

import requests

from config.settings import settings


class N8NConnector:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.N8N_BASE_URL).rstrip("/")

    def trigger_webhook(self, webhook_name: str, payload: dict):
        webhook = webhook_name.strip() or settings.N8N_DEFAULT_WEBHOOK
        url = f"{self.base_url}/webhook/{webhook}"
        response = requests.post(url, json=payload, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            return response.json()
        return {"status": "ok", "text": response.text[:400]}


n8n_connector = N8NConnector()