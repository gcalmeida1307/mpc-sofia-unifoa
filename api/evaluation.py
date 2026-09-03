"""Deterministic corpus and retrieval checks used by CI and the admin UI.

This is deliberately not presented as an LLM quality score.  It measures
whether each module has sources, whether the persisted document pipeline is
ready, and whether a representative module query retrieves evidence.  Human
reviewed golden cases can be added to ``tests/evals/manifest.json`` without
changing the runtime contract.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from .domains import DOMAIN_CONTRACTS
from .expansion import ExpansionStore
from .ingestion import files_for
from .policies import policy_for
from .retrieval import retrieve


def _normalize(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(char))


def _manifest_path(root: Path) -> Path:
    return root.parent / "tests" / "evals" / "manifest.json"


def _manifest(root: Path) -> dict[str, Any]:
    try:
        payload = json.loads(_manifest_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_cases(root: Path, *, reviewed_only: bool = False) -> list[dict[str, Any]]:
    cases = _manifest(root).get("cases", [])
    valid = [case for case in cases if isinstance(case, dict) and case.get("module") and case.get("question")]
    if reviewed_only:
        return [case for case in valid if case.get("reviewed") is True]
    return valid


def _expects_evidence(case: dict[str, Any]) -> bool:
    return bool(case.get("expected_evidence", case.get("category") not in {"insufficient_evidence"}))


def evaluation_coverage(root: Path) -> dict[str, Any]:
    """Report manifest coverage without pretending a draft case is approved."""
    manifest = _manifest(root)
    cases = _load_cases(root)
    reviewed = _load_cases(root, reviewed_only=True)
    configured_modules = [str(module) for module in manifest.get("modules", []) if str(module).strip()]
    rows: list[dict[str, Any]] = []
    for module_id in configured_modules:
        module_cases = [case for case in cases if str(case.get("module")) == module_id]
        module_reviewed = [case for case in reviewed if str(case.get("module")) == module_id]
        source_cases = [case for case in module_reviewed if _expects_evidence(case)]
        draft_source_cases = [case for case in module_cases if not case.get("reviewed") and _expects_evidence(case)]
        declared_sources = [case for case in source_cases if case.get("expected_sources")]
        paths = files_for(root, module_id)
        rows.append(
            {
                "module": module_id,
                "has_corpus": bool(paths),
                "documents": len(paths),
                "case_count": len(module_cases),
                "reviewed_case_count": len(module_reviewed),
                "draft_case_count": len(module_cases) - len(module_reviewed),
                "source_expectation_count": len(declared_sources),
                "source_expectations_required": len(source_cases),
                "draft_source_expectation_count": sum(1 for case in draft_source_cases if case.get("expected_sources")),
                "status": "no-data" if not paths else ("ready" if module_reviewed and len(declared_sources) == len(source_cases) else "needs-review"),
            }
        )
    return {
        "manifest_version": manifest.get("version"),
        "configured_modules": configured_modules,
        "case_count": len(cases),
        "reviewed_case_count": len(reviewed),
        "draft_case_count": len(cases) - len(reviewed),
        "modules": rows,
        "modules_without_reviewed_cases": [row["module"] for row in rows if row["has_corpus"] and not row["reviewed_case_count"]],
        "modules_without_corpus": [row["module"] for row in rows if not row["has_corpus"]],
    }


def evaluate_semantic_cases(root: Path) -> dict[str, Any]:
    """Evaluate evidence meaning, coverage and source targeting.

    This is intentionally a retrieval/evidence metric, not an invented
    percentage for generated prose.  A case may declare ``expected_terms``
    and ``expected_sources`` as reviewed expectations in the manifest.
    """
    rows: list[dict[str, Any]] = []
    for index, case in enumerate(_load_cases(root, reviewed_only=True), start=1):
        module_id = str(case["module"])
        question = str(case["question"])
        result = retrieve(root, module_id, question, policy_for(module_id), limit=6)
        context = _normalize(result.context)
        terms = [str(term) for term in case.get("expected_terms", []) if str(term).strip()]
        if not terms:
            terms = [term for term in re.findall(r"[\w]+", _normalize(question)) if len(term) >= 4 and term not in {"documento", "documentos", "conhecimento", "disponivel", "disponiveis", "modulo", "somente", "contexto"}]
        matched_terms = sum(1 for term in terms if _normalize(term) in context)
        term_coverage = round(matched_terms / max(1, len(terms)), 3)
        expected_sources = [str(source).casefold() for source in case.get("expected_sources", []) if str(source).strip()]
        source_match = None if not expected_sources else any(any(source in item.casefold() for source in expected_sources) for item in result.sources)
        expects_evidence = _expects_evidence(case)
        evidence_ok = bool(result.evidence) == expects_evidence
        provenance_ok = bool(expected_sources) if expects_evidence else True
        if not expects_evidence:
            score = 1.0 if evidence_ok else 0.0
        else:
            source_score = float(bool(source_match)) if expected_sources else 0.0
            score = 0.40 * float(bool(result.evidence)) + 0.30 * term_coverage + 0.20 * source_score + 0.10 * float(provenance_ok)
        rows.append({
            "case_id": f"case-{index:03d}",
            "module": module_id,
            "category": case.get("category", "unclassified"),
            "evidence_count": len(result.evidence),
            "term_coverage": term_coverage,
            "source_match": source_match,
            "expected_sources": expected_sources,
            "reviewed": True,
            "provenance_ok": provenance_ok,
            "expected_evidence": expects_evidence,
            "score": round(score * 100, 1),
            "status": "pass" if score >= 0.6 and provenance_ok else "review",
        })
    coverage = evaluation_coverage(root)
    return {
        "kind": "semantic_evidence",
        "cases": rows,
        "case_count": len(rows),
        "reviewed_case_count": len(rows),
        "global_score": round(sum(row["score"] for row in rows) / max(1, len(rows)), 1),
        "coverage": coverage,
        "note": "Métrica de recuperação, cobertura de termos e aderência de fontes; não representa a qualidade da redação de uma LLM.",
    }


def evaluate_corpus(root: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for module_id in sorted(DOMAIN_CONTRACTS):
        paths = files_for(root, module_id)
        query = f"Resuma o conhecimento disponível no módulo {module_id}"
        result = retrieve(root, module_id, query, policy_for(module_id), limit=4)
        status = ExpansionStore(root).snapshot(module_id)
        ready = int(status.get("documents_by_status", {}).get("READY", 0))
        corpus_score = 100.0 if paths else 0.0
        retrieval_score = 100.0 if result.evidence else 0.0
        readiness_score = 100.0 if ready >= len(paths) and paths else 0.0
        score = round((corpus_score + retrieval_score + readiness_score) / 3, 1)
        rows.append(
            {
                "module": module_id,
                "score": score,
                "documents": len(paths),
                "ready": ready,
                "retrieval_evidence": len(result.evidence),
                "status": "ready" if paths and ready >= len(paths) else "needs-data",
            }
        )
    semantic = evaluate_semantic_cases(root)
    return {
        "kind": "retrieval_smoke",
        "note": "Não é uma avaliação de qualidade de geração; respostas ainda precisam de casos dourados revisados por especialistas.",
        "modules": rows,
        "global_score": round(sum(row["score"] for row in rows) / max(1, len(rows)), 1),
        "semantic_evaluation": semantic,
        "evaluation_coverage": evaluation_coverage(root),
    }
