from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.service import openai_service
from connectors.zabbix import ZabbixConnector
from core.registry import registry
from services.docker_service import DockerService
from services.knowledge import search_knowledge
from services.marketplace import get_marketplace_catalog
from services.openai_reasoner import generate_answer, has_llm_enabled
from services.persistence import persistence
from services.postgres_store import postgres_store
from services.qdrant_store import qdrant_store
from services.vector_store import vector_store
from services.assistant_intelligence import build_investigation_plan, classify_question

router = APIRouter(prefix="/assistant", tags=["Assistant"])


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


def _looks_like_host_count(question: str) -> bool:
    count_terms = ["quantos", "quantas", "quantidade", "total", "numero", "número"]
    host_terms = ["host", "hosts"]
    return any(term in question for term in count_terms) and any(term in question for term in host_terms)


def _looks_like_severity_count(question: str) -> bool:
    count_terms = ["quantos", "quantas", "quantidade", "total", "numero", "número"]
    severity_terms = ["severity", "severidade", "average", "avg", "avarege", "avarage"]
    return any(term in question for term in count_terms) and any(term in question for term in severity_terms)


def _looks_like_problem_listing(question: str) -> bool:
    list_terms = [
        "quais problemas",
        "problemas listados",
        "problemas ativos",
        "listar problemas",
        "alertas ativos",
        "problemas no zabbix",
        "quais possuem problema",
        "possuem problema agora",
        "estao com problema agora",
        "estão com problema agora",
    ]
    return any(term in question for term in list_terms)


def _extract_group_name(question: str) -> str | None:
    if "grupo " not in question:
        return None
    tail = question.split("grupo ", 1)[1]
    separators = [",", "?", ".", " no zabbix", " agora", " quais"]
    for sep in separators:
        if sep in tail:
            tail = tail.split(sep, 1)[0]
    group = tail.strip()
    return group or None


def _looks_like_marketplace_question(question: str) -> bool:
    return any(token in question for token in ["marketplace", "marktplace", "market place"])


def _build_recommendations(question: str, modules: list[str], knowledge_hint: str) -> list[str]:
    q = question.lower()
    recommendations: list[str] = []
    if "zabbix" in modules and any(token in q for token in ["queda", "indispon", "lento", "severity", "alerta"]):
        recommendations.append("Consultar problemas ativos e hosts afetados no Zabbix para validar escopo do incidente.")
    if knowledge_hint:
        recommendations.append("Cruzar a evidência com runbook/documentação para evitar ações fora do padrão.")
    if "workflow" in modules:
        recommendations.append("Disparar workflow de investigação no n8n para automatizar coleta e notificação.")
    if not recommendations:
        recommendations.append("Registrar este contexto para melhorar respostas futuras e criar fluxo automatizado no n8n.")
    return recommendations


