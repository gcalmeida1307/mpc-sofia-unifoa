"""Deterministic admission checks for documents entering a module corpus.

The check is intentionally conservative: it rejects only clear cross-domain
contamination. Unknown or genuinely generic documents are not discarded here;
they still need to pass the normal extraction, quality and validation stages.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AdmissionDecision:
    accepted: bool
    reason: str = ""
    positive_markers: tuple[str, ...] = ()
    negative_markers: tuple[str, ...] = ()


_PROFILES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "infraestrutura": (
        (
            "zabbix", "monitoramento", "rede", "servidor", "windows", "linux",
            "firewall", "dns", "dhcp", "tcp ip", "switch", "roteador", "backup",
            "disponibilidade", "trigger", "host", "agent", "infraestrutura de ti",
            "infraestrutura de tecnologia", "tecnologia da informacao",
            "atendimento a usuarios", "recursos de tecnologia",
        ),
        (
            "influenza", "gripe", "cpf", "ciot", "dnit", "antt",
            "infraestrutura rodoviaria", "regularizacao fundiaria", "reurb",
            "ministerio da saude", "gestao documental", "ministerio da gestao",
            "acesso a informacao", "lei de acesso a informacao", "transparencia",
        ),
    ),
    "medicina": (
        (
            "paciente", "sintoma", "diagnostico", "tratamento", "doenca", "clinico",
            "influenza", "gripe", "saude", "medicina", "sinais de alerta",
        ),
        ("zabbix", "trigger", "ciot", "horas extras", "licitacao"),
    ),
    "direito": (
        (
            "lei", "artigo", "norma", "jurisprudencia", "tribunal", "contrato",
            "trabalhista", "jornada", "horas extras", "processo", "direito",
        ),
        ("zabbix", "trigger", "influenza", "riskusers"),
    ),
}


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def assess_module_document(module_id: str, path: Path, text: str) -> AdmissionDecision:
    """Reject only unmistakable cross-domain contamination before publication."""

    profile = _PROFILES.get(module_id.casefold())
    if profile is None:
        return AdmissionDecision(True)
    positive, negative = profile
    haystack = _normalize(f"{path.stem} {text[:160000]}")
    headline_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    headline = _normalize(headline_match.group(1) if headline_match else text[:800])
    def present(marker: str) -> bool:
        normalized_marker = re.escape(_normalize(marker)).replace(r"\ ", r"\s+")
        return re.search(rf"(?<![a-z0-9]){normalized_marker}(?![a-z0-9])", haystack) is not None

    positive_hits = tuple(marker for marker in positive if present(marker))
    negative_hits = tuple(marker for marker in negative if present(marker))
    positive_weight = sum(haystack.count(_normalize(marker)) for marker in positive)
    negative_weight = sum(haystack.count(_normalize(marker)) for marker in negative)
    if module_id.casefold() == "infraestrutura" and "gestao documental" in headline and not any(
        marker in headline for marker in ("zabbix", "tecnologia", "rede", "servidor")
    ):
        return AdmissionDecision(
            False,
            "título do documento indica gestão documental, não infraestrutura de TI",
            positive_hits,
            negative_hits,
        )
    if len(negative_hits) >= 2 and (
        not positive_hits or negative_weight >= max(4, positive_weight * 2)
    ):
        return AdmissionDecision(
            False,
            f"conteúdo incompatível com o módulo {module_id}: " + ", ".join(negative_hits[:5]),
            positive_hits,
            negative_hits,
        )
    return AdmissionDecision(True, positive_markers=positive_hits, negative_markers=negative_hits)
