"""Operational readiness checks for the Pipeline Explorer.

The checklist is intentionally conservative.  It reports what the local
runtime can prove from the corpus, pipeline metadata and telemetry; it never
turns a missing measurement into a green percentage.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .domains import domain_for
from .embeddings import embedding_status
from .evaluation import _load_cases
from .expansion import ExpansionStore
from .ingestion import files_for
from .neural import status as neural_status
from .observability import snapshot as observability_snapshot
from .policies import policy_for
from .privacy import status as privacy_status
from .retrieval import retrieve

_REQUIRED_ARTIFACTS = ("summary", "keywords_json", "entities_json", "concepts_json", "relations_json", "questions_json")
_OCR_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
_READY = "ready"
_PARTIAL = "partial"
_BLOCKED = "blocked"


def _json_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return value
    if value is None:
        return None
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def _level(
    number: int,
    title: str,
    status: str,
    score: float,
    details: str,
    evidence: list[str],
    action: str | None = None,
) -> dict[str, Any]:
    labels = {_READY: "Pronto", _PARTIAL: "Parcial", _BLOCKED: "Bloqueado"}
    return {
        "id": number,
        "title": title,
        "status": status,
        "status_label": labels.get(status, "Não avaliado"),
        "score": round(max(0.0, min(100.0, score)), 1),
        "details": details,
        "evidence": evidence[:6],
        "action": action,
    }


def _pipeline_data(root: Path, module_id: str) -> tuple[list[Path], list[dict[str, Any]], dict[str, Any]]:
    paths = files_for(root, module_id)
    store = ExpansionStore(root)
    documents = store.pipeline_documents(module_id, limit=500)
    return paths, documents, store.snapshot(module_id)


def _quality_level(paths: list[Path], documents: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    if not paths:
        return _level(1, "Ingestão estável", _BLOCKED, 0, "O módulo ainda não possui documentos locais.", ["Nenhum arquivo foi encontrado no diretório do módulo."], "Adicione um documento, imagem ou link e execute a atualização do pipeline.")

    by_name = {str(item.get("file_name", "")): item for item in documents}
    failed = [item for item in documents if str(item.get("status", "")).upper() in {"FAILED", "QUARANTINED"}]
    missing_pipeline = [path.name for path in paths if path.name not in by_name]
    missing_quality: list[str] = []
    missing_ocr: list[str] = []
    low_quality: list[str] = []
    ready_count = 0
    for path in paths:
        item = by_name.get(path.name)
        if not item:
            continue
        if str(item.get("status", "")).upper() == "READY":
            ready_count += 1
        artifacts = item.get("artifacts") or {}
        quality = item.get("extraction_quality")
        if quality is None:
            quality = artifacts.get("quality")
        try:
            quality_value = float(quality)
        except (TypeError, ValueError):
            quality_value = None
        if quality_value is None:
            missing_quality.append(path.name)
        elif quality_value < 0.60:
            low_quality.append(path.name)
        if path.suffix.casefold() in _OCR_EXTENSIONS:
            ocr_quality = item.get("ocr_quality")
            if ocr_quality is None:
                ocr_quality = artifacts.get("ocr_quality")
            try:
                ocr_value = float(ocr_quality)
            except (TypeError, ValueError):
                ocr_value = None
            if ocr_value is None:
                missing_ocr.append(path.name)
            elif ocr_value < 0.60:
                low_quality.append(f"OCR: {path.name}")

    if failed or low_quality:
        status = _BLOCKED
    elif missing_pipeline or missing_quality or missing_ocr or ready_count < len(paths):
        status = _PARTIAL
    else:
        status = _READY
    score = 100 * ready_count / max(1, len(paths))
    evidence = [f"{ready_count}/{len(paths)} documento(s) com estado READY.", f"{int(summary.get('processing_errors', 0) or 0)} erro(s) de processamento registrados."]
    if missing_pipeline:
        evidence.append(f"Fora do pipeline: {', '.join(missing_pipeline[:3])}.")
    if missing_quality:
        evidence.append(f"Sem score de qualidade: {', '.join(missing_quality[:3])}.")
    if missing_ocr:
        evidence.append(f"OCR sem score: {', '.join(missing_ocr[:3])}.")
    if failed:
        evidence.append(f"Falha/quarentena: {', '.join(str(item.get('file_name', 'documento')) for item in failed[:3])}.")
    return _level(1, "Ingestão estável", status, score, "Cada fonte precisa atravessar extração, OCR quando aplicável, qualidade e normalização antes de ser considerada pronta.", evidence, "Reprocesse os documentos fora do pipeline ou em falha; um OCR reprovado deve ser corrigido antes da publicação.")


def _comprehension_level(documents: list[dict[str, Any]]) -> dict[str, Any]:
    if not documents:
        return _level(2, "Compreensão", _BLOCKED, 0, "Não há documentos processados para gerar conhecimento derivado.", ["Resumo, palavras-chave, entidades, relações e perguntas ainda não podem ser auditados."], "Execute a ingestão do módulo.")
    complete = 0
    missing: list[str] = []
    for item in documents:
        artifacts = item.get("artifacts") or {}
        valid = bool(str(artifacts.get("summary") or item.get("summary") or "").strip())
        for field in _REQUIRED_ARTIFACTS[1:]:
            if _json_value(artifacts.get(field)) is None:
                valid = False
        if valid:
            complete += 1
        else:
            missing.append(str(item.get("file_name", "documento")))
    score = 100 * complete / max(1, len(documents))
    status = _READY if complete == len(documents) else (_PARTIAL if complete else _BLOCKED)
    evidence = [f"{complete}/{len(documents)} documento(s) têm os artefatos de compreensão registrados."]
    if missing:
        evidence.append(f"Incompletos: {', '.join(missing[:4])}.")
    return _level(2, "Compreensão", status, score, "O pipeline cria uma representação pesquisável do documento, sem confundir metadados de navegação com conhecimento.", evidence, "Reprocesse os documentos que não têm todos os artefatos derivados.")


def _organization_level(module_id: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
    if not documents:
        return _level(3, "Organização e proveniência", _BLOCKED, 0, "Sem documentos não há metadados para auditar.", [], "Ingestione ao menos uma fonte no módulo.")
    fields = ("module_id", "source_origin", "author", "created_at", "version_number", "sensitivity")
    present = 0
    missing: list[str] = []
    for item in documents:
        absent = [field for field in fields if item.get(field) in (None, "", [])]
        # The effective confidence is the pipeline quality persisted for the
        # document; it is reported separately because it is numeric evidence.
        if item.get("extraction_quality") is None and not (item.get("artifacts") or {}).get("quality"):
            absent.append("confidence")
        present += len(fields) + 1 - len(absent)
        if absent:
            missing.append(f"{item.get('file_name', 'documento')}: {', '.join(absent)}")
    total = len(documents) * (len(fields) + 1)
    score = 100 * present / max(1, total)
    status = _READY if not missing else _PARTIAL
    evidence = [f"{present}/{total} campos de proveniência preenchidos.", f"Módulo validado: {module_id}."]
    if missing:
        evidence.append(f"Pendências: {'; '.join(missing[:3])}.")
    return _level(3, "Organização e proveniência", status, score, "Cada fonte deve ser rastreável por módulo, origem, autoria, data, versão, confiança e sensibilidade.", evidence, "Complete os metadados ausentes na ingestão ou na tela de administração.")


def _rag_level(root: Path, module_id: str, documents: list[dict[str, Any]], embeddings: dict[str, Any]) -> dict[str, Any]:
    if not documents:
        return _level(4, "RAG e reranking", _BLOCKED, 0, "Não há corpus para classificar ou recuperar.", [], "Ingestione fontes no módulo.")
    question = "Resuma o conhecimento principal deste módulo"
    for item in documents:
        questions = _json_value((item.get("artifacts") or {}).get("questions_json")) or []
        if questions and isinstance(questions, list):
            question = str(questions[0])
            break
    try:
        result = retrieve(root, module_id, question, policy_for(module_id), limit=5)
    except (OSError, RuntimeError, ValueError):
        result = None
    evidence_count = len(result.evidence) if result else 0
    neural = next((row for row in embeddings.get("modules", []) if row.get("module_id") == module_id), {})
    neural_ready = neural.get("status") == "ready"
    if not evidence_count:
        status = _BLOCKED
    elif neural_ready:
        status = _READY
    else:
        status = _PARTIAL
    score = (70 if evidence_count else 0) + (30 if neural_ready else 0)
    evidence = [f"Recuperação de teste: {evidence_count} evidência(s) aceitas.", "Busca híbrida local com filtros de módulo e reranking lexical/semântico."]
    if not neural_ready:
        evidence.append(f"Índice neural do módulo: {neural.get('status', 'pending')}.")
    return _level(4, "RAG e reranking", status, score, "Antes da geração, o CORE classifica a consulta, recupera evidências do módulo e aplica o reranking disponível.", evidence, "Complete o índice neural do módulo e repita o teste de recuperação.")


def _validation_level(root: Path, module_id: str, documents: list[dict[str, Any]]) -> dict[str, Any]:
    if not documents:
        return _level(5, "Validação antes da resposta", _BLOCKED, 0, "Não há evidências para validar domínio, suficiência ou conflitos.", [], "Ingestione e valide o corpus.")
    valid = sum(1 for item in documents if str(item.get("validation_status", "")).upper() == "READY" and str(item.get("status", "")).upper() == "READY")
    score = 100 * valid / max(1, len(documents))
    status = _READY if valid == len(documents) else (_PARTIAL if valid else _BLOCKED)
    contract = domain_for(module_id)
    evidence = [f"{valid}/{len(documents)} documento(s) com validação READY.", f"Política do módulo: citações={'obrigatórias' if contract.require_citation else 'conforme o tipo de resposta'}, alto risco={'sim' if contract.high_risk else 'não'}."]
    return _level(5, "Validação antes da resposta", status, score, "O sistema verifica o domínio, a presença de evidência e o nível de risco antes de entregar uma síntese.", evidence, "Reprocesse documentos em estado VALIDATING ou corrija a evidência insuficiente antes de liberar o corpus.")


def _observability_level(root: Path, module_id: str) -> dict[str, Any]:
    payload = observability_snapshot(root, module_id, 20)
    traces = payload.get("traces", [])
    if not traces:
        return _level(6, "Observabilidade", _BLOCKED, 0, "Nenhuma execução observável foi registrada para este módulo.", ["Não há latência, provider, modelo ou confiança para auditar."], "Execute uma pergunta no chat e atualize o Explorer.")
    operational = 0
    complete_cost = 0
    for trace in traces:
        if trace.get("latency_ms") is not None and trace.get("provider") and trace.get("confidence") is not None:
            operational += 1
        metrics = _json_value(trace.get("metrics_json")) or {}
        if metrics.get("tokens") is not None and metrics.get("cost") is not None:
            complete_cost += 1
    score = 70 * operational / max(1, len(traces)) + 30 * complete_cost / max(1, len(traces))
    status = _READY if operational == len(traces) and complete_cost == len(traces) else _PARTIAL
    evidence = [f"{operational}/{len(traces)} trace(s) com latência, provider, modelo e confiança.", f"{complete_cost}/{len(traces)} trace(s) com tokens e custo."]
    if complete_cost < len(traces):
        evidence.append("Tokens e custo ainda não são retornados por todos os providers; não foram estimados.")
    return _level(6, "Observabilidade", status, score, "A execução registra telemetria operacional sem armazenar o conteúdo da pergunta ou da resposta.", evidence, "Instrumente usage_tokens e cost no adaptador de cada provider para fechar este nível.")


def _regression_level(root: Path, module_id: str) -> dict[str, Any]:
    cases = [case for case in _load_cases(root) if str(case.get("module")) == module_id]
    if not cases:
        return _level(7, "Suíte de regressão", _BLOCKED, 0, "Não há casos revisados para este módulo.", ["Sem perguntas douradas, não existe gate de regressão."], "Cadastre perguntas esperadas e fontes aprovadas em tests/evals/manifest.json.")
    expected_sources = sum(1 for case in cases if case.get("expected_sources"))
    # Defining a reviewed case is already part of the level; declaring the
    # expected source completes the stricter provenance half of the score.
    score = 40 + 60 * expected_sources / max(1, len(cases))
    status = _READY if expected_sources == len(cases) else _PARTIAL
    return _level(7, "Suíte de regressão", status, score, "A suíte existe, mas só deve liberar produção depois de uma avaliação revisada e repetível.", [f"{len(cases)} caso(s) revisável(is) no manifesto.", f"{expected_sources}/{len(cases)} caso(s) declaram fonte esperada.", "O score de geração não é inventado: precisa de revisão humana especializada."], "Execute Avaliar corpus e revise os casos que retornarem review antes de usar um gate de produção.")


def _security_level() -> dict[str, Any]:
    privacy = privacy_status()
    encryption = bool(os.getenv("SOFIA_ENCRYPTION_KEY") or os.getenv("SOFIA_DATA_ENCRYPTION_KEY"))
    controls = [
        bool(privacy.get("data_minimization")),
        bool(privacy.get("external_redaction")),
        bool(privacy.get("audit_log")),
        encryption,
    ]
    score = 100 * sum(controls) / len(controls)
    status = _READY if all(controls) else _PARTIAL
    evidence = [
        f"Minimização: {'ativa' if controls[0] else 'não configurada'}.",
        f"Redação externa: {'ativa' if controls[1] else 'não configurada'}.",
        f"Auditoria: {'ativa' if controls[2] else 'não configurada'}.",
        f"Chave de criptografia em repouso: {'configurada' if encryption else 'não configurada'}.",
        "Contexto clínico externo permanece bloqueado por padrão.",
    ]
    return _level(8, "Segurança, LGPD e auditoria", status, score, "Os controles técnicos são reportados separadamente da avaliação jurídica de finalidade, base legal e governança.", evidence, "Configure uma chave de criptografia em segredo do ambiente e valide retenção, acesso e base legal com o responsável.")


def _intelligence_level(root: Path, module_id: str, documents: list[dict[str, Any]], embeddings: dict[str, Any]) -> dict[str, Any]:
    try:
        neural = neural_status(root, module_id)
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        neural = {"trained": False, "stale": True, "error": "modelo neural indisponível"}
    neural_ready = bool(neural.get("trained")) and not bool(neural.get("stale"))
    has_docs = bool(documents)
    has_embedding = any(row.get("module_id") == module_id and row.get("items", 0) for row in embeddings.get("modules", []))
    score = 40 * has_docs + 30 * has_embedding + 30 * neural_ready
    status = _READY if score == 100 else (_PARTIAL if score else _BLOCKED)
    evidence = [
        f"Corpus local: {'disponível' if has_docs else 'ausente'}.",
        f"Embeddings: {'disponíveis' if has_embedding else 'ausentes'}.",
        f"Rede neural: {'treinada e atualizada' if neural_ready else 'não treinada ou desatualizada'}.",
        "Resumo, comparação, conflitos e recomendações dependem de evidência recuperada; não são respostas livres.",
    ]
    return _level(9, "Inteligência assistida por evidências", status, score, "As capacidades de síntese, comparação e análise de cenários são combinadas com RAG, embeddings e a rede do módulo.", evidence, "Treine/reindexe o módulo e revise as fontes antes de considerar as recomendações maduras.")


def _self_evaluation_level(root: Path, module_id: str) -> dict[str, Any]:
    payload = observability_snapshot(root, module_id, 20)
    traces = payload.get("traces", [])
    explainable = sum(1 for trace in traces if trace.get("provider") and trace.get("confidence") is not None and trace.get("metrics_json"))
    score = 100 * explainable / max(1, len(traces)) if traces else 0
    status = _READY if traces and explainable == len(traces) else (_PARTIAL if explainable else _BLOCKED)
    evidence = [f"{explainable}/{len(traces)} execução(ões) têm provider, confiança e métricas do caminho."] if traces else ["Nenhuma execução registrada."]
    evidence.append("A explicação é telemetria do pipeline e fontes usadas; não expõe cadeia privada de pensamento.")
    return _level(10, "Autoavaliação", status, score, "Antes da resposta, a Sofia pode informar domínio, fontes, etapas, verificação e confiança calculada.", evidence, "Execute uma consulta e mantenha o retorno de pipeline/context_package habilitado no cliente.")


def readiness_checklist(root: Path, module_id: str) -> dict[str, Any]:
    """Build the ten-level checklist for one module using only local facts."""
    paths, documents, summary = _pipeline_data(root, module_id)
    embeddings = embedding_status(root, module_id)
    levels = [
        _quality_level(paths, documents, summary),
        _comprehension_level(documents),
        _organization_level(module_id, documents),
        _rag_level(root, module_id, documents, embeddings),
        _validation_level(root, module_id, documents),
        _observability_level(root, module_id),
        _regression_level(root, module_id),
        _security_level(),
        _intelligence_level(root, module_id, documents, embeddings),
        _self_evaluation_level(root, module_id),
    ]
    ready_levels = sum(level["status"] == _READY for level in levels)
    partial_levels = sum(level["status"] == _PARTIAL for level in levels)
    blocked_levels = len(levels) - ready_levels - partial_levels
    return {
        "module_id": module_id,
        "evaluated_at": datetime.now(UTC).isoformat(),
        "ready_levels": ready_levels,
        "partial_levels": partial_levels,
        "blocked_levels": blocked_levels,
        "scale_ready": ready_levels == len(levels),
        "summary": f"{ready_levels}/10 níveis prontos; {partial_levels} parciais e {blocked_levels} bloqueados. O sistema só deve ser considerado escalável quando os dez níveis estiverem prontos.",
        "levels": levels,
    }
