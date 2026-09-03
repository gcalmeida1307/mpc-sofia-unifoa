"""Retrieval policy for Zabbix and infrastructure documentation."""

from __future__ import annotations

from pathlib import Path

from ..query_analysis import normalize
from .base import (
    DomainRetrievalPackage,
    QueryProfile,
    SourceSelection,
    named_source_paths,
)


class InfrastructurePackage(DomainRetrievalPackage):
    id = "infrastructure"

    def expand_query(self, query: str) -> str:
        normalized = normalize(query)
        additions: list[str] = []
        if "host" in normalized:
            additions.append("hosts dispositivo equipamento maquina monitorado")
        if any(term in normalized for term in ("adicionar", "adiciono", "configurar", "criar", "cadastrar")):
            additions.append("adicionar novo criar cadastrar configurar configurando assistente interfaces")
        if "zabbix" in normalized:
            additions.append("monitoramento agent agent2 template interface disponibilidade")
        if any(term in normalized for term in ("rede", "scan", "scanner")):
            additions.append("network descoberta scan varredura snmp interface tcp udp")
        return f"{query} {' '.join(additions)}".strip()

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        features: set[str] = set()
        if "host" in normalized:
            features.add("host")
        if any(term in normalized for term in ("adicionar", "adiciono", "configurar", "criar", "cadastrar")):
            features.add("procedure")
        if "7.4" in normalized:
            features.add("version_7_4")
        return QueryProfile(summary=super().profile(query).summary, features=frozenset(features), seed_markers=("uma entidade no zabbix que representa", "representa seu alvo de monitoramento"))

    def select_sources(self, paths: list[Path], query: str, retry: bool = False) -> SourceSelection:
        profile = self.profile(query)
        selected = named_source_paths(paths, query)
        zabbix = tuple(path for path in paths if "zabbix_documentation" in path.name.casefold())
        if "host" in profile.features and zabbix:
            if "version_7_4" in profile.features:
                versioned = tuple(path for path in zabbix if "7.4" in path.name)
                return SourceSelection(versioned or zabbix, profile)
            preferred = tuple(path for path in zabbix if "7.4" in path.name)
            return SourceSelection(preferred or zabbix, profile)
        if selected:
            return SourceSelection(selected, profile)
        return SourceSelection(tuple(paths), profile)

    def score_bonus(self, path: Path, text: str, query_terms: set[str], profile: QueryProfile) -> float:
        del query_terms
        bonus = 0.0
        if "procedure" in profile.features and any(marker in text for marker in ("configurando um host", "adicionar o host ao zabbix", "novo host")):
            bonus += 0.48
        if "host" in profile.features and "config/hosts/host" in text:
            bonus += 0.30
        if "procedure" in profile.features and "zabbix_documentation" in path.name.casefold():
            bonus += 0.22
        if "version_7_4" in profile.features and "7.4" in path.name:
            bonus += 0.16
        return bonus

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["version-aware", "procedure-aware"], "isolated": True}
