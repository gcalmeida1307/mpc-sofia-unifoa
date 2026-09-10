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
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .domain_packages import DomainRetrievalPackage, package_for
from .domain_packages.base import named_source_paths, requested_line_range
from .embeddings import semantic_scores
from .ingestion import ALLOW_HEAVY_EXTRACTION, DocumentChunk, files_for, ingest_module, read_exact_source_lines
from .secure_storage import decrypt_text, protect_for_storage
from .policies import ModulePolicy, expand_query


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

    @property
    def has_quality_evidence(self) -> bool:
        # Evidence from only one side of a named comparison is not enough to
        # authorize synthesis.  The accepted chunks remain available for the
        # diagnostic context, while the gate reports the source gap.  A source
        # can be present and still be too weak to authorize an answer; keeping
        # this threshold here prevents the external fallback from treating a
        # low-confidence navigation/menu match as authoritative evidence.
        return bool(self.evidence) and not self.missing_sources and self.judge_confidence >= 0.32

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
                passages.append(f"LOCALIZAÇÃO: {locator}\n{item.chunk.text}")
            blocks.append("\n".join(passages))
        return "\n\n---\n\n".join(blocks)


def _index_cache_path(root: Path, module_id: str) -> Path:
    return root.parent / "data" / "retrieval-index" / f"{module_id}.json"


