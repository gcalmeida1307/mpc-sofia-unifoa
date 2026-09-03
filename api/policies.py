from __future__ import annotations

from dataclasses import dataclass

from .domains import DOMAIN_CONTRACTS, domain_for
from .query_analysis import normalize


@dataclass(frozen=True)
class ModulePolicy:
    allow_general_knowledge: bool
    high_risk: bool
    min_evidence_score: float
    require_citation: bool


POLICIES = {
    module_id: ModulePolicy(
        contract.allow_general_knowledge,
        contract.high_risk,
        contract.minimum_evidence,
        contract.require_citation,
    )
    for module_id, contract in DOMAIN_CONTRACTS.items()
}


def policy_for(module_id: str) -> ModulePolicy:
    contract = domain_for(module_id)
    return POLICIES.get(
        module_id,
        ModulePolicy(
            contract.allow_general_knowledge,
            contract.high_risk,
            contract.minimum_evidence,
            contract.require_citation,
        ),
    )


def expand_query(module_id: str, query: str) -> str:
    expansions = {
        "gripe": "influenza sintomas febre tosse J09 J10 J11",
        "resfriado": "rinofaringite coriza sintomas",
        "pressao": "hipertensao hipotensao arterial",
        "dor de cabeca": "cefaleia enxaqueca",
        "sono": "sonolencia diurna microssono privacao de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano sedativos",
        "dormir": "sonolencia diurna microssono privacao de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano sedativos",
        "sonolencia": "sonolencia diurna microssono privacao de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano sedativos",
    }
    module_expansions = {
        "infraestrutura": {
            "host": "hosts dispositivo equipamento máquina monitorado",
            "adicion": "adicionar adiciono novo criar cadastrar configurar configurando assistente",
            "zabbix": "monitoramento agent agent2 template interface disponibilidade",
            "rede": "network descoberta scan varredura snmp interface tcp udp",
        },
        "departamento-pessoal": {
            "departamento": "departamento pessoal rotinas trabalhistas admissão folha férias rescisão eSocial obrigações",
            "hora extra": "horas extras jornada limite adicional compensação banco de horas",
            "hora": "horas extra extras extraordinárias jornada art. 59 duração diária limite duas",
            "funcion": "empregado trabalhador empregado empregador contrato trabalho",
            "falt": "falta faltas faltar ausência ausente jornada desconto remuneração",
            "negativ": "horas negativas saldo devedor compensação banco de horas acordo",
            "adiantamento": "décimo terceiro salário gratificação natalina antecipação pagamento",
            "decimo terceiro": "décimo terceiro salário gratificação natalina adiantamento antecipação",
            "13": "décimo terceiro salário gratificação natalina adiantamento antecipação",
        },
        "recursos-humanos": {
            "contrat": "contratação admissão recrutamento seleção processo seletivo integração vínculo cargo empregado pessoa candidata",
            "admiss": "admissão contratação documentos cadastro integração empregado vínculo",
            "recrut": "recrutamento seleção candidato vaga entrevista processo seletivo",
            "selec": "seleção candidato vaga entrevista processo seletivo contratação",
            "pessoa": "gestão de pessoas empregado trabalhador desenvolvimento clima desempenho",
            "funcion": "função atribuição rotina gestão de pessoas empregado trabalhador",
        },
        "contabilidade": {
            "balan": "balanço patrimonial demonstrações contábeis ativo passivo patrimônio líquido encerramento",
            "patrimonial": "balanço patrimonial demonstrações contábeis ativo passivo patrimônio líquido",
            "demonstra": "demonstrações contábeis balanço patrimonial ativo passivo patrimônio líquido notas explicativas",
            "ativo": "ativo circulante não circulante passivo patrimônio líquido demonstrações contábeis",
            "passivo": "passivo circulante não circulante ativo patrimônio líquido demonstrações contábeis",
        },
        "direito": {
            "lei": "legislação norma artigo dispositivo jurisprudência aplicação",
            "direit": "direito direitos remuneração salário jornada férias benefícios adicionais licenças cláusulas",
            "acordo coletivo": "convenção coletiva cláusula sindicato categoria benefício remuneração jornada",
            "hora": "horas extra extras extraordinárias jornada art. 59 duração diária limite duas",
            "funcion": "empregado trabalhador empregador contrato trabalho",
            "falt": "falta faltas faltar ausência ausente jornada desconto remuneração",
            "negativ": "horas negativas saldo devedor compensação banco de horas acordo",
            "adiantamento": "décimo terceiro salário gratificação natalina antecipação pagamento",
            "decimo terceiro": "décimo terceiro salário gratificação natalina adiantamento antecipação",
            "13": "décimo terceiro salário gratificação natalina adiantamento antecipação",
        },
        "medicina": {
            "sono": "sonolência diurna microssono privação de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano medicamentos sedativos",
            "dormir": "sonolência diurna microssono privação de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano medicamentos sedativos",
            "sonolencia": "sonolência diurna microssono privação de sono sono insuficiente apneia obstrutiva do sono narcolepsia ritmo circadiano medicamentos sedativos",
            "microssono": "microssono microsleep sonolência diurna privação de sono sono insuficiente",
            "piscada": "microssono sonolência diurna privação de sono sono insuficiente",
        },
    }
    normalized = normalize(query)
    extra_values = [value for key, value in expansions.items() if key in normalized]
    extra_values.extend(value for key, value in module_expansions.get(module_id, {}).items() if key in normalized)
    extra = " ".join(extra_values)
    return f"{query} {extra}".strip()
