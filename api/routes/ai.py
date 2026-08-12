from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.service import openai_service
from ai.domain_policy import OUT_OF_SCOPE_MESSAGE, is_it_question
from services.postgres_store import postgres_store
from semantic.interpreter import semantic_gateway
from core.domain_intelligence import domain_provider_registry

router = APIRouter(prefix="/ai", tags=["AI"])


class AIAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[dict[str, str]] = Field(default_factory=list, max_length=6)
    domain_id: str | None = Field(default=None, max_length=80)
    temporal_context: dict = Field(default_factory=dict)


def _contextual_question(payload: AIAskRequest) -> str:
    """Resolve short follow-ups without weakening the domain boundary."""
    history = [item for item in payload.history[-6:] if isinstance(item, dict)]
    prior_questions = [str(item.get("question", ""))[:500] for item in history if item.get("question")]
    temporal = payload.temporal_context if isinstance(payload.temporal_context, dict) else {}
    parts: list[str] = []
    if payload.domain_id:
        domain_context = "rede de computadores, sistemas e Zabbix" if payload.domain_id == "infrastructure" else payload.domain_id
        parts.append(f"Domínio ativo: {domain_context}.")
    if prior_questions:
        parts.append(f"Pergunta anterior: {prior_questions[-1]}")
    if temporal.get("title"):
        parts.append(f"Episódio temporal selecionado: {str(temporal['title'])[:300]}.")
    entities = temporal.get("entities", []) if isinstance(temporal.get("entities", []), list) else []
    if entities:
        parts.append("Entidades do episódio: " + ", ".join(map(str, entities[:12])) + ".")
    events = temporal.get("events", []) if isinstance(temporal.get("events", []), list) else []
    if events:
        observed = [f"{str(item.get('at', ''))[:25]} {str(item.get('title', ''))[:180]}" for item in events[:8] if isinstance(item, dict)]
        if observed:
            parts.append("Evidências temporais selecionadas: " + " | ".join(observed) + ".")
    return f"{' '.join(parts)} Solicitação atual: {payload.question}".strip() if parts else payload.question


def _is_contextual_follow_up(question: str) -> bool:
    normalized = question.lower()
    markers = (
        "plano de ação", "plano de acao", "prioriz", "evidência", "evidencia",
        "investigue", "detalhe", "continue", "compare", "explique melhor",
        "como resolv", "próxima ação", "proxima acao", "atenção", "atencao",
        "risco", "o que mudou", "padrão", "padrao", "resuma", "situação atual",
        "situacao atual", "isso", "esse", "esses", "elas", "eles",
    )
    return any(marker in normalized for marker in markers)


@router.post("/ask")
def ask(payload: AIAskRequest):
    effective_question = _contextual_question(payload)
    in_scope = is_it_question(payload.question) or (_is_contextual_follow_up(payload.question) and is_it_question(effective_question))
    if not in_scope:
        return {
            "answer": OUT_OF_SCOPE_MESSAGE,
            "plan": {"intent": "out_of_scope", "tools": []},
            "reasoning": {"mode": "domain_guard"},
            "critic": {"approved": True, "provider": "none"},
            "llm_provider": "none",
            "confidence": 1.0,
            "explainability": {"domain": "outside_information_technology"},
            "learning": {"stored": False, "reason": "out_of_scope"},
            "llm_used": False,
            "context": {},
            "source": "domain-policy",
        }

    postgres_store.add_message("user", payload.question, {"channel": "ai", "purpose": "training"})
    semantic = semantic_gateway.interpret(effective_question)
    try:
        provider = domain_provider_registry.get(payload.domain_id or "infrastructure")
        execution = provider.execute_semantic(semantic, effective_question) if provider and hasattr(provider, "execute_semantic") else None
        if execution:
            answer = execution["answer"]
            semantic_data = semantic.model_dump(mode="json")
            plan_data = {"intent":semantic.intent,"domain":semantic.domain,"semantic_query":semantic_data,"tools":["zabbix.event.get" if execution["days"] else "zabbix.list_problems"]}
            postgres_store.save_learning_cycle(
                question=payload.question, intent=semantic.intent,
                decision={"semantic_query":semantic_data,"validated_query":semantic_data,"plan":plan_data},
                evidence=[{"source":"zabbix","group":execution["group"],"matches":len(execution["matches"])}],
                outcome={"result":answer,"unique_host_count":len(execution["hosts"])},
                knowledge_updated=False,
                metadata={"feedback":None,"correction":None,"interpretation_source":semantic.interpretation_source},
            )
            postgres_store.add_message("assistant", answer, {"channel":"ai","purpose":"training","source":"semantic_zabbix"})
            return {
                "answer":answer,
                "plan":plan_data,
                "reasoning":{"mode":"validated_semantic_execution"},"critic":{"approved":True,"provider":"local"},
                "llm_provider":semantic.interpretation_source,"confidence":semantic.confidence,
                "explainability":{"domain":semantic.domain,"evidence_source":"zabbix","semantic_query":semantic_data},
                "learning":{"stored":True,"semantic_query":semantic_data},"llm_used":semantic.interpretation_source in {"anthropic","ollama"},
                "context":{"related_problem_count":len(execution["matches"]),"unique_host_count":len(execution["hosts"]),"group":execution["group"],"days":execution["days"]},
                "source":"semantic-zabbix",
                "response_mode":"evidence_based",
                "sources_used":["Zabbix", *( ["Claude (interpretação)"] if semantic.interpretation_source == "anthropic" else ["Ollama (interpretação)"] if semantic.interpretation_source == "ollama" else ["Regras locais"] )],
                "degraded":False,
            }
    except Exception:
        pass
    # Knowledge remains part of the context pipeline. Do not short-circuit operational
    # or conceptual questions with a merely similar document fragment.
    result = openai_service.answer(effective_question, semantic_query=semantic, domain_id=payload.domain_id)
    answer = result.get("answer", "")
    postgres_store.add_message(
        "assistant", answer,
        {"channel": "ai", "purpose": "training", "learning_signature": result.get("learning", {}).get("signature")},
    )
    provider = result.get("critic", {}).get("provider", "none")
    evidence_sources = result.get("explainability", {}).get("evidence_sources", []) or []
    sources_used = (["Claude"] if provider == "anthropic" else ["Ollama"] if provider == "ollama" else ["Regras locais"])
    sources_used.extend(str(item) for item in evidence_sources if item)
    return {
        "answer": answer,
        "plan": result.get("plan", {}),
        "reasoning": result.get("reasoning", {}),
        "critic": result.get("critic", {}),
        "llm_provider": result.get("critic", {}).get("provider", "none"),
        "confidence": result.get("confidence", 0.0),
        "explainability": result.get("explainability", {}),
        "learning": result.get("learning", {}),
        "llm_used": result.get("llm_used", False),
        "context": result.get("context", {}),
        "source": "claude-learning-pipeline",
        "response_mode":"full" if provider == "anthropic" else "local_fallback" if provider in {"ollama", "none"} else "degraded",
        "sources_used":list(dict.fromkeys(sources_used)),
        "degraded":provider not in {"anthropic"},
    }
