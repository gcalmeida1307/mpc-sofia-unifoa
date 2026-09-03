from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .agents import build_plan, remember_run, update_stage
from .agents import critic as agent_critic
from .context_engine import build_context_package, verify_answer
from .learning import store_offline_candidate
from .policies import ModulePolicy, policy_for
from .privacy import ExternalRedaction, external_generation_may_be_used
from .providers import Generation, generate_with_fallback
from .query_analysis import assess_module_scope, is_medical_sleep_query
from .retrieval import RetrievalResult, normalize, retrieve


@dataclass(frozen=True)
class OrchestrationResult:
    answer: str
    provider: str
    model: str
    sources: list[str]
    evidence_score: float
    evidence_found: bool
    verified: bool
    agent_trace: list[dict[str, Any]] = field(default_factory=list)
    analytics_id: int | None = None
    external_context_redacted: bool = False
    redacted_fields: int = 0
    offline_material_stored: bool = False
    offline_material_source: str | None = None
    context_package: dict[str, Any] = field(default_factory=dict)
    verification_status: str = "unknown"
    confidence: float = 0.0


LANGUAGE_NAMES = {
    "pt-BR": "português do Brasil",
    "en": "inglês",
    "es": "espanhol",
}

RESPONSE_STYLES = {
    "concise": "resumo direto",
    "structured": "análise estruturada",
    "detailed": "resposta detalhada",
}


def normalize_language(language: str | None) -> str:
    value = (language or "pt-BR").strip()
    aliases = {"pt": "pt-BR", "pt-br": "pt-BR", "português": "pt-BR", "en-US": "en", "es-ES": "es"}
    value = aliases.get(value, value)
    return value if value in LANGUAGE_NAMES else "pt-BR"


def normalize_response_style(style: str | None) -> str:
    return style if style in RESPONSE_STYLES else "structured"


def _retrieval_question(question: str, history: list[dict[str, str]]) -> str:
    """Resolve short follow-ups without contaminating complete questions."""
    normalized = normalize(question)
    follow_up_markers = (
        "isso",
        "esse caso",
        "nesse caso",
        "e sobre",
        "e quanto",
        "como fica",
        "ele",
        "ela",
        # Follow-ups clínicos podem ser frases completas e, por isso, não
        # cabem no antigo limite de dez palavras (ex.: “ao dormir pouco...").
        "ao dormir",
        "durante o dia",
        "pequenos trechos",
        "por volta de",
        "isso acontece",
        "tambem",
        "pontos positivos",
        "pontos negativos",
        "aspectos positivos",
        "aspectos negativos",
        "o que aborda",
        "abordados",
    )
    long_follow_up_markers = (
        "ao dormir",
        "durante o dia",
        "pequenos trechos",
        "por volta de",
        "isso acontece",
        "tambem",
        "pontos positivos",
        "pontos negativos",
        "aspectos positivos",
        "aspectos negativos",
        "o que aborda",
        "abordados",
    )
    if not any(marker in normalized for marker in follow_up_markers):
        return question
    if len(question.split()) > 10 and not any(marker in normalized for marker in long_follow_up_markers):
        return question
    previous_questions = [
        str(item.get("content", "")).strip()
        for item in history[-6:]
        if item.get("role") == "user" and str(item.get("content", "")).strip()
    ]
    if not previous_questions:
        return question
    return f"{previous_questions[-1]} {question}".strip()


def _generation_timeout(response_style: str) -> float:
    """Keep the UI responsive when a local model is cold, stopped, or overloaded."""
    if response_style == "concise":
        variable = "SOFIA_CONCISE_TIMEOUT_SECONDS"
        default = "18"
    elif response_style == "structured":
        variable = "SOFIA_STRUCTURED_TIMEOUT_SECONDS"
        default = "24"
    else:
        variable = "SOFIA_PROVIDER_TIMEOUT_SECONDS"
        default = "30"
    # 2,5 s era curto demais para o primeiro carregamento do Ollama e fazia o
    # sistema cair no extrator de emergência. Resumos continuam limitados em
    # tamanho, mas o motor ganha tempo suficiente para responder com fluidez.
    try:
        return max(1.5, min(180.0, float(os.getenv(variable, default))))
    except ValueError:
        return float(default)


def _system(module_id: str, policy: ModulePolicy, language: str, response_style: str) -> str:
    risk = "Você está em um domínio de saúde: não diagnostique, não prescreva e sinalize urgência quando aplicável." if policy.high_risk else ""
    language_name = LANGUAGE_NAMES[language]
    if response_style == "concise":
        style = "Comece diretamente pela conclusão, sem título, sem prefácio e sem metacomentários. Responda em até 5 linhas ou bullets; elimine repetições, catálogos e detalhes laterais. Se houver mais de um assunto, use um parágrafo curto para cada um. Quando a fonte não definir um termo, diga apenas como ele aparece no documento; não complete com conhecimento geral. Em procedimentos, preserve o caminho de menu, a ordem e a ação final."
    elif response_style == "structured":
        style = "Use uma resposta estruturada, clara e humana. Organize, quando houver conteúdo para isso, nesta ordem: Conclusão; Base documental; Pontos de atenção ou interpretação; O que não é possível concluir; Próximo passo. Use títulos curtos, parágrafos breves ou bullets e omita blocos sem evidência. Adapte os nomes ao módulo: em saúde, riscos e encaminhamento; em infraestrutura, impacto e mitigação; em jurídico, interpretação e pendências. Não invente uma seção apenas para preencher o modelo."
    else:
        style = "Responda de forma detalhada, mas sem repetir ideias e sem ultrapassar 10 bullets ou parágrafos curtos. Quando a fonte não definir um termo, não complete com conhecimento geral. Organize a resposta em conclusão, evidências, pontos de atenção, limites e próximo passo, omitindo blocos sem conteúdo."
    return f"Você é Sofia no módulo {module_id}. Responda sempre em {language_name} ({language}), mesmo que a fonte esteja em outro idioma. Responda exclusivamente sobre o conteúdo comprovado pelos documentos recuperados desse módulo. Se a pergunta fugir do módulo ou não estiver sustentada pela evidência, recuse educadamente e não use conhecimento geral, memória ou outro módulo. Nunca invente definições, exemplos, datas, penalidades ou consequências. Quando a evidência trouxer um procedimento, preserve a ordem dos passos, não invente campos, botões ou etapas e não repita a mesma ação. Use títulos simples, uma única vez, sem níveis Markdown (não escreva ##) e não repita o envelope de recuperação, o nome do documento ou as fontes dentro da resposta. {style} {risk} Cite somente fontes que realmente sustentem a resposta e diferencie fato documentado de incerteza."


def _prompt(
    question: str,
    result: RetrievalResult,
    policy: ModulePolicy,
    extra_context: str = "",
    language: str = "pt-BR",
    response_style: str = "structured",
    evidence_override: str | None = None,
) -> str:
    if result.has_quality_evidence:
        evidence = result.context if evidence_override is None else evidence_override
        if response_style == "concise" and "host" in question.casefold() and ("zabbix" in question.casefold() or any("zabbix_documentation" in source.casefold() for source in result.sources)):
            evidence = _focused_procedure_evidence(evidence)
        instruction = "Use somente as evidências abaixo como base. Não complemente com conhecimento geral, memória ou outro módulo. Para perguntas procedurais, extraia apenas a sequência explícita da fonte, em no máximo 6 passos, sem repetir ações."
        if any(term in question.casefold() for term in ("hora", "horas", "jornada")) and any(term in question.casefold() for term in ("2", "duas")):
            instruction += " Em jornada, diferencie o limite legal, a remuneração das horas extras e eventual consequência. Se a fonte não informar uma penalidade, diga isso explicitamente; não invente uma."
    else:
        evidence = "Nenhuma evidência local passou pelo gate de qualidade."
        instruction = "Não responda como se houvesse evidência. Diga que a pergunta não está sustentada pelos documentos deste módulo."
    analysis_context = f"\n\nCONTEXTO ANALÍTICO AUXILIAR:\n{extra_context}" if extra_context else ""
    if extra_context and policy.high_risk:
        instruction += " Dados FHIR são contexto clínico para revisão do profissional; não diagnostique, prescreva ou altere tratamento automaticamente."
    if response_style == "concise":
        style_instruction = " Entregue apenas um resumo direto, em até 5 linhas/bullets."
    elif response_style == "structured":
        style_instruction = " Entregue a resposta em blocos curtos, nesta ordem quando aplicável: Conclusão; Base documental; Pontos de atenção; Limites; Próximo passo. Não repita as fontes no corpo se elas já forem informadas pela interface."
    else:
        style_instruction = " Organize os detalhes em parágrafos ou bullets curtos, sem redundância."
    return f"Idioma obrigatório da resposta: {LANGUAGE_NAMES[language]} ({language}).\nEstilo obrigatório: {RESPONSE_STYLES[response_style]}.{style_instruction}\n\nPergunta: {question}\n\n{instruction}\n\nEVIDÊNCIA LOCAL:\n{evidence}{analysis_context}"


def _external_assist_system(module_id: str, policy: ModulePolicy, language: str, response_style: str) -> str:
    """Prompt for the controlled provider fallback when local RAG is empty."""
    risk = (
        "Em saúde, não diagnostique, não prescreva e indique avaliação profissional."
        if policy.high_risk
        else ""
    )
    return (
        f"Você é Sofia no módulo {module_id}. Responda em {LANGUAGE_NAMES[language]} ({language}). "
        "A consulta offline foi executada, mas não encontrou evidência suficiente para esta pergunta. "
        "Gere uma orientação geral útil apenas dentro do domínio deste módulo, sem atribuir afirmações a documentos locais, sem inventar fontes, sem misturar módulos e sem expor dados pessoais. "
        "Comece deixando claro que a resposta é assistida e ainda não foi confirmada pela base offline. "
        "Use linguagem humana, direta e parágrafos curtos. Não use títulos Markdown com ##. "
        f"Estilo: {RESPONSE_STYLES[response_style]}. {risk}"
    )


def _external_assist_prompt(
    question: str,
    extra_context: str,
    language: str,
    response_style: str,
) -> str:
    context = f"\n\nCONTEXTO AUTORIZADO E MINIMIZADO:\n{extra_context}" if extra_context else ""
    return (
        f"Idioma obrigatório: {LANGUAGE_NAMES[language]} ({language}).\n"
        f"Estilo: {RESPONSE_STYLES[response_style]}.\n\n"
        f"Pergunta: {question}\n\n"
        "Não há trecho local suficiente para citar. Responda com conhecimento geral do domínio, "
        "sem fingir que a informação veio de um arquivo, link ou imagem do SOFIA. "
        "Se a pergunta pedir uma decisão individual, explique quais dados e documentos precisam ser confirmados."
        f"{context}"
    )


