from __future__ import annotations

import re
import unicodedata
from typing import Any

from .domains import DOMAIN_CONTRACTS


def normalize(text: str) -> str:
    """Normalize accents and case for intent matching without changing evidence."""
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text.casefold())
        if not unicodedata.combining(char)
    )


SLEEP_MARKERS = (
    "piscada de sono",
    "piscadas de sono",
    "microssono",
    "micro sono",
    "sono durante o dia",
    "sonolencia diurna",
    "sonolencia durante o dia",
    "dormir pouco",
    "dormindo pouco",
    "sono insuficiente",
    "adormecer durante o dia",
    "ataque de sono",
    "trechos de sono",
)


def is_medical_sleep_query(question: str) -> bool:
    normalized = normalize(question)
    return any(marker in normalized for marker in SLEEP_MARKERS) or (
        any(term in normalized for term in ("sonolencia", "sono", "dormir", "adormecer"))
        and any(term in normalized for term in ("dia", "horas", "irritacao", "irritabilidade", "segundos", "5 horas"))
    )


MODULE_NAMES = {module_id: contract.name for module_id, contract in DOMAIN_CONTRACTS.items()}
MODULE_SCOPE_TERMS = {
    module_id: contract.keywords for module_id, contract in DOMAIN_CONTRACTS.items()
}

GENERIC_ANALYSIS_TERMS = (
    "resumo",
    "resuma",
    "conteudo",
    "conteúdo",
    "ponto",
    "pontos",
    "positivo",
    "positivos",
    "negativo",
    "negativos",
    "aspecto",
    "aspectos",
    "abordad",
    "analise",
    "análise",
    "vantagem",
    "desvantagem",
)


DIRECT_CONVERSATION_MARKERS = (
    "oi",
    "ola",
    "olá",
    "bom dia",
    "boa tarde",
    "boa noite",
    "obrigado",
    "obrigada",
    "quem e voce",
    "quem é você",
    "como voce pode ajudar",
    "como você pode ajudar",
)

DIRECT_WRITING_MARKERS = (
    "escreva",
    "redija",
    "reescreva",
    "reformule",
    "melhore este texto",
    "melhore esse texto",
    "corrija este texto",
    "corrija esse texto",
    "crie um email",
    "crie um e-mail",
    "escreva um email",
    "escreva um e-mail",
    "crie uma mensagem",
    "escreva uma mensagem",
    "traduza",
)

EVIDENCE_REQUEST_MARKERS = (
    "arquivo",
    "documento",
    "documentos",
    "fonte",
    "fontes",
    "link",
    "links",
    "base local",
    "base de conhecimento",
    "segundo",
    "conforme",
    "de acordo com",
    "no acordo",
    "na lei",
    "no contrato",
    "na imagem",
    "no csv",
    "no xlsx",
    "compare",
    "comparar",
    "jurisprudencia",
    "jurisprudência",
    "resuma",
    "resumo",
    "listar documentos",
    "o que temos sobre",
    "o que diz",
    "o que consta",
    "o que estabelece",
    "acordo coletivo",
    "convencao coletiva",
    "convenção coletiva",
    "vade mecum",
    "saae",
    "jurisprudencia",
    "jurisprudência",
    "prazo",
    "artigo",
    "clausula",
    "cláusula",
    "mandado de seguranca",
    "mandado de segurança",
    "enap",
    "escola virtual",
    "csv",
    "xlsx",
    "planilha",
    "tabela",
)

OPEN_CONVERSATION_MARKERS = (
    "me ajuda",
    "pode me ajudar",
    "preciso de ajuda",
    "tenho um problema",
    "estou com um problema",
    "posso te explicar",
    "posso explicar",
    "quero te explicar",
    "quero te contar",
    "vou te contar",
    "o que voce acha",
    "o que você acha",
    "me orienta",
    "preciso conversar",
    "posso falar",
    "tenho uma situacao",
    "tenho uma situação",
)

GENERAL_EXPLANATION_MARKERS = (
    "o que e ",
    "o que é ",
    "qual a diferenca",
    "qual é a diferença",
    "explique ",
    "me explique ",
    "como funciona",
    "fale sobre ",
    "defina ",
    "o que significa ",
    "por que ",
    "porque ",
    "como ",
)

PROCEDURE_MARKERS = (
    "como criar",
    "como configurar",
    "como definir",
    "como que defino",
    "como que configuro",
    "como que crio",
    "como faço para",
    "como faco para",
    "como organizar",
    "como vejo",
    "como identificar",
    "como acompanhar",
    "como analisar",
    "como medir",
    "como adicionar",
    "como cadastrar",
    "como executar",
    "qual o procedimento",
    "passo a passo",
)

