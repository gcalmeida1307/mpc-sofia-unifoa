# FastAPI dependency injection intentionally uses call expressions in
# endpoint signatures; broad lifecycle guards also preserve cancellation
# semantics for background workers.
# ruff: noqa: B008, BLE001

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import os
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server import MCPServer
from pydantic import BaseModel, Field

from .agents import build_plan, memory_status, specialist_for
from .analyst import analyze_scenario
from .analytics import (
    feedback_assessment,
    initialize_analytics_store,
    record_learning_event,
    theme_report,
    update_feedback,
)
from .auth import (
    ADMIN_CODE,
    activate_account,
    authenticate,
    change_password,
    create_access_request,
    create_password_reset_token,
    create_session,
    create_user,
    decide_access_request,
    enable_activation_two_factor,
    enable_two_factor,
    get_inactivity_policy,
    has_module_access,
    initialize_user_store,
    list_access_requests,
    list_users,
    login_allowed,
    register_login_failure,
    register_login_success,
    require_admin,
    require_module_access,
    require_user,
    reset_password_with_token,
    revoke_session,
    rotate_session,
    set_inactivity_policy,
    set_user_active,
    setup_two_factor,
    verify_session,
)
from .contracts import PIPELINE_STAGES
from .domains import DEFAULT_CONTRACT, DOMAIN_CONTRACTS, domain_for, manifests
from .embeddings import build_all_embeddings, build_module_embeddings, embedding_status
from .evaluation import evaluate_corpus, evaluate_semantic_cases
from .expansion import (
    ExpansionStore,
    audit_module_documents,
    expansion_settings,
    expansion_status,
    expansion_storage_status,
    initialize_expansion,
    pipeline_documents,
    record_document_pipeline,
    record_search_topic,
    run_expansion_cycle,
)
from .fhir import (
    capability_statement,
    get_resource,
    initialize_fhir_store,
    patient_context,
    save_resource,
    search_resources,
)
from .ingestion import (
    ALLOWED_EXTENSIONS,
    IMAGE_EXTENSIONS,
    files_for,
    ingest_module,
    ocr_status,
)
from .insights import generate_module_insights, initialize_insights_store
from .insights import snapshot as insights_snapshot
from .integrations import initialize as initialize_integrations
from .integrations import status as integration_status
from .integrations import sync as sync_integration
from .knowledge_graph import build_graph, read_graph
from .links import LinkRepository, ingest_link, link_not_modified
from .llmops import trace_metrics
from .mcp_contracts import TOOL_CONTRACTS
from .mcp_contracts import contracts as tool_contracts
from .mcp_security import bind_user, module_allowed, reset_user
from .mcp_security import enforce_admin as enforce_mcp_admin
from .mcp_security import enforce_module as enforce_mcp_module
from .neural import graph as neural_model_graph
from .neural import infer as neural_model_infer
from .neural import status as neural_model_status
from .neural import train as train_neural_model
from .observability import TraceRecorder
from .observability import initialize as initialize_observability
from .observability import snapshot as observability_snapshot
from .orchestration import answer as orchestrate_answer
from .orchestration import normalize_language, normalize_response_style
from .policies import policy_for
from .privacy import (
    audit_event,
    external_clinical_allowed,
    external_data_allowed,
    initialize_privacy_store,
    provider_guard,
)
from .privacy import status as privacy_status
from .production_gate import production_gate as run_production_gate
from .query_analysis import assess_module_scope
from .readiness import readiness_checklist
from .research import research_module
from .retrieval import retrieve
from .storage import status as storage_status

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = ROOT / "knowledge"
logger = logging.getLogger("sofia.server")
load_dotenv(ROOT / ".env", override=False)
initialize_user_store()
initialize_fhir_store()
initialize_privacy_store()
initialize_integrations()
initialize_analytics_store(KNOWLEDGE_ROOT)
initialize_expansion(KNOWLEDGE_ROOT)
initialize_observability(KNOWLEDGE_ROOT)
initialize_insights_store(KNOWLEDGE_ROOT)

MODULE_CATALOG: dict[str, dict[str, str]] = {
    module_id: {
        "name": contract.name,
        "category": contract.category,
        "color": contract.color,
        "icon": contract.icon,
        "manager": contract.manager,
        "focus": contract.focus,
    }
    for module_id, contract in DOMAIN_CONTRACTS.items()
}
DEFAULT_MODULE = {
    "category": DEFAULT_CONTRACT.category,
    "color": DEFAULT_CONTRACT.color,
    "icon": DEFAULT_CONTRACT.icon,
    "manager": DEFAULT_CONTRACT.manager,
    "focus": DEFAULT_CONTRACT.focus,
}


def discover_modules() -> dict[str, dict[str, str]]:
    """Activate every first-level directory physically present in knowledge/."""
    KNOWLEDGE_ROOT.mkdir(parents=True, exist_ok=True)
    module_ids = sorted(path.name for path in KNOWLEDGE_ROOT.iterdir() if path.is_dir())
    return {
        module_id: {
            "name": module_id.replace("-", " ").title(),
            **DEFAULT_MODULE,
            **MODULE_CATALOG.get(module_id, {}),
        }
        for module_id in module_ids
    }


MODULES = discover_modules()
AUTO_TRAINING: dict[str, asyncio.Task[Any]] = {}
TRAINING_QUEUE: asyncio.Queue[str] | None = None
TRAINING_WORKER: asyncio.Task[Any] | None = None
TRAINING_QUEUED: set[str] = set()
TRAINING_REASONS: dict[str, str] = {}
TRAINING_LOCK: asyncio.Lock | None = None
LINK_REFRESH_TASK: asyncio.Task[Any] | None = None
EXPANSION_TASK: asyncio.Task[Any] | None = None
DOCUMENT_AUDIT_TASK: asyncio.Task[Any] | None = None


def normalize_access_scopes(scopes: list[str]) -> list[str]:
    normalized = {
        str(scope).strip().casefold() for scope in scopes if str(scope).strip()
    }
    if "core" in normalized:
        return ["CORE"]
    invalid = sorted(scope for scope in normalized if scope not in MODULES)
    if invalid:
        raise HTTPException(400, f"Módulo(s) inválido(s): {', '.join(invalid)}")
    if not normalized:
        raise HTTPException(400, "Escolha pelo menos um módulo ou CORE")
    return sorted(normalized)


def refresh_modules() -> None:
    MODULES.clear()
    MODULES.update(discover_modules())


def module_root(module_id: str) -> Path:
    if module_id not in MODULES:
        refresh_modules()
    if module_id not in MODULES:
        raise HTTPException(404, f"Módulo desconhecido: {module_id}")
    try:
        enforce_mcp_module(module_id)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    return KNOWLEDGE_ROOT / module_id


def require_statistics_admin(current: dict[str, Any]) -> None:
    """Statistics are restricted to the designated AG000001 account."""
    require_admin(current)
    if current.get("sub") != ADMIN_CODE:
        raise HTTPException(403, "Somente AG000001 pode consultar estatísticas")


def status_for(module_id: str) -> dict[str, Any]:
    paths = files_for(KNOWLEDGE_ROOT, module_id)
    type_counts = Counter(path.suffix.lower().lstrip(".") for path in paths)
    link_repository = LinkRepository(KNOWLEDGE_ROOT)
    try:
        link_count = len(link_repository.list(module_id))
        link_storage = link_repository.backend
    except RuntimeError as exc:
        logger.warning("%s", exc)
        link_count = 0
        link_storage = "postgresql-unavailable"
    neural = neural_model_status(KNOWLEDGE_ROOT, module_id)
    embeddings = embedding_status(KNOWLEDGE_ROOT, module_id)
    contract = domain_for(module_id)
    pipeline = expansion_status(KNOWLEDGE_ROOT, module_id)
    training_task = AUTO_TRAINING.get(module_id)
    training_state = (
        "em andamento"
        if training_task and not training_task.done()
        else (
            "na fila"
            if module_id in TRAINING_QUEUED
            else (
                "pendente"
                if neural.get("stale")
                else ("atualizado" if neural.get("trained") else "não treinado")
            )
        )
    )
    return {
        "id": module_id,
        **MODULES[module_id],
        "domain_contract": contract.manifest(),
        "path": str(module_root(module_id)),
        "documents": len(paths),
        "files": [path.name for path in paths],
        "documents_by_type": dict(sorted(type_counts.items())),
        "links": link_count,
        "link_storage": link_storage,
        "neural": neural,
        "embeddings": embeddings,
        "training_state": training_state,
        "auto_training": os.getenv("SOFIA_AUTO_TRAIN", "true").strip().casefold()
        not in {"0", "false", "no", "off"},
        "ready": bool(paths),
        "pipeline": {
            "documents_by_status": pipeline.get("documents_by_status", {}),
            "processing_errors": pipeline.get("processing_errors", 0),
        },
    }


async def training_worker() -> None:
    """Train one module at a time so large knowledge bases do not compete."""
    global TRAINING_QUEUE
    if TRAINING_QUEUE is None:
        TRAINING_QUEUE = asyncio.Queue()
    while True:
        module_id = await TRAINING_QUEUE.get()
        TRAINING_QUEUED.discard(module_id)
        try:
            try:
                epochs = max(
                    1, min(2_000, int(os.getenv("SOFIA_AUTO_TRAIN_EPOCHS", "24")))
                )
            except ValueError:
                epochs = 24
            trigger = TRAINING_REASONS.pop(module_id, "source_update")
            task = asyncio.create_task(_train_module(module_id, epochs, 0.08, trigger))
            AUTO_TRAINING[module_id] = task
            try:
                await task
            finally:
                AUTO_TRAINING.pop(module_id, None)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Treinamento automático falhou para %s: %s", module_id, exc)
        finally:
            TRAINING_QUEUE.task_done()