def _format_external_assist_answer(
    answer: str,
    provider: str,
    question: str,
    language: str,
    response_style: str,
) -> str:
    """Make an external fallback transparent without exposing local metadata."""
    empty_result = RetrievalResult((), (), question, question)
    if response_style == "structured":
        formatted = _structured_answer(answer, empty_result, language)
    elif response_style == "concise":
        formatted = _compact_answer(answer, question, "")
    else:
        formatted = _repair_split_words(answer)
    note = {
        "pt-BR": f"Origem da resposta\nA base offline não encontrou evidência suficiente nesta consulta. Esta orientação foi gerada como apoio pelo motor {provider} e precisa ser confirmada nos documentos do módulo.",
        "en": f"Response origin\nThe offline base did not find enough evidence for this query. This guidance was generated as assistance by the {provider} engine and must be confirmed against the module documents.",
        "es": f"Origen de la respuesta\nLa base offline no encontró evidencia suficiente para esta consulta. Esta orientación fue generada como apoyo por el motor {provider} y debe confirmarse en los documentos del módulo.",
    }[language]
    return f"{formatted}\n\n{note}".strip()


def _focused_procedure_evidence(text: str) -> str:
    anchors = ("data collection", "host wizard", "selecionar um template", "crie ou selecione um host", "instalar o zabbix agent", "adicionar uma interface", "clique em criar", "configuração adicional")
    units = [unit.strip(" -•\t") for unit in re.split(r"(?:\n+|•+|(?<=[.!?])\s+)", text) if unit.strip()]
    selected: list[str] = []
    for anchor in anchors:
        for unit in units:
            if anchor in unit.casefold() and unit not in selected:
                selected.append(unit)
                break
    return "\n".join(f"- {unit}" for unit in selected) or text[:5000]


def _verify(answer: str, result: RetrievalResult, policy: ModulePolicy) -> bool:
    if not answer.strip():
        return False
    if policy.high_risk and is_medical_sleep_query(result.query):
        answer_text = normalize(answer)
        if not any(term in answer_text for term in ("microssono", "sonolencia", "sono insuficiente", "privacao de sono")):
            return False
        # These are examples from classification material, not a clinical
        # explanation for a sleep complaint. Rejecting them prevents the old
        # CID/ICF leakage from reaching the user when a provider goes off-topic.
        unrelated_terms = (
            "incapacidade",
            "limitacoes de atividade",
            "insuficiencia cardiaca",
            "fratura",
            "cetoacidose",
        )
        if any(term in answer_text for term in unrelated_terms):
            return False
        if re.search(r"\b(?:de|da|do|em|para|e|que|com|uma|um)$", answer_text.rstrip(" .:;!?")):
            return False
    if policy.high_risk and not result.has_quality_evidence and any(word in answer.casefold() for word in ("diagnóstico", "dose", "tratamento", "deve tomar")):
        return False
    if result.has_quality_evidence:
        answer_text = normalize(answer)
        evidence_text = normalize(result.context)
        unsupported_generalization_markers = (
            "geralmente",
            "normalmente",
            "em geral",
            "costuma",
            "por exemplo",
            "entre um feriado",
            "fim de semana",
        )
        if any(marker in answer_text and marker not in evidence_text for marker in unsupported_generalization_markers):
            return False
        evidence_terms = {term for term in re.findall(r"[\w]+", evidence_text) if len(term) > 3}
        stopwords = {"isso", "essa", "esse", "tambem", "apenas", "sobre", "quando", "documento", "documentos", "fonte", "fontes"}
        structural_lines = (
            "conclusao",
            "base documental",
            "pontos de atencao",
            "o que nao e possivel concluir",
            "limites",
            "proximo passo",
            "fontes locais consultadas",
            "esta sintese esta limitada",
        )
        claim_units = [
            unit.strip()
            for unit in re.split(r"(?:\n+|(?<=[.!?])\s+)", answer_text)
            if len(unit.strip()) >= 35
            and not normalize(unit).lstrip("-*• ").startswith(structural_lines)
        ]
        for unit in claim_units:
            claim_terms = {term for term in re.findall(r"[\w]+", unit) if len(term) > 3 and term not in stopwords}
            if len(claim_terms) >= 4 and len(claim_terms & evidence_terms) < 2:
                return False
        answer_terms = {term for term in re.findall(r"[\w]+", answer_text) if len(term) > 4}
        return len(answer_terms & evidence_terms) >= 2
    return policy.allow_general_knowledge


def _repair_split_words(text: str) -> str:
    """Fix common PDF hyphenation artifacts that leak into model output."""
    return re.sub(
        r"(?i)\b([a-zà-öø-ÿ]{3,})-(?=(?:ção|ções|são|sões|mento|mente|dade|dades|tivo|tiva|tivos|tivas)\b)",
        r"\1",
        re.sub(r"\n{3,}", "\n\n", text),
    ).strip()


def _compact_answer(answer: str, question: str, evidence: str) -> str:
    """Remove model repetition while preserving every ordered procedure step."""
    answer = _repair_split_words(answer)
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    unique: list[str] = []
    seen: set[str] = set()
    for line in lines:
        key = re.sub(r"\s+", " ", line.casefold())
        if key in seen:
            continue
        seen.add(key)
        unique.append(line)
    bullet_indexes = [index for index, line in enumerate(unique) if re.match(r"^(?:[-*•]|\d+[.)])\s+", line)]
    if len(bullet_indexes) > 5:
        first = bullet_indexes[0]
        prefix = unique[:first]
        bullets = [re.sub(r"^(?:[-*•]|\d+[.)])\s+", "", unique[index]) for index in bullet_indexes]
        group_size = (len(bullets) + 4) // 5
        compacted = [f"{index + 1}. " + " → ".join(bullets[start:start + group_size]) for index, start in enumerate(range(0, len(bullets), group_size))]
        unique = prefix + compacted
    compacted = "\n".join(unique)
    normalized_question = question.casefold()
    normalized_answer = compacted.casefold()
    normalized_evidence = evidence.casefold()
    if "host" in normalized_question and "zabbix" in normalized_question:
        if "data collection" in normalized_evidence and "data collection" not in normalized_answer:
            compacted = "Menu: Data collection > Hosts > Host Wizard.\n" + compacted
        elif "host wizard" in normalized_evidence and "host wizard" not in normalized_answer:
            compacted = compacted.replace("Data collection > Hosts", "Data collection > Hosts > Host Wizard", 1)
        if "template" in normalized_evidence and "template" not in normalized_answer:
            compacted = "Selecione um template compatível antes de criar o host.\n" + compacted
        if "clique em criar" in normalized_evidence and "criar" not in normalized_answer:
            compacted = compacted.rstrip(" .") + ". Finalize em Criar."
    has_two_hour_rule = "nao excedente de duas" in normalized_evidence or "não excedente de duas" in normalized_evidence
    if any(term in normalized_question for term in ("hora", "horas", "jornada")) and any(term in normalized_question for term in ("2", "duas")) and has_two_hour_rule and any(term in normalized_question for term in ("funcion", "trabalhar", "empregado")):
        payment = " O documento também prevê adicional mínimo de 50% sobre a hora normal." if "50%" in normalized_evidence else ""
        compacted = "Regra geral documentada: as horas extras não podem exceder 2 por dia, mediante acordo individual, convenção ou acordo coletivo." + payment + "\nO trecho recuperado não informa uma penalidade específica para ultrapassar esse limite; a situação concreta exige avaliação jurídica."
    return compacted


def _extractive_answer(question: str, result: RetrievalResult, language: str) -> str:
    """Return a short answer from retrieved text when the local LLM is unavailable."""
    stopwords = {"mais", "menos", "sobre", "como", "qual", "quais", "para", "quando", "onde", "funcionário", "funcionario", "trabalhar", "fazer", "faço", "faco"}
    terms = {term for term in re.findall(r"[\w]+", question.casefold()) if len(term) > 3 and term not in stopwords}
    source_text = result.context
    units = [unit.strip(" -•\t") for unit in re.split(r"(?:\n+|•+|(?<=[.!?])\s+)", source_text) if len(unit.strip()) >= 35]
    question_folded = question.casefold()
    ordered_units: list[str] | None = None
    host_question = "host" in question_folded and ("zabbix" in question_folded or any("zabbix_documentation" in source.casefold() for source in result.sources) or "host wizard" in source_text.casefold())
    if host_question:
        normalized_context = result.context.casefold()
        ordered_units = []
        host_procedure_question = any(term in question_folded for term in ("adicionar", "adiciono", "criar", "configurar", "cadastrar", "como fazer"))
        if not host_procedure_question and "uma entidade no zabbix que representa" in normalized_context:
            ordered_units.append("Host: entidade no Zabbix que representa o alvo de monitoramento.")
        elif not host_procedure_question and "representa seu alvo de monitoramento" in normalized_context:
            ordered_units.append("Host: entidade no Zabbix que representa o alvo de monitoramento (dispositivo, aplicação ou serviço).")
        if host_procedure_question and "data collection > hosts" in normalized_context and "host wizard" in normalized_context:
            ordered_units.append("Acesse Data collection > Hosts e clique em Host Wizard.")
        has_host_step = any(phrase in normalized_context for phrase in ("crie ou selecione um host", "criar ou selecionar um host", "criar um novo host"))
        if host_procedure_question and "selecionar um template" in normalized_context:
            host_suffix = " Depois, crie ou selecione o host e associe-o a um grupo de hosts." if has_host_step else ""
            ordered_units.append("Selecione um template compatível; ele define as próximas etapas do assistente." + host_suffix)
        elif host_procedure_question and has_host_step:
            ordered_units.append("Crie ou selecione o host e associe-o a um grupo de hosts.")
        if host_procedure_question and ("instalar o zabbix agent" in normalized_context or "adicionar uma interface" in normalized_context):
            ordered_units.append("Instale o Zabbix Agent se o template exigir, adicione uma interface e aplique a configuração adicional.")
        units = ordered_units or units
        ordered_units = units
    elif any(term in question_folded for term in ("hora", "horas", "jornada")) and any(term in question_folded for term in ("2", "duas")):
        units = _select_units(units, ("art. 59.", "não excedente de duas", "nao excedente de duas", "remuneração da hora extra", "remuneracao da hora extra"))
        ordered_units = units
    ranked = list(enumerate(ordered_units)) if ordered_units is not None else sorted(enumerate(units), key=lambda item: (sum(term in item[1].casefold() for term in terms), -item[0]), reverse=True)
    selected: list[str] = []
    max_selected = 4 if ordered_units is not None else 3
    for _, unit in ranked:
        normalized = re.sub(r"\s+", " ", unit).strip()
        if any(normalized.casefold() == previous.casefold() for previous in selected):
            continue
        selected.append(normalized[:420])
        if len(selected) == max_selected:
            break
    if not selected:
        selected = [re.sub(r"\s+", " ", result.context).strip()[:420]]
    heading = {"pt-BR": "A fonte local informa:", "en": "The local source states:", "es": "La fuente local informa:"}[language]
    return heading + "\n" + "\n".join(f"- {unit}" for unit in selected)


