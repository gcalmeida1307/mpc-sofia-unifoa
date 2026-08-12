from hashlib import sha256

from services.postgres_store import postgres_store
from services.qdrant_store import qdrant_store


def _signature(topic: str, payload: dict) -> str:
    value = f"{topic}:{payload.get('host', '')}:{payload.get('generated_at', '')}:{payload.get('problem_count', 0)}"
    return sha256(value.encode("utf-8")).hexdigest()


def _host_down(payload: dict) -> None:
    host = payload.get("host", "unknown")
    summary = f"Host {host} entrou em estado DOWN segundo o monitoramento instalado."
    postgres_store.save_insight(_signature("host.down", payload), "event.host.down", summary, payload)
    qdrant_store.add_text(summary, {"topic": "host.down", "host": host, "source": "event_bus"})


def _host_recovered(payload: dict) -> None:
    host = payload.get("host", "unknown")
    summary = f"Host {host} voltou ao estado UP segundo o monitoramento instalado."
    postgres_store.save_insight(_signature("host.recovered", payload), "event.host.recovered", summary, payload)
    qdrant_store.add_text(summary, {"topic": "host.recovered", "host": host, "source": "event_bus"})


def register(event_bus) -> None:
    event_bus.subscribe("host.down", _host_down)
    event_bus.subscribe("host.recovered", _host_recovered)
