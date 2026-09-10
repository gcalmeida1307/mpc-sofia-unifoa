"""Retrieval policy for Zabbix and infrastructure documentation."""

from __future__ import annotations

from pathlib import Path

from ..ingestion import extract_text
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
        if "trigger" in normalized or "alerta" in normalized:
            additions.append("criar trigger expressão de trigger condição problema evento severidade alerta")
        if any(term in normalized for term in ("rede", "scan", "scanner")):
            additions.append("network descoberta scan varredura snmp interface tcp udp")
        return f"{query} {' '.join(additions)}".strip()

    def profile(self, query: str) -> QueryProfile:
        normalized = normalize(query)
        features: set[str] = set()
        if "host" in normalized:
            features.add("host")
        if "trigger" in normalized or "alerta" in normalized:
            features.add("trigger")
        if any(term in normalized for term in ("adicionar", "adiciono", "configurar", "criar", "cadastrar")):
            features.add("procedure")
        if "7.4" in normalized:
            features.add("version_7_4")
        base = super().profile(query)
        features.update(base.features)
        seed_markers = (
            ("expressao de trigger", "trigger expression", "create trigger", "criar trigger", "problem event")
            if "trigger" in features
            else ("uma entidade no zabbix que representa", "representa seu alvo de monitoramento")
        )
        return QueryProfile(
            summary=base.summary,
            features=frozenset(features),
            seed_markers=seed_markers,
            comparison=base.comparison,
        )

    def select_sources(self, paths: list[Path], query: str, retry: bool = False) -> SourceSelection:
        profile = self.profile(query)
        selected = named_source_paths(paths, query)
        zabbix = tuple(path for path in paths if "zabbix_documentation" in path.name.casefold())
        official_zabbix = tuple(path for path in paths if "www-zabbix-com" in path.name.casefold())
        normalized = normalize(query)
        # Do not parse every version of the Zabbix manual for a normal
        # question. These PDFs are very large and contain overlapping content.
        # An explicitly named source always wins; comparisons and version
        # questions are the cases where loading more than one version is useful.
        compare_versions = any(marker in normalized for marker in ("compar", "versoes", "versao", "diferenca entre"))
        explicit_document = any(
            marker in normalized
            for marker in ("arquivo", "documento", "manual", "pdf", "6.0", "7.0", "7.4", "8.0", "zabbix_documentation")
        )
        if selected and explicit_document and not compare_versions:
            required = tuple(selected)
            for version in ("8.0", "7.4", "7.0", "6.0"):
                if version in normalized:
                    versioned = tuple(path for path in selected if version in path.name)
                    if versioned:
                        return SourceSelection(versioned, profile, required)
            return SourceSelection(selected, profile, required)
        if compare_versions and zabbix:
            # A version comparison names a pair of sources semantically; it
            # must not be interpreted as naming every manual in the corpus.
            # Select only the requested versions and require coverage for
            # those versions, otherwise the judge can reject a valid answer
            # merely because unrelated manuals were not loaded.
            requested_versions = tuple(version for version in ("6.0", "7.0", "7.4", "8.0") if version in normalized)
            versioned = tuple(
                path
                for version in requested_versions
                for path in zabbix
                if version in path.name
            )
            if len(versioned) >= 2:
                return SourceSelection(tuple(dict.fromkeys(versioned)), profile, tuple(dict.fromkeys(versioned)))
            if versioned:
                return SourceSelection(versioned, profile, versioned)
        if "trigger" in profile.features and official_zabbix and not compare_versions:
            trigger_sources = tuple(
                path
                for path in official_zabbix
                if any(marker in normalize(extract_text(path)) for marker in ("create trigger", "to configure a trigger", "criar trigger", "para configurar um trigger"))
            )
            return SourceSelection(trigger_sources[:1] or official_zabbix[:1], profile)
        if zabbix and any(term in normalized for term in ("zabbix", "trigger", "item", "template", "host", "monitoramento")) and not compare_versions:
            if "version_7_4" in profile.features:
                versioned = tuple(path for path in zabbix if "7.4" in path.name)
                return SourceSelection(versioned or zabbix[:1], profile)
            latest = tuple(path for path in zabbix if "8.0" in path.name)
            return SourceSelection(latest or zabbix[:1], profile)
        if "host" in profile.features and zabbix:
            if "version_7_4" in profile.features:
                versioned = tuple(path for path in zabbix if "7.4" in path.name)
                return SourceSelection(versioned or zabbix, profile)
            preferred = tuple(path for path in zabbix if "7.4" in path.name)
            return SourceSelection(preferred or zabbix, profile)
        if selected:
            return SourceSelection(selected, profile, tuple(selected))
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
        if "trigger" in profile.features:
            if any(marker in text for marker in ("expressao de trigger", "trigger expression", "create trigger", "criar trigger", "problem event")):
                bonus += 0.42
            if "www-zabbix-com" in path.name.casefold():
                bonus += 0.18
        if "version_7_4" in profile.features and "7.4" in path.name:
            bonus += 0.16
        return bonus

    def filter_text(self, path: Path, text: str, profile: QueryProfile) -> bool:
        if "trigger" not in profile.features:
            return True
        del path
        # Navigation chrome often repeats the word “trigger” thousands of
        # times without explaining how to configure one. Keep only chunks
        # with an actual trigger section or creation field.
        return any(
            marker in text
            for marker in (
                "para configurar um trigger",
                "to configure a trigger",
                "configurando um trigger no frontend",
                "configuring a trigger in the frontend",
            )
        )

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["version-aware", "procedure-aware"], "isolated": True}