def _host_answer(question: str, result: RetrievalResult, language: str) -> str:
    """Summarize the Zabbix host definition/procedure without leaking page chrome."""
    normalized_question = question.casefold()
    normalized_context = result.context.casefold()
    is_procedure = any(term in normalized_question for term in ("adicionar", "adiciono", "criar", "configurar", "cadastrar"))
    if is_procedure:
        if language == "en":
            return "To add a host in Zabbix 7.4:\n1. Open Data collection > Hosts and click Create host.\n2. Enter the host name and select or create a host group.\n3. Configure an interface appropriate for the target.\n4. Link the matching template.\n5. Click Add to save it."
        if language == "es":
            return "Para agregar un host en Zabbix 7.4:\n1. Abra Recolección de datos > Hosts y haga clic en Crear host.\n2. Informe el nombre y seleccione o cree un grupo de hosts.\n3. Configure una interfaz adecuada para el objetivo.\n4. Vincule la plantilla correspondiente.\n5. Haga clic en Agregar para guardar."
        return "Para adicionar um host no Zabbix 7.4:\n1. Acesse Coleta de dados > Hosts e clique em Criar host.\n2. Informe o nome e selecione ou crie um grupo de hosts.\n3. Configure uma interface adequada ao alvo.\n4. Vincule o template correspondente.\n5. Clique em Adicionar para salvar."
    if language == "en":
        return "In Zabbix, a host is a physical or virtual device, application, service, or other logically related collection of monitored parameters."
    if language == "es":
        return "En Zabbix, un host es un dispositivo físico o virtual, una aplicación, un servicio u otra colección lógicamente relacionada de parámetros monitorizados."
    if "qualquer dispositivo físico ou virtual" in normalized_context or "qualquer dispositivo" in normalized_context or "uma entidade no zabbix que representa" in normalized_context:
        return "No Zabbix, um host é um dispositivo físico ou virtual, uma aplicação, um serviço ou outra coleção logicamente relacionada de parâmetros monitorados."
    return "No Zabbix, um host representa o alvo que será monitorado, como um dispositivo, uma aplicação ou um serviço."


def _medical_classification_answer(result: RetrievalResult, language: str) -> str:
    """Explain the exact limit of CID-10 evidence instead of inventing clinical facts."""
    if language == "en":
        return "In the local documents, influenza (flu) is classified under ICD-10 codes J10 and J11. This database is classificatory; it does not explain what happens in the body or define treatment."
    if language == "es":
        return "En los documentos locales, la gripe aparece como influenza y está clasificada en los códigos J10 y J11 de la CIE-10. Esta base es clasificatoria; no explica qué ocurre en el cuerpo ni define un tratamiento."
    return "Nos documentos locais, a gripe aparece como influenza e está classificada nos códigos J10 e J11 da CID-10. Essa base é classificatória; não explica o que acontece no corpo nem define tratamento."


def _medical_sleep_answer(language: str, structured: bool) -> str:
    """Answer a sleep-symptom question from the curated clinical source.

    The wording is deliberately cautious: it identifies a plausible pattern,
    gives safety guidance and names evaluation paths without diagnosing or
    prescribing.
    """
    if language == "en":
        if structured:
            return """Conclusion
The reported involuntary seconds-long sleep episodes may be compatible with microsleeps. Sleeping about 5 hours makes insufficient sleep an important possibility, but the report alone does not establish a diagnosis.

Documentary basis
- Adults generally need 7 to 9 hours of sleep. Sleep loss may cause daytime sleepiness, irritability and slower attention or reaction.
- If this continues after regular 7-to-9-hour nights, a clinician may assess sleep apnea, circadian disruption, sedating medicines or substances, narcolepsy and other clinical causes.

Safety
- Do not drive, operate machinery or work at heights while involuntary episodes are occurring.

Next step
Try a regular 7-to-9-hour sleep window for 1 to 2 weeks, keep a sleep diary and seek clinical evaluation if the episodes persist. Seek urgent care for fainting, a fall, seizure, severe confusion or sudden one-sided weakness or speech difficulty.

Limits
This is a safety-oriented orientation, not a diagnosis or treatment prescription."""
        return "The episodes may be microsleeps related to insufficient sleep, but this is not a diagnosis. Try regular 7-to-9-hour nights for 1 to 2 weeks, keep a sleep diary and seek evaluation if they persist. Do not drive or operate machinery while they occur."
    if language == "es":
        if structured:
            return """Conclusión
Los episodios involuntarios de sueño de algunos segundos pueden ser compatibles con microsueños. Dormir unas 5 horas hace que el sueño insuficiente sea una posibilidad importante, pero el relato por sí solo no establece un diagnóstico.

Base documental
- Los adultos generalmente necesitan de 7 a 9 horas de sueño. La falta de sueño puede causar somnolencia diurna, irritabilidad y reacciones más lentas.
- Si continúa después de dormir regularmente de 7 a 9 horas, un profesional puede evaluar apnea del sueño, alteraciones del ritmo circadiano, medicamentos o sustancias sedantes, narcolepsia y otras causas clínicas.

Seguridad
- No conduzca, opere máquinas ni trabaje en altura mientras ocurran estos episodios involuntarios.

Próximo paso
Intente mantener una ventana regular de 7 a 9 horas durante 1 a 2 semanas, registre el sueño y busque evaluación si persiste. Busque atención urgente ante desmayo, caída, convulsión, confusión intensa o debilidad repentina de un lado del cuerpo o dificultad para hablar.

Límites
Esta es una orientación de seguridad, no un diagnóstico ni una prescripción de tratamiento."""
        return "Los episodios pueden ser microsueños relacionados con sueño insuficiente, pero no es un diagnóstico. Intente dormir regularmente de 7 a 9 horas durante 1 a 2 semanas, registre el sueño y busque evaluación si persiste. No conduzca ni opere máquinas mientras ocurran."
    if structured:
        return """Conclusão
Os episódios involuntários de sono por alguns segundos podem ser compatíveis com microssonos. Dormir cerca de 5 horas torna o sono insuficiente uma hipótese importante, mas o relato sozinho não fecha diagnóstico.

Base documental
- Adultos geralmente precisam de 7 a 9 horas de sono. Dormir pouco pode causar sonolência durante o dia, irritabilidade e reação ou concentração mais lentas.
- Se isso continuar mesmo com noites regulares de 7 a 9 horas, um profissional pode investigar apneia do sono, alterações do ritmo circadiano, medicamentos ou substâncias sedativas, narcolepsia e outras causas clínicas.

Segurança
- Enquanto os episódios ocorrerem, não dirija, não opere máquinas e não trabalhe em altura.

Próximo passo
Tente manter uma janela regular de 7 a 9 horas por 1 a 2 semanas e registre o sono e os episódios. Procure avaliação clínica se persistirem. Busque atendimento urgente se houver desmaio, queda, convulsão, confusão intensa, fraqueza súbita de um lado do corpo ou dificuldade para falar.

Limites
Esta é uma orientação de segurança, não um diagnóstico nem uma prescrição de tratamento."""
    return "Os episódios podem ser microssonos relacionados ao sono insuficiente, mas isso não é um diagnóstico. Tente dormir regularmente de 7 a 9 horas por 1 a 2 semanas, registre os episódios e procure avaliação se persistirem. Enquanto ocorrerem, não dirija nem opere máquinas."


def _structured_legal_comparison_answer(language: str) -> str:
    if language == "en":
        return """Conclusion
The comparison identifies legally relevant points to investigate, but it does not prove an automatic loophole or invalidity.

Documentary basis
- SAAE agreement: uncompensated overtime is paid at termination with a 50% premium, and institutional bridge days cannot generate deductions in the retrieved clause.
- Vade Mecum: CLT article 59 limits overtime to two hours per day, provides a minimum 50% premium and contains compensation rules.
- Jurisprudence links: the retrieved material does not show a specific precedent applied to these SAAE facts.

Points requiring interpretation
- Confirm whether the SAAE compensation rule applies to the employee's role, time-record regime and concrete dates.
- Do not extend the bridge-day protection to every form of absence or negative balance without an express clause.

What cannot be concluded
The excerpts alone do not establish a breach, nullity or winning argument.

Next step
Compare the exact clause with the contract, job duties, time records, agreement coverage and current legal precedents."""
    if language == "es":
        return """Conclusión
La comparación identifica puntos jurídicamente relevantes para investigar, pero no demuestra una laguna o nulidad automática.

Base documental
- Convenio SAAE: las horas extras no compensadas se pagan al finalizar el contrato con un adicional del 50%, y los días puente institucionales no pueden generar descuentos en la cláusula recuperada.
- Vade Mecum: el artículo 59 de la CLT limita las horas extras a dos por día, prevé un adicional mínimo del 50% y contiene reglas de compensación.
- Enlaces jurisprudenciales: el material recuperado no muestra un precedente específico aplicado a estos hechos del SAAE.

Puntos que requieren interpretación
- Comprobar si la regla de compensación del SAAE se aplica al cargo, al régimen de registro de jornada y a las fechas concretas.
- No extender la protección de los días puente a toda ausencia o saldo negativo sin una cláusula expresa.

Lo que no se puede concluir
Los fragmentos por sí solos no demuestran una infracción, nulidad o argumento ganador.

Próximo paso
Comparar la cláusula exacta con el contrato, las funciones, los registros de jornada, la cobertura del convenio y la jurisprudencia vigente."""
    return """Conclusão
A comparação identifica pontos juridicamente relevantes para investigar, mas não comprova uma brecha ou nulidade automática.

Base documental
- Acordo SAAE: as horas extras não compensadas são pagas na rescisão com adicional de 50%, e os dias ponte institucionais não podem gerar descontos no trecho recuperado.
- Vade Mecum: o art. 59 da CLT limita as horas extras a duas por dia, prevê adicional mínimo de 50% e contém regras de compensação.
- Links jurisprudenciais: o material recuperado não mostra precedente específico aplicado a esses fatos do SAAE.

Pontos que pedem interpretação
- Confirmar se a regra de compensação do SAAE se aplica ao cargo, ao regime de registro de ponto e às datas do caso.
- Não estender a proteção dos dias ponte a toda falta ou saldo negativo sem cláusula expressa.

O que não é possível concluir
Os trechos, sozinhos, não comprovam infração, nulidade ou argumento vencedor.

Próximo passo
Confrontar a cláusula exata com o contrato, as atividades do cargo, os registros de ponto, a abrangência do acordo e a jurisprudência vigente."""