async def _train_module(
    module_id: str, epochs: int, learning_rate: float, trigger: str = "manual"
) -> dict[str, Any]:
    global TRAINING_LOCK
    if TRAINING_LOCK is None:
        TRAINING_LOCK = asyncio.Lock()
    async with TRAINING_LOCK:
        embedding_result = await asyncio.to_thread(
            build_module_embeddings, KNOWLEDGE_ROOT, module_id
        )
        result = await asyncio.to_thread(
            train_neural_model,
            KNOWLEDGE_ROOT,
            module_id,
            epochs,
            learning_rate,
            trigger,
        )
        if isinstance(result, dict):
            result["embeddings"] = embedding_result
        return result


def ensure_training_worker() -> None:
    global TRAINING_QUEUE, TRAINING_WORKER
    if TRAINING_QUEUE is None:
        TRAINING_QUEUE = asyncio.Queue()
    if TRAINING_WORKER is None or TRAINING_WORKER.done():
        TRAINING_WORKER = asyncio.create_task(training_worker())


def schedule_auto_training(module_id: str, reason: str = "source_update") -> bool:
    if os.getenv("SOFIA_AUTO_TRAIN", "true").strip().casefold() in {
        "0",
        "false",
        "no",
        "off",
    }:
        return False
    current = AUTO_TRAINING.get(module_id)
    if (current and not current.done()) or module_id in TRAINING_QUEUED:
        TRAINING_REASONS.setdefault(module_id, reason)
        return True
    ensure_training_worker()
    TRAINING_QUEUED.add(module_id)
    TRAINING_REASONS[module_id] = reason
    TRAINING_QUEUE.put_nowait(module_id)
    return True


def refresh_stale_links() -> int:
    """Refresh user-approved domains and rewrite their offline documents."""
    if os.getenv("SOFIA_AUTO_REFRESH_LINKS", "true").strip().casefold() in {
        "0",
        "false",
        "no",
        "off",
    }:
        return 0
    try:
        refresh_hours = max(1, float(os.getenv("SOFIA_LINK_REFRESH_HOURS", "24")))
    except ValueError:
        refresh_hours = 24
    now = datetime.now(UTC)
    refreshed = 0
    repository = LinkRepository(KNOWLEDGE_ROOT)
    refresh_modules()
    for module_id in MODULES:
        try:
            records = repository.list(module_id)
        except RuntimeError as exc:
            logger.warning("Atualização automática de links indisponível: %s", exc)
            continue
        for record in records:
            try:
                fetched_at = datetime.fromisoformat(
                    str(record.get("fetched_at", "")).replace("Z", "+00:00")
                )
                if fetched_at.tzinfo is None:
                    fetched_at = fetched_at.replace(tzinfo=UTC)
                if (now - fetched_at).total_seconds() < refresh_hours * 3600:
                    continue
                pages = max(1, min(20, int(record.get("pages", 1))))
                if link_not_modified(
                    str(record["url"]),
                    str(record.get("etag", "")),
                    str(record.get("last_modified", "")),
                ):
                    repository.mark_checked(module_id, str(record["url"]))
                    continue
                updated = ingest_link(
                    KNOWLEDGE_ROOT, module_id, str(record["url"]), pages, 20.0, None, 1
                )
                local_path = (
                    KNOWLEDGE_ROOT / module_id / "links" / str(updated["file_name"])
                )
                source_id = ExpansionStore(KNOWLEDGE_ROOT).register_source(
                    module_id,
                    "url",
                    url=str(updated.get("url", record["url"])),
                    canonical_url=str(updated.get("final_url", record["url"])),
                    local_path=str(local_path),
                    title=str(updated.get("title", "")),
                    content_hash=str(updated.get("content_hash", "")) or None,
                    pages=int(updated.get("pages", 1) or 1),
                    bytes_count=local_path.stat().st_size if local_path.exists() else 0,
                    etag=str(updated.get("etag", "")),
                    last_modified=str(updated.get("last_modified", "")),
                )
                record_document_pipeline(
                    KNOWLEDGE_ROOT, module_id, local_path, source_id
                )
                refreshed += 1
            except (
                KeyError,
                TypeError,
                ValueError,
                OSError,
                RuntimeError,
                sqlite3.Error,
            ) as exc:
                logger.warning(
                    "Não foi possível atualizar link do módulo %s: %s", module_id, exc
                )
    return refreshed


