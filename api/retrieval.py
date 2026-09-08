"""Hybrid retrieval owned by the SOFIA CORE.

The CORE is intentionally domain-agnostic. Module behaviour is supplied by
``api.domain_packages`` through a small contract; this file only performs
indexing, candidate ranking and the common Evidence Judge boundary.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .domain_packages import DomainRetrievalPackage, package_for
from .domain_packages.base import named_source_paths
from .embeddings import semantic_scores
from .ingestion import DocumentChunk, files_for, ingest_module
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
        # diagnostic context, while the gate reports the source gap.
        return bool(self.evidence) and not self.missing_sources

    @property
    def context(self) -> str:
        return "\n\n--- DOCUMENTO: ".join(
            f"{item.chunk.path.name} · trecho {item.chunk.ordinal}\n{item.chunk.text}"
            for item in self.evidence
        )


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
    del signature
    selected_paths = tuple(Path(path) for path in source_paths) if source_paths else None
    return tuple(ingest_module(Path(root_text), module_id, selected_paths=selected_paths))


@lru_cache(maxsize=32)
def _normalized_index(root_text: str, module_id: str, signature: tuple[tuple[str, int, int], ...], source_paths: tuple[str, ...] = ()) -> tuple[str, ...]:
    return tuple(normalize(chunk.text) for chunk in _index(root_text, module_id, signature, source_paths))


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

    decision = judge_candidates(question, module_id, policy, result.evidence)
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


def retrieve(
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
    named_paths = named_source_paths(_candidate_paths, query)
    required_paths = selection.required_paths or named_paths
    required_sources = tuple(dict.fromkeys(path.name for path in required_paths))
    if not source_paths:
        return RetrievalResult((), (), query, expanded, required_sources=required_sources, missing_sources=required_sources)
    signature = tuple(sorted((str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in source_paths if path.exists()))
    source_keys = tuple(str(path) for path in source_paths if path.exists())
    chunks = _index(str(root), module_id, signature, source_keys)
    normalized_index = _normalized_index(str(root), module_id, signature, source_keys)
    eligible = [(chunk, text) for chunk, text in zip(chunks, normalized_index) if package.filter_text(chunk.path, text, selection.profile)]
    if not eligible:
        return RetrievalResult((), (), query, expanded, required_sources=required_sources, missing_sources=required_sources)
    chunks = tuple(chunk for chunk, _ in eligible)
    normalized_index = tuple(text for _, text in eligible)
    profile = selection.profile
    explicit_paths = {path.resolve() for path in named_source_paths(source_paths, query)}
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
    pre_ranked = pre_ranked[: max(60, limit * 25)]
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
        for required_source in required_sources:
            source_items = [item for item in finalized if item.chunk.path.name == required_source]
            for best in source_items[:2]:
                if any(item.chunk.path.name == required_source and item.chunk.ordinal == best.chunk.ordinal for item in selected):
                    continue
                replacement = next(
                    (index for index in range(len(selected) - 1, -1, -1) if selected[index].chunk.path.name not in required_sources),
                    None,
                )
                if replacement is None:
                    replacement = len(selected) - 1 if selected else None
                if replacement is None:
                    selected.append(best)
                else:
                    selected[replacement] = best
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