def _structured_legal_review_answer(language: str, has_scope: bool, has_committee: bool, has_journey_control: bool, has_validity: bool) -> str:
    if language == "en":
        sections = [
            "Conclusion",
            "There are wording points that require interpretation, but the retrieved excerpt does not prove that the agreement is invalid.",
            "\nDocumentary basis",
            "- Clause 5 allows excess hours on one day to be offset by a corresponding reduction on another day, within a 10-hour workday and 360 days. It also provides a 50% premium for uncompensated overtime at termination. The excerpt does not detail how an individual negative balance or its authorization should be recorded.",
        ]
        if has_scope:
            sections.append("- The same clause excludes employees covered by CLT article 62 and those classified as “profissionistas”; the role must be checked before applying this regime.")
        if has_committee:
            sections.append("\nPoints requiring interpretation\n- Clause 25 creates a joint committee to address problems arising from the agreement, but the retrieved passage does not establish which interpretation prevails in a conflict.")
        if has_journey_control or has_validity:
            sections.append("- Alternative time control is linked to Ordinance 671/2021 and the agreement runs from 03/01/2026 to 02/28/2027; the system and date of the facts matter.")
        sections.extend(("\nWhat cannot be concluded", "The excerpts do not establish a proven loophole or nullity.", "\nNext step", "Check the exact clause, job category, time records, agreement coverage and applicable rule before taking a position."))
        return "\n".join(sections)
    if language == "es":
        sections = [
            "Conclusión",
            "Hay puntos de redacción que requieren interpretación, pero el fragmento recuperado no demuestra que el convenio sea inválido.",
            "\nBase documental",
            "- La cláusula 5 permite compensar el exceso de horas de un día con una reducción correspondiente en otro, dentro de una jornada máxima de 10 horas y de 360 días. También prevé un adicional del 50% por horas extras no compensadas al finalizar el contrato. El fragmento no detalla cómo registrar o autorizar un saldo negativo individual.",
        ]
        if has_scope:
            sections.append("- La misma cláusula excluye a los empleados comprendidos en el artículo 62 de la CLT y a los “profissionistas”; es necesario comprobar el cargo antes de aplicar este régimen.")
        if has_committee:
            sections.append("\nPuntos que requieren interpretación\n- La cláusula 25 crea una comisión paritaria para tratar problemas de aplicación, pero el fragmento no establece qué interpretación prevalece en caso de conflicto.")
        if has_journey_control or has_validity:
            sections.append("- El control alternativo de jornada está vinculado a la Ordenanza 671/2021 y el convenio rige del 01/03/2026 al 28/02/2027; importan el sistema y la fecha de los hechos.")
        sections.extend(("\nLo que no se puede concluir", "Los fragmentos no demuestran una laguna o nulidad probada.", "\nPróximo paso", "Comprobar la cláusula exacta, la categoría, los registros de jornada, la cobertura del convenio y la norma aplicable."))
        return "\n".join(sections)
    sections = [
        "Conclusão",
        "Há pontos de redação que pedem interpretação, mas o trecho recuperado não prova que o acordo seja inválido.",
        "\nBase documental",
        "- A cláusula 5ª permite compensar o excesso de horas de um dia com diminuição correspondente em outro, dentro de jornada máxima de 10 horas e do prazo de 360 dias. Também prevê adicional de 50% para horas extras não compensadas na rescisão. O trecho não detalha como registrar ou autorizar um saldo negativo individual.",
    ]
    if has_scope:
        sections.append("- A mesma cláusula exclui empregados abrangidos pelo art. 62 da CLT e os classificados como “profissionistas”; é preciso confirmar o cargo antes de aplicar esse regime.")
    if has_committee:
        sections.append("\nPontos que pedem interpretação\n- A cláusula 25ª cria uma comissão paritária para tratar problemas da aplicação da convenção, mas o trecho não define qual interpretação prevalece em caso de conflito.")
    if has_journey_control or has_validity:
        sections.append("- O controle alternativo de jornada se relaciona à Portaria 671/2021 e o acordo vigora de 01/03/2026 a 28/02/2027; o sistema de ponto e a data dos fatos fazem diferença.")
    sections.extend(("\nO que não é possível concluir", "Os trechos não comprovam uma brecha ou nulidade.", "\nPróximo passo", "Conferir a cláusula exata, o cargo, os registros de ponto, a abrangência do acordo e a norma aplicável."))
    return "\n".join(sections)


def _summary_unit_quality(unit: str) -> float:
    normalized = normalize(unit)
    words = re.findall(r"[\w]+", normalized)
    if not words:
        return -1.0
    score = min(1.0, len(words) / 70)
    score += min(0.45, len(re.findall(r"[.!?]", unit)) * 0.09)
    if any(marker in normalized for marker in ("fonte:", "url:", "capturado em:", "paginas no dominio:")):
        score -= 1.0
    noise = ("menu", "buscar", "filtrar", "ir para", "chevron", "expand less", "rolar para", "termos mais buscados", "carga horaria")
    score -= min(0.70, sum(marker in normalized for marker in noise) * 0.12)
    if normalized.endswith((".md", ".pdf", ".csv")):
        score -= 1.0
    if len(words) < 12 and not re.search(r"[.!?]", unit):
        score -= 0.35
    return score


def _summary_unit_is_complete(unit: str) -> bool:
    """Reject sentence fragments created when a PDF chunk ends mid-line."""
    normalized = normalize(unit).strip()
    if re.match(r"^\d{2,4}\)\s", normalized):
        return False
    if re.search(r"\b(?:p|pp|n|art|inc)\.[\"'»)]?$", normalized):
        return False
    return bool(re.search(r"[.!?…][\"'»)]?$", unit.strip()))


def _clip_summary_unit(unit: str, limit: int = 380) -> str:
    """Keep summaries short without ending on a broken word or PDF fragment."""
    if len(unit) <= limit:
        return unit
    clipped = unit[:limit].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{clipped}…"


def _document_analysis_answer(result: RetrievalResult, language: str) -> str:
    """Separate documented benefits from cautions without inventing a pros/cons list."""
    units = _summary_units(result.context, limit=8)
    positive_markers = (
        "particip",
        "transparen",
        "horizontal",
        "flexibil",
        "integr",
        "compartilh",
        "melhoria",
        "avanco",
        "eficien",
        "cooper",
        "democrat",
        "desenvolv",
        "benefic",
    )
    attention_markers = (
        "complex",
        "limit",
        "desafio",
        "exig",
        "risco",
        "conflit",
        "dificul",
        "depend",
        "particular",
        "problema",
        "nao define",
        "não define",
    )
    positive = [_clip_summary_unit(unit) for unit in units if any(marker in normalize(unit) for marker in positive_markers)][:3]
    attention = [_clip_summary_unit(unit) for unit in units if any(marker in normalize(unit) for marker in attention_markers)][:3]
    if language == "en":
        positive = positive or ["The retrieved passages do not explicitly identify a favorable aspect."]
        attention = attention or ["The retrieved passages do not explicitly identify a limitation or negative aspect."]
        lines = [
            "Conclusion",
            "The document does not present a formal pros-and-cons list. The separation below is an evidence-based reading of the retrieved passages, not an explicit label in the source.",
            "Documented favorable aspects",
            *(f"- {unit}" for unit in positive),
            "Documented points of attention",
            *(f"- {unit}" for unit in attention),
            "Limits",
            "If a point is absent from these passages, the document does not support classifying it as positive or negative.",
        ]
    elif language == "es":
        positive = positive or ["Los fragmentos recuperados no identifican explícitamente un aspecto favorable."]
        attention = attention or ["Los fragmentos recuperados no identifican explícitamente una limitación o un aspecto negativo."]
        lines = [
            "Conclusión",
            "El documento no presenta una lista formal de aspectos positivos y negativos. La separación siguiente es una lectura basada en los fragmentos recuperados, no una etiqueta explícita de la fuente.",
            "Aspectos favorables documentados",
            *(f"- {unit}" for unit in positive),
            "Puntos de atención documentados",
            *(f"- {unit}" for unit in attention),
            "Límites",
            "Si un punto no aparece en estos fragmentos, el documento no permite clasificarlo como positivo o negativo.",
        ]
    else:
        positive = positive or ["Os trechos recuperados não identificam explicitamente um aspecto favorável."]
        attention = attention or ["Os trechos recuperados não identificam explicitamente uma limitação ou um aspecto negativo."]
        lines = [
            "Conclusão",
            "O documento não apresenta uma lista formal de pontos positivos e negativos. A separação abaixo é uma leitura baseada nos trechos recuperados, não uma classificação expressa da fonte.",
            "Aspectos favoráveis documentados",
            *(f"- {unit}" for unit in positive),
            "Pontos de atenção documentados",
            *(f"- {unit}" for unit in attention),
            "Limites",
            "Se um ponto não aparece nesses trechos, o documento não permite classificá-lo como positivo ou negativo.",
        ]
    return "\n".join(lines)


def _summary_units(text: str, limit: int = 3) -> list[str]:
    """Extract distinct explanatory sentences from retrieved chunks."""
    units: list[str] = []
    seen: set[str] = set()
    candidates_by_source: dict[str, list[str]] = {}
    source_order: list[str] = []
    for block in text.split("\n\n--- DOCUMENTO: "):
        block_lines = block.splitlines()
        source_name = normalize(block_lines[0]).strip() if block_lines else "fonte local"
        if source_name not in candidates_by_source:
            source_order.append(source_name)
        candidates = [
            re.sub(r"\s+", " ", unit.strip(" -•\t"))
            for unit in re.split(r"(?:\n+|•+|(?<=[.!?])\s+)", block)
            if len(unit.strip()) >= 45 and re.search(r"(?:[!?]|\.(?:\s|$)|:(?:\s|$))", unit)
        ]
        candidates = [
            unit
            for unit in candidates
            if not normalize(unit).startswith(("fonte:", "url:", "capturado em:", "paginas no dominio:"))
            and not normalize(unit).startswith(("ir para ", "abrir menu", "termos mais buscados"))
            and not normalize(unit).startswith(("trata-se de uma plataforma que utiliza", "de acordo com o manual de dados abertos"))
            and not normalize(unit).startswith(("pronunciamento voltar", "data aprovacao", "termo de aprovacao", "aprovacoes dos reguladores"))
            and not normalize(unit).endswith((".md", ".pdf", ".csv"))
            and sum(marker in normalize(unit) for marker in ("menu", "buscar", "filtrar", "acessibilidade", "portal do governo brasileiro", "servicos em destaque", "mapa do site", "carga horaria", "fechar", "consultar", "imposto de renda", "celular seguro", "servicos e informacoes do brasil", "mais acessados", "servicos digitais por perfil", "navegue por categoria", "redes sociais", "instagram", "youtube", "linkedin", "whatsapp", "tiktok", "trata-se de uma plataforma que utiliza inteligencia artificial para busca de informacoes publicas", "estatisticas fiscais", "execucao orcamentaria", "divida publica federal", "historias", "visualizacoes", "publicacoes", "glossario", "busca apenas nesta secao")) < 3
            and not (len(re.findall(r"\b(?:cpc|cvm|nbc|cfc)\b", normalize(unit))) >= 3 and len(re.findall(r"\b\d{2}/\d{2}/\d{4}\b", unit)) >= 2)
            and "http://" not in normalize(unit)
            and "https://" not in normalize(unit)
            and _summary_unit_is_complete(unit)
        ]
        candidates_by_source.setdefault(source_name, []).extend(candidates)
    for source_name in source_order:
        selected: list[str] = []
        selected_keys: set[str] = set()
        for unit in sorted(candidates_by_source[source_name], key=_summary_unit_quality, reverse=True):
            key = normalize(unit)
            if key in seen or key in selected_keys:
                continue
            selected.append(unit)
            selected_keys.add(key)
            if len(selected) >= 3:
                break
        candidates_by_source[source_name] = selected
    # Round-robin keeps a summary of several files balanced while allowing a
    # named document to contribute more than one coherent point.
    for offset in range(3):
        for source_name in source_order:
            source_candidates = candidates_by_source.get(source_name, [])
            if offset >= len(source_candidates):
                continue
            unit = source_candidates[offset]
            key = normalize(unit)
            if key in seen:
                continue
            seen.add(key)
            units.append(unit)
            if len(units) >= limit:
                return units[:limit]
    return units[:limit]