async def link_refresh_loop() -> None:
    """Keep explicitly registered domains current without blocking chat requests."""
    try:
        interval = max(
            900, int(float(os.getenv("SOFIA_LINK_REFRESH_INTERVAL_SECONDS", "3600")))
        )
    except ValueError:
        interval = 3600
    while True:
        await asyncio.sleep(interval)
        try:
            refreshed = await asyncio.to_thread(refresh_stale_links)
            if refreshed:
                for module_id in MODULES:
                    if neural_model_status(KNOWLEDGE_ROOT, module_id).get("stale"):
                        schedule_auto_training(module_id)
                logger.info(
                    "Documentos offline atualizados automaticamente: %s", refreshed
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Atualização automática de links falhou: %s", exc)


async def expansion_loop() -> None:
    """Run the persistent, bounded expansion queue without blocking chat."""
    settings = expansion_settings()
    interval = int(settings["interval_seconds"])
    while True:
        await asyncio.sleep(interval)
        try:
            result = await asyncio.to_thread(run_expansion_cycle, KNOWLEDGE_ROOT)
            metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
            if metrics.get("stored"):
                refresh_modules()
                for module_id in MODULES:
                    if neural_model_status(KNOWLEDGE_ROOT, module_id).get("stale"):
                        schedule_auto_training(module_id, "knowledge_expansion")
                logger.info(
                    "Expansão contínua concluída: tópicos=%s, novas=%s, atualizadas=%s, erros=%s",
                    metrics.get("topics_completed", 0),
                    metrics.get("pages_new", 0),
                    metrics.get("pages_updated", 0),
                    metrics.get("errors", 0),
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning(
                "Expansão contínua falhou; a fila será retomada no próximo ciclo: %s",
                exc,
            )


async def audit_existing_documents_once() -> None:
    """Register the current local corpus once without delaying application startup."""
    try:
        snapshot = await asyncio.to_thread(expansion_status, KNOWLEDGE_ROOT)
        if snapshot.get("documents_by_status"):
            return
        for module_id in MODULES:
            await asyncio.to_thread(audit_module_documents, KNOWLEDGE_ROOT, module_id)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.warning("Auditoria inicial do corpus não concluída: %s", exc)


def full_context(module_id: str) -> str:
    chunks = ingest_module(KNOWLEDGE_ROOT, module_id)
    return "\n\n--- DOCUMENTO: ".join(
        f"{chunk.path.name}\n{chunk.text}" for chunk in chunks
    )[:50000]


# The MCP server is the canonical tool surface. The web API below only adapts
# those same capabilities for the local browser client.
mcp = MCPServer(
    name="sofia-local",
    version="1.0.0",
    description="Sofia local RAG, AI and numerical tools",
)


@mcp.tool()
async def list_knowledge_modules() -> list[dict[str, Any]]:
    """List modules and files physically present under knowledge/."""
    refresh_modules()
    return [status_for(module_id) for module_id in MODULES if module_allowed(module_id)]


@mcp.tool()
async def search_knowledge(
    module_id: str, query: str, limit: int = 6
) -> dict[str, Any]:
    """Retrieve evidence from a local knowledge module using TF-IDF and policy gates."""
    module_root(module_id)
    result = retrieve(KNOWLEDGE_ROOT, module_id, query, policy_for(module_id), limit)
    return {
        "module": module_id,
        "sources": list(result.sources),
        "context": result.context,
        "evidence_found": result.has_quality_evidence,
        "evidence_score": max((item.score for item in result.evidence), default=0.0),
        "expanded_query": result.expanded_query,
        "rejected_evidence": [
            {
                "source": item.chunk.path.name,
                "reason": item.rejection_reason,
                "score": item.score,
            }
            for item in result.rejected_evidence
        ],
        "conflicts": list(result.conflicts),
        "judge_confidence": result.judge_confidence,
    }


@mcp.tool()
async def agent_plan(
    module_id: str, question: str, patient_context: bool = False
) -> dict[str, Any]:
    """Return the module-scoped plan without executing external actions."""
    module_root(module_id)
    if not question.strip():
        raise ValueError("question não pode ser vazia")
    policy = policy_for(module_id)
    return {
        "module": module_id,
        "specialist": specialist_for(module_id),
        "plan": build_plan(module_id, question, policy.high_risk, patient_context),
        "execution": "approval_required",
    }


@mcp.tool()
async def agent_memory_status(module_id: str | None = None) -> dict[str, Any]:
    """Return privacy-preserving execution memory metrics, never raw prompts or answers."""
    if module_id:
        module_root(module_id)
    return memory_status(KNOWLEDGE_ROOT, module_id)


async def query_theme_report(
    module_id: str | None = None, days: int = 30, limit: int = 12
) -> dict[str, Any]:
    """Return aggregate consultation themes; exposed only through the admin API adapter."""
    enforce_mcp_admin()
    if module_id:
        module_root(module_id)
    return await asyncio.to_thread(theme_report, KNOWLEDGE_ROOT, module_id, days, limit)


@mcp.tool()
async def tensor_multiply(
    left: list[list[float]], right: list[list[float]]
) -> dict[str, Any]:
    """Multiply two numeric tensors with NumPy."""
    a, b = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError("Matrizes incompatíveis para multiplicação")
    value = a @ b
    return {"shape": list(value.shape), "values": value.round(6).tolist()}


@mcp.tool()
async def random_generate(
    distribution: str = "normal", size: int = 10, seed: int | None = None
) -> dict[str, Any]:
    """Generate reproducible uniform or normal samples."""
    if distribution not in {"normal", "uniform"} or not 1 <= size <= 10000:
        raise ValueError(
            "distribution deve ser normal/uniform e size deve estar entre 1 e 10000"
        )
    rng = np.random.default_rng(seed)
    values = (
        rng.uniform(0, 1, size) if distribution == "uniform" else rng.normal(0, 1, size)
    )
    return {
        "distribution": distribution,
        "seed": seed,
        "size": size,
        "sample": values.round(6).tolist(),
        "mean": round(float(values.mean()), 6),
    }


@mcp.tool()
async def neural_train(
    module_id: str, epochs: int = 120, learning_rate: float = 0.08
) -> dict[str, Any]:
    """Train a module-scoped autoencoder using features extracted from knowledge/."""
    module_root(module_id)
    return await _train_module(module_id, epochs, learning_rate, "manual")


@mcp.tool()
async def neural_status(module_id: str) -> dict[str, Any]:
    """Return whether the module has a persisted trained neural model."""
    module_root(module_id)
    return neural_model_status(KNOWLEDGE_ROOT, module_id)


@mcp.tool()
async def neural_infer(module_id: str, values: list[float]) -> dict[str, Any]:
    """Run inference with the trained neural model for one knowledge module."""
    module_root(module_id)
    return await asyncio.to_thread(
        neural_model_infer, KNOWLEDGE_ROOT, module_id, values
    )


@mcp.tool()
async def neural_graph(module_id: str) -> dict[str, Any]:
    """Build a semantic graph from module documents and the trained network state."""
    module_root(module_id)
    return await asyncio.to_thread(neural_model_graph, KNOWLEDGE_ROOT, module_id)


@mcp.tool()
async def knowledge_graph(module_id: str) -> dict[str, Any]:
    """Return the persisted evidence graph for an authorized module."""
    enforce_mcp_admin()
    module_root(module_id)
    return await asyncio.to_thread(read_graph, KNOWLEDGE_ROOT, module_id)


@mcp.tool()
async def semantic_embedding_status(module_id: str) -> dict[str, Any]:
    """Return the local Ollama embedding index state for one module."""
    module_root(module_id)
    return await asyncio.to_thread(embedding_status, KNOWLEDGE_ROOT, module_id)


@mcp.tool()
async def semantic_embed(module_id: str, force: bool = False) -> dict[str, Any]:
    """Build the module's neural embedding index locally, one module at a time."""
    enforce_mcp_admin()
    module_root(module_id)
    return await asyncio.to_thread(
        build_module_embeddings, KNOWLEDGE_ROOT, module_id, force
    )


@mcp.tool()
async def readiness_check(module_id: str) -> dict[str, Any]:
    """Return the evidence-based ten-level readiness checklist for AG000001."""
    enforce_mcp_admin()
    module_root(module_id)
    return await asyncio.to_thread(readiness_checklist, KNOWLEDGE_ROOT, module_id)


@mcp.tool()
async def production_gate() -> dict[str, Any]:
    """Evaluate all ten levels and safety gates for the administrator."""
    enforce_mcp_admin()
    return await asyncio.to_thread(run_production_gate, KNOWLEDGE_ROOT)


@mcp.tool()
async def monte_carlo_estimate(
    samples: int = 10000, seed: int | None = None
) -> dict[str, Any]:
    """Estimate Pi with Monte Carlo and return a 95% confidence interval."""
    if not 100 <= samples <= 2_000_000:
        raise ValueError("samples deve estar entre 100 e 2.000.000")
    rng = np.random.default_rng(seed)
    points = rng.uniform(-1, 1, (samples, 2))
    inside = np.sum(np.sum(points * points, axis=1) <= 1)
    estimate = 4 * inside / samples
    error = 1.96 * math.sqrt(max(estimate * (1 - estimate), 1e-12) / samples)
    return {
        "samples": samples,
        "seed": seed,
        "pi": round(float(estimate), 8),
        "confidence_95": [
            round(float(estimate - error), 8),
            round(float(estimate + error), 8),
        ],
    }


@mcp.resource("knowledge://{module_id}", mime_type="text/plain")
async def knowledge_resource(module_id: str) -> str:
    """Expose the physical contents of one knowledge module as an MCP resource."""
    module_root(module_id)
    return full_context(module_id) or "Este módulo não possui documentos."


@mcp.tool()
async def institutional_integration_status() -> dict[str, Any]:
    """Return connector, job, checkpoint and DLQ status without exposing RAW payloads."""
    enforce_mcp_admin()
    return await asyncio.to_thread(integration_status)


@mcp.tool()
async def institutional_integration_sync(
    connector: str = "tasy", resource: str = "patients", max_pages: int = 1
) -> dict[str, Any]:
    """Run a bounded, resumable read from a configured institutional connector."""
    enforce_mcp_admin()
    return await asyncio.to_thread(sync_integration, connector, resource, max_pages)


def answer_payload(
    module_id: str,
    result: Any,
    patient_id: str | None = None,
    language: str = "pt-BR",
    response_style: str = "structured",
    retry: bool = False,
    retry_attempt: int = 0,
    question: str = "",
    trace_id: str | None = None,
) -> dict[str, Any]:
    """Serialize one guarded RAG result for both MCP and the browser adapter."""
    # Keep this as a public execution trace, not chain-of-thought.  The UI and
    # MCP clients need to know which guarded subsystem ran, why a fallback was
    # used and where the evidence gate stopped the request.
    trace = list(getattr(result, "agent_trace", []) or [])
    pipeline = [
        {
            "stage": item.get("id", item.get("stage", "unknown")),
            "label": item.get("stage", item.get("id", "unknown")),
            "status": item.get("status", "unknown"),
            "agent": item.get("agent"),
        }
        for item in trace
    ]
    if not pipeline:
        pipeline = [
            {
                "stage": "perceive",
                "label": "Perceber",
                "status": "complete",
                "agent": "SOFIA CORE",
            },
            {
                "stage": "route",
                "label": "Roteiar",
                "status": "complete",
                "agent": "Planner",
            },
            {
                "stage": "plan",
                "label": "Planejar",
                "status": "complete",
                "agent": "Planner",
            },
        ]
    retrieval_step = next(
        (item for item in pipeline if item["stage"] == "retrieve"), None
    )
    if retrieval_step is not None:
        retrieval_step.update(
            {
                "tool": "mcp.search_knowledge",
                "evidence_found": result.evidence_found,
                "sources": list(result.sources),
            }
        )
    pipeline.append(
        {
            "stage": "mcp.search_knowledge",
            "label": "RAG + MCP",
            "status": "evidence_found" if result.evidence_found else "blocked",
            "sources": list(result.sources),
        }
    )
    pipeline.append(
        {
            "stage": "llm",
            "label": "LLM / Provider",
            "status": "complete"
            if result.provider not in {"policy", "error"}
            else "not_called",
            "provider": result.provider,
            "model": result.model,
        }
    )
    pipeline.append(
        {
            "stage": "verification",
            "label": "Critic / Verificação",
            "status": getattr(result, "verification_status", "unknown"),
            "confidence": float(getattr(result, "confidence", 0.0)),
        }
    )
    pipeline.append(
        {
            "stage": "output",
            "label": "Entregar",
            "status": "verified" if result.verified else "rejected",
        }
    )
    if patient_id:
        pipeline.insert(
            2,
            {
                "stage": "mcp.fhir_patient_context",
                "status": "complete",
                "patient_id": patient_id,
            },
        )
    retry_message = None
    if retry:
        retry_message = "O SOFIA está em constante aprendizado. Seu feedback ajuda a melhorar as próximas respostas."
        if getattr(result, "offline_material_stored", False):
            retry_message += " A síntese anonimizada foi adicionada ao conhecimento offline como candidata e continua subordinada às fontes locais."
    learning = {
        "is_retry": retry,
        "attempt": max(0, retry_attempt),
        "message": retry_message,
        "offline_material": {
            "stored": bool(result.sources),
            "source_count": len(result.sources),
            "sources": list(result.sources),
            "note": "As fontes locais que fundamentaram esta resposta permanecem disponíveis offline."
            if result.sources
            else "Nenhuma fonte local foi recuperada.",
        },
        "external_provider_used": result.provider in {"openai", "gemini", "claude"},
        "offline_candidate_stored": bool(
            getattr(result, "offline_material_stored", False)
        ),
        "offline_candidate_source": getattr(result, "offline_material_source", None),
    }
    privacy = {
        "external_context_redacted": bool(
            getattr(result, "external_context_redacted", False)
        ),
        "redacted_fields": int(getattr(result, "redacted_fields", 0)),
        "note": (
            "Contexto identificável foi minimizado antes de uma possível chamada externa; "
            "a resposta foi reidratada localmente apenas pelos marcadores autorizados. "
            "O mapa temporário não foi salvo."
            if getattr(result, "external_context_redacted", False)
            else "Nenhum contexto foi enviado a um provedor externo nesta execução."
        ),
    }
    return {
        "answer": result.answer,
        "provider": result.provider,
        "model": result.model,
        "sources": result.sources,
        "evidence_found": result.evidence_found,
        "evidence_score": result.evidence_score,
        "verified": result.verified,
        "verification_status": getattr(result, "verification_status", "unknown"),
        "confidence": float(getattr(result, "confidence", result.evidence_score)),
        "module": module_id,
        "module_only": True,
        "module_scope": assess_module_scope(module_id, question) if question else None,
        "patient_id": patient_id,
        "language": language,
        "response_style": response_style,
        "pipeline": pipeline,
        "agent_trace": getattr(result, "agent_trace", []),
        "trace_id": trace_id,
        "context_package": getattr(result, "context_package", {}),
        "analytics_id": getattr(result, "analytics_id", None),
        "learning": learning,
        "privacy": privacy,
    }


@mcp.tool()
async def rag_answer(
    module_id: str,
    provider: str,
    question: str,
    history: list[dict[str, str]] | None = None,
    patient_id: str | None = None,
    language: str = "pt-BR",
    response_style: str = "structured",
    user_code: str | None = None,
    retry: bool = False,
    retry_of: int | None = None,
    retry_attempt: int = 0,
) -> dict[str, Any]:
    """Run the complete guarded MCP -> RAG -> AI -> verification pipeline."""
    module_root(module_id)
    if provider not in {"auto", "openai", "gemini", "claude", "ollama"}:
        raise ValueError("provider deve ser auto, openai, gemini, claude ou ollama")
    if not question.strip():
        raise ValueError("question não pode ser vazia")
    language = normalize_language(language)
    response_style = normalize_response_style(response_style)
    if patient_id and module_id != "medicina":
        raise ValueError("patient_id só pode ser usado no módulo medicina")
    trace = TraceRecorder(KNOWLEDGE_ROOT, module_id, question, user_code)
    trace.span(
        "understand",
        "complete",
        {"language": language, "response_style": response_style},
    )
    try:
        # This is a privacy-minimized topic record. It creates the persistent
        # expansion queue but never blocks an answer if its local store is
        # temporarily unavailable.
        await asyncio.to_thread(
            record_search_topic, KNOWLEDGE_ROOT, module_id, question, user_code
        )
    except Exception as exc:  # noqa: BLE001
        # Topic analytics and expansion are auxiliary. A database dialect or
        # migration issue must never turn a valid RAG question into HTTP 500.
        logger.warning("Não foi possível registrar o tema para expansão: %s", exc)
    clinical_scope = module_id == "medicina" or bool(patient_id)
    effective_provider = provider
    if provider == "auto" and clinical_scope and not external_clinical_allowed():
        # O contexto FHIR não sai da máquina por padrão, mesmo no modo
        # automático. A autorização clínica externa continua explícita.
        effective_provider = "ollama"
    provider_guard(
        effective_provider, patient_id=patient_id, clinical=module_id == "medicina"
    )
    neural_state = neural_model_status(KNOWLEDGE_ROOT, module_id)
    if (not neural_state.get("trained") or neural_state.get("stale")) and os.getenv(
        "SOFIA_AUTO_TRAIN", "true"
    ).strip().casefold() not in {"0", "false", "no", "off"}:
        # Arquivos adicionados diretamente à pasta knowledge/ também ativam a
        # atualização do modelo na próxima consulta, sem depender do botão de
        # upload da interface.
        schedule_auto_training(module_id)
    clinical_context = ""
    if patient_id:
        clinical_context = json.dumps(
            await asyncio.to_thread(patient_context, patient_id), ensure_ascii=False
        )
    allowed_external = (
        external_clinical_allowed() if clinical_scope else external_data_allowed()
    )
    trace.span(
        "plan",
        "complete",
        {"provider_mode": effective_provider, "external_allowed": allowed_external},
    )
    try:
        result = await orchestrate_answer(
            root=KNOWLEDGE_ROOT,
            module_id=module_id,
            provider=effective_provider,
            question=question,
            history=history or [],
            extra_context=clinical_context,
            language=language,
            response_style=response_style,
            external_allowed=allowed_external,
            user_code=user_code,
            retry=retry,
            retry_of=retry_of,
        )
    except Exception:
        trace.finish(
            status="ERROR",
            provider=effective_provider,
            metrics=trace_metrics(module_id, question, effective_provider, retry=retry),
        )
        raise
    package = getattr(result, "context_package", {})
    trace.span(
        "retrieve",
        "complete" if result.evidence_found else "blocked",
        {
            "evidence": len(package.get("accepted_evidence", [])),
            "sources": len(result.sources),
        },
    )
    trace.span(
        "verify",
        result.verification_status,
        {"confidence": result.confidence, "verified": result.verified},
    )
    trace.finish(
        status="READY",
        intent=package.get("intent"),
        complexity=package.get("complexity"),
        router=package.get("complexity"),
        provider=result.provider,
        model=result.model,
        confidence=result.confidence,
        metrics=trace_metrics(
            module_id,
            question,
            result.provider,
            evidence_score=result.evidence_score,
            source_count=len(result.sources),
            retry=retry,
        ),
    )
    payload = answer_payload(
        module_id,
        result,
        patient_id,
        language,
        response_style,
        retry,
        retry_attempt,
        question,
        trace.trace_id,
    )
    payload["learning"]["retry_of"] = retry_of
    payload["learning"]["provider_mode"] = (
        "auto com provedores externos autorizados"
        if retry and allowed_external and effective_provider == "auto"
        else "política local vigente"
    )
    return payload


@mcp.tool()
async def analyst_scenario(
    module_id: str,
    provider: str,
    question: str,
    baseline: float = 100.0,
    volatility: float = 0.1,
    samples: int = 5000,
    patient_id: str | None = None,
    language: str = "pt-BR",
) -> dict[str, Any]:
    """Combine guarded RAG, LLM, random sampling, neural signal and Monte Carlo scenarios."""
    module_root(module_id)
    if provider not in {"auto", "openai", "gemini", "claude", "ollama"}:
        raise ValueError("provider deve ser auto, openai, gemini, claude ou ollama")
    if not question.strip():
        raise ValueError("question não pode ser vazia")
    clinical_scope = module_id == "medicina" or bool(patient_id)
    effective_provider = (
        "ollama"
        if provider == "auto" and clinical_scope and not external_clinical_allowed()
        else provider
    )
    provider_guard(
        effective_provider, patient_id=patient_id, clinical=module_id == "medicina"
    )
    allowed_external = (
        external_clinical_allowed() if clinical_scope else external_data_allowed()
    )
    return await analyze_scenario(
        KNOWLEDGE_ROOT,
        module_id,
        effective_provider,
        question,
        baseline,
        volatility,
        samples,
        patient_id,
        language,
        allowed_external,
    )


class LoginRequest(BaseModel):
    identifier: str | None = Field(default=None, max_length=200)
    email: str | None = Field(default=None, max_length=200)
    password: str = Field(min_length=1, max_length=200)
    otp: str | None = Field(default=None, pattern=r"^\d{6}$")


class UserCreateRequest(BaseModel):
    user_code: str | None = Field(default=None, max_length=32)
    email: str = Field(min_length=3, max_length=200)
    name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=200)
    scopes: list[str] = Field(min_length=1, max_length=20)
    primary_module: str | None = Field(default=None, max_length=80)


class AccessRequestCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=3, max_length=200)
    requested_module: str = Field(min_length=2, max_length=80)
    scopes: list[str] = Field(min_length=1, max_length=20)