TOOL_ACTION_MARKERS = (
    "execute ",
    "executar ",
    "reinicie ",
    "reiniciar ",
    "altere ",
    "alterar ",
    "aplique ",
    "aplicar ",
    "sincronize ",
    "sincronizar ",
)

STRUCTURED_MARKERS = (
    "quantos",
    "quantas",
    "soma",
    "media",
    "média",
    "total",
    "conte",
    "contagem",
    "csv",
    "xlsx",
    "planilha",
    "tabela",
)

COMPLEX_REASONING_MARKERS = (
    "infer",
    "correlac",
    "padrao",
    "padrão",
    "causal",
    "relacione",
    "relacionar",
    "recomende",
    "recomendação",
    "cenário",
    "cenario",
    "prejuiz",
)


def _route_payload(
    route: str,
    task_route: str,
    retrieval_required: bool,
    response_mode: str,
    reason: str,
) -> dict[str, Any]:
    """Return the public route contract with a stable legacy alias.

    ``route`` remains compatible with the existing orchestration stages;
    ``task_route`` is the stricter task taxonomy used by the new router and
    observability.  Keeping both avoids breaking old clients while making it
    impossible to confuse a conversational task with document retrieval.
    """
    return {
        "route": route,
        "task_route": task_route,
        "retrieval_required": retrieval_required,
        "response_mode": response_mode,
        "reason": reason,
    }


def _has_explicit_evidence_request(compact: str) -> bool:
    return any(marker in compact for marker in EVIDENCE_REQUEST_MARKERS)


def _has_conversation_follow_up(history: list[dict[str, str]] | None) -> bool:
    if not history:
        return False
    for item in reversed(history[-6:]):
        if item.get("role") != "assistant":
            continue
        text = normalize(str(item.get("content", "")))
        if any(
            marker in text
            for marker in (
                "me conte",
                "o que aconteceu",
                "qual situacao",
                "qual situação",
                "pode explicar",
                "conte mais",
                "como posso ajudar",
            )
        ):
            return True
        break
    return False


def recent_documentary_answer(history: list[dict[str, str]] | None) -> str:
    """Return the latest bounded assistant answer that carries local evidence."""

    for item in reversed((history or [])[-8:]):
        if item.get("role") != "assistant":
            continue
        content = str(item.get("content", "")).strip()
        normalized = normalize(content)
        if any(marker in normalized for marker in ("fontes e trechos", "base documental", "fato documentado", "documento local")):
            return content[:2200]
    return ""


def recent_documentary_question(history: list[dict[str, str]] | None) -> str:
    """Return the user question that produced the latest local evidence."""

    items = list((history or [])[-8:])
    for index in range(len(items) - 1, -1, -1):
        item = items[index]
        if item.get("role") != "assistant":
            continue
        content = str(item.get("content", ""))
        if not any(marker in normalize(content) for marker in ("fontes e trechos", "base documental", "fato documentado", "documento local")):
            continue
        for previous in reversed(items[:index]):
            if previous.get("role") == "user" and str(previous.get("content", "")).strip():
                return str(previous["content"]).strip()[:1600]
    return ""


def _has_contextual_evidence_follow_up(question: str, history: list[dict[str, str]] | None) -> bool:
    """Recognize a follow-up that resumes a documented topic.

    A greeting such as ``me ajuda`` must stay conversational.  Once the prior
    turn contains a verified local answer, a substantive overlap such as
    ``indisponibilidade`` means the user is asking to continue that evidence
    thread, even when they do not repeat ``documento`` or ``fonte``.
    """

    previous = recent_documentary_answer(history)
    if not previous:
        return False
    normalized = normalize(question)
    if any(marker in normalized for marker in ("bom dia", "boa tarde", "boa noite", "obrigado", "obrigada")) and len(normalized.split()) <= 8:
        return False
    stopwords = {
        "ajuda", "ajudar", "quero", "saber", "pode", "podemos", "falar", "fala", "dizer", "diga", "mais",
        "sobre", "isso", "esse", "essa", "aquela", "aquele", "sim", "por", "favor", "vc", "voce", "você",
    }
    question_terms = {term for term in re.findall(r"[\w]+", normalized) if len(term) >= 6 and term not in stopwords}
    previous_terms = set(re.findall(r"[\w]+", normalize(previous)))
    return any(
        question_term == previous_term
        or (
            len(question_term) >= 7
            and len(previous_term) >= 7
            and question_term[:7] == previous_term[:7]
        )
        for question_term in question_terms
        for previous_term in previous_terms
    )