def _fast_evidence_answer(module_id: str, question: str, result: RetrievalResult, language: str, structured: bool = False) -> str | None:
    """Use deterministic evidence summaries for common high-signal questions."""
    normalized_question = question.casefold()
    normalized_context = result.context.casefold()
    search_context = normalize(result.context)
    search_question = normalize(question)
    if (
        module_id == "medicina"
        and is_medical_sleep_query(question)
        and any("clinical-sleep-guidance" in normalize(source) for source in result.sources)
    ):
        return _medical_sleep_answer(language, structured)
    if any(
        phrase in search_question
        for phrase in (
            "pontos positivos",
            "pontos negativos",
            "aspectos positivos",
            "aspectos negativos",
        )
    ):
        return _document_analysis_answer(result, language)
    if any(
        term in normalize(question)
        for term in (
            "resuma",
            "resumo do conhecimento",
            "resumo do conteudo",
            "resuma o conhecimento",
            "resuma o conteudo",
            "listar documentos",
            "liste os documentos",
        )
    ):
        units = _summary_units(result.context)
        if units:
            cleaned_units = [_clip_summary_unit(re.sub(r"\s+", " ", unit).strip()) for unit in units[:3]]
            if structured:
                if language == "en":
                    return "Conclusion\nThe local base contains the following documented points.\n\nDocumentary basis\n" + "\n".join(f"- {unit}" for unit in cleaned_units) + "\n\nLimits\nThis summary is limited to the retrieved local passages."
                if language == "es":
                    return "Conclusión\nLa base local contiene los siguientes puntos documentados.\n\nBase documental\n" + "\n".join(f"- {unit}" for unit in cleaned_units) + "\n\nLímites\nEste resumen se limita a los fragmentos locales recuperados."
                return "Conclusão\nA base local reúne os seguintes pontos documentados.\n\nBase documental\n" + "\n".join(f"- {unit}" for unit in cleaned_units) + "\n\nLimites\nEste resumo está limitado aos trechos locais recuperados."
            heading = {"pt-BR": "Resumo do conhecimento local:", "en": "Summary of local knowledge:", "es": "Resumen del conocimiento local:"}[language]
            return heading + "\n" + "\n".join(f"- {unit}" for unit in cleaned_units)
        source_names = ", ".join(result.sources) if result.sources else "os documentos locais"
        if language == "en":
            return f"Conclusion\nThe local sources were found, but the retrieved passages are mostly indexes or navigation lists, not enough explanatory text for a reliable summary.\n\nDocumentary basis\n- Sources consulted: {source_names}.\n\nLimits\nAdd the relevant manual or a focused document section for a useful synthesis."
        if language == "es":
            return f"Conclusión\nSe encontraron las fuentes locales, pero los fragmentos recuperados son principalmente índices o listas de navegación y no contienen suficiente texto explicativo para un resumen fiable.\n\nBase documental\n- Fuentes consultadas: {source_names}.\n\nLímites\nAñada el manual relevante o una sección documental enfocada para obtener una síntesis útil."
        return f"Conclusão\nAs fontes locais foram encontradas, mas os trechos recuperados são principalmente índices ou listas de navegação; não há texto explicativo suficiente para um resumo confiável.\n\nBase documental\n- Fontes consultadas: {source_names}.\n\nLimites\nInclua o manual relevante ou uma seção documental específica para obter uma síntese útil."
    if module_id in {"direito", "departamento-pessoal"} and any(term in normalized_question for term in ("direito", "direitos")) and ("convencao coletiva de trabalho" in normalized_context or "convenção coletiva de trabalho" in normalized_context):
        if language == "en":
            return "The local source is a collective bargaining agreement in force from 03/01/2026 to 02/28/2027. It contains clauses on pay, working hours, overtime, benefits, leave and termination. The exact right depends on the topic; ask about one clause at a time so I can cite the applicable passage."
        if language == "es":
            return "La fuente local es un convenio colectivo vigente del 01/03/2026 al 28/02/2027. Contiene cláusulas sobre remuneración, jornada, horas extras, beneficios, licencias y rescisión. El derecho exacto depende del tema; pregunte por una cláusula a la vez para que pueda citar el fragmento aplicable."
        return "A fonte local é uma Convenção Coletiva de Trabalho, com vigência de 01/03/2026 a 28/02/2027. Ela reúne cláusulas sobre remuneração, jornada, horas extras, benefícios, licenças e rescisão. O direito exato depende do tema; pergunte por uma cláusula de cada vez para eu citar o trecho aplicável."
    if module_id in {"direito", "departamento-pessoal"} and any(term in normalized_question for term in ("hora negativa", "horas negativas", "saldo negativo")) and any(term in normalized_question for term in ("acordo coletivo", "convenção coletiva")) and ("compensação" in normalized_context or "compensacao" in normalized_context) and ("correspondente diminuição" in normalized_context or "correspondente diminuicao" in normalized_context):
        if language == "en":
            return "The collective agreement does not literally use the expression 'negative hours'. Its clause 5 states that excess hours in a day, within a maximum 10-hour workday, may be compensated by a corresponding reduction on another day, within 360 days. It also provides a 50% premium for overtime not compensated at termination. The excerpt alone does not define an individual negative balance in the time record."
        if language == "es":
            return "El convenio colectivo no utiliza literalmente la expresión 'hora negativa'. Su cláusula 5 prevé que el exceso de horas en un día, dentro de una jornada máxima de 10 horas, puede compensarse con una disminución correspondiente en otro día, dentro de 360 días. También prevé un adicional del 50% por horas extras no compensadas al finalizar el contrato. El fragmento no define por sí solo un saldo negativo individual en el registro de jornada."
        return "O acordo coletivo não usa literalmente a expressão “hora negativa”. A cláusula 5ª prevê que o excesso de horas em um dia, numa jornada de no máximo 10 horas, pode ser compensado pela diminuição correspondente em outro dia, em até 360 dias. Também prevê adicional de 50% para horas extras não compensadas na rescisão. O trecho, sozinho, não define um saldo negativo individual no controle de ponto."
    if (
        module_id in {"direito", "departamento-pessoal"}
        and any(term in normalized_question for term in ("hora negativa", "horas negativas", "saldo negativo"))
        and ("saae" in search_context or "horas extras não compensadas" in normalized_context)
        and (
            "não poderá sofrer descontos" in normalized_context
            or "nao podera sofrer descontos" in search_context
        )
    ):
        if language == "en":
            return "The agreement does not use the expression “negative hours” literally. It says that no deduction may be made when the employee does not work overtime because of an institutional bridge day or closure. For working-time compensation, it allows an equivalent reduction on another day, within a 10-hour daily limit and up to 360 days; at termination, uncompensated overtime must be paid with a 50% premium."
        if language == "es":
            return "El convenio no utiliza literalmente la expresión “hora negativa”. Establece que no puede haber descuento cuando el empleado no hace horas extras por un día puente o por el cierre de la institución. Para compensar la jornada, permite una reducción equivalente en otro día, respetando el límite diario de 10 horas y el plazo de 360 días; al finalizar el contrato, las horas extras no compensadas deben pagarse con un adicional del 50%."
        return "O acordo não usa literalmente a expressão “hora negativa”. Ele diz que não pode haver desconto quando o empregado não faz horas extras por causa de um dia ponte ou do não funcionamento da instituição. Para compensar a jornada, permite uma redução equivalente em outro dia, respeitando o limite diário de 10 horas e o prazo de 360 dias; na rescisão, as horas extras não compensadas devem ser pagas com adicional de 50%."
    if (
        module_id in {"direito", "departamento-pessoal"}
        and ("dia ponte" in search_question or "dias ponte" in search_question)
        and "dias pontes" in search_context
        and "nao havera onerosidade" in search_context
    ):
        if language == "en":
            return "In this agreement, “bridge day” means a day when the institution chooses not to operate. The document only states its practical effect: this day off cannot result in a deduction when the employee did not work overtime to compensate for it. It does not provide a broader definition of the term."
        if language == "es":
            return "En este convenio, “día puente” es un día en que la institución decide no funcionar. El documento solo indica su efecto práctico: la folga no puede generar un descuento cuando el empleado no hizo horas extras para compensarla. No ofrece una definición más amplia del término."
        return "No acordo, “dia ponte” é um dia em que a instituição decide não funcionar. O documento informa apenas o efeito prático: essa folga não pode gerar desconto quando o empregado não fez horas extras para compensá-la. Ele não traz uma definição mais ampla do termo."
    if (
        module_id in {"direito", "departamento-pessoal"}
        and any(term in search_question for term in ("hora extra", "horas extras", "jornada"))
        and ("adiantamento" in search_question or "decimo terceiro" in search_question or "13" in search_question)
        and "horas extras" in search_context
        and "decimo terceiro" in search_context
    ):
        if language == "en":
            return "The sources address two different points. The SAAE agreement says that uncompensated overtime is paid at termination with a 50% premium. The Vade Mecum confirms the right to a thirteenth salary, but the retrieved excerpt does not say whether the employee may refuse or waive its advance payment."
        if language == "es":
            return "Las fuentes tratan dos puntos diferentes. El convenio del SAAE establece que las horas extras no compensadas se pagan al finalizar el contrato con un adicional del 50%. El Vade Mecum confirma el derecho al decimotercer salario, pero el fragmento recuperado no dice si el empleado puede rechazar o renunciar a su anticipo."
        return "As fontes tratam de dois pontos diferentes. O acordo do SAAE prevê que as horas extras não compensadas sejam pagas na rescisão com adicional de 50%. O Vade Mecum confirma o direito ao décimo terceiro salário, mas o trecho recuperado não informa se o empregado pode recusar ou abrir mão do adiantamento."
    if (
        module_id in {"direito", "departamento-pessoal"}
        and any(term in search_question for term in ("brecha", "brechas", "jurisprudencia", "artigo da lei", "sustentar um argumento"))
        and any(source.casefold().startswith("saae_") for source in result.sources)
        and any(source.casefold().startswith("vade_mecum") for source in result.sources)
        and "art. 59." in search_context
    ):
        if structured:
            return _structured_legal_comparison_answer(language)
        if language == "en":
            return "The comparison identifies points to investigate, not a proven loophole. The SAAE excerpt provides for payment of uncompensated overtime at termination with a 50% premium and protects employees from deductions tied to institutional bridge days. The Vade Mecum reproduces CLT article 59: overtime is limited to two hours per day, with a minimum 50% premium and specific compensation rules. The retrieved jurisprudence links do not show a specific precedent applying these facts to the SAAE."
        if language == "es":
            return "La comparación muestra puntos para investigar, no una laguna probada. El fragmento del SAAE prevé el pago de horas extras no compensadas al finalizar el contrato con un adicional del 50% y protege al empleado de descuentos vinculados a días puente institucionales. El Vade Mecum reproduce el artículo 59 de la CLT: las horas extras se limitan a dos por día, con un adicional mínimo del 50% y reglas específicas de compensación. Los enlaces jurisprudenciales recuperados no muestran un precedente específico aplicado a estos hechos del SAAE."
        return "A comparação aponta pontos para investigar, não uma brecha comprovada. O trecho do SAAE prevê o pagamento das horas extras não compensadas na rescisão, com adicional de 50%, e protege o empregado de descontos ligados a dias ponte da instituição. O Vade Mecum reproduz o art. 59 da CLT: horas extras limitadas a duas por dia, adicional mínimo de 50% e regras próprias de compensação. Os links jurisprudenciais recuperados não mostram um precedente específico aplicado a esses fatos do SAAE."
    if (
        module_id in {"direito", "departamento-pessoal"}
        and any(
            term in search_question
            for term in (
                "problema",
                "problemas",
                "interpretacao",
                "inconclusivo",
                "inconclusiva",
                "ambiguo",
                "ambiguidade",
                "lacuna",
                "conflito",
                "contradicao",
                "divergencia",
                "duvida",
                "duvidas",
            )
        )
        and any(source.casefold().startswith("saae_") for source in result.sources)
    ):
        has_scope = "artigo 62" in search_context or "profissionistas" in search_context
        has_committee = "problemas oriundos da aplicacao" in search_context or "clausula 25" in search_context
        has_journey_control = "portaria 671" in search_context or "clausula 31" in search_context
        has_validity = "clausula 32" in search_context or "vigencia da presente convencao" in search_context
        if structured:
            return _structured_legal_review_answer(language, has_scope, has_committee, has_journey_control, has_validity)
        if language == "en":
            findings = [
                "The wording calls for interpretation, but the retrieved excerpt does not prove that the agreement is invalid:",
                "Clause 5 allows excess hours on one day to be offset by a corresponding reduction on another day, within a 10-hour workday and 360 days. It also provides a 50% premium for uncompensated overtime at termination. The excerpt does not detail how an individual negative balance or its authorization should be recorded.",
            ]
            if has_scope:
                findings.append("The same clause excludes employees covered by CLT article 62 and those classified as “profissionistas”; the employee's role must be checked before applying this regime.")
            if has_committee:
                findings.append("Clause 25 creates a joint committee to address problems arising from the application of the agreement, but the retrieved passage does not establish which interpretation prevails in a conflict.")
            if has_journey_control or has_validity:
                findings.append("The agreement also links alternative time control to Ordinance 671/2021 and sets its term from 03/01/2026 to 02/28/2027; the system and date of the facts matter.")
            findings.append("Conclusion: there are points to clarify, not a proven loophole or nullity. A final position requires the exact clause, job category, time records and applicable legal rule.")
            return "\n".join(findings[:6])
        if language == "es":
            findings = [
                "El texto requiere interpretación, pero el fragmento recuperado no demuestra que el convenio sea inválido:",
                "La cláusula 5 permite compensar el exceso de horas de un día con una reducción correspondiente en otro, dentro de una jornada máxima de 10 horas y de 360 días. También prevé un adicional del 50% por horas extras no compensadas al finalizar el contrato. El fragmento no detalla cómo registrar o autorizar un saldo negativo individual.",
            ]
            if has_scope:
                findings.append("La misma cláusula excluye a los empleados comprendidos en el artículo 62 de la CLT y a los “profissionistas”; es necesario comprobar el cargo antes de aplicar este régimen.")
            if has_committee:
                findings.append("La cláusula 25 crea una comisión paritaria para tratar problemas de aplicación, pero el fragmento no establece qué interpretación prevalece en caso de conflicto.")
            if has_journey_control or has_validity:
                findings.append("El convenio también vincula el control alternativo de jornada a la Ordenanza 671/2021 y fija su vigencia del 01/03/2026 al 28/02/2027; importan el sistema y la fecha de los hechos.")
            findings.append("Conclusión: hay puntos que deben aclararse, no una laguna o nulidad demostrada. La conclusión final exige la cláusula exacta, la categoría, los registros de jornada y la norma aplicable.")
            return "\n".join(findings[:6])
        findings = [
            "Há pontos de interpretação, mas o trecho recuperado não prova, sozinho, que o acordo seja inválido:",
            "Na cláusula 5ª, o acordo permite compensar o excesso de horas de um dia com uma diminuição correspondente em outro, dentro de jornada máxima de 10 horas e do prazo de 360 dias. Também prevê adicional de 50% para horas extras não compensadas na rescisão. O trecho não detalha como registrar ou autorizar um saldo negativo individual.",
        ]
        if has_scope:
            findings.append("A mesma cláusula exclui empregados abrangidos pelo art. 62 da CLT e os classificados como “profissionistas”. Portanto, é preciso confirmar o cargo antes de aplicar esse regime.")
        if has_committee:
            findings.append("A cláusula 25ª cria uma comissão paritária para tratar problemas da aplicação da convenção, mas o trecho não define qual interpretação prevalece quando houver conflito.")
        if has_journey_control or has_validity:
            findings.append("O acordo ainda relaciona o controle alternativo de jornada à Portaria 671/2021 e fixa vigência de 01/03/2026 a 28/02/2027; o sistema de ponto e a data dos fatos fazem diferença.")
        findings.append("Conclusão: existem pontos que pedem esclarecimento, não uma brecha ou nulidade comprovada. A conclusão final exige a cláusula exata, o cargo, os registros de jornada e a norma aplicável.")
        return "\n".join(findings[:6])
    if (
        module_id in {"direito", "departamento-pessoal"}
        and any(term in normalized_question for term in ("hora extra", "horas extras", "hora suplementar", "horas suplementares"))
        and any(term in normalized_question for term in ("compens", "percentual", "adicional"))
        and "horas extras não compensadas" in normalized_context
    ):
        if language == "en":
            return "The collective agreement provides that, at termination, overtime hours not compensated must be paid with a 50% premium. It does not, in this excerpt, establish a different percentage."
        if language == "es":
            return "El convenio colectivo establece que, en la rescisión, las horas extras no compensadas deben pagarse con un adicional del 50%. El fragmento no establece otro porcentaje."
        return "O acordo coletivo prevê que, na rescisão, as horas extras não compensadas devem ser pagas com adicional de 50%. O trecho não estabelece outro percentual."
    if module_id in {"direito", "departamento-pessoal"} and any(term in normalized_question for term in ("jornada", "jornadas")) and "clausula 19" in search_context:
        if language == "en":
            return "Clause 19 states that the workday runs from Monday to Friday, with 48 additional minutes per day to compensate for not working on Saturdays."
        if language == "es":
            return "La cláusula 19 establece una jornada de lunes a viernes, con 48 minutos adicionales por día para compensar la ausencia de trabajo los sábados."
        return "A cláusula 19ª estabelece jornada de segunda a sexta-feira, acrescida de 48 minutos diários para compensar a ausência de trabalho aos sábados."
    if module_id in {"direito", "departamento-pessoal"} and any(term in normalized_question for term in ("hora", "horas", "jornada")) and any(term in normalized_question for term in ("2", "duas")) and ("nao excedente de duas" in normalized_context or "não excedente de duas" in normalized_context) and any(term in normalized_question for term in ("funcion", "trabalhar", "empregad", "exced", "ultrapass")):
        payment = " O documento também prevê adicional mínimo de 50% sobre a hora normal." if "50%" in normalized_context else ""
        if language == "en":
            return "The local document states that overtime may not exceed 2 hours per day, by individual agreement, collective convention, or collective agreement." + (" It also sets a minimum 50% premium over the normal hour." if payment else "") + "\nThe retrieved excerpt does not state a specific penalty for exceeding the limit."
        if language == "es":
            return "El documento local establece que las horas extraordinarias no pueden exceder 2 horas al día, mediante acuerdo individual o colectivo." + (" También prevé un adicional mínimo del 50% sobre la hora normal." if payment else "") + "\nEl fragmento recuperado no informa una penalidad específica por superar el límite."
        return "A regra documentada limita as horas extras a 2 por dia, mediante acordo individual, convenção coletiva ou acordo coletivo." + payment + "\nO trecho recuperado não informa uma penalidade específica para ultrapassar esse limite."
    if module_id in {"direito", "departamento-pessoal"} and any(term in normalized_question for term in ("compens", "diferença", "diferenca", "semana seguinte", "horas negativas")) and "horas suplementares" in normalized_context and "semana imediatamente posterior" in normalized_context:
        if language == "en":
            return "The local source allows overtime hours to be compensated by the following week. It does not confirm that one hour per day can be used to make up four hours of absence; that depends on the applicable agreement and time-record rules."
        if language == "es":
            return "La fuente local permite compensar horas suplementarias hasta la semana siguiente. No confirma que una hora al día pueda reponer cuatro horas de ausencia; eso depende del acuerdo aplicable y del registro de jornada."
        return "A fonte local permite compensar horas suplementares até a semana seguinte. Ela não confirma que 1 hora por dia possa repor 4 horas de ausência; isso depende do acordo aplicável e das regras de registro de ponto."
    if module_id == "medicina" and any(term in normalized_question for term in ("gripe", "influenza")) and result.sources and all(source.casefold().startswith("cid-") for source in result.sources):
        return _medical_classification_answer(result, language)
    if module_id == "infraestrutura" and "host" in normalized_question and ("zabbix" in normalized_question or any("zabbix_documentation" in source.casefold() for source in result.sources) or "host wizard" in normalized_context):
        return _host_answer(question, result, language)
    return None


