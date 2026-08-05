from __future__ import annotations

import os
import socket
from datetime import datetime, timezone
from typing import Any

import requests

from config.settings import settings
from services.infrastructure import get_server_resources
from services.postgres_store import postgres_store
from ai.service import openai_service


def _tcp_status(host: str, port: int) -> str:
    try:
        with socket.create_connection((host, port), timeout=1.2):
            return "online"
    except OSError:
        return "offline"


def _http_status(url: str) -> str:
    try:
        response = requests.get(url, timeout=1.5)
        return "online" if response.status_code < 500 else "degraded"
    except requests.RequestException:
        return "offline"


def _database_details() -> dict[str, Any]:
    try:
        with postgres_store._connect() as conn:
            row = conn.execute("""SELECT pg_database_size(current_database())::bigint,
                (SELECT count(*) FROM pg_stat_activity WHERE datname=current_database()),
                current_setting('max_connections')::int""").fetchone()
        size_bytes, connections, max_connections = row
        return {
            "size_mb": round(size_bytes / 1024 / 1024, 2),
            "size_gb": round(size_bytes / 1024 / 1024 / 1024, 3),
            "connections": connections,
            "max_connections": max_connections,
            "connection_percent": round((connections / max_connections) * 100, 1) if max_connections else 0,
        }
    except Exception:
        return {"status": "unavailable"}


def _training_activity() -> dict[str, Any]:
    try:
        with postgres_store._connect() as conn:
            totals = conn.execute("""SELECT count(*), count(*) FILTER (WHERE knowledge_updated),
                max(created_at) FROM ai_learning_cycles""").fetchone()
            rows = conn.execute("""SELECT question,intent,knowledge_updated,created_at
                FROM ai_learning_cycles ORDER BY created_at DESC LIMIT 12""").fetchall()
        return {
            "cycles": totals[0], "knowledge_updates": totals[1],
            "last_training_at": totals[2].isoformat() if totals[2] else None,
            "recent_prompts": [{"question":r[0][:240],"intent":r[1],"knowledge_updated":r[2],"created_at":r[3].isoformat()} for r in rows],
        }
    except Exception:
        return {"cycles": 0, "knowledge_updates": 0, "recent_prompts": []}


def _provider_status() -> list[dict[str, Any]]:
    last_provider = None; last_at = None
    try:
        with postgres_store._connect() as conn:
            row=conn.execute("SELECT metadata->>'llm_provider',created_at FROM ai_response_metrics WHERE llm_used=TRUE ORDER BY created_at DESC LIMIT 1").fetchone()
            if row: last_provider,last_at=row[0],row[1]
    except Exception:
        pass
    anthropic_configured=bool(settings.ANTHROPIC_API_KEY.strip())
    last_error = openai_service.client.last_anthropic_error
    anthropic_status = last_error or ("operational" if anthropic_configured and last_provider=="anthropic" else ("configured" if anthropic_configured else "not_configured"))
    error_help = {
        "invalid_or_expired_key": "Chave inválida ou expirada. Revise ANTHROPIC_API_KEY.",
        "credit_or_rate_limit": "Sem crédito ou limite de requisições atingido.",
        "provider_unavailable": "Serviço Anthropic temporariamente indisponível.",
        "unavailable": "Falha de conexão com Anthropic.",
    }
    anthropic_detail = error_help.get(last_error) if last_error else (f"Último uso confirmado: {last_at.isoformat()}" if last_at and last_provider=="anthropic" else "Aguardando chamada válida" if anthropic_configured else "ANTHROPIC_API_KEY ausente")
    return [
        {"name":"Claude","status":anthropic_status,"detail":anthropic_detail},
        {"name":"Ollama","status":_http_status(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"),"detail":settings.OLLAMA_MODEL},
        {"name":"Grafana","status":"not_configured" if not os.getenv("GRAFANA_URL","").strip() else _http_status(os.getenv("GRAFANA_URL","").rstrip('/')+"/api/health"),"detail":"GRAFANA_URL/GRAFANA_TOKEN ausentes" if not os.getenv("GRAFANA_URL","").strip() else "API configurada"},
    ]


def dashboard_summary() -> dict[str, Any]:
    resources=get_server_resources(); resources["database"]=_database_details()
    return {
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "resources":resources,
        "services":[
            {"name":"SOFIA API","status":"online"},
            {"name":"PostgreSQL","status":_tcp_status("sofia_postgres",5432)},
            {"name":"Redis","status":_tcp_status("sofia_redis",6379)},
            {"name":"Qdrant","status":_http_status("http://sofia_qdrant:6333/healthz")},
            {"name":"Ollama","status":_http_status(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")},
            {"name":"n8n","status":_http_status("http://sofia_n8n:5678/healthz")},
            {"name":"Grafana","status":_http_status("http://sofia_grafana:3000/api/health")},
            {"name":"Prometheus","status":_http_status("http://sofia_prometheus:9090/-/ready")},
            {"name":"Loki","status":_http_status("http://sofia_loki:3100/ready")},
            {"name":"Alloy","status":_http_status("http://sofia_alloy:12345/-/ready")},
        ],
        "providers":_provider_status(),
        "training":_training_activity(),
    }
