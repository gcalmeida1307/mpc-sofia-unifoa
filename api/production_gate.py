"""Single release gate combining quality, security and regression evidence."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .domains import DOMAIN_CONTRACTS
from .evaluation import evaluate_semantic_cases
from .expansion import ExpansionStore
from .readiness import readiness_checklist
from .storage import status as storage_status


def production_gate(root: Path) -> dict[str, Any]:
    module_rows: list[dict[str, Any]] = []
    for module_id in sorted(DOMAIN_CONTRACTS):
        try:
            module_rows.append(readiness_checklist(root, module_id))
        except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:  # pragma: no cover - deployment failures
            module_rows.append({"module_id": module_id, "ready_levels": 0, "partial_levels": 0, "blocked_levels": 10, "scale_ready": False, "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
    semantic = evaluate_semantic_cases(root)
    storage = storage_status()
    issues: list[str] = []
    warnings: list[str] = []
    if not storage.get("healthy"):
        message = "PostgreSQL primário não está saudável"
        (issues if storage.get("mode") == "production-primary" else warnings).append(message)
    incomplete = [row["module_id"] for row in module_rows if not row.get("scale_ready")]
    if incomplete:
        issues.append(f"módulos abaixo do checklist 10/10: {', '.join(incomplete)}")
    if not semantic.get("case_count"):
        issues.append("não há casos dourados revisados no manifesto de avaliação")
    else:
        failed_cases = [case for case in semantic.get("cases", []) if case.get("status") != "pass"]
        if failed_cases:
            issues.append(f"{len(failed_cases)} caso(s) de regressão sem aprovação")
    if not os.getenv("SOFIA_ENCRYPTION_KEY") and not os.getenv("SOFIA_DATA_ENCRYPTION_KEY"):
        issues.append("chave de criptografia em repouso não configurada")
    if storage.get("mode") == "production-primary" and storage.get("local_scope_pending_migration"):
        issues.append("stores locais de autenticação, FHIR, integrações e insights ainda precisam ser migrados ou aprovados formalmente")
    quarantined = 0
    for module_id in DOMAIN_CONTRACTS:
        try:
            snapshot = ExpansionStore(root).snapshot(module_id)
            quarantined += int(snapshot.get("documents_by_status", {}).get("QUARANTINED", 0) or 0)
        except (KeyError, OSError, RuntimeError, TypeError, ValueError):
            issues.append(f"não foi possível auditar o armazenamento do módulo {module_id}")
    if quarantined:
        issues.append(f"{quarantined} documento(s) em quarentena")
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "blocked" if issues else "ready",
        "release_allowed": not issues,
        "issues": issues,
        "warnings": warnings,
        "storage": storage,
        "semantic_evaluation": {"score": semantic.get("global_score", 0), "case_count": semantic.get("case_count", 0)},
        "modules": [
            {
                "module_id": row["module_id"],
                "ready_levels": row["ready_levels"],
                "partial_levels": row["partial_levels"],
                "blocked_levels": row["blocked_levels"],
                "scale_ready": row["scale_ready"],
            }
            for row in module_rows
        ],
        "policy": "O gate não transforma score parcial em aprovação e não libera produção com falhas de segurança, corpus, evidência ou regressão.",
    }