class AccessDecisionRequest(BaseModel):
    approve: bool
    scopes: list[str] = Field(default_factory=list, max_length=20)
    note: str | None = Field(default=None, max_length=500)


class AccountActivationRequest(BaseModel):
    user_code: str = Field(min_length=8, max_length=8, pattern=r"^[A-Z]{2}\d{6}$")
    activation_token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)


class ActivationTwoFactorRequest(BaseModel):
    user_code: str = Field(min_length=8, max_length=8, pattern=r"^[A-Z]{2}\d{6}$")
    activation_token: str = Field(min_length=20, max_length=200)
    code: str = Field(pattern=r"^\d{6}$")


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=10, max_length=200)


class PasswordResetRequest(BaseModel):
    user_code: str = Field(min_length=8, max_length=8, pattern=r"^[A-Z]{2}\d{6}$")
    reset_token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)


class UserStatusRequest(BaseModel):
    active: bool
    reason: str | None = Field(default=None, max_length=500)


class InactivityPolicyRequest(BaseModel):
    inactive_lock_days: int = Field(ge=1, le=3650)


class TwoFactorCodeRequest(BaseModel):
    code: str = Field(pattern=r"^\d{6}$")


class LinkCreateRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2_000)
    max_pages: int = Field(default=1, ge=1, le=20)
    dense: bool = False
    max_depth: int = Field(default=1, ge=0, le=3)


class ExpansionRunRequest(BaseModel):
    module_id: str | None = Field(default=None, max_length=80)


