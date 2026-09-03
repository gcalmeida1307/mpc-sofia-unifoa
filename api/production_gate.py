"""Single release gate combining quality, security and regression evidence."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .domains import DOMAIN_CONTRACTS
from .evaluation import evaluate_semantic_cases, evaluation_coverage
from .expansion import ExpansionStore
from .readiness import readiness_checklist
from .storage import status as storage_status


def production_gate(root: Path) -> dict[str, Any]:
    root = Path(root)
    # Accept both the API's knowledge root and the project root when the gate
    # is run from a maintenance script.  This prevents a false all-empty gate
    # caused solely by passing ``Path('.')``.
    if (root / "knowledge").is_dir() and not any((root / module_id).is_dir() for module_id in DOMAIN_CONTRACTS):
        root = root / "knowledge"
    module_rows: list[dict[str, Any]] = []
    for module_id in sorted(DOMAIN_CONTRACTS):
        try:
            module_rows.append(readiness_checklist(root, module_id))
        except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:  # pragma: no cover - deployment failures
            module_rows.append({"module_id": module_id, "ready_levels": 0, "partial_levels": 0, "blocked_levels": 10, "scale_ready": False, "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
    semantic_error: str | None = None
    try:
        semantic = evaluate_semantic_cases(root)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:  # pragma: no cover - deployment failures
        semantic_error = f"{type(exc).__name__}: {str(exc)[:180]}"
        semantic = {"case_count": 0, "reviewed_case_count": 0, "global_score": 0, "cases": [], "coverage": evaluation_coverage(root)}
    coverage = semantic.get("coverage", {})
    storage = storage_status()
    issues: list[str] = []
    warnings: list[str] = []
    if not storage.get("healthy"):
        message = "PostgreSQL primário não está saudável"
        (issues if storage.get("mode") == "production-primary" else warnings).append(message)
    incomplete = [row["module_id"] for row in module_rows if not row.get("scale_ready")]
    if incomplete:
        issues.append(f"módulos abaixo do checklist 10/10: {', '.join(incomplete)}")
    modules_without_corpus = [str(item) for item in coverage.get("modules_without_corpus", [])]
    modules_without_cases = [str(item) for item in coverage.get("modules_without_reviewed_cases", [])]
    if modules_without_cases:
        issues.append(f"módulos com corpus sem caso dourado revisado: {', '.join(modules_without_cases)}")
    if modules_without_corpus:
        issues.append(f"módulos sem corpus local: {', '.join(modules_without_corpus)}")
    if not semantic.get("case_count"):
        issues.append("não há casos dourados revisados no manifesto de avaliação")
    else:
        failed_cases = [case for case in semantic.get("cases", []) if case.get("status") != "pass"]
        if failed_cases:
            issues.append(f"{len(failed_cases)} caso(s) de regressão sem aprovação")
    if semantic_error:
        issues.append(f"avaliação semântica não executada: {semantic_error}")
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
        "semantic_evaluation": {
            "score": semantic.get("global_score", 0),
            "case_count": semantic.get("case_count", 0),
            "reviewed_case_count": semantic.get("reviewed_case_count", 0),
            "coverage": coverage,
        },
        "modules": [
            {
                "module_id": row["module_id"],
                "ready_levels": row["ready_levels"],
                "partial_levels": row["partial_levels"],
                "blocked_levels": row["blocked_levels"],
                "scale_ready": row["scale_ready"],
                "blocking_levels": [
                    {
                        "id": level["id"],
                        "title": level["title"],
                        "status": level["status"],
                        "score": level["score"],
                        "evidence": level["evidence"],
                        "action": level.get("action"),
                    }
                    for level in row.get("levels", [])
                    if level.get("status") != "ready"
                ],
            }
            for row in module_rows
        ],
        "coverage": coverage,
        "passed_checks": {
            "storage": bool(storage.get("healthy")) and not storage.get("local_scope_pending_migration"),
            "encryption": bool(os.getenv("SOFIA_ENCRYPTION_KEY") or os.getenv("SOFIA_DATA_ENCRYPTION_KEY")),
            "semantic_cases": bool(semantic.get("case_count")) and not any(case.get("status") != "pass" for case in semantic.get("cases", [])),
            "module_checklists": not incomplete,
            "quarantine": quarantined == 0,
        },
        "evaluation_error": semantic_error,
        "policy": "O gate não transforma score parcial em aprovação e não libera produção com falhas de segurança, corpus, evidência ou regressão.",
    }
