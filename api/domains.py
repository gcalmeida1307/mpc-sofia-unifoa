"""Domain contracts shared by the CORE, retrieval and administrative UI.

The registry is intentionally data-only.  Domain-specific policies live here
instead of being scattered through HTTP routes or the orchestration engine.
Adding a module therefore does not require changing CORE behaviour.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DomainContract:
    id: str
    name: str
    category: str
    color: str
    icon: str
    manager: str
    focus: str
    keywords: tuple[str, ...] = ()
    source_profile: str = "module_document"
    high_risk: bool = False
    allow_general_knowledge: bool = False
    require_citation: bool = True
    minimum_evidence: float = 0.30
    external_requires_consent: bool = True
    skills: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    risk_flags: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)

    def manifest(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_CONTRACT = DomainContract(
    id="unknown",
    name="Domínio",
    category="Domínio",
    color="#818cf8",
    icon="◈",
    manager="Gestor do módulo",
    focus="Conhecimento e procedimentos do domínio.",
)


DOMAIN_CONTRACTS: dict[str, DomainContract] = {
    "almoxarifado": DomainContract(
        "almoxarifado", "Almoxarifado", "Operações", "#818cf8", "▣", "Gestor de estoque",
        "Materiais, inventário, compras e movimentações.",
        ("estoque", "inventário", "compras", "material", "insumo", "fornecedor"),
        skills=("inventory_analysis", "procurement_review"),
        tools=("search_knowledge", "analyst_scenario"),
    ),
    "contabilidade": DomainContract(
        "contabilidade", "Contabilidade", "Finanças", "#f59e0b", "▤", "Gestor contábil",
        "Lançamentos, conformidade, fechamentos e indicadores.",
        ("contabilidade", "balanço", "patrimonial", "lançamento", "fechamento", "CPC", "ECF"),
        skills=("accounting_review", "compliance_check"),
        tools=("search_knowledge", "analyst_scenario"),
    ),
    "departamento-pessoal": DomainContract(
        "departamento-pessoal", "Departamento Pessoal", "Pessoas", "#f472b6", "♙", "Gestor de pessoal",
        "Rotinas trabalhistas, admissões, férias e folha.",
        ("folha", "admissão", "férias", "rescisão", "eSocial", "jornada", "hora extra"),
        source_profile="legal_primary_source",
        skills=("labor_policy_review",),
        tools=("search_knowledge", "analyst_scenario"),
    ),
    "direito": DomainContract(
        "direito", "Direito", "Jurídico", "#a78bfa", "⚖", "Gestor jurídico",
        "Leis, normas, conexões entre dispositivos e riscos.",
        ("lei", "legislação", "jurisprudência", "acordo coletivo", "contrato", "artigo", "empregado", "mandado de segurança", "prazo processual", "CLT"),
        source_profile="legal_primary_source",
        skills=("legal_comparison", "legal_interpretation"),
        tools=("search_knowledge", "analyst_scenario"),
        risk_flags=("revisao_juridica",),
    ),
    "financeiro": DomainContract(
        "financeiro", "Financeiro", "Finanças", "#fbbf24", "▥", "Gestor financeiro",
        "Fluxo de caixa, orçamento, custos e cenários.",
        ("fluxo de caixa", "receita", "despesa", "custo", "orçamento", "contas a pagar", "contas a receber"),
        skills=("cashflow_analysis", "scenario_analysis"),
        tools=("search_knowledge", "analyst_scenario", "monte_carlo_estimate"),
    ),
    "gestao-empresarial": DomainContract(
        "gestao-empresarial", "Gestão Empresarial", "Gestão", "#fb923c", "▤", "Gestor executivo",
        "Processos, metas, riscos e melhoria contínua.",
        ("processo", "metas", "indicadores", "riscos", "governança", "planejamento", "melhoria", "produção", "desvio", "realizado", "perdas", "produtividade"),
        skills=("process_mapping", "continuous_improvement"),
        tools=("search_knowledge", "analyst_scenario"),
    ),
    "infraestrutura": DomainContract(
        "infraestrutura", "Infraestrutura", "Tecnologia", "#22d3ee", "⌂", "Gestor de infraestrutura",
        "Redes, Zabbix, sistemas operacionais, segurança e disponibilidade.",
        ("Zabbix", "host", "rede", "servidor", "Linux", "Windows", "SNMP", "monitoramento"),
        source_profile="technical_documentation",
        skills=("zabbix_operations", "network_diagnostics"),
        tools=("search_knowledge", "analyst_scenario"),
    ),
    "medicina": DomainContract(
        "medicina", "Medicina", "Saúde", "#34d399", "✚", "Gestor clínico",
        "Protocolos, literatura, indicadores populacionais e interoperabilidade FHIR.",
        ("paciente", "sintoma", "gripe", "febre", "tratamento", "exame", "FHIR", "protocolo"),
        source_profile="clinical_guideline",
        high_risk=True,
        external_requires_consent=True,
        skills=("clinical_information", "fhir_review"),
        tools=("search_knowledge", "analyst_scenario", "fhir_patient_context"),
        risk_flags=("avaliacao_profissional", "dados_de_saude"),
    ),
    "prefeitura": DomainContract(
        "prefeitura", "Prefeitura", "Administração Pública", "#60a5fa", "⌂", "Gestor público",
        "Serviços públicos, legislação, contratos e prestação de contas.",
        ("prefeitura", "serviço público", "licitação", "contrato público", "prestação de contas"),
        source_profile="legal_primary_source",
        skills=("public_management", "procurement_review"),
        tools=("search_knowledge", "analyst_scenario"),
    ),
    "recursos-humanos": DomainContract(
        "recursos-humanos", "Recursos Humanos", "Pessoas", "#fb7185", "♟", "Gestor de RH",
        "Pessoas, desenvolvimento, clima, políticas e indicadores.",
        ("recrutamento", "seleção", "clima", "desempenho", "treinamento", "pessoas", "candidato"),
        skills=("people_management", "policy_review"),
        tools=("search_knowledge", "analyst_scenario"),
    ),
    "secretaria": DomainContract(
        "secretaria", "Secretaria", "Administrativo", "#c084fc", "▱", "Gestor administrativo",
        "Documentos, atendimento, agendas e fluxos administrativos.",
        ("agenda", "atendimento", "protocolo", "documento", "ofício", "arquivo"),
        skills=("document_workflow",),
        tools=("search_knowledge", "analyst_scenario"),
    ),
}


def domain_for(module_id: str) -> DomainContract:
    return DOMAIN_CONTRACTS.get(module_id.casefold(), DomainContract(**{**DEFAULT_CONTRACT.manifest(), "id": module_id}))


def manifests(module_ids: list[str] | tuple[str, ...] | None = None) -> list[dict[str, Any]]:
    ids = module_ids or sorted(DOMAIN_CONTRACTS)
    return [domain_for(module_id).manifest() for module_id in ids]

