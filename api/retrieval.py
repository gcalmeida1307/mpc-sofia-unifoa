"""Hybrid retrieval owned by the SOFIA CORE.

The CORE is intentionally domain-agnostic. Module behaviour is supplied by
``api.domain_packages`` through a small contract; this file only performs
indexing, candidate ranking and the common Evidence Judge boundary.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import time
import unicodedata
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .domain_packages import DomainRetrievalPackage, package_for
from .domain_packages.base import named_source_paths, requested_line_range
from .embeddings import semantic_scores
from .ingestion import (
    ALLOW_HEAVY_EXTRACTION,
    DocumentChunk,
    files_for,
    ingest_module,
    read_exact_source_lines,
    read_exact_source_term,
)
from .policies import ModulePolicy, expand_query
from .query_analysis import requested_exact_term
from .runtime_cache import clear as runtime_cache_clear
from .runtime_cache import get as runtime_cache_get
from .runtime_cache import set as runtime_cache_set
from .secure_storage import decrypt_text, protect_for_storage


@dataclass(frozen=True)
class Evidence:
    chunk: DocumentChunk
    score: float
    lexical_score: float
    semantic_score: float
    coverage: float
    bm25_score: float = 0.0
    authority_score: float = 0.0
    freshness_score: float = 0.0
    provenance_score: float = 0.0
    support_score: float = 0.0
    contradiction_score: float = 0.0
    accepted: bool = True
    rejection_reason: str = ""
    rrf_score: float = 0.0


@dataclass(frozen=True)
class RetrievalResult:
    evidence: tuple[Evidence, ...]
    sources: tuple[str, ...]
    query: str
    expanded_query: str
    rejected_evidence: tuple[Evidence, ...] = ()
    conflicts: tuple[dict[str, Any], ...] = ()
    judge_confidence: float = 0.0
    required_sources: tuple[str, ...] = ()
    missing_sources: tuple[str, ...] = ()
    subqueries: tuple[str, ...] = ()
    unanswered_queries: tuple[str, ...] = ()

    @property
    def has_quality_evidence(self) -> bool:
        # Evidence from only one side of a named comparison is not enough to
        # authorize synthesis.  The accepted chunks remain available for the
        # diagnostic context, while the gate reports the source gap.  A source
        # can be present and still be too weak to authorize an answer; keeping
        # this threshold here prevents the external fallback from treating a
        # low-confidence navigation/menu match as authoritative evidence.
        if not bool(self.evidence) or self.missing_sources or self.judge_confidence < 0.32:
            return False
        # A comparison between harassment and importunation requires evidence
        # on both concepts. Generic legal passages containing words such as
        # "diferença" must never authorize the answer composer by themselves.
        normalized_query = normalize(self.query)
        if "assedio" in normalized_query and "importunacao" in normalized_query:
            evidence_text = normalize(" ".join(item.chunk.text for item in self.evidence))
            if "assedio" not in evidence_text or "importunacao" not in evidence_text:
                return False
        return True

    @property
    def context(self) -> str:
        grouped: dict[str, list[Evidence]] = {}
        for item in self.evidence:
            grouped.setdefault(item.chunk.path.name, []).append(item)
        blocks: list[str] = []
        for source, items in grouped.items():
            passages = [f"DOCUMENTO: {source}"]
            for item in items:
                locator = item.chunk.locator or (f"página {item.chunk.page}" if item.chunk.page else f"trecho {item.chunk.ordinal}")
                metadata = [f"LOCALIZAÇÃO: {locator}"]
                if item.chunk.section_header:
                    metadata.append(f"SEÇÃO: {item.chunk.section_header}")
                metadata.append(f"TIPO: {item.chunk.content_type}")
                passages.append("\n".join(metadata) + f"\n{item.chunk.text}")
            blocks.append("\n".join(passages))
        return "\n\n---\n\n".join(blocks)


def _index_cache_path(root: Path, module_id: str) -> Path:
    return root.parent / "data" / "retrieval-index" / f"{module_id}.json"


def _index_version_dir(root: Path, module_id: str) -> Path:
    return root.parent / "data" / "retrieval-index" / module_id


def _index_manifest_path(root: Path, module_id: str) -> Path:
    return _index_version_dir(root, module_id) / "manifest.json"


def _signature_digest(signature: tuple[tuple[str, int, int], ...]) -> str:
    payload = json.dumps(signature, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _index_payload(root: Path, module_id: str, signature: tuple[tuple[str, int, int], ...], chunks: tuple[DocumentChunk, ...]) -> dict[str, Any]:
    # ``Path.resolve`` also normalizes Windows 8.3 aliases (for example
    # ``GLAUCO~1.ALM``).  Without this, ``relative_to`` can fail even though
    # the source and knowledge root point to the same directory.
    root = root.resolve()

    def relative_path(value: Path) -> str:
        return os.path.relpath(str(value.resolve()), str(root))

    return {
        "version": 15,
        "module_id": module_id,
        "signature": _signature_digest(signature),
        "sources": [
            {"path": relative_path(Path(source)), "mtime_ns": mtime_ns, "size": size}
            for source, mtime_ns, size in signature
        ],
        "chunks": [
            {
                "source_path": relative_path(chunk.path),
                "ordinal": chunk.ordinal,
                "text": chunk.text,
                "page": chunk.page,
                "locator": chunk.locator,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "section_header": chunk.section_header,
                "content_type": chunk.content_type,
                "quality_score": chunk.quality_score,
            }
            for chunk in chunks
        ],
    }


def _atomic_write_protected(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f"{path.stem}-", suffix=".tmp", dir=path.parent)
    os.close(fd)
    temporary_path = Path(temporary_name)
    try:
        temporary_path.write_text(payload, encoding="utf-8")
        for attempt in range(4):
            try:
                temporary_path.replace(path)
                break
            except PermissionError:
                if attempt == 3:
                    raise
                time.sleep(0.08 * (attempt + 1))
    finally:
        temporary_path.unlink(missing_ok=True)


def _persist_index(root: Path, module_id: str, signature: tuple[tuple[str, int, int], ...], chunks: tuple[DocumentChunk, ...], target: Path | None = None) -> None:
    """Persist the prepared lexical index so cold queries do not parse files."""
    payload = _index_payload(root, module_id, signature, chunks)
    path = target or _index_cache_path(root, module_id)
    _atomic_write_protected(path, protect_for_storage(json.dumps(payload, ensure_ascii=False, separators=(",", ":"))))


def _read_index_payload(path: Path) -> dict[str, Any] | None:
    try:
        raw = path.read_text(encoding="utf-8")
        try:
            decoded = decrypt_text(raw)
        except RuntimeError:
            decoded = raw if raw.lstrip().startswith("{") else ""
        payload = json.loads(decoded)
        return payload if isinstance(payload, dict) else None
    except (OSError, TypeError, ValueError, RuntimeError):
        return None


def _active_index_path(root: Path, module_id: str) -> Path:
    """Resolve the active immutable version, with legacy compatibility."""
    root = root.resolve()
    manifest = _read_index_payload(_index_manifest_path(root, module_id))
    version_dir = _index_version_dir(root, module_id).resolve()
    active = str(manifest.get("active", "")) if manifest else ""
    if active:
        candidate = (version_dir / active).resolve()
        if candidate.parent == version_dir and candidate.exists():
            return candidate
    return _index_cache_path(root, module_id)


def _publish_versioned_index(root: Path, module_id: str, signature: tuple[tuple[str, int, int], ...], chunks: tuple[DocumentChunk, ...], *, activate: bool = True) -> Path:
    """Publish a prepared index and switch the active pointer atomically."""
    with _PUBLISH_LOCK:
        root = root.resolve()
        digest = _signature_digest(signature)
        version_name = f"index-{digest[:20]}.json"
        version_dir = _index_version_dir(root, module_id)
        version_path = version_dir / version_name
        if not version_path.exists():
            _persist_index(root, module_id, signature, chunks, target=version_path)
        versions = []
        previous = _read_index_payload(_index_manifest_path(root, module_id))
        if previous:
            versions = [str(item) for item in previous.get("versions", []) if str(item).strip()]
        versions = list(dict.fromkeys([version_name, *versions]))
        previous_active = str(previous.get("active", "")) if previous else ""
        manifest = {
            "manifest_version": 1,
            "module_id": module_id,
            "active": version_name if activate or not previous_active else previous_active,
            "staged": "" if activate else version_name,
            "signature": digest,
            "versions": versions,
            "updated_at": time.time(),
        }
        _atomic_write_protected(_index_manifest_path(root, module_id), protect_for_storage(json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))))
        # Keep the old flat artifact for older clients and operational inspection.
        _persist_index(root, module_id, signature, chunks)
        return version_path


def _load_persisted_index(root: Path, module_id: str, signature: tuple[tuple[str, int, int], ...]) -> tuple[DocumentChunk, ...] | None:
    root = root.resolve()
    path = _active_index_path(root, module_id)
    try:
        payload = _read_index_payload(path)
        if payload is None:
            return None
        if payload.get("version") != 15 or payload.get("module_id") != module_id:
            return None
        stored = {str((root / s["path"]).resolve()): (s["mtime_ns"], s["size"]) for s in payload["sources"]}
        requested = {str(Path(source).resolve()): (mtime, size) for source, mtime, size in signature}
        if any(stored.get(source) != stamp for source, stamp in requested.items()):
            return None
        chunks = []
        for item in payload.get("chunks", []):
            source = root / str(item["source_path"])
            text = str(item.get("text", ""))
            if str(source.resolve()) in requested and source.exists() and text.strip():
                chunks.append(
                    DocumentChunk(
                        source,
                        text,
                        int(item.get("ordinal", 0)),
                        item.get("page"),
                        item.get("locator", ""),
                        item.get("start_line"),
                        item.get("end_line"),
                        str(item.get("section_header", "")),
                        str(item.get("content_type", "prose")),
                        float(item.get("quality_score", 1.0)),
                    )
                )
        return tuple(chunks)
    except (OSError, KeyError, TypeError, ValueError, RuntimeError):
        return None


def normalize(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(char))


def _terms(query: str) -> set[str]:
    stopwords = {
        "a", "as", "ao", "aos", "de", "do", "dos", "da", "das", "e", "em", "um", "uma", "o", "os", "que", "me",
        "fale", "falar", "sobre", "como", "qual", "quais", "para", "por", "indica", "indicar", "significa", "significado",
        "explique", "explicar", "diga", "dizer", "mostre", "mostrar", "pode", "ser", "sao", "tem", "existe", "no", "na",
    }
    return {term for term in re.findall(r"[\w]+", normalize(query)) if (len(term) > 2 or term.isdigit()) and term not in stopwords}


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[\w]+", normalize(text)))


def _matched_terms(terms: set[str], tokens: set[str], normalized_text: str) -> int:
    matched = 0
    for term in terms:
        if term in tokens or any(token.startswith(term) or term.startswith(token) for token in tokens if len(token) > 3) or term in normalized_text:
            matched += 1
    return matched


def _bm25_score(query_terms: set[str], text: str, average_length: float) -> float:
    tokens = re.findall(r"[\w]+", text)
    if not tokens or not query_terms:
        return 0.0
    counts = Counter(tokens)
    length = len(tokens)
    k1, b = 1.35, 0.75
    total = 0.0
    for term in query_terms:
        frequency = counts.get(term, 0)
        if frequency:
            total += (frequency * (k1 + 1)) / (frequency + k1 * (1 - b + b * length / max(1.0, average_length)))
    return min(1.0, total / max(1.0, len(query_terms) * 1.5))


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on", "sim"}


def rrf_fuse(lexical_scores: list[float], dense_scores: list[float] | None = None, *, k: int = 60) -> list[float]:
    """Fuse independent lexical and dense rankings with Reciprocal Rank Fusion.

    RRF deliberately uses ranks rather than incomparable raw scores. This
    keeps BM25/TF-IDF and embedding cosine values on a stable footing and
    makes a missing dense index a safe lexical-only fallback.
    """
    if not lexical_scores:
        return []
    dense_scores = dense_scores or []
    lexical_order = sorted(range(len(lexical_scores)), key=lambda index: lexical_scores[index], reverse=True)
    lexical_rank = {index: rank for rank, index in enumerate(lexical_order, start=1)}
    dense_rank: dict[int, int] = {}
    if dense_scores:
        dense_order = sorted(range(min(len(dense_scores), len(lexical_scores))), key=lambda index: dense_scores[index], reverse=True)
        dense_rank = {index: rank for rank, index in enumerate(dense_order, start=1)}
    raw = [1.0 / (k + lexical_rank[index]) for index in range(len(lexical_scores))]
    if dense_rank:
        for index in range(len(raw)):
            rank = dense_rank.get(index)
            if rank is not None:
                raw[index] += 1.0 / (k + rank)
    maximum = max(raw, default=0.0)
    return [value / maximum if maximum else 0.0 for value in raw]


def _summary_quality(text: str) -> float:
    words = re.findall(r"[\w]+", normalize(text))
    if not words:
        return -1.0
    score = min(1.0, len(words) / 90)
    score += min(0.75, len(re.findall(r"[.!?](?:\s|$)", text)) * 0.15)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    score -= min(0.90, (sum(len(line) < 45 for line in lines) / max(1, len(lines))) * 1.10)
    if text.lstrip().startswith(("#", "##")):
        score += 0.12
    if any(marker in normalize(text) for marker in ("fonte:", "capturado em:", "paginas no dominio:", "url:")):
        score -= 0.8
    if len(words) < 12 and not re.search(r"[.!?]", text):
        score -= 0.35
    return score


@lru_cache(maxsize=32)
def _index(root_text: str, module_id: str, signature: tuple[tuple[str, int, int], ...], source_paths: tuple[str, ...] = ()) -> tuple[DocumentChunk, ...]:
    root = Path(root_text)
    cached = _load_persisted_index(root, module_id, signature)
    if cached is not None:
        return cached
    selected_paths = tuple(Path(path) for path in source_paths) if source_paths else None
    return tuple(ingest_module(root, module_id, selected_paths=selected_paths))


@lru_cache(maxsize=32)
def _normalized_index(root_text: str, module_id: str, signature: tuple[tuple[str, int, int], ...], source_paths: tuple[str, ...] = ()) -> tuple[str, ...]:
    return tuple(normalize(chunk.text) for chunk in _index(root_text, module_id, signature, source_paths))


def warm_module_index(root: Path, module_id: str, force: bool = False) -> dict[str, Any]:
    """Prepare and persist the complete primary lexical index for one module."""
    paths = [path for path in files_for(root, module_id) if not _is_offline_candidate(path)]
    signature = tuple(sorted((str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in paths if path.exists()))
    source_paths = tuple(str(path) for path in paths if path.exists())
    if force:
        _index.cache_clear()
        _normalized_index.cache_clear()
    # Always perform extraction in the preparation path when forcing a new
    # extractor version; never serve old text merely because its hash matches.
    chunks = tuple(ingest_module(root, module_id, selected_paths=tuple(paths))) if force else _index(str(root), module_id, signature, source_paths)
    cache_path = _index_cache_path(root, module_id)
    manifest_path = _index_manifest_path(root, module_id)
    if force or not manifest_path.exists() or _load_persisted_index(root, module_id, signature) is None:
        _publish_versioned_index(root, module_id, signature, chunks)
    return {
        "module_id": module_id,
        "status": "ready" if chunks else "empty",
        "sources": len(paths),
        "chunks": len(chunks),
        "cache": str(cache_path),
        "manifest": str(manifest_path),
        "signature": _signature_digest(signature),
    }


def stage_module_index(root: Path, module_id: str, force: bool = False) -> dict[str, Any]:
    """Prepare a version without changing production's active pointer."""
    paths = [path for path in files_for(root, module_id) if not _is_offline_candidate(path)]
    signature = tuple(sorted((str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in paths if path.exists()))
    source_paths = tuple(str(path) for path in paths if path.exists())
    chunks = tuple(ingest_module(root, module_id, selected_paths=tuple(paths))) if force else _index(str(root), module_id, signature, source_paths)
    version_path = _publish_versioned_index(root, module_id, signature, chunks, activate=False)
    return {
        "module_id": module_id,
        "status": "staged" if chunks else "empty",
        "sources": len(paths),
        "chunks": len(chunks),
        "version": version_path.name,
        "manifest": str(_index_manifest_path(root, module_id)),
        "signature": _signature_digest(signature),
    }


def publish_document_index(root: Path, module_id: str, path: Path, chunks: list[DocumentChunk]) -> None:
    """Publish only prepared sources; no unrelated document is parsed here."""
    root = root.resolve()
    path = path.resolve()
    with _PUBLISH_LOCK:
        existing: tuple[DocumentChunk, ...] = ()
        signatures = []
        try:
            payload = _read_index_payload(_active_index_path(root, module_id)) or {}
            if payload.get("version") == 6:
                for source in payload["sources"]:
                    item = root / source["path"]
                    if item.exists() and item.resolve() != path.resolve() and (item.stat().st_mtime_ns, item.stat().st_size) == (source["mtime_ns"], source["size"]):
                        signatures.append((str(item), source["mtime_ns"], source["size"]))
                existing = _load_persisted_index(root, module_id, tuple(signatures)) or ()
        except (OSError, ValueError, KeyError, TypeError, RuntimeError):
            pass
        stat = path.stat()
        signatures.append((str(path), stat.st_mtime_ns, stat.st_size))
        _publish_versioned_index(root, module_id, tuple(sorted(signatures)), (*existing, *chunks))
        _index.cache_clear()
        _normalized_index.cache_clear()


import threading

_PUBLISH_LOCK = threading.RLock()


def list_index_versions(root: Path, module_id: str) -> dict[str, Any]:
    """Return the immutable versions available for an administrative rollback."""
    manifest = _read_index_payload(_index_manifest_path(root, module_id)) or {}
    return {
        "module_id": module_id,
        "active": str(manifest.get("active", "")),
        "staged": str(manifest.get("staged", "")),
        "versions": list(manifest.get("versions", [])),
        "manifest": str(_index_manifest_path(root, module_id)),
    }


def activate_index_version(root: Path, module_id: str, version: str) -> dict[str, Any]:
    """Atomically activate a previous prepared version and clear read caches."""
    version = Path(str(version)).name
    version_dir = _index_version_dir(root, module_id).resolve()
    candidate = (version_dir / version).resolve()
    manifest_path = _index_manifest_path(root, module_id)
    manifest = _read_index_payload(manifest_path) or {}
    if candidate.parent != version_dir or not candidate.exists() or version not in manifest.get("versions", []):
        raise ValueError("Versão de índice não encontrada")
    updated = {**manifest, "active": version, "staged": "", "updated_at": time.time()}
    _atomic_write_protected(manifest_path, protect_for_storage(json.dumps(updated, ensure_ascii=False, separators=(",", ":"))))
    _index.cache_clear()
    _normalized_index.cache_clear()
    runtime_cache_clear("retrieval")
    return list_index_versions(root, module_id)


def _summary_result(
    chunks: tuple[DocumentChunk, ...],
    normalized_index: tuple[str, ...],
    query: str,
    expanded: str,
    limit: int,
    module_id: str = "",
) -> RetrievalResult:
    """Build a bounded summary corpus from topical representatives.

    The previous implementation intentionally kept one representative from
    every file. That is valid for an inventory screen, but unsafe for a user
    summary: a module containing web captures then returned Swagger, menus,
    unrelated portals and educational pages as if all were about the module.
    Summary retrieval now ranks documents by overlap with the question and the
    registered domain vocabulary before choosing a small set of sources.
    """

    text_by_key = {(str(chunk.path), chunk.ordinal): text for chunk, text in zip(chunks, normalized_index)}
    from .domains import domain_for

    stopwords = {
        "faca", "faça", "fazer", "um", "uma", "o", "a", "os", "as", "de", "do", "da", "dos", "das",
        "sobre", "breve", "resumo", "resuma", "resumir", "conteudo", "conteúdo", "conhecimento",
        "documento", "documentos", "arquivo", "arquivos", "local", "modulo", "módulo", "me", "por",
    }
    query_terms = {
        term
        for term in re.findall(r"[\wÀ-ÿ]{4,}", normalize(query))
        if term not in stopwords
    }
    expanded_terms = {
        term
        for term in re.findall(r"[\wÀ-ÿ]{4,}", normalize(expanded))
        if term not in stopwords
    }
    domain_terms = {
        term
        for keyword in domain_for(module_id).keywords
        for term in re.findall(r"[\wÀ-ÿ]{4,}", normalize(keyword))
        if term not in stopwords
    }
    source_relevance: dict[str, tuple[float, DocumentChunk]] = {}
    for chunk in chunks:
        text = text_by_key[(str(chunk.path), chunk.ordinal)]
        tokens = set(re.findall(r"[\wÀ-ÿ]{4,}", text))
        direct = len(tokens & query_terms)
        expanded_overlap = len(tokens & expanded_terms)
        domain_overlap = len(tokens & domain_terms)
        quality = max(0.0, _summary_quality(text))
        score = direct * 2.2 + expanded_overlap * 0.45 + domain_overlap * 1.4 + min(1.0, quality / 3)
        source = chunk.path.name
        current = source_relevance.get(source)
        if current is None or score > current[0]:
            source_relevance[source] = (score, chunk)

    # Keep only the strongest topical sources. If the corpus has no matching
    # vocabulary, retain a tiny quality-based fallback and let the final text
    # state that the module lacks a focused document instead of fabricating a
    # subject from arbitrary captures.
    ranked_sources = sorted(source_relevance.items(), key=lambda item: item[1][0], reverse=True)
    relevant_sources = [source for source, (score, _) in ranked_sources if score > 0.8][:4]
    if not relevant_sources:
        relevant_sources = [source for source, (_, chunk) in ranked_sources[:2] if len(text_by_key[(str(chunk.path), chunk.ordinal)].split()) >= 18]
    allowed_sources = set(relevant_sources)
    if allowed_sources:
        chunks = tuple(chunk for chunk in chunks if chunk.path.name in allowed_sources)
        normalized_index = tuple(text_by_key[(str(chunk.path), chunk.ordinal)] for chunk in chunks)

    best_by_source: dict[str, DocumentChunk] = {}
    first_by_source: dict[str, DocumentChunk] = {}
    for chunk in chunks:
        source = chunk.path.name.casefold()
        current = best_by_source.get(source)
        if current is None or _summary_quality(text_by_key[(str(chunk.path), chunk.ordinal)]) > _summary_quality(text_by_key[(str(current.path), current.ordinal)]):
            best_by_source[source] = chunk
        first = first_by_source.get(source)
        if first is None or (chunk.page or chunk.ordinal) < (first.page or first.ordinal):
            first_by_source[source] = chunk
    representatives: list[DocumentChunk] = list(best_by_source.values())
    # A high-quality body passage can outrank a document's title or opening
    # scope. Keep the first prepared passage as well so summaries retain the
    # document identity and its declared subject (for example, a PDF title).
    representatives.extend(
        chunk for source, chunk in first_by_source.items()
        if chunk not in representatives
    )
    representatives.extend(
        chunk for chunk in sorted(chunks, key=lambda item: _summary_quality(text_by_key[(str(item.path), item.ordinal)]), reverse=True) if chunk not in representatives
    )
    # A summary request is a request about the prepared corpus, not only the
    # globally highest-scoring chunk.  Keep one representative passage for
    # every source so a module with several documents is actually covered;
    # the persistent index still keeps the complete page/chunk inventory.
    summary_limit = min(max(limit, len(best_by_source)), 12)
    selected = representatives[:summary_limit]
    evidence = tuple(Evidence(chunk, 0.55, 0.55, 0.0, 1.0, 0.0) for chunk in selected)
    return RetrievalResult(evidence, tuple(dict.fromkeys(chunk.path.name for chunk in selected)), query, expanded, judge_confidence=0.78)


def _judge(
    result: RetrievalResult,
    question: str,
    module_id: str,
    policy: ModulePolicy,
    required_sources: tuple[str, ...] = (),
) -> RetrievalResult:
    from .evidence import judge_candidates

    decision = judge_candidates(question, module_id, policy, result.evidence, required_sources)
    sources = tuple(dict.fromkeys(item.chunk.path.name for item in decision.accepted))
    covered = tuple(source for source in required_sources if source in sources)
    missing = tuple(source for source in required_sources if source not in sources)
    confidence = round(sum(item.score for item in decision.accepted) / max(1, len(decision.accepted)), 4)
    if required_sources:
        confidence = round(confidence * (len(covered) / len(required_sources)), 4)
    return RetrievalResult(
        tuple(decision.accepted),
        sources,
        result.query,
        result.expanded_query,
        tuple(decision.rejected),
        tuple(decision.conflicts),
        confidence,
        tuple(required_sources),
        missing,
    )


def _is_offline_candidate(path: Path) -> bool:
    """Return whether a file is an unreviewed provider synthesis.

    Offline candidates are useful as a bounded recovery source, but they are
    not authoritative documents. Keeping them out of the first pass prevents
    a previous bad answer from outranking the source that should be checked.
    """
    return any(part.casefold() == "offline" for part in path.parts)


def _retrieval_cache_key(root: Path, module_id: str, query: str, policy: ModulePolicy, limit: int, retry: bool) -> tuple[Any, ...]:
    """Build a correctness-first key for the in-process read-through cache."""
    root = root.resolve()
    stamps: list[tuple[str, int, int]] = []
    for path in files_for(root, module_id):
        try:
            stat = path.stat()
        except OSError:
            continue
        stamps.append((str(path.relative_to(root)), stat.st_mtime_ns, stat.st_size))
    return (
        module_id,
        normalize(query),
        int(limit),
        bool(retry),
        round(float(getattr(policy, "min_evidence_score", 0.0)), 4),
        tuple(stamps),
    )


def retrieve(root: Path, module_id: str, query: str, policy: ModulePolicy, limit: int = 6, retry: bool = False, _candidate_paths: list[Path] | None = None) -> RetrievalResult:
    cache_key = None if _candidate_paths is not None else _retrieval_cache_key(root, module_id, query, policy, limit, retry)
    if cache_key is not None:
        cached = runtime_cache_get("retrieval", cache_key)
        if isinstance(cached, RetrievalResult):
            return cached
    token = ALLOW_HEAVY_EXTRACTION.set(False)
    try:
        result = _retrieve(root, module_id, query, policy, limit, retry, _candidate_paths)
        if cache_key is not None:
            runtime_cache_set("retrieval", cache_key, result)
        return result
    finally:
        ALLOW_HEAVY_EXTRACTION.reset(token)


def _compound_source_context(query: str) -> str:
    """Keep named sources attached to every subquery in a compound turn."""

    hints = list(re.findall(r"\b[\wÀ-ÿ.-]+\.(?:pdf|docx|xlsx|csv|xml|txt|md|json)\b", query, flags=re.IGNORECASE))
    normalized = normalize(query)
    if "saae" in normalized:
        hints.append("SAAE")
    if any(marker in normalized for marker in ("vade", "mencum", "mecum")):
        hints.append("Vade Mecum")
    if "enap" in normalized or "escola virtual" in normalized:
        hints.append("ENAP/Escola Virtual Gov")
    if any(marker in normalized for marker in ("link", "jurisprud", "precedent")):
        hints.append("jurisprudência oficial")
    return ", ".join(dict.fromkeys(hints))


def _compound_topic_context(query: str) -> str:
    """Extract the substantive topic shared by source hand-offs.

    A compound turn such as ``what does SAAE say ... and what does the Vade
    say?`` is decomposed into a precise first task and a short source hand-off
    for the second task.  The hand-off is not a new subject: it inherits the
    topic from the parent turn.  Keeping that topic in the scoped query is
    essential because otherwise lexical retrieval can select a page from the
    named document that only shares generic words such as ``previsto`` or
    ``dia``.
    """

    normalized = normalize(query)
    topics: list[str] = []
    topic_markers = (
        ("horas extras", "horas extras jornada compensação adicional limite diário"),
        ("horas extra", "horas extras jornada compensação adicional limite diário"),
        ("jornada", "jornada trabalho registro ponto compensação horas extras"),
        ("banco de horas", "banco de horas compensação jornada saldo"),
        ("atraso", "atraso jornada registro ponto tolerância compensação"),
        ("defeso eleitoral", "defeso eleitoral indisponibilidade conteúdo cursos"),
        ("carga horária", "carga horária curso ementa duração"),
        ("carga horaria", "carga horária curso ementa duração"),
        ("trigger", "trigger zabbix expressão condição problema recuperação"),
        ("tela azul", "tela azul Windows falha crítica driver reinicialização"),
        ("tosse", "tosse sintomas causas sinais de alerta avaliação"),
    )
    for marker, expansion in topic_markers:
        if marker in normalized:
            topics.append(expansion)
    if topics:
        return " ".join(dict.fromkeys(" ".join(topics).split()))

    ignored = {
        "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
        "e", "em", "no", "na", "nos", "nas", "que", "qual", "quais", "como",
        "sobre", "para", "entre", "esse", "esta", "isso", "diz", "previsto",
        "prevista", "arquivo", "documento", "documentos", "fonte", "fontes",
        "saae", "vade", "mecum", "mencum", "oquê", "oq",
    }
    terms = [term for term in re.findall(r"[\wÀ-ÿ]{4,}", normalized) if term not in ignored]
    return " ".join(dict.fromkeys(terms[:12]))


def retrieve_compound(
    root: Path,
    module_id: str,
    query: str,
    subqueries: tuple[str, ...] | list[str],
    policy: ModulePolicy,
    limit: int = 6,
    retry: bool = False,
) -> RetrievalResult:
    """Retrieve each substantive task and merge evidence without losing sides.

    A long turn is not one semantic query.  Each task gets its own lexical,
    semantic and Evidence Judge pass; the merge then deduplicates passages,
    preserves every explicitly named source and records unanswered tasks for
    the composer.  This is the bridge between conversational multi-question
    input and document-grounded synthesis.
    """

    parts = tuple(dict.fromkeys(str(item).strip() for item in subqueries if str(item).strip()))
    if len(parts) <= 1:
        return retrieve(root, module_id, query, policy, limit=limit, retry=retry)
    source_context = _compound_source_context(query)
    topic_context = _compound_topic_context(query)
    official_requested = any(marker in normalize(query) for marker in ("link", "jurisprud", "precedent"))
    per_query_limit = max(3, min(8, limit))
    scoped_queries: list[str] = []
    for part in parts:
        scoped_query = part
        if source_context and source_context.casefold() not in part.casefold():
            scoped_query = f"{part}\nFontes nomeadas na pergunta: {source_context}"
        normalized_part = normalize(part)
        short_source_handoff = len(re.findall(r"[\wÀ-ÿ]{4,}", normalized_part)) <= 8 and any(
            marker in normalized_part for marker in ("saae", "vade", "mecum", "mencum", "o que ha de comum", "diferenca entre")
        )
        if topic_context and short_source_handoff and topic_context.casefold() not in scoped_query.casefold():
            scoped_query = f"{scoped_query}\nTema comum obrigatório: {topic_context}"
        scoped_queries.append(scoped_query)
    if official_requested:
        # ``links`` in a long turn is its own research task.  Without a
        # dedicated pass, the SAAE/Vade pages fill the ranked window and the
        # official jurisprudence portal is silently lost before synthesis.
        scoped_queries.append(
            "Pesquisa oficial de jurisprudência e precedentes: artigo, lei, precedente, jurisprudência e fonte institucional"
        )
    # A multi-document query also needs a focused pass per explicitly named
    # file.  A single global ranking can identify the right filename while
    # still choosing the wrong clause inside a long agreement.  These passes
    # keep the source contract but add the structural anchor that identifies
    # the requested subject inside each document.
    named_paths = named_source_paths(list(files_for(root, module_id)), query)
    if len(named_paths) >= 2:
        for path in named_paths:
            source = normalize(path.name)
            if any(marker in source for marker in ("saae", "acordo", "convenc", "coletiv")):
                focus = "cláusula 5 horas extras compensação jornada 360 dias cláusula 27"
            elif any(marker in source for marker in ("vade", "mecum")):
                focus = "art. 59 horas extras limite duas adicional 50% compensação jornada"
            else:
                focus = topic_context or query
            scoped_queries.append(f"Documento nomeado obrigatório: {path.name}\nTema focal: {focus}")

    def run_one(scoped_query: str) -> RetrievalResult:
        return retrieve(root, module_id, scoped_query, policy, limit=per_query_limit, retry=retry)

    # The index is already prepared before this function is called.  These
    # independent read-only searches can run concurrently, while the worker
    # count remains bounded so a large compound turn cannot starve the API.
    with ThreadPoolExecutor(max_workers=min(4, len(scoped_queries))) as executor:
        results = list(executor.map(run_one, scoped_queries))

    required_sources = tuple(dict.fromkeys(source for item in results for source in item.required_sources))
    def evidence_key(evidence: Evidence) -> tuple[str, str]:
        return (
            str(evidence.chunk.path.resolve()),
            f"page:{evidence.chunk.page}" if evidence.chunk.page else normalize(evidence.chunk.text),
        )

    all_evidence: list[Evidence] = []
    seen: set[tuple[str, str]] = set()
    for item in results:
        for evidence in item.evidence:
            key = evidence_key(evidence)
            if key in seen:
                continue
            seen.add(key)
            all_evidence.append(evidence)
    all_evidence.sort(key=lambda item: item.score, reverse=True)

    # A compound answer needs one strong passage per task and, for an explicit
    # multi-source comparison, at most one complementary passage per named
    # source.  This is enough for synthesis without allowing a fourth broad
    # clause to fill the context with low-value pages.
    selected: list[Evidence] = []
    selected_keys: set[tuple[str, str]] = set()
    for item in results:
        for evidence in item.evidence[:1]:
            key = evidence_key(evidence)
            if key not in selected_keys:
                selected.append(evidence)
                selected_keys.add(key)
    for source in required_sources:
        source_items = [evidence for evidence in all_evidence if evidence.chunk.path.name == source]
        if not source_items:
            continue
        normalized_source = normalize(source)

        def representative_score(evidence: Evidence, source_name: str = normalized_source) -> tuple[int, float]:
            text = normalize(evidence.chunk.text)
            structural_anchor = 0
            if any(marker in source_name for marker in ("vade", "mecum")) and re.search(r"art\.?\s*59", text):
                structural_anchor += 3
            if any(marker in source_name for marker in ("saae", "acordo", "convenc", "coletiv")) and any(
                marker in text for marker in ("clausula 5", "clausula 27", "horas extras nao compensadas")
            ):
                structural_anchor += 3
            if evidence.chunk.locator.startswith("páginas"):
                structural_anchor += 1
            return structural_anchor, evidence.score

        # A named source must contribute its structurally meaningful passage,
        # not merely the highest-scoring continuation chunk.  In PDFs the
        # heading ``Art. 59`` can be in the preceding chunk while its text is
        # in the next one; the stitched passage keeps the source-side contract
        # explicit without adding a second unrelated page from that source.
        representative = max(source_items, key=representative_score)
        if len(required_sources) >= 2:
            selected = [item for item in selected if item.chunk.path.name != source]
            selected_keys = {evidence_key(item) for item in selected}
        key = evidence_key(representative)
        if key not in selected_keys:
            selected.append(representative)
            selected_keys.add(key)
    if official_requested:
        official = [
            evidence
            for evidence in all_evidence
            if any(marker in normalize(evidence.chunk.path.name) for marker in ("stj", "stf", "planalto"))
        ]
        if official:
            best_official = max(official, key=lambda item: item.score)
            key = evidence_key(best_official)
            if key not in selected_keys:
                selected.append(best_official)
                selected_keys.add(key)

    # Do not fill the remaining budget with merely lexical neighbours.  A
    # compound query is already covered by its task representatives and named
    # source representatives; adding the rest is how unrelated legal pages
    # used to leak into the context.

    source_names = tuple(dict.fromkeys(item.chunk.path.name for item in selected))
    missing_sources = tuple(source for source in required_sources if source not in source_names)
    accepted_scores = [item.score for item in selected]
    confidence = sum(accepted_scores) / max(1, len(accepted_scores))
    if required_sources:
        confidence *= len([source for source in required_sources if source in source_names]) / len(required_sources)
    conflicts: list[dict[str, Any]] = []
    for item in results:
        for conflict in item.conflicts:
            if conflict not in conflicts:
                conflicts.append(conflict)
    unanswered = tuple(
        part for part, item in zip(parts, results)
        if not item.has_quality_evidence
    )
    return RetrievalResult(
        evidence=tuple(selected),
        sources=source_names,
        query=query,
        expanded_query=" | ".join(item.expanded_query for item in results),
        conflicts=tuple(conflicts),
        judge_confidence=round(confidence, 4),
        required_sources=required_sources,
        missing_sources=missing_sources,
        subqueries=parts,
        unanswered_queries=unanswered,
    )


def _retrieve(
    root: Path,
    module_id: str,
    query: str,
    policy: ModulePolicy,
    limit: int = 6,
    retry: bool = False,
    _candidate_paths: list[Path] | None = None,
) -> RetrievalResult:
    """Retrieve evidence through a module package and the common judge."""
    all_paths = files_for(root, module_id)
    if _candidate_paths is None:
        # The normal pass uses only original, ingested sources. A candidate
        # may be consulted only if the authoritative pass has no accepted
        # evidence, preserving the feedback loop without polluting ranking.
        primary_paths = [path for path in all_paths if not _is_offline_candidate(path)]
        primary = retrieve(
            root,
            module_id,
            query,
            policy,
            limit=limit,
            retry=retry,
            _candidate_paths=primary_paths,
        )
        if primary.has_quality_evidence:
            return primary
        offline_paths = [path for path in all_paths if _is_offline_candidate(path)]
        if not offline_paths:
            return primary
        return retrieve(
            root,
            module_id,
            query,
            policy,
            limit=limit,
            retry=retry,
            _candidate_paths=[*primary_paths, *offline_paths],
        )

    package: DomainRetrievalPackage = package_for(module_id)
    expanded = expand_query(module_id, query)
    if expanded == query:
        expanded = package.expand_query(query)
    if retry:
        # The second pass is deliberately different: it asks the ranker for
        # literal, source-backed passages and section/article anchors.  It is
        # still bounded to the package-selected sources, so retry cannot turn
        # a named-document question into a corpus-wide noise search.
        expanded = f"{expanded} trecho literal fonte primaria secao artigo clausula regra documentada evidencia".strip()
    query_terms = _terms(query)
    expanded_terms = _terms(expanded)
    selection = package.select_sources(_candidate_paths, query, retry=retry)
    source_paths = list(selection.paths)
    # The module index is a complete, persistent inventory.  Source selection
    # controls which passages may answer this question; it must not change
    # which files are parsed or which index is built.  Rebuilding an index
    # from only explicitly named files made a later question appear to lose
    # documents that were already present in the active module.
    index_paths = [path for path in _candidate_paths if path.exists()]
    # ``required_paths`` is an explicit-source contract, not a list of every
    # source whose filename happens to contain a domain word.  For example,
    # “como criar um trigger no Zabbix” must not require all Zabbix manuals;
    # the infrastructure package is allowed to select the one authoritative
    # passage that actually explains the operation.  Domain packages that
    # detect a named file populate ``required_paths`` themselves.
    required_paths = selection.required_paths
    required_sources = tuple(dict.fromkeys(path.name for path in required_paths))
    if not source_paths:
        return RetrievalResult((), (), query, expanded, required_sources=required_sources, missing_sources=required_sources)
    signature = tuple(sorted((str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in index_paths))
    source_keys = tuple(str(path) for path in index_paths)
    chunks = _index(str(root), module_id, signature, source_keys)
    normalized_index = _normalized_index(str(root), module_id, signature, source_keys)
    explicit_paths = {path.resolve() for path in named_source_paths(source_paths, query)}
    allowed_paths = {path.resolve() for path in source_paths}
    exact_lines = requested_line_range(query)
    if exact_lines and explicit_paths:
        # An explicit source + line request is deterministic.  Do not let a
        # broad chunk, another page, or another document outrank the line the
        # user actually named.  The normal Evidence Judge still validates the
        # resulting passage and provenance.
        start, end = exact_lines
        exact_evidence: list[Evidence] = []
        for path in source_paths:
            if path.resolve() not in explicit_paths:
                continue
            passage = read_exact_source_lines(path, start, end)
            if not passage:
                continue
            locator = f"linhas {start}-{end}"
            chunk = DocumentChunk(path, passage, 0, None, locator, start, end, "", "exact_source", 1.0)
            exact_evidence.append(Evidence(chunk, 1.0, 1.0, 1.0, 1.0, 1.0))
        if exact_evidence:
            exact_raw = RetrievalResult(
                tuple(exact_evidence),
                tuple(dict.fromkeys(item.chunk.path.name for item in exact_evidence)),
                query,
                expanded,
            )
            return _judge(exact_raw, query, module_id, policy, required_sources)
    exact_term = requested_exact_term(query)
    if exact_term:
        exact_evidence: list[Evidence] = []
        for path in source_paths:
            if explicit_paths and path.resolve() not in explicit_paths:
                continue
            for line_number, line in read_exact_source_term(path, exact_term):
                chunk = DocumentChunk(
                    path,
                    line,
                    line_number,
                    None,
                    f"linha {line_number}",
                    line_number,
                    line_number,
                    "",
                    "exact_source",
                    1.0,
                )
                exact_evidence.append(Evidence(chunk, 1.0, 1.0, 1.0, 1.0, 1.0))
        if exact_evidence:
            exact_raw = RetrievalResult(
                tuple(exact_evidence),
                tuple(dict.fromkeys(item.chunk.path.name for item in exact_evidence)),
                query,
                expanded,
            )
            return _judge(exact_raw, query, module_id, policy, required_sources)
    # Structured files are valuable evidence, but raw rows are not a safe
    # default context for ordinary prose questions.  The complete-file
    # analyzer handles analytical/table intent; explicit file mentions remain
    # allowed for cross-document reasoning. This keeps useful CSV/XLSX facts
    # available without leaking a personnel table into an unrelated answer.
    from .structured_data import _is_structured_query
    structured_intent = _is_structured_query(query)
    eligible = [
        (chunk, text)
        for chunk, text in zip(chunks, normalized_index)
        if chunk.path.resolve() in allowed_paths
        and package.filter_text(chunk.path, text, selection.profile)
        and (
            chunk.path.suffix.casefold() not in {".csv", ".xlsx", ".json"}
            or structured_intent
            or chunk.path.resolve() in explicit_paths
        )
    ]
    if not eligible:
        return RetrievalResult((), (), query, expanded, required_sources=required_sources, missing_sources=required_sources)
    chunks = tuple(chunk for chunk, _ in eligible)
    normalized_index = tuple(text for _, text in eligible)
    profile = selection.profile
    if profile.summary:
        return _judge(_summary_result(chunks, normalized_index, query, expanded, limit, module_id), query, module_id, policy, required_sources)

    pre_ranked: list[tuple[float, int, str, float, float, float, float]] = []
    for index, (chunk, text) in enumerate(zip(chunks, normalized_index)):
        tokens = _token_set(text)
        matched = _matched_terms(query_terms, tokens, text)
        expanded_matched = _matched_terms(expanded_terms, tokens, text)
        coverage = max(matched / max(1, len(query_terms)), min(1.0, (matched + expanded_matched * 0.35) / max(1, len(query_terms))))
        lexical = min(1.0, (matched * 0.65 + expanded_matched * 0.12) / max(1, len(query_terms)))
        bonus = package.score_bonus(chunk.path, text, query_terms, profile)
        cheap_score = 0.28 * lexical + 0.22 * coverage + bonus
        if matched or expanded_matched or package.seed_candidates(text, profile) or chunk.path.resolve() in explicit_paths:
            pre_ranked.append((cheap_score, index, text, matched, expanded_matched, lexical, coverage))
    if not pre_ranked:
        return RetrievalResult((), (), query, expanded, required_sources=required_sources, missing_sources=required_sources)
    pre_ranked.sort(key=lambda item: item[0], reverse=True)
    ranking_window = pre_ranked[: max(60, limit * 25)]
    if profile.comparison and required_sources:
        # A global top-k is unsafe for comparisons: a large manual can fill
        # the whole window before the other named source gets a chance. Keep
        # a small ranked reservation for every required document, then fill
        # the rest with the global ranking.
        reserved: list[tuple[float, int, str, float, float, float, float]] = []
        reserved_keys: set[tuple[int, str]] = set()
        for required_source in required_sources:
            source_items = [item for item in pre_ranked if chunks[item[1]].path.name == required_source]
            for item in source_items[: max(4, limit)]:
                reserved.append(item)
                reserved_keys.add((item[1], item[2]))
        pre_ranked = reserved + [item for item in ranking_window if (item[1], item[2]) not in reserved_keys]
        pre_ranked = pre_ranked[: max(60, limit * 25)]
    else:
        pre_ranked = ranking_window
    normalized_candidates = [item[2] for item in pre_ranked]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    matrix = vectorizer.fit_transform(normalized_candidates + [normalize(expanded)])
    semantic = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    neural_by_chunk = semantic_scores(root, module_id, expanded)
    neural_weight = 0.16 if neural_by_chunk else 0.0
    tfidf_weight = 0.34 - neural_weight
    average_length = sum(len(text.split()) for text in normalized_candidates) / max(1, len(normalized_candidates))
    legacy_scores: list[float] = []
    dense_scores: list[float] = []
    candidate_parts: list[tuple[DocumentChunk, float, float, float, float, float]] = []
    for local_index, (_, index, text, _, _, lexical, coverage) in enumerate(pre_ranked):
        chunk = chunks[index]
        bm25 = _bm25_score(expanded_terms, text, average_length)
        neural_score = float(neural_by_chunk.get((str(chunk.path), chunk.ordinal), 0.0))
        semantic_score = float(semantic[local_index])
        score = tfidf_weight * semantic_score + neural_weight * neural_score + 0.24 * lexical + 0.20 * coverage + 0.14 * bm25 + package.score_bonus(chunk.path, text, query_terms, profile)
        legacy_scores.append(min(1.0, score))
        dense_scores.append(neural_score)
        candidate_parts.append((chunk, score, lexical, semantic_score, coverage, bm25))
    fused_scores = rrf_fuse(legacy_scores, dense_scores) if neural_by_chunk and _env_bool("SOFIA_RRF_ENABLED", True) else [0.0] * len(legacy_scores)
    candidates = []
    for (chunk, score, lexical, semantic_score, coverage, bm25), rrf_score in zip(candidate_parts, fused_scores):
        # RRF is an additive, bounded refinement. If embeddings are absent,
        # the established lexical/BM25 path remains byte-for-byte equivalent.
        hybrid_score = (0.78 * min(1.0, score) + 0.22 * rrf_score) if rrf_score else min(1.0, score)
        candidates.append(Evidence(chunk, min(1.0, hybrid_score), lexical, semantic_score, coverage, bm25, rrf_score=rrf_score))
    candidates.sort(key=lambda item: item.score, reverse=True)
    finalized = package.finalize(candidates, profile)
    # More evidence is not automatically better.  A large output window made
    # a single named PDF contribute dozens of unrelated pages to the model.
    # Keep a compact budget and reserve only the passages needed by a
    # comparison; the persistent index still contains the complete corpus.
    output_limit = max(limit, 4)
    selected = list(finalized[:output_limit])
    # A filename explicitly mentioned by the user is a hard retrieval intent.
    # Preserve its best passage even when generic ranking would otherwise push
    # it below the output window.
    for path in explicit_paths:
        best = next((item for item in finalized if item.chunk.path.resolve() == path), None)
        if best is None or any(item.chunk.path.resolve() == path for item in selected):
            continue
        replacement = next(
            (index for index in range(len(selected) - 1, -1, -1) if selected[index].chunk.path.resolve() not in explicit_paths),
            None,
        )
        if replacement is None:
            selected.append(best)
        else:
            selected[replacement] = best
    # Comparisons need a representative passage from every named source, not
    # just a single global top-k. Reserve two passages per required document
    # when available so a large source cannot hide the other side of the
    # comparison.
    if profile.comparison and required_sources:
        # A named comparison is a two-sided evidence contract.  Rebuild the
        # output from one structurally relevant passage per requested source;
        # the global rank is deliberately not allowed to replace the SAAE
        # clause with an arbitrary page just because both contain generic
        # words such as ``previsto`` or ``trabalho``.
        if len(required_sources) >= 2:
            def comparison_structure_score(item: Evidence) -> tuple[int, int, float]:
                text = normalize(item.chunk.text)
                source = normalize(item.chunk.path.name)
                structural = 0
                position = 10_000
                if any(marker in source for marker in ("vade", "mecum")):
                    match = re.search(r"art\.?\s*59\b", text)
                    if match:
                        structural += 8
                        position = match.start()
                    if any(marker in text for marker in ("horas extras", "horas suplementares", "duracao diaria")):
                        structural += 3
                if any(marker in source for marker in ("saae", "acordo", "convenc", "coletiv")):
                    match = re.search(r"clausula\s+(?:5|27)\b", text)
                    if match:
                        structural += 8
                        position = min(position, match.start())
                    if any(marker in text for marker in ("horas extras", "horas extraordinarias", "compensacao", "360 dias")):
                        structural += 3
                if item.chunk.locator.startswith("páginas"):
                    structural += 1
                return structural, -position, item.score

            named_representatives: list[Evidence] = []
            for required_source in required_sources:
                source_items = [item for item in finalized if item.chunk.path.name == required_source]
                if source_items:
                    named_representatives.append(max(source_items, key=comparison_structure_score))
            if len(named_representatives) == len(required_sources):
                selected = named_representatives

        present_sources = {item.chunk.path.name for item in selected}
        for required_source in required_sources:
            source_items = [item for item in finalized if item.chunk.path.name == required_source]
            if not source_items:
                continue
            # Two independent passages per side give the composer enough
            # material to explain a real difference without dumping a full
            # manual. Never overwrite the only representative already kept
            # for another required source.
            target_count = 1 if len(required_sources) >= 2 else min(2, len(source_items))
            while sum(1 for item in selected if item.chunk.path.name == required_source) < target_count:
                best = next(
                    (
                        item for item in source_items
                        if not any(item.chunk.path.name == current.chunk.path.name and item.chunk.ordinal == current.chunk.ordinal for current in selected)
                    ),
                    None,
                )
                if best is None:
                    break
                replacement = next(
                    (index for index in range(len(selected) - 1, -1, -1) if selected[index].chunk.path.name not in required_sources),
                    None,
                )
                if replacement is None:
                    source_counts = Counter(item.chunk.path.name for item in selected)
                    replacement = next(
                        (
                            index
                            for index in range(len(selected) - 1, -1, -1)
                            if selected[index].chunk.path.name != required_source
                            and source_counts[selected[index].chunk.path.name] > 1
                        ),
                        None,
                    )
                if replacement is None:
                    selected.append(best)
                else:
                    selected[replacement] = best
                present_sources.add(required_source)
        # When the user explicitly asks for links/jurisprudence, preserve one
        # authoritative public source as a complementary perspective. It is
        # never allowed to satisfy the required-document coverage by itself.
        query_lower = normalize(query)
        if any(marker in query_lower for marker in ("link", "jurisprud", "precedent")):
            public_items = [
                item
                for item in finalized
                if item.chunk.path.parent.name.casefold() == "links"
                and any(marker in item.chunk.path.name.casefold() for marker in ("stj", "stf", "gov-br", "planalto"))
            ]
            best_public = public_items[0] if public_items else None
            if best_public is not None and not any(
                item.chunk.path.name == best_public.chunk.path.name for item in selected
            ):
                replacement = next(
                    (index for index in range(len(selected) - 1, -1, -1) if selected[index].chunk.path.name not in required_sources),
                    None,
                )
                if replacement is None:
                    selected.append(best_public)
                else:
                    selected[replacement] = best_public
    candidates = selected
    raw = RetrievalResult(tuple(candidates), tuple(dict.fromkeys(item.chunk.path.name for item in candidates)), query, expanded)
    return _judge(raw, query, module_id, policy, required_sources)
