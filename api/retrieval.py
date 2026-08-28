from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .ingestion import DocumentChunk, ingest_module
from .policies import ModulePolicy, expand_query


@dataclass(frozen=True)
class Evidence:
    chunk: DocumentChunk
    score: float
    lexical_score: float
    semantic_score: float
    coverage: float


@dataclass(frozen=True)
class RetrievalResult:
    evidence: tuple[Evidence, ...]
    sources: tuple[str, ...]
    query: str
    expanded_query: str

    @property
    def has_quality_evidence(self) -> bool:
        return bool(self.evidence)

    @property
    def context(self) -> str:
        return "\n\n--- DOCUMENTO: ".join(f"{item.chunk.path.name}\n{item.chunk.text}" for item in self.evidence)


def normalize(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(char))


def _terms(query: str) -> set[str]:
    stopwords = {"a", "as", "ao", "aos", "de", "do", "dos", "da", "das", "e", "em", "um", "uma", "o", "os", "que", "me", "fale", "sobre", "como", "qual", "quais", "para", "por"}
    return {term for term in re.findall(r"[\w]+", normalize(query)) if len(term) > 2 and term not in stopwords}


@lru_cache(maxsize=32)
def _index(root_text: str, module_id: str, signature: tuple[tuple[str, int], ...]) -> tuple[DocumentChunk, ...]:
    del signature
    return tuple(ingest_module(Path(root_text), module_id))


def retrieve(root: Path, module_id: str, query: str, policy: ModulePolicy, limit: int = 6) -> RetrievalResult:
    paths = [path for path in (root / module_id).rglob("*") if path.is_file()]
    signature = tuple(sorted((str(path), path.stat().st_mtime_ns) for path in paths))
    chunks = _index(str(root), module_id, signature)
    if not chunks:
        return RetrievalResult((), (), query, query)
    expanded = expand_query(module_id, query)
    normalized_chunks = [normalize(chunk.text) for chunk in chunks]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    matrix = vectorizer.fit_transform(normalized_chunks + [normalize(expanded)])
    semantic = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    query_terms = _terms(query)
    expanded_terms = _terms(expanded)
    candidates: list[Evidence] = []
    for index, chunk in enumerate(chunks):
        text = normalized_chunks[index]
        matched = sum(term in text for term in query_terms)
        expanded_matched = sum(term in text for term in expanded_terms)
        coverage = matched / max(1, len(query_terms))
        lexical = min(1.0, (matched * 0.7 + expanded_matched * 0.1) / max(1, len(query_terms)))
        # O reranker privilegia cobertura e frase exata, sem deixar similaridade
        # genérica de TF-IDF passar sozinha pelo gate.
        exact_phrase = 0.25 if normalize(query) in text else 0.0
        score = 0.5 * float(semantic[index]) + 0.3 * lexical + 0.2 * coverage + exact_phrase
        candidates.append(Evidence(chunk, score, lexical, float(semantic[index]), coverage))
    ranked = sorted(candidates, key=lambda item: item.score, reverse=True)
    selected = tuple(item for item in ranked if item.score >= policy.min_evidence_score and (item.coverage > 0 or item.semantic_score >= 0.22))[:limit]
    sources = tuple(dict.fromkeys(item.chunk.path.name for item in selected))
    return RetrievalResult(selected, sources, query, expanded)