def route_query(
    module_id: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Choose the smallest safe intelligence route for a user request.

    Open-ended help requests are conversational by default.  They only enter
    RAG after the user names a source, asks for a documented rule, requests a
    structured calculation, or supplies enough specificity for an evidence
    task.  ``history`` is deliberately limited to the current session and is
    used only to recognize a conversational follow-up.
    """

    normalized_module = normalize(module_id)
    normalized = normalize(question).strip()
    compact = re.sub(r"[!?.,;:]+", " ", normalized)
    compact = re.sub(r"\s+", " ", compact).strip()
    words = compact.split()
    explicit_evidence = _has_explicit_evidence_request(compact)
    open_conversation = any(marker in compact for marker in OPEN_CONVERSATION_MARKERS)
    conversation_follow_up = _has_conversation_follow_up(history)
    contextual_evidence_follow_up = _has_contextual_evidence_follow_up(compact, history)

    if (open_conversation or conversation_follow_up) and not explicit_evidence and not contextual_evidence_follow_up:
        return _route_payload(
            "conversation",
            "conversation",
            False,
            "conversational",
            "pedido aberto ou continuação de conversa sem exigência de evidência interna",
        )

    if contextual_evidence_follow_up and not explicit_evidence:
        return _route_payload(
            "evidence",
            "document_rag",
            True,
            "evidence",
            "continuação de um tema documental já confirmado na sessão",
        )

    if (
        any(compact == marker or compact.startswith(f"{marker} ") for marker in DIRECT_CONVERSATION_MARKERS)
        or (len(words) <= 5 and any(compact.startswith(marker) for marker in ("oi ", "ola ", "olá ")))
    ):
        return _route_payload(
            "conversation",
            "conversation",
            False,
            "conversational",
            "saudação ou conversa sem pedido de evidência interna",
        )

    if any(marker in compact for marker in DIRECT_WRITING_MARKERS) and not explicit_evidence:
        return _route_payload(
            "writing",
            "writing",
            False,
            "conversational",
            "tarefa de escrita sem exigência explícita de fonte interna",
        )

    if any(marker in compact for marker in TOOL_ACTION_MARKERS) and not any(
        marker in compact for marker in ("como ", "o que ", "qual ")
    ):
        return _route_payload(
            "tool",
            "tool_action",
            True,
            "evidence",
            "pedido de ação: validar ferramenta, permissão e evidência antes de executar",
        )

    multi_document = any(
        marker in compact
        for marker in (
            "compare",
            "comparar",
            "comparando",
            "diferenca entre",
            "confronte",
            "cruze os",
            "relacione os documentos",
            "entre os documentos",
        )
    )
    # Match structured operators as words.  A substring check made ``conte``
    # classify ordinary words such as ``conteúdo`` as a table query, which
    # sent explicit document-line requests through the wrong task contract.
    structured = any(re.search(rf"\b{re.escape(marker)}\b", compact) for marker in STRUCTURED_MARKERS)
    complex_reasoning = any(marker in compact for marker in COMPLEX_REASONING_MARKERS)
    if explicit_evidence or multi_document or structured or complex_reasoning:
        if multi_document:
            return _route_payload(
                "evidence",
                "multi_document",
                True,
                "evidence",
                "a pergunta exige recuperação e cobertura de mais de uma fonte",
            )
        if structured:
            return _route_payload(
                "evidence",
                "structured_data",
                True,
                "evidence",
                "a pergunta pode exigir leitura integral e cálculo em dados estruturados",
            )
        if complex_reasoning:
            return _route_payload(
                "evidence",
                "complex_reasoning",
                True,
                "evidence",
                "a pergunta exige premissas documentais para inferência ou relação",
            )
        return _route_payload(
            "evidence",
            "document_rag",
            True,
            "evidence",
            "a pergunta referencia conhecimento, documento ou fonte verificável",
        )

    if any(marker in compact for marker in GENERAL_EXPLANATION_MARKERS):
        # Legal and clinical explanations remain local-first because their
        # safety policy requires a source even when the user does not name it.
        protected_module = normalized_module in {"medicina", "direito", "departamento pessoal", "departamento-pessoal"}
        procedure = any(marker in compact for marker in PROCEDURE_MARKERS)
        retrieval_required = protected_module or procedure
        return _route_payload(
            "explanation",
            "general_explanation",
            retrieval_required,
            "evidence" if retrieval_required else "conversational",
            "explicação geral; consultar documentos apenas quando o domínio ou o procedimento exigir evidência",
        )

    # A short, underspecified domain sentence is a conversation opener rather
    # than permission to scan every document in the module.
    if len(words) <= 12 and not explicit_evidence and normalized_module not in {"medicina", "direito", "departamento pessoal", "departamento-pessoal"}:
        return _route_payload(
            "conversation",
            "conversation",
            False,
            "conversational",
            "pedido ainda não especifica uma tarefa ou fonte; solicitar contexto antes de consultar o módulo",
        )

    return _route_payload(
        "explanation",
        "general_explanation",
        normalized_module in {"medicina", "direito", "departamento pessoal", "departamento-pessoal"},
        "evidence" if normalized_module in {"medicina", "direito", "departamento pessoal", "departamento-pessoal"} else "conversational",
        "explicação de domínio sem marcador documental explícito",
    )


def build_conversation_memory(
    module_id: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build bounded, session-scoped memory for the response composer.

    This is not a long-term content store. It exposes only the recent turns,
    a lightweight topic/intent label, detected source/entity hints and the
    assistant's pending question, so a follow-up can remain coherent without
    forcing retrieval or persisting sensitive conversation text.
    """
    turns = [
        {"role": str(item.get("role", "")), "content": str(item.get("content", ""))[:4000]}
        for item in (history or [])[-8:]
        if item.get("role") in {"user", "assistant"} and str(item.get("content", "")).strip()
    ]
    combined = " ".join(item["content"] for item in turns + [{"role": "user", "content": question}])
    normalized = normalize(combined)
    route = route_query(module_id, question, history=[])
    entity_patterns = (
        r"\b[\wÀ-ÿ-]+\.(?:pdf|docx|xlsx|csv|xml|txt)\b",
        r"\b(?:SAAE|Zabbix|FHIR|HL7|CLT|STJ|STF)\b",
    )
    entities: list[str] = []
    for pattern in entity_patterns:
        for match in re.findall(pattern, combined, flags=re.IGNORECASE):
            value = str(match)
            if value.casefold() not in {item.casefold() for item in entities}:
                entities.append(value)
    pending_question = ""
    for item in reversed(turns):
        if item["role"] == "assistant" and "?" in item["content"]:
            pending_question = item["content"].strip()[:500]
            break
    topic_terms = [
        term
        for term in re.findall(r"[\wÀ-ÿ]{4,}", normalize(question))
        if term not in {"para", "sobre", "como", "qual", "esse", "esta", "problema", "ajuda"}
    ]
    return {
        "topic": " ".join(dict.fromkeys(topic_terms[:8])) or normalize(module_id),
        "intent": route.get("task_route", route.get("route", "conversation")),
        "entities": entities[:12],
        "context_recent": turns[-6:],
        "pending_question": pending_question,
        "module": module_id,
        "has_context": bool(turns),
        "context_terms": sorted(set(re.findall(r"[\wÀ-ÿ]{5,}", normalized)))[:24],
    }


def _with_route(
    profile: dict[str, Any],
    module_id: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    enriched = dict(profile)
    enriched.update(route_query(module_id, question, history=history))
    return enriched


def assess_module_scope(module_id: str, question: str) -> dict[str, Any]:
    """Explain whether a question appears aligned with the active module."""
    normalized = normalize(question)
    scores: dict[str, tuple[int, list[str]]] = {}
    for candidate, terms in MODULE_SCOPE_TERMS.items():
        matched = [term for term in terms if normalize(term) in normalized]
        if matched:
            scores[candidate] = (len(matched), matched[:4])
    current_score, current_terms = scores.get(module_id, (0, []))
    other_scores = [(score, candidate, terms) for candidate, (score, terms) in scores.items() if candidate != module_id]
    other_scores.sort(reverse=True)
    best_other = other_scores[0] if other_scores else (0, "", [])
    if current_score > 0 and current_score >= best_other[0]:
        status = "aligned"
        confidence = "high" if current_score >= 2 else "medium"
        related_module = module_id
    elif best_other[0] > 0 and not (
        best_other[0] == 1 and any(term in normalized for term in GENERIC_ANALYSIS_TERMS)
    ):
        status = "outside"
        confidence = "medium"
        related_module = best_other[1]
        current_terms = best_other[2]
    else:
        status = "uncertain"
        confidence = "low"
        related_module = module_id
    return {
        "status": status,
        "confidence": confidence,
        "module_id": module_id,
        "module_name": MODULE_NAMES.get(module_id, module_id),
        "related_module_id": related_module,
        "related_module_name": MODULE_NAMES.get(related_module, related_module),
        "matched_terms": current_terms,
    }


def classify_query(
    module_id: str,
    question: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Return a privacy-safe semantic label used by retrieval and analytics.

    This is intentionally a small, explainable taxonomy. It routes a query to
    the right evidence profile; it never generates medical or legal conclusions.
    """
    normalized = normalize(question)
    tokens = set(re.findall(r"[\w]+", normalized))

    if module_id == "medicina" and is_medical_sleep_query(question):
        return _with_route({
            "intent": "clinical_symptom_assessment",
            "theme": "Sono e sonolência",
            "concepts": [
                "sonolência diurna",
                "microssono",
                "privação de sono",
                "sono insuficiente",
            ],
            "risk_flags": ["acidente_por_sonolencia"],
            "source_profile": "clinical_guideline",
        }, module_id, question, history)

    if module_id == "medicina":
        if any(term in normalized for term in ("sintoma", "dor", "febre", "tosse", "gripe", "influenza")):
            return _with_route({
                "intent": "clinical_symptom_assessment",
                "theme": "Sintomas e avaliação clínica",
                "concepts": ["sintomas", "avaliação clínica"],
                "risk_flags": ["avaliacao_profissional"],
                "source_profile": "clinical_guideline",
            }, module_id, question, history)
        if any(term in normalized for term in ("paciente", "prontuario", "fhir", "exame", "tratamento")):
            return _with_route({
                "intent": "clinical_record_or_protocol",
                "theme": "Protocolos e registros clínicos",
                "concepts": ["protocolo", "registro clínico", "FHIR"],
                "risk_flags": ["dados_de_saude"],
                "source_profile": "clinical_guideline",
            }, module_id, question, history)
        return _with_route({
            "intent": "medical_knowledge_lookup",
            "theme": "Conhecimento médico",
            "concepts": sorted(tokens)[:8],
            "risk_flags": ["avaliacao_profissional"],
            "source_profile": "clinical_guideline",
        }, module_id, question, history)

    if module_id in {"direito", "departamento-pessoal"}:
        if any(term in normalized for term in ("hora extra", "horas extras", "jornada", "hora negativa", "banco de horas")):
            theme = "Jornada, horas extras e compensação"
        elif any(term in normalized for term in ("acordo coletivo", "convencao coletiva", "saae")):
            theme = "Acordo coletivo e interpretação"
        elif any(term in normalized for term in ("ferias", "salario", "decimo terceiro", "13")):
            theme = "Direitos trabalhistas e remuneração"
        else:
            theme = "Legislação e documentos"
        return _with_route({
            "intent": "legal_document_analysis",
            "theme": theme,
            "concepts": sorted(tokens)[:8],
            "risk_flags": ["revisao_juridica"],
            "source_profile": "legal_primary_source",
        }, module_id, question, history)

    if module_id == "infraestrutura":
        if any(term in normalized for term in ("zabbix", "host", "monitoramento", "agent")):
            theme = "Zabbix e monitoramento"
        elif any(term in normalized for term in ("rede", "scan", "scanner", "snmp", "tcp", "udp")):
            theme = "Redes e diagnóstico"
        elif any(term in normalized for term in ("sistema operacional", "linux", "windows", "servidor")):
            theme = "Sistemas e disponibilidade"
        else:
            theme = "Infraestrutura e operações"
        return _with_route({
            "intent": "technical_procedure_or_diagnosis",
            "theme": theme,
            "concepts": sorted(tokens)[:8],
            "risk_flags": [],
            "source_profile": "technical_documentation",
        }, module_id, question, history)

    if module_id == "gestao-empresarial" and (
        ("desvio" in normalized or "variacao" in normalized)
        and "producao" in normalized
    ):
        return _with_route({
            "intent": "production_variance_analysis",
            "theme": "Desvios de produção e indicadores",
            "concepts": ["produção", "meta", "realizado", "desvio", "indicadores"],
            "risk_flags": [],
            "source_profile": "module_document",
        }, module_id, question, history)

    return _with_route({
        "intent": "module_knowledge_lookup",
        "theme": "Outros temas do módulo",
        "concepts": sorted(tokens)[:8],
        "risk_flags": [],
        "source_profile": "module_document",
    }, module_id, question, history)
