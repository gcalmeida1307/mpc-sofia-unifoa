from __future__ import annotations

import asyncio
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .fhir import patient_context
from .neural import infer as neural_infer
from .neural import status as neural_status
from .orchestration import answer as orchestrate_answer
from .orchestration import local_no_evidence, normalize_language
from .policies import policy_for
from .retrieval import retrieve


def _seed(module_id: str, question: str) -> int:
    return int(hashlib.sha256(f"{module_id}:{question}".encode()).hexdigest()[:8], 16)


def _simulate(baseline: float, volatility: float, samples: int, seed: int) -> dict[str, Any]:
    scale = max(abs(baseline) * volatility, volatility, 1e-6)
    values = np.random.default_rng(seed).normal(baseline, scale, samples)
    mean = float(values.mean())
    standard_deviation = float(values.std(ddof=1))
    confidence = 1.96 * standard_deviation / math.sqrt(samples)
    return {
        "baseline": round(baseline, 6),
        "volatility": round(volatility, 6),
        "samples": samples,
        "random_seed": seed,
        "mean": round(mean, 6),
        "p10": round(float(np.percentile(values, 10)), 6),
        "p50": round(float(np.percentile(values, 50)), 6),
        "p90": round(float(np.percentile(values, 90)), 6),
        "probability_below_baseline": round(float(np.mean(values < baseline)), 6),
        "confidence_95_mean": [round(mean - confidence, 6), round(mean + confidence, 6)],
    }


async def analyze_scenario(root: Path, module_id: str, provider: str, question: str, baseline: float = 100.0, volatility: float = 0.1, samples: int = 5000, patient_id: str | None = None, language: str = "pt-BR", external_allowed: bool | None = None) -> dict[str, Any]:
    language = normalize_language(language)
    if not math.isfinite(baseline) or not 0 <= volatility <= 1 or not 100 <= samples <= 200_000:
        raise ValueError("baseline deve ser finito, volatility deve estar entre 0 e 1 e samples entre 100 e 200.000")
    if patient_id and module_id != "medicina":
        raise ValueError("patient_id só pode ser usado no módulo medicina")
    policy = policy_for(module_id)
    evidence = retrieve(root, module_id, question, policy)
    if not evidence.has_quality_evidence:
        return {
            "module": module_id,
            "module_only": True,
            "analysis": local_no_evidence(policy, language),
            "provider": "policy",
            "model": "evidence-gate",
            "sources": [],
            "evidence_found": False,
            "verified": True,
            "scenario": None,
            "neural": {"trained": False, "status": "não executada sem evidência local"},
            "pipeline": ["mcp.search_knowledge:blocked", "random_generate:not_called", "neural_infer:not_called", "monte_carlo_estimate:not_called", "llm:not_called"],
        }
    simulation = _simulate(baseline, volatility, samples, _seed(module_id, question))
    model = neural_status(root, module_id)
    neural_result: dict[str, Any] = {"trained": False, "status": "treine o modelo deste módulo para incluir o sinal neural"}
    if model.get("trained"):
        neural_input = [min(1.0, abs(baseline) / (abs(baseline) + 1.0)), volatility, 0.5]
        neural_result = neural_infer(root, module_id, neural_input)
        neural_result["input_definition"] = "baseline normalizado, volatilidade, confiança neutra"
    clinical = await asyncio.to_thread(patient_context, patient_id) if patient_id else None
    context = json.dumps({"monte_carlo": simulation, "neural": neural_result, "fhir_patient_context": clinical}, ensure_ascii=False)
    result = await orchestrate_answer(root=root, module_id=module_id, provider=provider, question=question, history=[], extra_context=context, language=language, external_allowed=external_allowed)
    return {
        "module": module_id,
        "patient_id": patient_id,
        "language": language,
        "module_only": True,
        "analysis": result.answer,
        "provider": result.provider,
        "model": result.model,
        "sources": result.sources,
        "evidence_found": result.evidence_found,
        "evidence_score": result.evidence_score,
        "verified": result.verified,
        "scenario": simulation,
        "neural": neural_result,
        "guardrail": "Cenário de apoio à decisão; não é previsão, diagnóstico ou autorização automática.",
        "pipeline": ["mcp.search_knowledge:evidence_found", "random_generate:complete", "neural_infer:complete" if model.get("trained") else "neural_infer:skipped_untrained", "monte_carlo_estimate:complete", f"llm:{result.provider}", "output:verified" if result.verified else "output:rejected"],
    }