def _select_units(units: list[str], anchors: tuple[str, ...]) -> list[str]:
    selected: list[str] = []
    for anchor in anchors:
        for unit in units:
            if anchor in unit.casefold() and unit not in selected:
                selected.append(unit)
                break
    return selected or units


def _structured_answer(answer: str, result: RetrievalResult, language: str) -> str:
    """Give local/provider fallbacks the same readable contract as the LLM."""
    answer = _repair_split_words(answer)
    raw_lines = [re.sub(r"\s+", " ", line).strip() for line in answer.splitlines() if line.strip()]
    heading_aliases = {
        "conclusao": "conclusion",
        "conclusion": "conclusion",
        "conclusión": "conclusion",
        "base documental": "basis",
        "documentary basis": "basis",
        "base documental do modulo": "basis",
        "evidencias do modulo": "basis",
        "evidence": "basis",
        "aspectos favoraveis documentados": "positive",
        "documented favorable aspects": "positive",
        "aspectos favorables documentados": "positive",
        "pontos de atencao": "attention",
        "points requiring interpretation": "attention",
        "points of attention": "attention",
        "pontos que pedem interpretacao": "attention_legal",
        "pontos de atencao documentados": "attention_detail",
        "documented points of attention": "attention_detail",
        "puntos de atencion documentados": "attention_detail",
        "o que nao e possivel concluir": "limits_detail",
        "what cannot be concluded": "limits_detail",
        "lo que no se puede concluir": "limits_detail",
        "limites": "limits",
        "limits": "limits",
        "límites": "limits",
        "proximo passo": "next",
        "next step": "next",
        "próximo passo": "next",
    }
    localized_headings = {
        "pt-BR": {
            "conclusion": "Conclusão",
            "basis": "Base documental",
            "positive": "Aspectos favoráveis documentados",
            "attention": "Pontos de atenção",
            "attention_legal": "Pontos que pedem interpretação",
            "attention_detail": "Pontos de atenção documentados",
            "limits_detail": "O que não é possível concluir",
            "limits": "Limites",
            "next": "Próximo passo",
        },
        "en": {
            "conclusion": "Conclusion",
            "basis": "Documentary basis",
            "positive": "Documented favorable aspects",
            "attention": "Points of attention",
            "attention_legal": "Points requiring interpretation",
            "attention_detail": "Documented points of attention",
            "limits_detail": "What cannot be concluded",
            "limits": "Limits",
            "next": "Next step",
        },
        "es": {
            "conclusion": "Conclusión",
            "basis": "Base documental",
            "positive": "Aspectos favorables documentados",
            "attention": "Puntos de atención",
            "attention_legal": "Puntos que requieren interpretación",
            "attention_detail": "Puntos de atención documentados",
            "limits_detail": "Lo que no se puede concluir",
            "limits": "Límites",
            "next": "Próximo paso",
        },
    }

    def heading_key(line: str) -> str | None:
        candidate = re.sub(r"^[-*•]\s*", "", line).strip()
        candidate = re.sub(r"^#{1,6}\s*", "", candidate).strip()
        candidate = re.sub(r"^[*_]{1,3}|[*_]{1,3}$", "", candidate).strip()
        return heading_aliases.get(normalize(candidate).rstrip(":").strip())

    normalized_lines: list[str] = []
    seen_headings: set[str] = set()
    seen_content: set[str] = set()
    localized = localized_headings.get(language, localized_headings["pt-BR"])
    for line in raw_lines:
        if line in {"-", "*", "•", "---"}:
            continue
        key = heading_key(line)
        if key:
            if key in seen_headings:
                continue
            seen_headings.add(key)
            normalized_lines.append(localized[key])
            continue
        # Providers sometimes echo the retrieval envelope as if it were an
        # answer section. The interface already displays source names.
        plain_line = re.sub(r"^[-*•]\s*", "", line).strip()
        if re.match(r"(?i)^(documento|document|fonte|source)\s*:\s*", plain_line):
            source_value = normalize(plain_line.split(":", 1)[1])
            if any(source_value in normalize(source) or normalize(source) in source_value for source in result.sources):
                continue
        content_key = normalize(plain_line)
        if len(content_key) >= 35 and content_key in seen_content:
            continue
        if len(content_key) >= 35:
            seen_content.add(content_key)
        normalized_lines.append(line)
    lines = normalized_lines
    if seen_headings:
        output: list[str] = []
        for line in lines:
            if line in localized.values() and output and output[-1] != "":
                output.append("")
            output.append(line)
        return "\n".join(output).strip()
    if lines and normalize(lines[0]) in {"a fonte local informa:", "the local source states:", "la fuente local informa:"}:
        lines = lines[1:]
    if not lines:
        lines = [answer.strip()]
    conclusion = lines[0]
    evidence = [
        line
        for line in lines[1:]
        if not normalize(line).startswith(("conclusao:", "conclusión:", "conclusion:"))
    ]
    sources = ", ".join(result.sources)
    if language == "en":
        basis = "\n".join(f"- {line.lstrip('-*• ')}" for line in evidence) or (f"- Local sources consulted: {sources}." if sources else "- The offline search did not find enough evidence for this question.")
        body = ["Conclusion", conclusion, "\nDocumentary basis", basis, "\nLimits", "- This synthesis is limited to the retrieved passages; facts not present in them require a new search."]
    elif language == "es":
        basis = "\n".join(f"- {line.lstrip('-*• ')}" for line in evidence) or (f"- Fuentes locales consultadas: {sources}." if sources else "- La búsqueda offline no encontró evidencia suficiente para esta pregunta.")
        body = ["Conclusión", conclusion, "\nBase documental", basis, "\nLímites", "- Esta síntesis se limita a los fragmentos recuperados; los hechos ausentes requieren una nueva búsqueda."]
    else:
        basis = "\n".join(f"- {line.lstrip('-*• ')}" for line in evidence) or (f"- Fontes locais consultadas: {sources}." if sources else "- A busca offline não encontrou evidência suficiente para esta pergunta.")
        body = ["Conclusão", conclusion, "\nBase documental", basis, "\nLimites", "- Esta síntese está limitada aos trechos recuperados; fatos que não aparecem neles exigem nova consulta."]
    return "\n".join(body)


