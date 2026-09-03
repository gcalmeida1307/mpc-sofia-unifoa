"""Stable extension contract for module-specific retrieval behaviour."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from ..query_analysis import normalize


@dataclass(frozen=True)
class QueryProfile:
    """Domain interpretation used by retrieval, never by the provider."""

    summary: bool = False
    features: frozenset[str] = frozenset()
    seed_markers: tuple[str, ...] = ()
    required_markers: tuple[str, ...] = ()
    summary_markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class SourceSelection:
    paths: tuple[Path, ...]
    profile: QueryProfile


def token_terms(query: str) -> set[str]:
    return {token for token in re.findall(r"[\w]+", normalize(query)) if len(token) > 2}


def named_source_paths(paths: Iterable[Path], query: str) -> tuple[Path, ...]:
    """Resolve filenames mentioned by the user, regardless of separators."""

    ignored = {
        "arquivo", "arquivos", "documento", "documentos", "fonte", "fontes",
        "base", "bases", "dados", "texto", "textos", "imagem", "imagens",
        "link", "links", "pdf", "docx", "xlsx", "csv", "json", "pt",
        "documentation", "documentacao", "senado", "federal",
    }
    normalized_query = normalize(query).replace("_", " ").replace("-", " ")
    query_tokens = set(re.findall(r"[\w]+", normalized_query))
    ranked: list[tuple[int, Path]] = []
    for path in paths:
        source_tokens = {
            token
            for token in re.findall(r"[\w]+", normalize(path.stem).replace("_", " ").replace("-", " "))
            if len(token) >= 3 and not token.isdigit() and token not in ignored
        }
        overlap = source_tokens & query_tokens
        if not overlap:
            continue
        label = " ".join(re.split(r"[_-]+", normalize(path.stem))).strip()
        score = len(overlap) + (3 if label and label in normalized_query else 0)
        ranked.append((score, path))
    if not ranked:
        return ()
    if len(ranked) > 1:
        return tuple(path for _, path in ranked)
    best = max(score for score, _ in ranked)
    return tuple(path for score, path in ranked if score == best)


class DomainRetrievalPackage:
    """Default package; domain packages override only what they need."""

    id = "default"

    def expand_query(self, query: str) -> str:
        return query

    def select_sources(self, paths: list[Path], query: str, retry: bool = False) -> SourceSelection:
        selected = named_source_paths(paths, query)
        profile = self.profile(query)
        if selected:
            if retry:
                selected = tuple(dict.fromkeys([*selected, *(path for path in paths if path.parent.name.casefold() in {"links", "research", "offline"})]))
            return SourceSelection(selected, profile)
        return SourceSelection(tuple(paths), profile)

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        summary_markers = (
            "resuma", "faca um resumo", "um resumo do conteudo", "resumo do conteudo",
            "resumo do conhecimento", "resumo do documento", "resumo do arquivo",
            "resumir o documento", "resumir o arquivo", "documentos disponiveis", "listar documentos",
            "leia o documento", "ler o documento", "leia o arquivo", "ler o arquivo", "ler e responder",
            "leia e responda", "pontos positivos", "pontos negativos", "aspectos positivos",
            "aspectos negativos", "o que aborda",
        )
        return QueryProfile(summary=any(marker in normalized for marker in summary_markers))

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        del path, text, profile
        return True

    def seed_candidates(self, text: str, profile: QueryProfile) -> bool:
        return any(marker in text for marker in profile.seed_markers)

    def score_bonus(self, path: Path, text: str, query_terms: set[str], profile: QueryProfile) -> float:
        del path, text, query_terms, profile
        return 0.0

    def finalize(self, ranked: list, profile: QueryProfile) -> list:
        del profile
        return ranked

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": [], "isolated": True}
