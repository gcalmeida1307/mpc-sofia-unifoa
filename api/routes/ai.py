from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.service import openai_service
from ai.domain_policy import OUT_OF_SCOPE_MESSAGE, is_it_question
from services.postgres_store import postgres_store
from connectors.zabbix import ZabbixConnector
from ai.operational_query import format_historical_triggers, format_related_problems, historical_trigger_group, historical_trigger_window, related_problems, unique_affected_hosts, wants_related_alarm_list

router = APIRouter(prefix="/ai", tags=["AI"])


class AIAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@router.post("/ask")
def ask(payload: AIAskRequest):
    if not is_it_question(payload.question):
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

    days = historical_trigger_window(payload.question)
    if days:
        try:
            group_name, entity_label = historical_trigger_group(payload.question)
            connector = ZabbixConnector()
            events = connector.list_trigger_events(days=days, limit=5000, group_name=group_name)
            active_now = connector.list_active_problems(limit=2000, group_name=group_name)
            related = events
            affected_hosts = unique_affected_hosts(related)
            answer = format_historical_triggers(related, len(events), days, entity_label, active_now)
            postgres_store.add_message('assistant', answer, {'channel':'ai','purpose':'training','source':'zabbix_historical_local'})
            return {'answer':answer,'plan':{'intent':'historical_triggers','tools':['zabbix.event.get']},
                'reasoning':{'mode':'local_historical_correlation'},'critic':{'approved':True,'provider':'local'},
                'llm_provider':'none','confidence':1.0,'explainability':{'domain':'information_technology','evidence_source':'zabbix','days':days},
                'learning':{'stored':True,'reused':False},'llm_used':False,
                'context':{'total_event_count':len(events),'related_event_count':len(related),'unique_host_count':len(affected_hosts)},
                'source':'zabbix-historical-correlation'}
        except Exception:
            pass

    if wants_related_alarm_list(payload.question):
        try:
            active = ZabbixConnector().list_active_problems(limit=2000)
            related = related_problems(payload.question, active)
            affected_hosts = unique_affected_hosts(related)
            answer = format_related_problems(related, len(active), payload.question)
            postgres_store.add_message('assistant', answer, {'channel':'ai','purpose':'training','source':'zabbix_related_local'})
            return {
                'answer':answer,'plan':{'intent':'related_active_alarms','tools':['zabbix.list_problems']},
                'reasoning':{'mode':'local_operational_correlation'},'critic':{'approved':True,'provider':'local'},
                'llm_provider':'none','confidence':1.0,'explainability':{'domain':'information_technology','evidence_source':'zabbix','related_count':len(related)},
                'learning':{'stored':True,'reused':False},'llm_used':False,'context':{'active_problem_count':len(active),'related_problem_count':len(related),'unique_host_count':len(affected_hosts)},
                'source':'zabbix-local-correlation',
            }
        except Exception:
            pass
    # Knowledge remains part of the context pipeline. Do not short-circuit operational
    # or conceptual questions with a merely similar document fragment.
    result = openai_service.answer(payload.question)
    answer = result.get("answer", "")
    postgres_store.add_message(
        "assistant", answer,
        {"channel": "ai", "purpose": "training", "learning_signature": result.get("learning", {}).get("signature")},
    )
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
    }
