from __future__ import annotations

from hashlib import sha1
from typing import Any

from services.postgres_store import postgres_store
from services.qdrant_store import qdrant_store


def _build_signature(topic: str, payload: dict[str, Any]) -> str:
    base = f"{topic}:{payload.get('host', '')}:{payload.get('generated_at', '')}:{payload.get('problem_count', 0)}"
    return sha1(base.encode("utf-8")).hexdigest()


def _handle_host_down(payload: dict[str, Any]) -> None:
    host = payload.get("host", "unknown")
    summary = f"Host {host} entrou em estado DOWN segundo snapshot do Zabbix."
    signature = _build_signature("host.down", payload)
    postgres_store.save_insight(signature, "event.host.down", summary, payload)
    qdrant_store.add_text(summary, {"topic": "host.down", "host": host, "source": "event_bus"})


def _handle_host_recovered(payload: dict[str, Any]) -> None:
    host = payload.get("host", "unknown")
    summary = f"Host {host} voltou ao estado UP segundo snapshot do Zabbix."
    signature = _build_signature("host.recovered", payload)
    postgres_store.save_insight(signature, "event.host.recovered", summary, payload)
    qdrant_store.add_text(summary, {"topic": "host.recovered", "host": host, "source": "event_bus"})


def _handle_ai_answered(payload: dict[str, Any]) -> None:
    question = payload.get("question", "")
    answer = payload.get("answer", "")
    summary = "Resposta gerada pela camada de IA do SOFIA"
    signature = _build_signature("ai.answered", {"host": "", "generated_at": payload.get("generated_at", "")})
    postgres_store.save_insight(
        signature,
        "event.ai.answered",
        summary,
        {"question": question[:500], "answer": answer[:1000], "llm_used": payload.get("llm_used", False)},
    )


def _handle_investigation_created(payload: dict[str, Any]) -> None:
    watcher = payload.get("watcher", "unknown")
    title = payload.get("title", "investigation")
    summary = payload.get("summary", "Autonomous investigation created.")
    signature = _build_signature("investigation.created", {"host": watcher, "generated_at": title})
    postgres_store.save_insight(
        signature,
        "event.investigation.created",
        summary,
        {
            "watcher": watcher,
            "title": title,
            "severity": payload.get("severity", "unknown"),
        },
    )
    qdrant_store.add_text(summary, {"topic": "investigation.created", "watcher": watcher, "source": "event_bus"})


def register_default_event_handlers(event_bus: Any) -> None:
    event_bus.subscribe("host.down", _handle_host_down)
    event_bus.subscribe("host.recovered", _handle_host_recovered)
    event_bus.subscribe("ai.answered", _handle_ai_answered)
    event_bus.subscribe("investigation.created", _handle_investigation_created)