class ExpansionPauseRequest(BaseModel):
    paused: bool


class ExpansionDomainRequest(BaseModel):
    module_id: str = Field(min_length=2, max_length=80)
    domain: str = Field(min_length=3, max_length=255)
    mode: str = Field(default="allow", pattern="^(allow|block)$")
    reason: str = Field(default="admin", max_length=240)


class ExpansionReprocessRequest(BaseModel):
    module_id: str = Field(min_length=2, max_length=80)
    file_name: str | None = Field(default=None, max_length=500)


class ChatRequest(BaseModel):
    module_id: str
    provider: str = Field(
        default="auto", pattern="^(auto|openai|gemini|claude|ollama)$"
    )
    message: str = Field(min_length=1, max_length=20000)
    history: list[dict[str, str]] = Field(default_factory=list)
    patient_id: str | None = Field(default=None, max_length=64)
    language: str = Field(default="pt-BR", pattern="^(pt-BR|en|es)$")
    response_style: str = Field(
        default="structured", pattern="^(concise|structured|detailed)$"
    )
    retry: bool = False
    retry_of: int | None = Field(default=None, ge=1)
    retry_attempt: int = Field(default=0, ge=0, le=3)


class ToolRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


class FeedbackRequest(BaseModel):
    analytics_id: int = Field(ge=1)
    feedback: str = Field(pattern="^(good|medium|bad)$")
    # Used only for the bounded admin recovery pass. It is never written to
    # analytics, audit events or learning records.
    question: str | None = Field(default=None, max_length=20000)


class IntegrationSyncRequest(BaseModel):
    resource: str = Field(default="patients", min_length=1, max_length=120)
    max_pages: int = Field(default=1, ge=1, le=20)


app = FastAPI(title="Sofia Local MCP", version="1.0.0")


@app.middleware("http")
async def protect_mcp_transport(request: Request, call_next):
    """Require a Sofia session for the mounted streamable MCP transport.

    Stdio remains available for a locally trusted process. HTTP MCP calls use
    the same session and module authorization as the browser API.
    """
    if not request.url.path.startswith("/mcp") or request.method == "OPTIONS":
        return await call_next(request)
    authorization = request.headers.get("authorization", "")
    token = (
        authorization[7:].strip() if authorization.lower().startswith("bearer ") else ""
    )
    try:
        user = verify_session(token)
    except HTTPException as exc:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    context_token = bind_user(user)
    try:
        return await call_next(request)
    finally:
        reset_user(context_token)


@app.on_event("startup")
async def start_background_refresh() -> None:
    global LINK_REFRESH_TASK, EXPANSION_TASK, DOCUMENT_AUDIT_TASK
    ensure_training_worker()
    refresh_modules()
    initialize_expansion(KNOWLEDGE_ROOT)
    if os.getenv("SOFIA_AUTO_TRAIN_ON_STARTUP", "true").strip().casefold() not in {
        "0",
        "false",
        "no",
        "off",
    }:
        for module_id in MODULES:
            neural = neural_model_status(KNOWLEDGE_ROOT, module_id)
            if not neural.get("trained") or neural.get("stale"):
                schedule_auto_training(module_id)
    if os.getenv("SOFIA_AUTO_REFRESH_LINKS", "true").strip().casefold() not in {
        "0",
        "false",
        "no",
        "off",
    }:
        LINK_REFRESH_TASK = asyncio.create_task(link_refresh_loop())
    if expansion_settings()["enabled"]:
        EXPANSION_TASK = asyncio.create_task(expansion_loop())
        if os.getenv(
            "SOFIA_EXPANSION_AUDIT_ON_STARTUP", "true"
        ).strip().casefold() not in {"0", "false", "no", "off"}:
            DOCUMENT_AUDIT_TASK = asyncio.create_task(audit_existing_documents_once())


@app.on_event("shutdown")
async def stop_background_refresh() -> None:
    for task in (
        LINK_REFRESH_TASK,
        EXPANSION_TASK,
        DOCUMENT_AUDIT_TASK,
        TRAINING_WORKER,
    ):
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5174", "http://localhost:5174"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?::\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    refresh_modules()
    return {
        "status": "ok",
        "server": "sofia-local",
        "mcp": "/mcp",
        "knowledge": str(KNOWLEDGE_ROOT),
        "modules": len(MODULES),
        "fhir": "/fhir/metadata",
        "storage": storage_status(),
    }