@router.post("/ask")
def ask(payload: AssistantRequest):
    question = payload.question.lower()
    snapshot = registry.get_snapshot()
    modules = snapshot["modules"]
    capabilities = snapshot["capabilities"]

    persistence.add_message("user", payload.question)
    postgres_store.add_message("user", payload.question, {"channel": "assistant"})

    intent = classify_question(payload.question)
    is_zabbix_context = intent["needs_zabbix"] or "zabbix" in question or "severity" in question or "severidade" in question or "average" in question or "avarege" in question or "avg" in question or "host group" in question or "hostgroup" in question or "problem" in question or "trigger" in question or "alert" in question
    is_host_count_question = _looks_like_host_count(question)
    is_severity_count_question = _looks_like_severity_count(question)
    is_problem_listing_question = _looks_like_problem_listing(question)
    is_marketplace_question = _looks_like_marketplace_question(question)
    group_name = _extract_group_name(question)

    knowledge_result = search_knowledge(payload.question)
    knowledge_hint = knowledge_result["results"][0]["snippet"] if knowledge_result["results"] else ""
    vector_store.add(payload.question, {"source": "assistant"})
    qdrant_ok = qdrant_store.add_text(payload.question, {"role": "user", "source": "assistant"})
    memory_hits = qdrant_store.search(payload.question, limit=2)
    if not memory_hits:
        try:
            memory_hits = [
                {
                    "score": 0.0,
                    "text": item.get("text", ""),
                    "payload": item.get("metadata", {}),
                }
                for item in vector_store.search(payload.question, limit=2)
            ]
        except Exception:
            memory_hits = []
    recent_history = postgres_store.get_recent_messages(limit=6)
    recommendations = _build_recommendations(payload.question, modules, knowledge_hint)
    append_context = True

    try:
        ai_result = openai_service.answer(payload.question)
        answer = ai_result.get("answer", "")
        if answer:
            append_context = False
            plan_tools = ai_result.get("plan", {}).get("tools", [])
            if plan_tools:
                recommendations = [f"Planner tools usados: {', '.join(plan_tools)}"]
            memory_hits = ai_result.get("context", {}).get("memory", {}).get("semantic", memory_hits)

            persistence.add_message("assistant", answer)
            postgres_store.add_message("assistant", answer, {"channel": "assistant", "source": "openai_service"})
            if not qdrant_ok:
                vector_store.add(answer, {"role": "assistant", "source": "assistant-fallback"})
            else:
                qdrant_store.add_text(answer, {"role": "assistant", "source": "assistant"})

            return {
                "answer": answer,
                "modules": modules,
                "capabilities": capabilities,
                "recommendations": recommendations,
                "memory_hits": memory_hits,
                "llm_enabled": has_llm_enabled(),
                "planner": ai_result.get("plan", {}),
                "agent": ai_result.get("context", {}).get("agent", {}),
                "hypothesis": ai_result.get("context", {}).get("hypothesis", {}),
                "learning": ai_result.get("learning", {}),
                "source": "openai-service+context-engine",
            }
    except Exception:
        # Keep local assistant logic as deterministic fallback.
        pass

    if "n8n" in question or "workflow" in question or "automacao" in question or "automação" in question:
        answer = (
            "Você pode usar o n8n como motor de execução do SOFIA. Fluxo recomendado: "
            "1) criar webhook no n8n (ex: sofia-investigation); "
            "2) receber evento do SOFIA com incidente e prioridade; "
            "3) consultar APIs (Zabbix/Grafana/SQL); "
            "4) correlacionar horários; "
            "5) enviar conclusão para Teams/Jira. "
            "Endpoint pronto no SOFIA: POST /workflows/n8n/run com webhook e event."
        )
    elif is_problem_listing_question:
        try:
            connector = ZabbixConnector()
            problems = connector.list_active_problems(limit=20, group_name=group_name)
            if not problems:
                if group_name:
                    answer = f"No momento não há problemas ativos no grupo {group_name} no Zabbix."
                else:
                    answer = "No momento não há problemas ativos listados no Zabbix."
            else:
                lines = []
                for idx, problem in enumerate(problems[:5], start=1):
                    host_label = ", ".join(problem.get("hosts", [])[:2]) or "host não identificado"
                    lines.append(
                        f"{idx}) {problem.get('severity_label')} - {problem.get('name')} (hosts: {host_label})"
                    )
                evidence = (
                    f"grupo: {group_name or 'todos'}\n"
                    f"total_problemas: {len(problems)}\n"
                    f"itens: {'; '.join(lines)}"
                )
                llm_answer = generate_answer(payload.question, evidence)
                if llm_answer:
                    answer = llm_answer
                else:
                    scope = f"no grupo {group_name}" if group_name else "no recorte atual"
                    answer = (
                        f"Agora há {len(problems)} problema(s) ativo(s) {scope} do Zabbix. "
                        f"Top ocorrências: {'; '.join(lines)}"
                    )
            append_context = False
        except Exception as exc:
            answer = f"Não consegui listar os problemas do Zabbix agora. Erro: {exc}"
    elif is_severity_count_question:
        try:
            connector = ZabbixConnector()
            count = connector.count_hosts()
            summary = connector.get_problem_summary(limit=200)
            answer = (
                f"Ambiente atual: {count} host(s) cadastrados no Zabbix. "
                f"No recorte de problemas ativos, {summary['affected_hosts']} host(s) aparecem impactados em {summary['total_problems']} evento(s). "
                f"Distribuição por severidade: {summary['severity_buckets']}. "
                "Decisão sugerida: priorizar severidades 4 e 5, abrir investigação no n8n e correlacionar com runbook antes de remediação."
            )
        except Exception as exc:
            answer = f"Não consegui consultar o Zabbix agora. Erro: {exc}"
    elif intent["kind"] == "investigation" and (intent["needs_zabbix"] or intent["needs_knowledge"]):
        plan = build_investigation_plan(payload.question, modules, capabilities, knowledge_hint)
        answer = (
            f"Estou tratando isso como uma investigação operacional.\n{plan}"
        )
    elif is_zabbix_context:
        if is_host_count_question:
            try:
                connector = ZabbixConnector()
                count = connector.count_hosts()
                if any(term in question for term in ["severity", "severidade", "average", "avarege", "avg"]):
                    answer = (
                        f"Hoje o Zabbix tem {count} host(s) cadastrados. "
                        "Para saber quais deles têm um valor de severity average, eu precisaria de uma consulta mais específica de triggers ou problemas."
                    )
                else:
                    answer = f"Você possui {count} host(s) cadastrados no Zabbix."
            except Exception as exc:
                answer = f"Não consegui consultar o Zabbix agora. Erro: {exc}"
        else:
            if "severity" in question or "average" in question:
                answer = (
                    "Para investigar severity average no Zabbix, eu faria a análise em três passos: "
                    "1) identificar o host group afetado; 2) revisar a média de severidade do grupo; "
                    "3) correlacionar alertas com runbooks e incidentes. O Knowledge encontrou contexto relevante para isso: "
                    f"{knowledge_hint}"
                )
            else:
                answer = (
                    f"O módulo Zabbix está disponível e suas capacidades incluem {', '.join(capabilities.get('zabbix', []))}. "
                    f"Além disso, o Knowledge encontrou contexto relevante: {knowledge_hint}"
                )
    elif "docker" in question:
        docker_service = DockerService()
        containers = docker_service.list_containers()
        answer = (
            f"O SOFIA identifica o módulo Docker e pode operar as capacidades {', '.join(capabilities.get('docker', []))}. "
            f"O Knowledge trouxe contexto: {knowledge_hint}. Containers atualmente: {containers}"
        )
    elif is_marketplace_question:
        catalog = get_marketplace_catalog()
        modules_catalog = catalog.get("modules", [])
        if any(token in question for token in ["quantos", "quantidade", "total"]):
            answer = f"Você possui {len(modules_catalog)} módulo(s) no Marketplace: {', '.join([m['name'] for m in modules_catalog])}."
        else:
            answer = (
                f"O Marketplace está disponível e contém módulos como {', '.join([m['name'] for m in modules_catalog])}."
            )
    elif "knowledge" in question or "doc" in question or "runbook" in question:
        if knowledge_result["results"]:
            answer = (
                f"O Knowledge Service encontrou contexto relevante para a sua pergunta: {knowledge_result['results'][0]['snippet']}"
            )
        else:
            answer = "O Knowledge Service não encontrou contexto documental relevante no diretório docs ainda."
    else:
        if has_openai_enabled():
            answer = (
                f"Eu consigo responder com base no registry atual, no Knowledge e no histórico da conversa. Hoje o SOFIA possui os módulos {', '.join(modules)}. "
                f"Se você quiser, eu posso usar o Zabbix, Docker, o Marketplace ou o Workflow para responder de forma mais específica."
            )
            if knowledge_hint:
                answer += f" Contexto documental encontrado: {knowledge_hint}"
        else:
            answer = (
                "Ainda não há um provedor de IA configurado neste servidor. "
                "Defina OPENAI_API_KEY (ou outro provedor equivalente) para o SOFIA responder como um chat livre."
            )

    if append_context and memory_hits:
        answer += f" Memória correlata: {memory_hits[0].get('text', '')[:120]}"
    if append_context and recent_history:
        answer += f" Histórico recente observado: {len(recent_history)} interação(ões)."
    if append_context and recommendations:
        answer += f" Recomendações: {' | '.join(recommendations)}"

    persistence.add_message("assistant", answer)
    postgres_store.add_message("assistant", answer, {"channel": "assistant"})
    if not qdrant_ok:
        vector_store.add(answer, {"role": "assistant", "source": "assistant-fallback"})
    else:
        qdrant_store.add_text(answer, {"role": "assistant", "source": "assistant"})

    return {
        "answer": answer,
        "modules": modules,
        "capabilities": capabilities,
        "recommendations": recommendations,
        "memory_hits": memory_hits,
        "llm_enabled": has_openai_enabled(),
        "source": "registry+knowledge+mcp",
    }