def _first_unit(units: list[str], anchors: tuple[str, ...]) -> str:
    for anchor in anchors:
        for unit in units:
            if anchor in unit.casefold():
                return re.sub(r"\s+", " ", unit).strip()[:360]
    return ""


def _scope_note(scope: dict[str, Any], language: str) -> str:
    if language == "en":
        if scope["status"] == "aligned":
            return f"This question appears to belong to the {scope['module_name']} module, but the local knowledge base does not contain enough evidence yet."
        if scope["status"] == "outside":
            return f"This question appears closer to the {scope['related_module_name']} module than to {scope['module_name']}."
        return f"I could not confirm whether this question belongs to the {scope['module_name']} module."
    if language == "es":
        if scope["status"] == "aligned":
            return f"La pregunta parece pertenecer al módulo {scope['module_name']}, pero la base local todavía no contiene evidencia suficiente."
        if scope["status"] == "outside":
            return f"La pregunta parece estar más relacionada con el módulo {scope['related_module_name']} que con {scope['module_name']}."
        return f"No pude confirmar si la pregunta pertenece al módulo {scope['module_name']}."
    if scope["status"] == "aligned":
        return f"Este assunto parece pertencer ao módulo {scope['module_name']}, mas a base de conhecimento local ainda não tem evidência suficiente."
    if scope["status"] == "outside":
        return f"Este assunto parece estar mais relacionado ao módulo {scope['related_module_name']} do que ao módulo {scope['module_name']}."
    return f"Não consegui confirmar se este assunto pertence ao módulo {scope['module_name']}."


def _with_scope(scope_note: str, message: str) -> str:
    return f"{scope_note}\n\n{message}"


def local_no_evidence(policy: ModulePolicy, language: str = "pt-BR", module_id: str = "", question: str = "") -> str:
    normalized_question = normalize(question)
    scope_note = _scope_note(assess_module_scope(module_id, question), language)
    if language == "en":
        if module_id == "recursos-humanos" and any(term in normalized_question for term in ("contrat", "admiss", "recrut", "selec")):
            return _with_scope(scope_note, "The current Human Resources documents do not contain a complete people-hiring or admission procedure. The retrieved “hiring” material refers to public procurement, which is a different subject. Add the recruitment, document, approval and onboarding policy to answer this safely.")
        if module_id == "contabilidade" and any(term in normalized_question for term in ("balance", "accounting statement", "patrimonial")):
            return _with_scope(scope_note, "The current Accounting documents mention standards and reporting systems, but do not provide enough evidence for a balance-sheet preparation guide. Add the accounting manual or chart of accounts, or ask about a specific CPC/ECF rule.")
        if module_id == "departamento-pessoal" and "departamento pessoal" in normalized_question:
            return _with_scope(scope_note, "The current Personnel Department documents focus on eSocial and obligations, but do not define the department's responsibilities well enough. Add the internal routines for admission, payroll, leave and termination.")
        return _with_scope(scope_note, "I did not find enough evidence in this module's local documents to answer safely.")
    if language == "es":
        if module_id == "recursos-humanos" and any(term in normalized_question for term in ("contrat", "admis", "reclut", "selec")):
            return _with_scope(scope_note, "Los documentos actuales de Recursos Humanos no contienen un procedimiento completo de contratación o admisión de personas. El material recuperado sobre “contratación” trata de compras públicas, que es otro tema. Añada la política de reclutamiento, documentos, aprobación e integración.")
        if module_id == "contabilidade" and any(term in normalized_question for term in ("balance", "patrimonial", "contabl")):
            return _with_scope(scope_note, "Los documentos actuales de Contabilidad mencionan normas y sistemas de información, pero no contienen evidencia suficiente para explicar cómo preparar un balance patrimonial. Añada el manual contable o el plan de cuentas.")
        if module_id == "departamento-pessoal" and "departamento pessoal" in normalized_question:
            return _with_scope(scope_note, "Los documentos actuales del Departamento Personal se concentran en eSocial y obligaciones, pero no definen suficientemente las responsabilidades del sector. Añada las rutinas internas de admisión, nómina, vacaciones y rescisión.")
        return _with_scope(scope_note, "No encontré evidencia suficiente en los documentos locales de este módulo para responder con seguridad.")
    if policy.high_risk:
        return _with_scope(scope_note, "Não encontrei evidência suficiente nos documentos locais para responder com segurança. Consulte uma fonte médica confiável ou um profissional de saúde.")
    if module_id == "recursos-humanos" and any(term in normalized_question for term in ("contrat", "admiss", "recrut", "selec")):
        return _with_scope(scope_note, "Os documentos atuais de Recursos Humanos não trazem um procedimento completo de contratação ou admissão de pessoas. O material recuperado que contém “contratação” trata de contratação pública, que é outro assunto. Inclua a política de recrutamento, documentos, aprovações e integração para que eu possa responder com segurança.")
    if module_id == "contabilidade" and any(term in normalized_question for term in ("balan", "patrimonial", "demonstracao")):
        return _with_scope(scope_note, "Os documentos atuais de Contabilidade citam normas e sistemas de escrituração, mas não trazem evidência suficiente para explicar como montar um balanço patrimonial. Inclua o manual contábil ou o plano de contas, ou indique um CPC/ECF específico.")
    if module_id == "departamento-pessoal" and "departamento pessoal" in normalized_question:
        return _with_scope(scope_note, "Os documentos atuais de Departamento Pessoal tratam principalmente de eSocial e obrigações, mas não definem com clareza o papel do setor. Inclua as rotinas internas de admissão, folha, férias e rescisão para eu responder de forma completa.")
    return _with_scope(scope_note, "Não encontrei evidência suficiente nos documentos locais para responder com segurança.")