def _signature_digest(signature: tuple[tuple[str, int, int], ...]) -> str:
    payload = json.dumps(signature, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _persist_index(root: Path, module_id: str, signature: tuple[tuple[str, int, int], ...], chunks: tuple[DocumentChunk, ...]) -> None:
    """Persist the prepared lexical index so cold queries do not parse files."""
    # ``Path.resolve`` also normalizes Windows 8.3 aliases (for example
    # ``GLAUCO~1.ALM``).  Without this, ``relative_to`` can fail even though
    # the source and knowledge root point to the same directory.
    root = root.resolve()
    path = _index_cache_path(root, module_id)
    def relative_path(value: Path) -> str:
        return os.path.relpath(str(value.resolve()), str(root))

    payload = {
        "version": 4,
        "module_id": module_id,
        "signature": _signature_digest(signature),
        "sources": [
            {"path": relative_path(Path(source)), "mtime_ns": mtime_ns, "size": size}
            for source, mtime_ns, size in signature
        ],
        "chunks": [
            {"source_path": relative_path(chunk.path), "ordinal": chunk.ordinal, "text": chunk.text, "page": chunk.page, "locator": chunk.locator}
            for chunk in chunks
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f"{path.stem}-", suffix=".tmp", dir=path.parent)
    os.close(fd)
    Path(temporary_name).write_text(protect_for_storage(json.dumps(payload, ensure_ascii=False, separators=(",", ":"))), encoding="utf-8")
    try:
        Path(temporary_name).replace(path)
    finally:
        Path(temporary_name).unlink(missing_ok=True)


def _load_persisted_index(root: Path, module_id: str, signature: tuple[tuple[str, int, int], ...]) -> tuple[DocumentChunk, ...] | None:
    root = root.resolve()
    path = _index_cache_path(root, module_id)
    try:
        raw = path.read_text(encoding="utf-8")
        try:
            decoded = decrypt_text(raw)
        except RuntimeError:
            # A cache generated with an encryption key must not crash a
            # read-only query when the key is temporarily unavailable.  A
            # legacy plaintext cache remains safe to use; an encrypted cache
            # simply returns None and will be rebuilt by the preparation path.
            decoded = raw if raw.lstrip().startswith("{") else ""
        payload = json.loads(decoded)
        if payload.get("version") != 4 or payload.get("module_id") != module_id:
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
                chunks.append(DocumentChunk(source, text, int(item.get("ordinal", 0)), item.get("page"), item.get("locator", "")))
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
    if force or not cache_path.exists() or _load_persisted_index(root, module_id, signature) is None:
        _persist_index(root, module_id, signature, chunks)
    return {
        "module_id": module_id,
        "status": "ready" if chunks else "empty",
        "sources": len(paths),
        "chunks": len(chunks),
        "cache": str(cache_path),
        "signature": _signature_digest(signature),
    }


def publish_document_index(root: Path, module_id: str, path: Path, chunks: list[DocumentChunk]) -> None:
    """Publish only prepared sources; no unrelated document is parsed here."""
    import threading
    root = root.resolve()
    path = path.resolve()
    with _PUBLISH_LOCK:
        existing: tuple[DocumentChunk, ...] = ()
        signatures = []
        try:
            raw = _index_cache_path(root, module_id).read_text(encoding="utf-8")
            try:
                decoded = decrypt_text(raw)
            except RuntimeError:
                decoded = raw if raw.lstrip().startswith("{") else ""
            payload = json.loads(decoded)
            if payload.get("version") == 4:
                for source in payload["sources"]:
                    item = root / source["path"]
                    if item.exists() and item.resolve() != path.resolve() and (item.stat().st_mtime_ns, item.stat().st_size) == (source["mtime_ns"], source["size"]):
                        signatures.append((str(item), source["mtime_ns"], source["size"]))
                existing = _load_persisted_index(root, module_id, tuple(signatures)) or ()
        except (OSError, ValueError, KeyError, TypeError, RuntimeError):
            pass
        stat = path.stat()
        signatures.append((str(path), stat.st_mtime_ns, stat.st_size))
        _persist_index(root, module_id, tuple(sorted(signatures)), (*existing, *chunks))
        _index.cache_clear()
        _normalized_index.cache_clear()


import threading
_PUBLISH_LOCK = threading.RLock()


def _summary_result(chunks: tuple[DocumentChunk, ...], normalized_index: tuple[str, ...], query: str, expanded: str, limit: int) -> RetrievalResult:
    text_by_key = {(str(chunk.path), chunk.ordinal): text for chunk, text in zip(chunks, normalized_index)}
    best_by_source: dict[str, DocumentChunk] = {}
    for chunk in chunks:
        source = chunk.path.name.casefold()
        current = best_by_source.get(source)
        if current is None or _summary_quality(text_by_key[(str(chunk.path), chunk.ordinal)]) > _summary_quality(text_by_key[(str(current.path), current.ordinal)]):
            best_by_source[source] = chunk
    representatives: list[DocumentChunk] = list(best_by_source.values())
    representatives.extend(
        chunk for chunk in sorted(chunks, key=lambda item: _summary_quality(text_by_key[(str(item.path), item.ordinal)]), reverse=True) if chunk not in representatives
    )
    evidence = tuple(Evidence(chunk, 0.55, 0.55, 0.0, 1.0, 0.0) for chunk in representatives[:limit])
    return RetrievalResult(evidence, tuple(dict.fromkeys(chunk.path.name for chunk in representatives[:limit])), query, expanded, judge_confidence=0.78)


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


def retrieve(root: Path, module_id: str, query: str, policy: ModulePolicy, limit: int = 6, retry: bool = False, _candidate_paths: list[Path] | None = None) -> RetrievalResult:
    token = ALLOW_HEAVY_EXTRACTION.set(False)
    try:
        return _retrieve(root, module_id, query, policy, limit, retry, _candidate_paths)
    finally:
        ALLOW_HEAVY_EXTRACTION.reset(token)


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
    signature = tuple(sorted((str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in source_paths if path.exists()))
    source_keys = tuple(str(path) for path in source_paths if path.exists())
    chunks = _index(str(root), module_id, signature, source_keys)
    normalized_index = _normalized_index(str(root), module_id, signature, source_keys)
    explicit_paths = {path.resolve() for path in named_source_paths(source_paths, query)}
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
            chunk = DocumentChunk(path, passage, 0, None, locator)
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
        if package.filter_text(chunk.path, text, selection.profile)
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
        return _judge(_summary_result(chunks, normalized_index, query, expanded, limit), query, module_id, policy, required_sources)

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
    candidates: list[Evidence] = []
    for local_index, (_, index, text, _, _, lexical, coverage) in enumerate(pre_ranked):
        chunk = chunks[index]
        bm25 = _bm25_score(expanded_terms, text, average_length)
        neural_score = float(neural_by_chunk.get((str(chunk.path), chunk.ordinal), 0.0))
        semantic_score = float(semantic[local_index])
        score = tfidf_weight * semantic_score + neural_weight * neural_score + 0.24 * lexical + 0.20 * coverage + 0.14 * bm25 + package.score_bonus(chunk.path, text, query_terms, profile)
        candidates.append(Evidence(chunk, min(1.0, score), lexical, semantic_score, coverage, bm25))
    candidates.sort(key=lambda item: item.score, reverse=True)
    finalized = package.finalize(candidates, profile)
    output_limit = max(limit * 3, limit)
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
        present_sources = {item.chunk.path.name for item in selected}
        for required_source in required_sources:
            source_items = [item for item in finalized if item.chunk.path.name == required_source]
            if not source_items:
                continue
            # Two independent passages per side give the composer enough
            # material to explain a real difference without dumping a full
            # manual. Never overwrite the only representative already kept
            # for another required source.
            target_count = min(2, len(source_items))
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