@app.get("/api/analytics/themes")
async def analytics_themes(
    module_id: str | None = None,
    days: int = 30,
    limit: int = 12,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    """Show real consultation themes to AG000001 only."""
    require_statistics_admin(current)
    if module_id:
        module_root(module_id)
    return await asyncio.to_thread(theme_report, KNOWLEDGE_ROOT, module_id, days, limit)


@app.post("/api/analytics/feedback")
async def analytics_feedback(
    request: FeedbackRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    """Save an optional quality signal without storing prompt or answer text."""
    try:
        updated = await asyncio.to_thread(
            update_feedback,
            KNOWLEDGE_ROOT,
            request.analytics_id,
            request.feedback,
            current["sub"],
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not updated:
        raise HTTPException(404, "Resposta analítica não encontrada")
    assessment = await asyncio.to_thread(
        feedback_assessment,
        KNOWLEDGE_ROOT,
        request.analytics_id,
        current["sub"],
    )
    if assessment is None:
        raise HTTPException(404, "Resposta analítica não encontrada")
    research_result: dict[str, Any] = {
        "status": "not_requested",
        "searched": 0,
        "stored": 0,
        "items": [],
        "errors": [],
    }
    if request.feedback == "bad":
        if current.get("sub") != ADMIN_CODE:
            research_result = {
                **research_result,
                "status": "not_authorized",
                "reason": "admin_only",
                "note": "A pesquisa externa e a ampliação automática da base são exclusivas do AG000001.",
            }
        elif not (request.question or "").strip():
            research_result = {
                **research_result,
                "status": "blocked",
                "reason": "question_required_for_research",
                "note": "A pergunta original não foi enviada para a recuperação administrativa.",
            }
        else:
            # Network and document ingestion are blocking operations; keep
            # them out of the event loop while preserving one bounded pass.
            research_result = await asyncio.to_thread(
                research_module,
                KNOWLEDGE_ROOT,
                str(assessment["module_id"]),
                request.question,
            )
            refresh_modules()

            # Newly accepted sources must be visible to the learning event and
            # the following retry, without copying the original question.
            research_sources = [
                str(item.get("file_name"))
                for item in research_result.get("items", [])
                if item.get("file_name")
            ]
            if research_sources:
                assessment = {
                    **assessment,
                    "source_names": list(
                        dict.fromkeys(
                            [*assessment.get("source_names", []), *research_sources]
                        )
                    )[:20],
                }

    # A policy/evidence-gate response has no factual base to improve by
    # calling another provider. The admin recovery pass can create that base;
    # ordinary users are told to add material rather than entering a loop.
    has_recoverable_evidence = (
        assessment["provider"] != "policy" and bool(assessment.get("source_names"))
    ) or bool(research_result.get("stored"))
    retry_recommended = request.feedback == "bad" and has_recoverable_evidence
    training_scheduled = False
    if research_result.get("stored"):
        # New public material is a source update even when the aggregate
        # quality score is not yet low enough to trigger negative-feedback
        # retraining. The worker still serializes modules one at a time.
        training_scheduled = schedule_auto_training(
            str(assessment["module_id"]), "admin_external_research"
        )
    elif (
        request.feedback == "bad"
        and assessment["needs_improvement"]
        and has_recoverable_evidence
    ):
        # The worker serializes modules, so a large knowledge base cannot
        # start concurrent retraining jobs for every negative opinion.
        training_scheduled = schedule_auto_training(
            str(assessment["module_id"]), "negative_feedback"
        )
    learning_event_stored = await asyncio.to_thread(
        record_learning_event,
        KNOWLEDGE_ROOT,
        assessment,
        retry_recommended,
        training_scheduled,
    )
    audit_event(current["sub"], "answer_feedback", request.feedback)
    return {
        "updated": True,
        "feedback": request.feedback,
        "retry_recommended": retry_recommended,
        "external_research": research_result,
        "sensitive_expansion_requires_authorization": current.get("sub") != ADMIN_CODE,
        "learning": {
            "module_id": assessment["module_id"],
            "theme": assessment["theme"],
            "quality_score": assessment["quality_score"],
            "evaluated_answers": assessment["evaluated_answers"],
            "good_answers": assessment["good_answers"],
            "bad_answers": assessment["bad_answers"],
            "neutral_answers": assessment["medium_answers"],
            "needs_improvement": assessment["needs_improvement"],
            "training_scheduled": training_scheduled,
            "learning_event_stored": learning_event_stored,
            "offline_sources": assessment["source_names"],
            "external_research_status": research_result.get("status"),
            "external_research_stored": int(research_result.get("stored", 0) or 0),
            "message": (
                (
                    f"O SOFIA está em constante aprendizado. Consultei {research_result.get('searched', 0)} referências públicas e "
                    f"armazenei {research_result.get('stored', 0)} item(ns) anonimizados no módulo. A próxima resposta usará essa base offline."
                    if research_result.get("status") == "completed"
                    else "O SOFIA está em constante aprendizado. Seu feedback foi registrado, mas nenhuma fonte externa foi incorporada nesta tentativa."
                )
                if request.feedback == "bad" and current.get("sub") == ADMIN_CODE
                else (
                    "Feedback registrado. Como o RAG não encontrou evidência local, não vou repetir a mesma resposta automaticamente. "
                    "Inclua documentos, imagens ou links neste módulo para ampliar a base."
                    if request.feedback == "bad" and not has_recoverable_evidence
                    else "Feedback registrado. Consultas sem opinião permanecem neutras e não acionam treinamento."
                )
            ),
        },
    }


@app.get("/api/admin/expansion")
async def admin_expansion_status(
    module_id: str | None = None, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    """Expose expansion queue and processing metrics only to AG000001."""
    require_statistics_admin(current)
    if module_id:
        module_root(module_id)
    return await asyncio.to_thread(expansion_status, KNOWLEDGE_ROOT, module_id)


@app.post("/api/admin/expansion/run")
async def admin_expansion_run(
    request: ExpansionRunRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_statistics_admin(current)
    if request.module_id:
        module_root(request.module_id)
    result = await asyncio.to_thread(
        run_expansion_cycle, KNOWLEDGE_ROOT, request.module_id
    )
    audit_event(current["sub"], "expansion_run", request.module_id or "all")
    refresh_modules()
    return result


@app.post("/api/admin/expansion/pause")
async def admin_expansion_pause(
    request: ExpansionPauseRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_statistics_admin(current)
    store = ExpansionStore(KNOWLEDGE_ROOT)
    await asyncio.to_thread(store.set_paused, request.paused)
    audit_event(current["sub"], "expansion_pause", str(request.paused).lower())
    return {
        "paused": request.paused,
        "status": await asyncio.to_thread(expansion_status, KNOWLEDGE_ROOT),
    }


@app.post("/api/admin/expansion/domains")
async def admin_expansion_domain(
    request: ExpansionDomainRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_statistics_admin(current)
    module_root(request.module_id)
    store = ExpansionStore(KNOWLEDGE_ROOT)
    await asyncio.to_thread(
        store.allow_domain,
        request.module_id,
        request.domain,
        request.mode,
        request.reason,
    )
    audit_event(current["sub"], "expansion_domain", request.module_id, request.domain)
    return {
        "saved": True,
        "module_id": request.module_id,
        "domain": request.domain,
        "mode": request.mode,
    }


@app.post("/api/admin/expansion/reprocess")
async def admin_expansion_reprocess(
    request: ExpansionReprocessRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_statistics_admin(current)
    root = module_root(request.module_id).resolve()
    if request.file_name:
        candidate = (root / request.file_name).resolve()
        if root not in candidate.parents or not candidate.is_file():
            raise HTTPException(404, "Arquivo não encontrado dentro do módulo")
        result = await asyncio.to_thread(
            record_document_pipeline, KNOWLEDGE_ROOT, request.module_id, candidate
        )
    else:
        result = await asyncio.to_thread(
            audit_module_documents, KNOWLEDGE_ROOT, request.module_id
        )
    audit_event(
        current["sub"],
        "expansion_reprocess",
        request.module_id,
        request.file_name or "all",
    )
    refresh_modules()
    return result


@app.get("/api/admin/pipeline")
async def admin_pipeline(
    module_id: str | None = None,
    limit: int = 100,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    """Return document states and stage events for the Pipeline Explorer."""
    require_statistics_admin(current)
    if module_id:
        module_root(module_id)
    if not module_id:
        module_id = next(iter(MODULES), "")
    return {
        "module_id": module_id,
        "stages": list(PIPELINE_STAGES),
        "documents": await asyncio.to_thread(
            pipeline_documents, KNOWLEDGE_ROOT, module_id, limit
        ),
    }


@app.get("/api/admin/evaluation")
async def admin_evaluation(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    """Run the deterministic corpus/retrieval smoke evaluation for AG000001."""
    require_statistics_admin(current)
    result = await asyncio.to_thread(evaluate_corpus, KNOWLEDGE_ROOT)
    audit_event(current["sub"], "evaluation_run", "all-modules")
    return result


@app.get("/api/admin/evaluation/semantic")
async def admin_semantic_evaluation(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    """Run only the reviewed semantic evidence cases for AG000001."""
    require_statistics_admin(current)
    result = await asyncio.to_thread(evaluate_semantic_cases, KNOWLEDGE_ROOT)
    audit_event(current["sub"], "semantic_evaluation_run", "all-modules")
    return result


@app.get("/api/admin/embeddings")
async def admin_embeddings_status(
    module_id: str | None = None, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    """Return neural embedding readiness; restricted to AG000001."""
    require_statistics_admin(current)
    if module_id:
        module_root(module_id)
    return await asyncio.to_thread(embedding_status, KNOWLEDGE_ROOT, module_id)


@app.get("/api/admin/readiness")
async def admin_readiness(
    module_id: str | None = None, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    """Return the ten-level operational checklist; restricted to AG000001."""
    require_statistics_admin(current)
    refresh_modules()
    resolved_module = module_id or next(iter(MODULES), "")
    module_root(resolved_module)
    return await asyncio.to_thread(readiness_checklist, KNOWLEDGE_ROOT, resolved_module)


@app.get("/api/admin/knowledge-graph")
async def admin_knowledge_graph(
    module_id: str | None = None,
    rebuild: bool = False,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    """Return the evidence graph and optionally rebuild its derived artifact."""
    require_statistics_admin(current)
    refresh_modules()
    resolved_module = module_id or next(iter(MODULES), "")
    module_root(resolved_module)
    result = await asyncio.to_thread(
        build_graph if rebuild else read_graph, KNOWLEDGE_ROOT, resolved_module
    )
    audit_event(current["sub"], "knowledge_graph_read", resolved_module)
    return result


@app.get("/api/admin/production-gate")
async def admin_production_gate(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    """Evaluate the single release gate for AG000001."""
    require_statistics_admin(current)
    result = await asyncio.to_thread(run_production_gate, KNOWLEDGE_ROOT)
    audit_event(current["sub"], "production_gate_run", result.get("status", "unknown"))
    return result


@app.post("/api/admin/embeddings/build")
async def admin_embeddings_build(
    module_id: str | None = None,
    force: bool = False,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    """Build local embeddings sequentially, optionally for one module."""
    require_statistics_admin(current)
    if module_id:
        module_root(module_id)
        result = await asyncio.to_thread(
            build_module_embeddings, KNOWLEDGE_ROOT, module_id, force
        )
    else:
        result = await asyncio.to_thread(
            build_all_embeddings, KNOWLEDGE_ROOT, sorted(MODULES), force
        )
    audit_event(current["sub"], "embedding_build", module_id or "all-modules")
    return result


@app.get("/api/admin/observability")
async def admin_observability(
    module_id: str | None = None,
    limit: int = 100,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_statistics_admin(current)
    return await asyncio.to_thread(
        observability_snapshot, KNOWLEDGE_ROOT, module_id, limit
    )


@app.get("/api/admin/insights")
async def admin_insights(
    module_id: str | None = None,
    limit: int = 100,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_statistics_admin(current)
    return await asyncio.to_thread(insights_snapshot, KNOWLEDGE_ROOT, module_id, limit)


@app.post("/api/admin/insights/run")
async def admin_insights_run(
    module_id: str, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_statistics_admin(current)
    module_root(module_id)
    result = await asyncio.to_thread(
        generate_module_insights, KNOWLEDGE_ROOT, module_id
    )
    audit_event(current["sub"], "insights_run", module_id)
    return result


@app.post("/api/auth/login")
async def login(request: LoginRequest, http_request: Request) -> dict[str, Any]:
    identifier = (request.identifier or request.email or "").strip()
    client_host = http_request.client.host if http_request.client else "local"
    rate_key = f"{client_host}:{identifier.casefold()}"
    if not login_allowed(rate_key):
        raise HTTPException(
            429, "Muitas tentativas. Aguarde um minuto e tente novamente."
        )
    user = authenticate(identifier, request.password, request.otp)
    if user is None:
        register_login_failure(rate_key)
        raise HTTPException(401, "E-mail ou senha inválidos")
    if user.get("requires_2fa"):
        return {"requires_2fa": True}
    register_login_success(rate_key)
    audit_event(user["user_code"], "login")
    return {"token": create_session(user), "user": user}


@app.get("/api/auth/me")
async def me(user: dict[str, Any] = Depends(require_user)) -> dict[str, Any]:
    return {
        "user": {key: value for key, value in user.items() if key not in {"sub", "sid"}}
    }


@app.post("/api/auth/logout")
async def logout(
    http_request: Request, user: dict[str, Any] = Depends(require_user)
) -> dict[str, bool]:
    header = http_request.headers.get("Authorization", "")
    revoke_session(header[7:].strip())
    audit_event(user["sub"], "logout")
    return {"logged_out": True}


@app.post("/api/auth/token/rotate")
async def token_rotate(
    http_request: Request, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    header = http_request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(401, "Faça login para continuar")
    try:
        result = rotate_session(header[7:].strip())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(401, str(exc)) from exc
    audit_event(current["sub"], "session_rotate")
    return result


@app.post("/api/auth/requests")
async def request_access(request: AccessRequestCreate) -> dict[str, Any]:
    scopes = normalize_access_scopes(request.scopes)
    if request.requested_module.casefold() not in MODULES:
        raise HTTPException(400, "Módulo principal inválido")
    try:
        result = create_access_request(
            request.name, request.email, request.requested_module, scopes
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            409, "O código de usuário ou solicitação já existe"
        ) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "created": True,
        **result,
        "message": "Solicitação enviada. Aguarde a aprovação da AG000001.",
    }


@app.get("/api/auth/requests")
async def access_requests(
    status: str = "pending", current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_admin(current)
    if status not in {"pending", "approved", "rejected"}:
        raise HTTPException(400, "status deve ser pending, approved ou rejected")
    return {"requests": list_access_requests(status)}


@app.post("/api/auth/requests/{request_id}/decision")
async def access_decision(
    request_id: int,
    request: AccessDecisionRequest,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_admin(current)
    scopes = (
        normalize_access_scopes(request.scopes)
        if request.approve and request.scopes
        else []
    )
    try:
        result = decide_access_request(
            request_id, request.approve, scopes, ADMIN_CODE, request.note
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "Código ou e-mail já cadastrado") from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(
        current["sub"], "access_decision", str(request_id), result.get("status", "")
    )
    return result


@app.post("/api/auth/users")
async def users_endpoint(
    request: UserCreateRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_admin(current)
    scopes = normalize_access_scopes(request.scopes)
    primary_module = request.primary_module or (
        scopes[0] if scopes and scopes[0] != "CORE" else None
    )
    if primary_module and primary_module.casefold() not in MODULES:
        raise HTTPException(400, "Módulo principal inválido")
    try:
        user = create_user(
            request.email,
            request.name,
            request.password,
            scopes=scopes,
            primary_module=primary_module,
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "Usuário ou e-mail já cadastrado") from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"created": True, "user": user}


@app.get("/api/auth/users")
async def users_list(current: dict[str, Any] = Depends(require_user)) -> dict[str, Any]:
    require_admin(current)
    return {
        "users": list_users(),
        "inactivity": get_inactivity_policy(),
        "session_rotation_seconds": 600,
    }


@app.post("/api/auth/users/inactivity-policy")
async def users_inactivity_policy(
    request: InactivityPolicyRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_admin(current)
    try:
        result = set_inactivity_policy(request.inactive_lock_days)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(current["sub"], "inactivity_policy", str(request.inactive_lock_days))
    return result


@app.post("/api/auth/users/{user_code}/reset")
async def user_password_reset(
    user_code: str, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_admin(current)
    try:
        result = create_password_reset_token(user_code, current["sub"])
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    audit_event(current["sub"], "password_reset_token", user_code)
    return {
        "created": True,
        **result,
        "message": "Token de recuperação criado. Ele expira em 10 minutos e só pode ser usado uma vez.",
    }


@app.post("/api/auth/users/{user_code}/status")
async def user_status(
    user_code: str,
    request: UserStatusRequest,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_admin(current)
    try:
        user = set_user_active(user_code, request.active, request.reason)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(
        current["sub"],
        "user_status",
        user_code,
        "active" if request.active else "blocked",
    )
    return {"updated": True, "user": user}


@app.post("/api/auth/activation")
async def account_activation(request: AccountActivationRequest) -> dict[str, Any]:
    try:
        artifact = activate_account(
            request.user_code, request.activation_token, request.new_password
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        **artifact,
        "message": "Senha criada. Adicione o QR ao seu aplicativo autenticador e valide o código para concluir.",
    }


@app.post("/api/auth/activation/2fa")
async def activation_two_factor(request: ActivationTwoFactorRequest) -> dict[str, Any]:
    try:
        enable_activation_two_factor(
            request.user_code, request.activation_token, request.code
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "enabled": True,
        "message": "Conta ativada. Agora entre com o e-mail ou a matrícula gerada.",
    }


@app.post("/api/auth/password/reset")
async def password_reset(request: PasswordResetRequest) -> dict[str, Any]:
    try:
        result = reset_password_with_token(
            request.user_code, request.reset_token, request.new_password
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "reset": True,
        **result,
        "message": "Senha redefinida. Entre com a matrícula ou e-mail cadastrado.",
    }


@app.post("/api/auth/password")
async def password_change(
    request: PasswordChangeRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, bool]:
    try:
        change_password(current["sub"], request.current_password, request.new_password)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(current["sub"], "password_change")
    return {"changed": True}


@app.post("/api/auth/2fa/setup")
async def two_factor_setup(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_admin(current)
    return setup_two_factor(ADMIN_CODE)


@app.post("/api/auth/2fa/enable")
async def two_factor_enable(
    request: TwoFactorCodeRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, bool]:
    require_admin(current)
    try:
        enable_two_factor(ADMIN_CODE, request.code)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(current["sub"], "two_factor_enable")
    return {"enabled": True}


@app.get("/api/modules")
async def modules_endpoint(
    current: dict[str, Any] = Depends(require_user),
) -> list[dict[str, Any]]:
    refresh_modules()
    return [
        status_for(module_id)
        for module_id in MODULES
        if has_module_access(current, module_id)
    ]


@app.get("/api/domain-contracts")
async def domain_contracts_endpoint(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    refresh_modules()
    visible = [
        module_id for module_id in MODULES if has_module_access(current, module_id)
    ]
    return {"domains": manifests(visible), "contract_version": "1.0"}


@app.get("/api/tools")
async def tools_endpoint(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    del current
    return {
        "tools": tool_contracts(),
        "allowlist_only": True,
        "os_access": False,
        "arbitrary_network_access": False,
    }


@app.get("/api/capabilities")
async def capabilities(_: dict[str, Any] = Depends(require_user)) -> dict[str, Any]:
    privacy = privacy_status()
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    openai_store = os.getenv("OPENAI_STORE_RESPONSES", "false").strip().casefold() in {
        "1",
        "true",
        "yes",
        "on",
        "sim",
    }
    gemini_key = bool(os.getenv("GEMINI_API_KEY"))
    claude_key = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "ocr": ocr_status(),
        "links": {
            "enabled": True,
            "storage": LinkRepository(KNOWLEDGE_ROOT).backend,
            "postgres_configured": bool(
                os.getenv("SOFIA_POSTGRES_URL") or os.getenv("DATABASE_URL")
            ),
        },
        "expansion_storage": expansion_storage_status(),
        "storage": storage_status(),
        "embeddings": embedding_status(KNOWLEDGE_ROOT),
        "providers": {
            "auto": True,
            "ollama": True,
            "openai": openai_key and privacy["external_data_allowed"],
            "gemini": gemini_key and privacy["external_data_allowed"],
            "claude": claude_key and privacy["external_data_allowed"],
            "openai_key": openai_key,
            "gemini_key": gemini_key,
            "claude_key": claude_key,
        },
        "openai_store_responses": openai_store,
        "models": {
            "ollama": os.getenv("OLLAMA_MODEL", "qwen3.5:4b"),
            "openai": os.getenv("OPENAI_MODEL", "gpt-5.5"),
            "gemini": os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            "claude": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        },
        "privacy": privacy,
        "integrations": integration_status(),
        "training": {
            "sequential": True,
            "queued_modules": sorted(TRAINING_QUEUED),
            "active_modules": sorted(
                module_id
                for module_id, task in AUTO_TRAINING.items()
                if not task.done()
            ),
        },
        "expansion": {
            "enabled": expansion_settings()["enabled"],
            "admin_only": True,
            "status_endpoint": "/api/admin/expansion",
            "queue_persistent": True,
            "bounded_pages_per_topic": expansion_settings()["max_pages_per_topic"],
            "module_sequential_training": True,
        },
        "mcp": {"transport_http": "/mcp", "transport_stdio": True},
        "architecture": {
            "domain_contracts": True,
            "context_package": True,
            "hybrid_retrieval": {
                "lexical": "BM25-like",
                "vector": "TF-IDF local + Ollama neural",
                "rerank": True,
                "metadata_filter": True,
            },
            "pipeline_explorer": "/api/admin/pipeline",
            "readiness_checklist": "/api/admin/readiness",
            "knowledge_graph": "/api/admin/knowledge-graph",
            "production_gate": "/api/admin/production-gate",
            "domain_packages": True,
            "evidence_judge": True,
            "agent_harness": True,
            "observability": "/api/admin/observability",
            "semantic_evaluation": "/api/admin/evaluation",
            "embeddings": "/api/admin/embeddings",
            "insights": "/api/admin/insights",
            "raw_os_access": False,
        },
        "agents": {
            "core": True,
            "planner": True,
            "critic": True,
            "memory": True,
            "vision": "OCR local para imagens; vídeo e áudio ainda não instrumentados",
            "execution": "approval_required",
        },
    }


@app.get("/api/privacy")
async def privacy(_: dict[str, Any] = Depends(require_user)) -> dict[str, Any]:
    return privacy_status()


@app.get("/api/integrations")
async def integrations(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_admin(current)
    return await asyncio.to_thread(integration_status)


@app.post("/api/integrations/{connector}/sync")
async def integrations_sync(
    connector: str,
    request: IntegrationSyncRequest,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_admin(current)
    try:
        result = await asyncio.to_thread(
            sync_integration, connector, request.resource, request.max_pages
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(current["sub"], "institutional_sync", connector, request.resource)
    return result


@app.post("/api/modules/{module_id}/upload")
async def upload(
    module_id: str,
    file: UploadFile = File(...),
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    module_root(module_id)
    require_module_access(current, module_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Formato não suportado: {suffix or 'sem extensão'}")
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "Arquivo maior que 50 MB")
    destination_root = module_root(module_id) / (
        "imagens" if suffix in IMAGE_EXTENSIONS else "textos"
    )
    destination_root.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "arquivo").name
    destination = destination_root / safe_name
    digest = hashlib.sha256(content).digest()
    for existing in files_for(KNOWLEDGE_ROOT, module_id):
        if existing == destination or existing.stat().st_size != len(content):
            continue
        if hashlib.sha256(existing.read_bytes()).digest() == digest:
            raise HTTPException(
                409, f"Arquivo duplicado: conteúdo já existe em {existing.name}"
            )
    destination.write_bytes(content)
    pipeline = await asyncio.to_thread(
        record_document_pipeline, KNOWLEDGE_ROOT, module_id, destination
    )
    audit_event(current["sub"], "upload", module_id, safe_name)
    if pipeline.get("status") == "READY":
        schedule_auto_training(module_id, reason="document_ready")
    return {
        "uploaded": True,
        "module": module_id,
        "file": safe_name,
        "bytes": len(content),
        "ocr": ocr_status()
        if suffix in IMAGE_EXTENSIONS
        else {"available": False, "status": "not-applicable"},
        "processing": pipeline,
        "status": status_for(module_id),
    }


@app.post("/api/modules/{module_id}/links")
async def add_link(
    module_id: str,
    request: LinkCreateRequest,
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    module_root(module_id)
    require_module_access(current, module_id)
    max_pages = max(request.max_pages, 10) if request.dense else request.max_pages
    try:
        record = await asyncio.to_thread(
            ingest_link,
            KNOWLEDGE_ROOT,
            module_id,
            request.url,
            max_pages,
            20.0,
            None,
            request.max_depth,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    local_path = KNOWLEDGE_ROOT / module_id / "links" / str(record["file_name"])
    source_id = await asyncio.to_thread(
        ExpansionStore(KNOWLEDGE_ROOT).register_source,
        module_id,
        "url",
        url=str(record.get("url", request.url)),
        canonical_url=str(record.get("final_url", request.url)),
        local_path=str(local_path),
        title=str(record.get("title", "")),
        content_hash=str(record.get("content_hash", "")) or None,
        pages=int(record.get("pages", 1) or 1),
        bytes_count=local_path.stat().st_size if local_path.exists() else 0,
        etag=str(record.get("etag", "")),
        last_modified=str(record.get("last_modified", "")),
    )
    pipeline = await asyncio.to_thread(
        record_document_pipeline, KNOWLEDGE_ROOT, module_id, local_path, source_id
    )
    audit_event(
        current["sub"], "link_ingest", module_id, str(record.get("url", request.url))
    )
    if pipeline.get("status") == "READY":
        schedule_auto_training(module_id, reason="link_ready")
    return {
        "ingested": True,
        "module": module_id,
        "link": {
            **record,
            "requested_pages": max_pages,
            "max_depth": request.max_depth,
            "dense": request.dense,
            "offline_document": True,
            "offline_path": f"knowledge/{module_id}/links/{record['file_name']}",
            "sync_status": "saved",
            "processing": pipeline,
        },
        "status": status_for(module_id),
    }


@app.get("/api/modules/{module_id}/links")
async def module_links(
    module_id: str, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    module_root(module_id)
    require_module_access(current, module_id)
    repository = LinkRepository(KNOWLEDGE_ROOT)
    try:
        records = await asyncio.to_thread(repository.list, module_id)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    enriched = [
        {
            **record,
            "storage": record.get("storage", repository.backend),
            "offline_document": True,
            "offline_path": f"knowledge/{module_id}/links/{record.get('file_name', '')}",
            "sync_status": "saved",
        }
        for record in records
    ]
    return {"module": module_id, "storage": repository.backend, "links": enriched}


@app.get("/fhir/metadata")
async def fhir_metadata(
    current: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_module_access(current, "medicina")
    return capability_statement()


@app.get("/fhir/{resource_type}")
async def fhir_search(
    resource_type: str,
    patient: str | None = None,
    code: str | None = None,
    _count: int = 50,
    _: dict[str, Any] = Depends(require_user),
) -> dict[str, Any]:
    require_module_access(_, "medicina")
    try:
        return await asyncio.to_thread(
            search_resources, resource_type, patient, code, _count
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.get("/fhir/{resource_type}/{resource_id}")
async def fhir_read(
    resource_type: str, resource_id: str, _: dict[str, Any] = Depends(require_user)
) -> JSONResponse:
    require_module_access(_, "medicina")
    try:
        resource = await asyncio.to_thread(get_resource, resource_type, resource_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    if resource is None:
        raise HTTPException(404, "Recurso FHIR não encontrado")
    return JSONResponse(resource, media_type="application/fhir+json")


@app.post("/fhir/{resource_type}")
async def fhir_create(
    resource_type: str,
    resource: dict[str, Any],
    current: dict[str, Any] = Depends(require_user),
) -> JSONResponse:
    require_module_access(current, "medicina")
    if current.get("role") not in {"admin", "clinician"}:
        raise HTTPException(
            403,
            "Somente administradores ou profissionais autorizados podem gravar recursos FHIR",
        )
    try:
        stored = await asyncio.to_thread(save_resource, resource_type, resource)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(current["sub"], "fhir_create", resource_type, str(stored.get("id", "")))
    return JSONResponse(
        stored,
        status_code=201,
        media_type="application/fhir+json",
        headers={"Location": f"/fhir/{resource_type}/{stored['id']}"},
    )


@app.put("/fhir/{resource_type}/{resource_id}")
async def fhir_update(
    resource_type: str,
    resource_id: str,
    resource: dict[str, Any],
    current: dict[str, Any] = Depends(require_user),
) -> JSONResponse:
    require_module_access(current, "medicina")
    if current.get("role") not in {"admin", "clinician"}:
        raise HTTPException(
            403,
            "Somente administradores ou profissionais autorizados podem gravar recursos FHIR",
        )
    resource["id"] = resource_id
    try:
        stored = await asyncio.to_thread(save_resource, resource_type, resource)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    audit_event(current["sub"], "fhir_update", resource_type, resource_id)
    return JSONResponse(stored, media_type="application/fhir+json")


@app.get("/api/fhir/patients/{patient_id}/context")
async def fhir_patient_context(
    patient_id: str, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_module_access(current, "medicina")
    return await asyncio.to_thread(patient_context, patient_id)


@app.post("/api/chat")
async def chat(
    request: ChatRequest, current: dict[str, Any] = Depends(require_user)
) -> dict[str, Any]:
    require_module_access(current, request.module_id)
    try:
        return await rag_answer(
            request.module_id,
            request.provider,
            request.message,
            request.history,
            request.patient_id,
            request.language,
            request.response_style,
            current["sub"],
            request.retry,
            request.retry_of,
            request.retry_attempt,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/tools/{tool_name}")
async def run_tool(
    tool_name: str,
    request: ToolRequest,
    current: dict[str, Any] = Depends(require_user),
) -> Any:
    tools = {
        "list_knowledge_modules": list_knowledge_modules,
        "tensor_multiply": tensor_multiply,
        "random_generate": random_generate,
        "neural_train": neural_train,
        "neural_status": neural_status,
        "neural_infer": neural_infer,
        "neural_graph": neural_graph,
        "knowledge_graph": knowledge_graph,
        "semantic_embedding_status": semantic_embedding_status,
        "semantic_embed": semantic_embed,
        "readiness_check": readiness_check,
        "production_gate": production_gate,
        "monte_carlo_estimate": monte_carlo_estimate,
        "search_knowledge": search_knowledge,
        "agent_plan": agent_plan,
        "agent_memory_status": agent_memory_status,
        "query_theme_report": query_theme_report,
        "rag_answer": rag_answer,
        "analyst_scenario": analyst_scenario,
        "institutional_integration_status": institutional_integration_status,
        "institutional_integration_sync": institutional_integration_sync,
    }
    tool = tools.get(tool_name)
    if tool is None:
        raise HTTPException(404, "Ferramenta MCP desconhecida")
    contract = TOOL_CONTRACTS.get(tool_name)
    if contract is None:
        raise HTTPException(403, "Ferramenta não possui contrato de segurança")
    module_id = request.arguments.get("module_id")
    if module_id:
        module_root(str(module_id))
        require_module_access(current, str(module_id))
    if tool_name in {
        "institutional_integration_status",
        "institutional_integration_sync",
    }:
        require_admin(current)
    if tool_name in {"semantic_embed", "readiness_check"}:
        require_admin(current)
    if tool_name == "query_theme_report":
        require_statistics_admin(current)
    audit_event(
        current["sub"], contract.audit_event, tool_name, contract.required_capability
    )
    try:
        if tool_name == "list_knowledge_modules":
            refresh_modules()
            return [
                status_for(module_id)
                for module_id in MODULES
                if has_module_access(current, module_id)
            ]
        return await tool(**request.arguments)
    except (TypeError, ValueError) as exc:
        raise HTTPException(400, str(exc)) from exc


app.mount("/mcp", mcp.streamable_http_app())

if __name__ == "__main__":
    if os.getenv("SOFIA_TRANSPORT") == "stdio":
        mcp.run(transport="stdio")
    else:
        import uvicorn

        uvicorn.run(
            "api.server:app",
            host=os.getenv("SOFIA_BIND_HOST", "0.0.0.0"),
            port=8787,
            reload=False,
        )