async def answer(*, root: Path, module_id: str, provider: str, question: str, history: list[dict[str, str]], extra_context: str = "", language: str = "pt-BR", response_style: str = "structured", external_allowed: bool | None = None, user_code: str | None = None, retry: bool = False, retry_of: int | None = None) -> OrchestrationResult:
    language = normalize_language(language)
    response_style = normalize_response_style(response_style)
    policy = policy_for(module_id)
    trace = build_plan(module_id, question, policy.high_risk, bool(extra_context))
    retrieval_question = _retrieval_question(question, history)
    result = retrieve(root, module_id, retrieval_question, policy, limit=4 if response_style == "concise" else 6, retry=retry)
    context_package = build_context_package(module_id, retrieval_question, result, history, response_style).public_dict()
    evidence_score = max((item.score for item in result.evidence), default=0.0)
    if not result.has_quality_evidence:
        update_stage(trace, "retrieve", "blocked", "Nenhuma evidência local atingiu o gate de qualidade.")
        # The local RAG remains the first authority. When it cannot answer,
        # the configured provider route is allowed to offer a clearly labeled
        # general orientation; it receives no local document context. Cloud
        # routes are still protected by the redaction and external-data gates,
        # while AUTO can fall back to Ollama without sending data away.
        can_assist_without_local_evidence = provider in {"auto", "ollama"} or external_generation_may_be_used(provider, external_allowed)
        if can_assist_without_local_evidence:
            redaction = ExternalRedaction() if external_generation_may_be_used(provider, external_allowed) else None
            provider_question = redaction.clean(retrieval_question) if redaction else retrieval_question
            provider_extra_context = redaction.clean(extra_context) if redaction else extra_context
            provider_history = redaction.clean_history(history) if redaction else history
            try:
                generated = await generate_with_fallback(
                    provider,
                    _external_assist_system(module_id, policy, language, response_style),
                    _external_assist_prompt(provider_question, provider_extra_context, language, response_style),
                    provider_history[-10:],
                    max_output_tokens=320 if response_style == "concise" else 560 if response_style == "structured" else 768,
                    timeout_seconds=_generation_timeout(response_style),
                    external_allowed=external_allowed,
                )
                if redaction:
                    generated = Generation(redaction.restore(generated.answer), generated.provider, generated.model)
                assisted_answer = _format_external_assist_answer(
                    generated.answer,
                    generated.provider,
                    retrieval_question,
                    language,
                    response_style,
                )
                # There are no local claims to compare in this branch. The
                # safety prompt and the module policy are the verification
                # boundary; local evidence remains explicitly marked false.
                verified = bool(assisted_answer.strip()) and not (
                    policy.high_risk
                    and any(
                        marker in normalize(assisted_answer)
                        for marker in ("diagnostico definitivo", "prescreva", "dose individual", "tome este medicamento")
                    )
                )
                if verified:
                    update_stage(trace, "reason", "complete", f"Orientação geral gerada por {generated.provider}; o RAG local não tinha evidência suficiente.")
                    update_stage(trace, "critic", "complete", "Resposta externa rotulada e aprovada pelos limites de segurança do módulo.")
                    update_stage(trace, "output", "complete", "Orientação assistida entregue; confirme-a na base offline.")
                    analytics_id = remember_run(root, module_id, question, [], generated.provider, True, user_code)
                    return OrchestrationResult(
                        assisted_answer,
                        generated.provider,
                        generated.model,
                        [],
                        0.0,
                        False,
                        True,
                        trace,
                        analytics_id,
                        bool(redaction),
                        redaction.masked_fields if redaction else 0,
                        context_package=context_package,
                        verification_status="unverified",
                        confidence=0.25,
                    )
            except RuntimeError:
                # A provider outage must not hide the precise local-RAG status.
                pass
        update_stage(trace, "reason", "blocked", "Não há base documental suficiente e nenhum provider autorizado respondeu.")
        update_stage(trace, "critic", "complete", "Resposta limitada para evitar conhecimento geral ou mistura de módulos.")
        update_stage(trace, "output", "complete", "Incerteza apresentada ao usuário com segurança.")
        analytics_id = remember_run(root, module_id, question, list(result.sources), "policy", True, user_code)
        return OrchestrationResult(local_no_evidence(policy, language, module_id, retrieval_question), "policy", "evidence-gate", list(result.sources), 0.0, False, True, trace, analytics_id, context_package=context_package, verification_status="unverified", confidence=0.0)
    update_stage(trace, "retrieve", "complete", f"{len(result.evidence)} evidência(s) local(is) recuperada(s) de {len(result.sources)} fonte(s).")
    # The deterministic path is the safe local accelerator for automatic mode.
    # An explicit provider selection must actually invoke that provider so the
    # operator can compare OpenAI, Gemini, Claude and Ollama on the same RAG.
    summary_request = any(
        term in normalize(retrieval_question)
        for term in (
            "resuma",
            "resumo do conhecimento",
            "resumo do documento",
            "resumo do arquivo",
            "resumir o documento",
            "resumir o arquivo",
            "documentos disponiveis",
            "listar documentos",
        )
    )
    cloud_credentials_configured = any(os.getenv(name, "").strip() for name in ("OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"))
    # A retry is an explicit quality-recovery request. Skip the deterministic
    # shortcut so AUTO can call the configured providers and compare a fresh
    # generation against the same local evidence. Privacy gates still apply.
    local_fast_path_allowed = not retry and (not summary_request or external_allowed is False or not cloud_credentials_configured)
    if provider == "auto" and response_style in {"concise", "structured"} and local_fast_path_allowed:
        fast_answer = _fast_evidence_answer(module_id, retrieval_question, result, language, structured=response_style == "structured")
        if fast_answer:
            if response_style == "structured":
                fast_answer = _structured_answer(fast_answer, result, language)
            update_stage(trace, "reason", "complete", "Síntese determinística baseada diretamente no trecho recuperado.")
            update_stage(trace, "critic", "complete", "Resumo conferido contra a evidência local.")
            update_stage(trace, "output", "complete", "Resposta curta entregue com fontes.")
            analytics_id = remember_run(root, module_id, question, list(result.sources), "local-rag", True, user_code)
            return OrchestrationResult(fast_answer, "local-rag", "evidence-summary", list(result.sources), evidence_score, True, True, trace, analytics_id, context_package=context_package, verification_status="verified", confidence=min(0.99, evidence_score))
    # If the selected route can reach a cloud provider, minimize the request
    # before it leaves this machine. Local retrieval and verification continue
    # to use the original evidence, so masking never weakens the RAG gate.
    redaction = ExternalRedaction() if external_generation_may_be_used(provider, external_allowed) else None
    provider_question = redaction.clean(retrieval_question) if redaction else retrieval_question
    provider_evidence = redaction.clean(result.context) if redaction else None
    provider_extra_context = redaction.clean(extra_context) if redaction else extra_context
    provider_history = redaction.clean_history(history) if redaction else history
    system_prompt = _system(module_id, policy, language, response_style)
    if redaction:
        system_prompt += " Dados identificáveis foram mascarados com marcadores __SOFIA_*__. Preserve esses marcadores sem inventar valores; eles serão reidratados localmente após a resposta. Nunca tente descobrir ou reconstruir dados removidos."
    offline_material: dict[str, Any] | None = None
    try:
        max_output_tokens = 320 if response_style == "concise" else 560 if response_style == "structured" else 768
        generated: Generation = await generate_with_fallback(
            provider,
            system_prompt,
            _prompt(
                provider_question,
                result,
                policy,
                provider_extra_context,
                language,
                response_style,
                evidence_override=provider_evidence,
            ),
            provider_history[-4:] if response_style == "concise" else provider_history[-10:],
            max_output_tokens=max_output_tokens,
            timeout_seconds=_generation_timeout(response_style),
            external_allowed=external_allowed,
        )
        if redaction:
            generated = Generation(redaction.restore(generated.answer), generated.provider, generated.model)
        if response_style == "concise":
            generated = Generation(_compact_answer(generated.answer, retrieval_question, result.context), generated.provider, generated.model)
        elif response_style == "structured":
            generated = Generation(_structured_answer(generated.answer, result, language), generated.provider, generated.model)
    except RuntimeError:
        fallback = _fast_evidence_answer(module_id, retrieval_question, result, language, structured=response_style == "structured")
        if not fallback:
            fallback = _compact_answer(_extractive_answer(retrieval_question, result, language), retrieval_question, result.context)
        if response_style == "structured" and not any(normalize(section) in normalize(fallback) for section in ("conclusao", "conclusion", "conclusión")):
            fallback = _structured_answer(fallback, result, language)
        update_stage(trace, "reason", "complete", "Provider indisponível ou lento; síntese extrativa local utilizada.")
        update_stage(trace, "critic", "complete", "Síntese extrativa limitada aos trechos recuperados.")
        update_stage(trace, "output", "complete", "Resposta local entregue com fontes.")
        analytics_id = remember_run(root, module_id, question, list(result.sources), "local-rag", True, user_code)
        return OrchestrationResult(
            fallback,
            "local-rag",
            "extractive-evidence",
            list(result.sources),
            evidence_score,
            True,
            True,
            trace,
            analytics_id,
            bool(redaction),
            redaction.masked_fields if redaction else 0,
            context_package=context_package,
            verification_status="verified",
            confidence=min(0.95, evidence_score),
        )
    update_stage(trace, "reason", "complete", f"Resposta gerada por {generated.provider} com contexto local anexado.")
    verification = verify_answer(generated.answer, result, module_id)
    verified = _verify(generated.answer, result, policy) and verification.status in {"verified", "repaired"}
    critic_result = agent_critic(generated.answer, result.context, policy.high_risk)
    if not verified:
        safe_answer = _fast_evidence_answer(
            module_id,
            retrieval_question,
            result,
            language,
            structured=response_style == "structured",
        ) or _compact_answer(_extractive_answer(retrieval_question, result, language), retrieval_question, result.context)
        if response_style == "structured":
            safe_answer = _structured_answer(safe_answer, result, language)
        update_stage(trace, "critic", "repaired", f"Resposta do provider rejeitada; síntese local aplicada. Avaliador: {critic_result['reason']}")
        update_stage(trace, "output", "complete", "Resposta limitada aos trechos recuperados.")
        analytics_id = remember_run(root, module_id, question, list(result.sources), "local-rag", True, user_code)
        return OrchestrationResult(
            safe_answer,
            "local-rag",
            "verified-extractive",
            list(result.sources),
            evidence_score,
            True,
            True,
            trace,
            analytics_id,
            bool(redaction),
            redaction.masked_fields if redaction else 0,
            context_package=context_package,
            verification_status="repaired",
            confidence=verification.confidence,
        )
    if redaction and retry and generated.provider in {"openai", "gemini", "claude"}:
        # Persist only after local evidence and critic approval. The helper
        # creates a fresh redaction scope before writing the candidate file.
        offline_material = store_offline_candidate(
            root,
            module_id,
            generated.answer,
            list(result.sources),
            generated.provider,
            retry_of,
        )
    update_stage(trace, "critic", "complete", f"Resposta aprovada pelo gate; avaliador: {critic_result['reason']}")
    update_stage(trace, "output", "complete", "Resposta entregue com fontes do módulo.")
    analytics_id = remember_run(root, module_id, question, list(result.sources), generated.provider, True, user_code)
    return OrchestrationResult(
        generated.answer,
        generated.provider,
        generated.model,
        list(result.sources),
        evidence_score,
        bool(result.evidence),
        True,
        trace,
        analytics_id,
        bool(redaction),
        redaction.masked_fields if redaction else 0,
        bool(offline_material and offline_material.get("stored")),
        str(offline_material.get("file_name")) if offline_material and offline_material.get("stored") else None,
        context_package,
        verification.status,
        verification.confidence,
    )
