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
            rows = conn.execute("""SELECT intent,knowledge_updated,created_at
                FROM ai_learning_cycles ORDER BY created_at DESC LIMIT 5""").fetchall()
        now = datetime.now(timezone.utc)
        last_at = totals[2]
        in_progress = bool(last_at and (now - last_at).total_seconds() < 45)
        return {
            "cycles": totals[0], "knowledge_updates": totals[1],
            "last_training_at": last_at.isoformat() if last_at else None,
            "status": "in_progress" if in_progress else "completed" if last_at else "idle",
            "status_message": "Treinamento em curso" if in_progress else "Treinamento concluído" if last_at else "Aguardando primeiro treinamento",
            "recent_activity": [{"intent":r[0],"knowledge_updated":r[1],"status":"completed","message":"Treinamento concluído","created_at":r[2].isoformat()} for r in rows],
        }
    except Exception:
        return {"cycles": 0, "knowledge_updates": 0, "status":"idle", "status_message":"Aguardando primeiro treinamento", "recent_activity": []}


def _hourly_device_timeline(hours: int = 12) -> list[dict[str, Any]]:
    try:
        with postgres_store._connect() as conn:
            rows = conn.execute("""
                SELECT DISTINCT ON (hour) hour, generated_at, summary, payload, readings
                FROM (
                    SELECT date_trunc('hour', generated_at) AS hour, generated_at, summary, payload,
                           COUNT(*) OVER (PARTITION BY date_trunc('hour', generated_at))::int AS readings
                    FROM domain_snapshots
                    WHERE domain_id='infrastructure' AND generated_at >= NOW() - (%s || ' hours')::interval
                ) hourly
                ORDER BY hour, generated_at DESC
            """, (str(max(2, min(hours, 48))),)).fetchall()
        result = []
        previous_items: dict[str, dict[str, Any]] | None = None
        previous_total: int | None = None
        for hour, _generated_at, summary, payload, readings in rows:
            summary=summary or {};problems=((payload or {}).get("zabbix") or {}).get("problems",[]) or []
            current_items={str(item.get("eventid")):item for item in problems if item.get("eventid")};current_total=int(summary.get("problems",len(current_items)) or 0)
            if previous_items is None:
                new_items=[];resolved_items=[]
            else:
                new_items=[current_items[key] for key in current_items.keys()-previous_items.keys()]
                resolved_items=[previous_items[key] for key in previous_items.keys()-current_items.keys()]
            delta=0 if previous_total is None else current_total-previous_total
            complete=current_total==len(current_items) and (previous_total is None or previous_total==len(previous_items or {}))
            if previous_items is None: explanation="Primeiro ponto do período"
            elif complete: explanation=f"{len(new_items)} alerta(s) entraram e {len(resolved_items)} foram resolvidos"
            else: explanation=f"O total variou {delta:+d}; os exemplos abaixo pertencem ao recorte disponível"
            result.append({"hour":hour.isoformat(),"devices":int(summary.get("hosts",0) or 0),"problems":current_total,"readings":int(readings),"change":delta,"new_count":len(new_items) if complete else max(0,delta),"resolved_count":len(resolved_items) if complete else max(0,-delta),"new_alerts":[str(item.get("name") or "Alerta sem descrição") for item in new_items[:5]],"resolved_alerts":[str(item.get("name") or "Alerta sem descrição") for item in resolved_items[:5]],"explanation":explanation,"complete_comparison":complete})
            previous_items=current_items;previous_total=current_total
        return result
    except Exception:
        return []


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
        "device_timeline":_hourly_device_timeline(),
    }
