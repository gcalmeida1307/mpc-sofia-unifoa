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


def _load_cases(root: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(_manifest_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    cases = payload.get("cases", []) if isinstance(payload, dict) else []
    return [case for case in cases if isinstance(case, dict) and case.get("module") and case.get("question")]


def evaluate_semantic_cases(root: Path) -> dict[str, Any]:
    """Evaluate evidence meaning, coverage and source targeting.

    This is intentionally a retrieval/evidence metric, not an invented
    percentage for generated prose.  A case may declare ``expected_terms``
    and ``expected_sources`` as reviewed expectations in the manifest.
    """
    rows: list[dict[str, Any]] = []
    for index, case in enumerate(_load_cases(root), start=1):
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
        expects_evidence = bool(case.get("expected_evidence", case.get("category") not in {"insufficient_evidence"}))
        evidence_ok = bool(result.evidence) == expects_evidence
        if not expects_evidence:
            score = 1.0 if evidence_ok else 0.0
        else:
            source_score = 1.0 if source_match is None and result.evidence else float(bool(source_match))
            score = 0.45 * float(bool(result.evidence)) + 0.35 * term_coverage + 0.20 * source_score
        rows.append({
            "case_id": f"case-{index:03d}",
            "module": module_id,
            "category": case.get("category", "unclassified"),
            "evidence_count": len(result.evidence),
            "term_coverage": term_coverage,
            "source_match": source_match,
            "expected_evidence": expects_evidence,
            "score": round(score * 100, 1),
            "status": "pass" if score >= 0.6 else "review",
        })
    return {
        "kind": "semantic_evidence",
        "cases": rows,
        "case_count": len(rows),
        "global_score": round(sum(row["score"] for row in rows) / max(1, len(rows)), 1),
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
    }
