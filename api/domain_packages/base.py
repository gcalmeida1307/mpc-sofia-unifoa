"""Stable extension contract for module-specific retrieval behaviour."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from difflib import SequenceMatcher
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
    # A comparison is a retrieval contract, not merely a writing style.  The
    # CORE uses this flag to require source coverage before generation.
    comparison: bool = False


@dataclass(frozen=True)
class SourceSelection:
    paths: tuple[Path, ...]
    profile: QueryProfile
    # These are the files the user explicitly named.  Optional recovery
    # sources may be added to ``paths`` on a retry, but they never satisfy the
    # coverage contract by themselves.
    required_paths: tuple[Path, ...] = ()


_SOURCE_STOPWORDS = {
    "a", "as", "ao", "aos", "da", "das", "de", "do", "dos", "e", "em",
    "na", "nas", "no", "nos", "o", "os", "para", "por", "um", "uma",
    "com", "como", "que", "se", "sem", "sobre", "entre", "este", "esta",
    "esse", "essa", "arquivo", "arquivos", "documento", "documentos", "fonte",
    "fontes", "base", "bases", "dados", "texto", "textos", "imagem", "imagens",
    "link", "links", "pdf", "docx", "xlsx", "csv", "json", "xml", "pt",
    "br", "www", "http", "https", "org", "com", "senado", "federal",
    "documentation", "documentacao", "manual", "site", "pagina", "paginas",
}


def comparison_requested(query: str) -> bool:
    """Return whether the user requested a multi-source analysis."""

    normalized = normalize(query)
    return any(
        marker in normalized
        for marker in (
            "compare", "comparar", "comparando", "comparacao", "versus", " vs ",
            "diferenca entre", "confront", "cruzar", "relacionar os documentos",
            "relacionar as fontes", "em conjunto com",
        )
    )


def token_terms(query: str) -> set[str]:
    return {token for token in re.findall(r"[\w]+", normalize(query)) if len(token) > 2}


def requested_line_range(query: str) -> tuple[int, int] | None:
    """Extract an explicit text-line request from a user question.

    A locator is part of the retrieval contract, not a ranking hint.  When a
    user asks for ``linha 62`` the CORE must be able to return that line from
    the named source instead of selecting a large, approximate chunk.
    """

    normalized = normalize(query)
    match = re.search(
        r"\b(?:linha|linhas|line|lines)\s*(\d+)\s*(?:(?:-|a|ate|to)\s*(\d+))?\b",
        normalized,
    )
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2) or start)
    if start < 1 or end < start:
        return None
    return start, end


def named_source_paths(paths: Iterable[Path], query: str) -> tuple[Path, ...]:
    """Resolve explicit filenames without treating common words as sources.

    The previous resolver considered ``com`` a meaningful filename token.  A
    query such as ``compare o arquivo A com o arquivo B`` could therefore
    select every URL-derived file containing ``-com-``.  Source resolution is
    now based on meaningful filename tokens and high-confidence exact/fuzzy
    matches only; generic corpus search remains the fallback when no source
    is named.
    """

    normalized_query = normalize(query).replace("_", " ").replace("-", " ")
    query_tokens = {
        token
        for token in re.findall(r"[\w]+", normalized_query)
        if len(token) >= 3 and token not in _SOURCE_STOPWORDS and not token.isdigit()
    }
    compact_query = re.sub(r"[^a-z0-9]+", "", normalize(query))
    ranked: list[tuple[float, Path]] = []
    for path in paths:
        source_tokens = {
            token
            for token in re.findall(r"[\w]+", normalize(path.stem).replace("_", " ").replace("-", " "))
            if len(token) >= 3 and not token.isdigit() and token not in _SOURCE_STOPWORDS
        }
        overlap = source_tokens & query_tokens
        label = " ".join(re.split(r"[_-]+", normalize(path.stem))).strip()
        compact_label = re.sub(r"[^a-z0-9]+", "", label)
        compact_source_tokens = {
            re.sub(r"[^a-z0-9]+", "", token) for token in source_tokens
        }
        # A user may cite a shortened filename, such as “RiskUsers” for
        # “RiskyUsers.csv”. Compare meaningful filename tokens, never the
        # whole natural-language question.
        token_fuzzy = max(
            (
                SequenceMatcher(None, source_token, query_token).ratio()
                for source_token in compact_source_tokens
                for query_token in query_tokens
                if len(source_token) >= 4 and len(query_token) >= 4
            ),
            default=0.0,
        )
        label_in_query = bool(compact_label and compact_label in compact_query)
        # ``ENAP`` is the institution named in Escola Virtual Gov captures.
        # The URL-derived filename does not contain that acronym, so it needs
        # an explicit, conservative alias instead of a broad semantic match.
        enap_alias = "enap" in query_tokens and "escolavirtual" in compact_label
        escola_virtual_alias = "escola virtual" in normalized_query and "escolavirtual" in compact_label
        if not overlap and not label_in_query and not enap_alias and not escola_virtual_alias and token_fuzzy < 0.82:
            continue
        score = float(len(overlap) * 5)
        if label_in_query:
            score += 12
        if enap_alias or escola_virtual_alias:
            score += 14
        if token_fuzzy >= 0.82:
            score += 4
        # A filename token must be meaningful.  This guard prevents a URL
        # slug from winning merely because it shares a short common token.
        if not overlap and not label_in_query and not enap_alias and not escola_virtual_alias and token_fuzzy < 0.88:
            continue
        ranked.append((score, path))
    if not ranked:
        return ()
    best = max(score for score, _ in ranked)
    # Keep all strong ties (e.g. two explicitly named documents), while
    # dropping weak incidental matches from URL slugs.
    return tuple(path for score, path in ranked if score >= max(4.0, best - 5.0))


class DomainRetrievalPackage:
    """Default package; domain packages override only what they need."""

    id = "default"

    def expand_query(self, query: str) -> str:
        return query

    def select_sources(self, paths: list[Path], query: str, retry: bool = False) -> SourceSelection:
        selected = named_source_paths(paths, query)
        profile = self.profile(query)
        if selected:
            required = selected
            # A comparison retry must stay inside the named source set unless
            # the user explicitly asked for additional links.  Broadening a
            # two-document comparison with the whole module reintroduces the
            # very noise the first pass was supposed to remove.
            if retry and not profile.comparison:
                selected = tuple(dict.fromkeys([*selected, *(path for path in paths if path.parent.name.casefold() in {"links", "research", "offline"})]))
            return SourceSelection(selected, profile, required)
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
        comparison = comparison_requested(normalized)
        return QueryProfile(summary=any(marker in normalized for marker in summary_markers), comparison=comparison, features=frozenset({"comparison"} if comparison else ()))

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
