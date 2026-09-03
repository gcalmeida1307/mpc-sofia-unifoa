from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .analytics import record_query

MODULE_AGENTS = {
    "infraestrutura": "Agente de Infraestrutura",
    "medicina": "Agente Clínico",
    "direito": "Agente Jurídico",
    "financeiro": "Agente Financeiro",
    "recursos-humanos": "Agente de Pessoas",
    "departamento-pessoal": "Agente Trabalhista",
}
ACTION_TERMS = (
    "execute",
    "executar",
    "corrija",
    "corrigir",
    "altere",
    "alterar",
    "crie",
    "criar",
    "aplique",
    "aplicar",
    "reinicie",
    "reiniciar",
)


def specialist_for(module_id: str) -> str:
    return MODULE_AGENTS.get(module_id, f"Agente de {module_id.replace('-', ' ').title()}")


def build_plan(module_id: str, question: str, high_risk: bool = False, patient_context: bool = False) -> list[dict[str, Any]]:
    action_requested = any(term in question.casefold() for term in ACTION_TERMS)
    specialist = specialist_for(module_id)
    plan: list[dict[str, Any]] = [
        {
            "id": "perceive",
            "stage": "Perceber",
            "agent": "SOFIA CORE",
            "status": "complete",
            "detail": "Objetivo e idioma identificados; fontes externas não são usadas sem configuração.",
        },
        {
            "id": "route",
            "stage": "Roteiar",
            "agent": specialist,
            "status": "complete",
            "detail": f"A tarefa foi isolada no módulo {module_id}.",
        },
        {
            "id": "plan",
            "stage": "Planejar",
            "agent": "Planner",
            "status": "complete",
            "detail": "Consultar evidências locais, gerar uma síntese e validar cada afirmação.",
        },
        {
            "id": "retrieve",
            "stage": "Consultar RAG",
            "agent": f"RAG {module_id}",
            "status": "running",
            "detail": "Buscando chunks e documentos que sustentam a pergunta.",
        },
        {
            "id": "reason",
            "stage": "Raciocinar",
            "agent": "LLM local ou provider autorizado",
            "status": "pending",
            "detail": "Usar apenas as evidências aprovadas pelo gate do módulo.",
        },
        {
            "id": "critic",
            "stage": "Criticar",
            "agent": "Evaluator/Critic",
            "status": "pending",
            "detail": "Verificar aderência ao módulo, fontes e riscos antes de responder.",
        },
        {
            "id": "output",
            "stage": "Entregar",
            "agent": "SOFIA",
            "status": "pending",
            "detail": "Entregar resumo claro, com fontes e incertezas explícitas.",
        },
    ]
    if patient_context:
        plan.insert(
            4,
            {
                "id": "clinical_context",
                "stage": "Contextualizar",
                "agent": "MCP FHIR",
                "status": "complete",
                "detail": "Contexto clínico autorizado anexado para revisão profissional.",
            },
        )
    if high_risk:
        plan[5 if patient_context else 4]["detail"] += " Domínio de alto risco: sem diagnóstico, prescrição ou alteração automática."
    if action_requested:
        plan.append(
            {
                "id": "execution",
                "stage": "Agir",
                "agent": "MCP + Policy Engine",
                "status": "approval_required",
                "detail": "Ação externa somente com ferramenta configurada e autorização explícita; o modo atual não executa.",
            }
        )
    return plan


def update_stage(trace: list[dict[str, Any]], stage_id: str, status: str, detail: str | None = None) -> None:
    for item in trace:
        if item["id"] == stage_id:
            item["status"] = status
            if detail:
                item["detail"] = detail
            return


def critic(answer: str, evidence: str, high_risk: bool) -> dict[str, Any]:
    if not answer.strip():
        return {"verified": False, "reason": "A resposta ficou vazia."}
    if high_risk and not evidence.strip():
        return {"verified": False, "reason": "Domínio de alto risco sem evidência local."}
    answer_terms = {term for term in answer.casefold().split() if len(term) > 4}
    evidence_terms = {term for term in evidence.casefold().split() if len(term) > 4}
    overlap = len(answer_terms & evidence_terms)
    return {"verified": overlap >= 2, "reason": f"{overlap} termos verificáveis em comum."}


def remember_run(root: Path, module_id: str, question: str, sources: list[str], provider: str, verified: bool, user_code: str | None = None) -> int | None:
    """Store only operational metadata; never persist prompt, answer or clinical content."""
    path = root.parent / "data" / "agent_memory.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS agent_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, module_id TEXT NOT NULL, question_hash TEXT NOT NULL, sources TEXT NOT NULL, provider TEXT NOT NULL, verified INTEGER NOT NULL, created_at TEXT NOT NULL)"
        )
        digest = hashlib.sha256(question.strip().casefold().encode()).hexdigest()
        connection.execute(
            "INSERT INTO agent_runs (module_id, question_hash, sources, provider, verified, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (module_id, digest, ",".join(sources[:20]), provider, int(verified), datetime.now(UTC).isoformat()),
        )
        connection.commit()
    finally:
        connection.close()
    try:
        return record_query(root, module_id, question, sources, provider, verified, user_code=user_code)
    except Exception:  # noqa: BLE001
        # Analytics must never make a valid local answer unavailable.
        return None


def memory_status(root: Path, module_id: str | None = None) -> dict[str, Any]:
    path = root.parent / "data" / "agent_memory.sqlite3"
    if not path.exists():
        return {"runs": 0, "modules": [], "stores_raw_content": False}
    with sqlite3.connect(path) as connection:
        if module_id:
            row = connection.execute("SELECT COUNT(*), MAX(created_at) FROM agent_runs WHERE module_id = ?", (module_id,)).fetchone()
            return {"module": module_id, "runs": int(row[0] or 0), "last_run_at": row[1], "stores_raw_content": False}
        rows = connection.execute("SELECT module_id, COUNT(*) FROM agent_runs GROUP BY module_id ORDER BY module_id").fetchall()
    return {"runs": sum(int(row[1]) for row in rows), "modules": [{"module": row[0], "runs": row[1]} for row in rows], "stores_raw_content": False}
