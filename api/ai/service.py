from __future__ import annotations

import json
from datetime import datetime, timezone
from time import perf_counter

from ai.agent_runtime import agent_runtime
from ai.client import ReasoningProvider
from ai.critic import critic_engine
from ai.hypothesis import hypothesis_engine
from ai.learning_loop import learning_loop
from ai.models import AIAnswerModel
from ai.planner import build_plan
from ai.prompts import SYSTEM_PROMPT
from ai.reasoning import reasoning_engine
from context.builder import context_builder
from core.event_bus import event_bus
from services.postgres_store import postgres_store
from services.openai_reasoner import has_llm_enabled
from semantic.interpreter import SemanticGateway
from semantic.models import SemanticQuery
from services.zabbix_investigator import format_investigation


class OpenAIService:
    def __init__(self):
        self.client = ReasoningProvider()
        self.semantic_gateway = SemanticGateway(self.client)

    @staticmethod
    def _build_explainability(question: str, plan: dict, context: dict, reasoning: dict, critic: dict) -> dict:
        return {
            "flow": ["question", "planner", "context", "reasoning", "openai_or_fallback", "critic", "response"],
            "question": question,
            "intent": plan.get("intent", "unknown"),
            "capabilities": plan.get("capabilities", []),
            "tools": plan.get("tools", []),
            "agent": context.get("agent", {}),
            "selected_hypothesis": context.get("hypothesis", {}).get("selected_hypothesis"),
            "evidence_sources": [trace.get("tool") for trace in context.get("evidence", [])],
            "risk_levels": [risk.get("level") for risk in context.get("risks", [])],
            "justification": reasoning.get("justification", ""),
            "critic_issues": critic.get("issues", []),
            "provider": critic.get("provider", "unknown"),
        }

    @staticmethod
    def _compact_context_for_llm(context: dict) -> dict:
        tools = context.get("tools", {}) if isinstance(context, dict) else {}
        problems = tools.get("zabbix.list_problems", {}).get("problems", [])
        if not isinstance(problems, list):
            problems = []

        compact_problems = []
        for item in problems[:10]:
            if not isinstance(item, dict):
                continue
            compact_problems.append(
                {
                    "name": item.get("name", ""),
                    "severity": item.get("severity_label", item.get("severity", "")),
                    "hosts": (item.get("hosts", []) or [])[:2],
                    "groups": (item.get("groups", []) or [])[:2],
                }
            )
            if len(compact_problems) >= 3:
                break

        knowledge = context.get("knowledge", []) if isinstance(context.get("knowledge", []), list) else []
        insights = context.get("insights", []) if isinstance(context.get("insights", []), list) else []

        compact_knowledge = []
        for item in knowledge[:1]:
            if not isinstance(item, dict):
                continue
            compact_knowledge.append(
                {
                    "source": item.get("source", ""),
                    "score": item.get("score", 0),
                    "snippet": str(item.get("snippet", ""))[:220],
                }
            )

        compact_insights = []
        for item in insights[:2]:
            if not isinstance(item, dict):
                continue
            compact_insights.append(
                {
                    "family": item.get("family", ""),
                    "count": item.get("count", 0),
                    "insight": str(item.get("insight", ""))[:180],
                }
            )

        risks = context.get("risks", []) if isinstance(context.get("risks", []), list) else []
        investigation = tools.get("zabbix.investigate", {}) if isinstance(tools.get("zabbix.investigate", {}), dict) else {}
        investigation_evidence=[]
        for entry in (investigation.get("evidence",[]) or [])[:8]:
            if not isinstance(entry,dict):continue
            investigation_evidence.append({"problem":entry.get("problem"),"severity":entry.get("severity"),"started_at":entry.get("started_at"),"entity":entry.get("entity"),"hosts":entry.get("hosts",[])[:3],"recurrence":entry.get("recurrence"),"trigger":entry.get("trigger"),"data_coverage":entry.get("data_coverage"),"items":[{"name":item.get("name"),"current_value":item.get("current_value"),"interpreted_value":item.get("interpreted_value"),"previous_value":item.get("previous_value"),"units":item.get("units"),"last_collected_at":item.get("last_collected_at"),"history_summary":item.get("history_summary")} for item in (entry.get("items",[]) or [])[:6]]})

        return {
            "summary": context.get("summary", {}),
            "intent": context.get("intent", "unknown"),
            "agent": {
                "name": context.get("agent", {}).get("name", ""),
                "critic_focus": context.get("agent", {}).get("critic_focus", ""),
            },
            "hypothesis": {
                "domain": context.get("hypothesis", {}).get("domain", ""),
                "selected_hypothesis": context.get("hypothesis", {}).get("selected_hypothesis", ""),
                "confidence": context.get("hypothesis", {}).get("confidence", 0.0),
            },
            "top_problems": compact_problems,
            "knowledge": compact_knowledge,
            "insights": compact_insights,
            "risk": risks[:2],
            "zabbix_investigation":{"scope":investigation.get("scope",{}),"evidence":investigation_evidence,"missing_data":investigation.get("missing_data",[])},
        }

    @staticmethod
    def _presentation(context:dict,confidence:float)->dict:
        tools=context.get("tools",{}) if isinstance(context,dict) else {};investigation=tools.get("zabbix.investigate",{}) if isinstance(tools,dict) else {};entries=investigation.get("evidence",[]) if isinstance(investigation,dict) else []
        hosts=sorted({str(host) for entry in entries if isinstance(entry,dict) for host in (entry.get("hosts") or [])})
        timeline=[{"at":entry.get("started_at"),"title":entry.get("problem") or "Ocorrência","entity":", ".join(entry.get("hosts") or [])} for entry in entries if isinstance(entry,dict) and entry.get("started_at")][:12]
        severities={}
        for entry in entries:
            if isinstance(entry,dict):key=str(entry.get("severity") or "Não classificado");severities[key]=severities.get(key,0)+1
        return {"version":"1.0","summary_cards":[{"label":"Evidências","value":len(entries)},{"label":"Entidades","value":len(hosts)},{"label":"Confiança","value":round(confidence*100),"suffix":"%"}],"timeline":timeline,"chart":{"type":"bar","title":"Ocorrências por severidade","series":[{"label":key,"value":value} for key,value in severities.items()]},"entities":hosts[:20],"evidence_level":"observed" if entries else "inferred","actions":[{"label":"Abrir Linha do Tempo","href":"/ui/timeline.html"}]}

    def answer(self, question: str, semantic_query: SemanticQuery | None = None) -> dict:
        start = perf_counter()
        event_bus.publish_sync(
            "ai.question.received",
            {"question": question, "generated_at": datetime.now(timezone.utc).isoformat()},
        )
        semantic_query = semantic_query or self.semantic_gateway.interpret(question)
        plan = build_plan(question, semantic_query)
        agent = agent_runtime.resolve(question=question, plan=plan)
        context = context_builder.build(question, plan, agent=agent)
        hypothesis = hypothesis_engine.build(question=question, plan=plan, context=context)
        context["hypothesis"] = hypothesis
        context["agent"] = agent
        reasoning = reasoning_engine.build(question, plan, context)

        postgres_store.save_hypothesis_run(
            question=question,
            symptom=hypothesis.get("symptom", question),
            domain=hypothesis.get("domain", "general"),
            hypotheses=hypothesis.get("hypotheses", []),
            selected_hypothesis=hypothesis.get("selected_hypothesis"),
            confidence=float(hypothesis.get("confidence", 0.0) or 0.0),
            metadata={
                "intent": plan.get("intent", "unknown"),
                "agent": agent.get("name", "unknown"),
                "confirmed": bool(float(hypothesis.get("confidence", 0.0) or 0.0) >= 0.6),
            },
        )

        investigation_result=context.get("tools",{}).get("zabbix.investigate",{})
        candidate_answer = format_investigation(investigation_result) if isinstance(investigation_result,dict) and investigation_result.get("evidence") else reasoning.get("deterministic_answer")
        llm_used = False
        llm_provider = "none"
        usage: dict = {}

        if not candidate_answer:
            llm_context = self._compact_context_for_llm(context)
            llm_context_json = json.dumps(llm_context, ensure_ascii=False)
            if not llm_context.get("zabbix_investigation", {}).get("evidence") and len(llm_context_json) > 1400:
                llm_context_json = llm_context_json[:1400]
            reasoning_note = reasoning_engine.to_developer_note(reasoning)
            if len(reasoning_note) > 140:
                reasoning_note = reasoning_note[:140]
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "developer", "content": llm_context_json},
                {"role": "developer", "content": reasoning_note},
                {"role": "user", "content": question},
            ]
            if llm_context.get("zabbix_investigation", {}).get("evidence"):
                messages.insert(3,{"role":"developer","content":"Use somente zabbix_investigation. Separe fatos comprovados, dados ausentes e hipótese. Não atribua core, energia, cabo, processo ou causa sem evidência. Cite componente, valores, horário, histórico e recorrência disponíveis; termine com ação segura e verificável."})

            llm_result = self.client.reason(messages,max_tokens=900) if llm_context.get("zabbix_investigation", {}).get("evidence") else self.client.reason(messages)
            if llm_result and llm_result.get("text"):
                candidate_answer = str(llm_result.get("text", "")).strip()
                usage = llm_result.get("usage", {}) if isinstance(llm_result.get("usage", {}), dict) else {}
                llm_used = True
                llm_provider = str(llm_result.get("provider", "unknown"))

        if not candidate_answer:
            candidate_answer = self._fallback_answer(question, context)

        critic = critic_engine.evaluate(question, plan, context, candidate_answer)
        critic["provider"] = llm_provider
        final_answer = candidate_answer
        if not critic.get("approved", False):
            revised_answer = critic.get("revised_answer")
            if revised_answer:
                final_answer = revised_answer
            else:
                final_answer = self._fallback_answer(question, context)

        confidence = float(critic.get("confidence", critic.get("score", 0.0)) or 0.0)
        explainability = self._build_explainability(
            question=question,
            plan=plan,
            context=context,
            reasoning=reasoning,
            critic=critic,
        )

        latency_ms = int((perf_counter() - start) * 1000)
        tokens_in = int(usage.get("input_tokens", 0) or 0)
        tokens_out = int(usage.get("output_tokens", 0) or 0)
        cache_creation_tokens = int(usage.get("cache_creation_input_tokens", 0) or 0)
        cache_read_tokens = int(usage.get("cache_read_input_tokens", 0) or 0)
        # Conservative estimate for dashboard cost trend.
        cost_usd = round((tokens_in * 0.0000005) + (tokens_out * 0.0000015), 8)

        postgres_store.save_ai_metric(
            question=question,
            intent=plan.get("intent", "unknown"),
            llm_used=llm_used,
            latency_ms=latency_ms,
            confidence=confidence,
            critic_approved=bool(critic.get("approved", False)),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_usd=cost_usd,
            tools=plan.get("tools", []),
            metadata={
                "critic_issues": critic.get("issues", []),
                "capabilities": plan.get("capabilities", []),
                "agent": agent.get("name", "unknown"),
                "selected_hypothesis": hypothesis.get("selected_hypothesis"),
                "llm_provider": llm_provider,
                "prompt_cache": {
                    "creation_input_tokens": cache_creation_tokens,
                    "read_input_tokens": cache_read_tokens,
                    "hit": cache_read_tokens > 0,
                },
            },
        )

        learning = learning_loop.process(
            question=question,
            plan=plan,
            context=context,
            reasoning=reasoning,
            critic=critic,
            answer=final_answer,
            hypothesis=hypothesis,
            agent=agent,
            semantic_query=semantic_query.model_dump(mode="json"),
        )

        result = AIAnswerModel(
            answer=final_answer,
            plan=plan,
            context=context,
            llm_used=llm_used,
            reasoning=reasoning,
            critic=critic,
            confidence=confidence,
            explainability=explainability,
            learning=learning,
            presentation=self._presentation(context,confidence),
        )
        event_bus.publish_sync(
            "ai.answered",
            {
                "question": question,
                "answer": final_answer,
                "llm_used": llm_used,
                "llm_provider": llm_provider,
                "agent": agent.get("name", "unknown"),
                "selected_hypothesis": hypothesis.get("selected_hypothesis"),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return result.model_dump()

    def _fallback_answer(self, question: str, context: dict) -> str:
        tools = context.get("tools", {})
        investigation=tools.get("zabbix.investigate",{})
        if isinstance(investigation,dict) and investigation.get("evidence"):
            return format_investigation(investigation)
        knowledge = context.get("knowledge", []) if isinstance(context.get("knowledge", []), list) else []
        if knowledge:
            first = knowledge[0] if isinstance(knowledge[0], dict) else {}
            snippet = str(first.get("snippet", "")).strip()
            source = str(first.get("source", "base de conhecimento")).strip()
            if snippet:
                evidence = snippet[:420].rstrip()
                return (
                    f"Segundo a base {source}: {evidence} "
                    "Proximo passo: valide essa orientacao com o estado atual do ambiente antes de executar qualquer acao."
                )
        insights = context.get("insights", []) if isinstance(context.get("insights", []), list) else []
        q = question.lower()
        temporal = context.get("snapshot", {}).get("temporal", {}) if isinstance(context.get("snapshot", {}), dict) else {}
        trends = temporal.get("group_trends_30d", []) if isinstance(temporal.get("group_trends_30d", []), list) else []

        if any(term in q for term in ["30 dias", "reincid", "grupo", "grupos"]) and trends:
            top = trends[:5]
            ranking = "; ".join([f"{item.get('group')} ({item.get('occurrences')} ocorrencias)" for item in top])
            return (
                "Nos ultimos 30 dias, os grupos com maior reincidencia observada foram: "
                f"{ranking}. "
                "Recomendo iniciar pelos dois primeiros grupos, correlacionar com runbooks do Knowledge e priorizar eventos de maior severidade."
            )

        operational_terms = [
            "zabbix",
            "docker",
            "container",
            "containers",
            "problem",
            "problema",
            "alert",
            "severity",
            "severidade",
            "grupo",
            "marketplace",
            "marktplace",
            "workflow",
            "n8n",
            "knowledge",
            "documentacao",
            "documentação",
            "doc",
        ]
        if not has_llm_enabled() and not any(term in q for term in operational_terms):
            return (
                "Ainda nao ha um provedor de IA funcional neste servidor. "
                "Configure ANTHROPIC_API_KEY com quota ativa ou OLLAMA_BASE_URL/OLLAMA_MODEL para chat livre."
            )

        if "market" in q:
            catalog = tools.get("marketplace.catalog", {})
            modules = catalog.get("modules", []) if isinstance(catalog, dict) else []
            module_names = ", ".join([module.get("name", "") for module in modules])
            return f"Você possui {len(modules)} módulo(s) no Marketplace: {module_names}."

        if "zabbix.list_problems" in tools:
            data = tools.get("zabbix.list_problems", {})
            problems = data.get("problems", []) if isinstance(data, dict) else []
            if not problems:
                return "No momento não há problemas ativos no recorte consultado do Zabbix."
            top = []
            for item in problems[:5]:
                sev = item.get("severity_label", item.get("severity", "?"))
                name = item.get("name", "problema sem nome")
                hosts = ", ".join(item.get("hosts", [])[:2]) or "host não identificado"
                top.append(f"{sev} - {name} (hosts: {hosts})")
            pattern_lines = []
            for pattern in insights[:2]:
                if isinstance(pattern, dict):
                    pattern_lines.append(pattern.get("insight", ""))
            if pattern_lines:
                return f"Encontrei {len(problems)} problema(s) ativo(s). Top: {'; '.join(top)}. Padrões aprendidos: {' | '.join(pattern_lines)}"
            return f"Encontrei {len(problems)} problema(s) ativo(s). Top: {'; '.join(top)}"

        if "docker.list_containers" in tools:
            containers = tools.get("docker.list_containers", {}).get("containers", [])
            if isinstance(containers, list):
                return f"Há {len(containers)} container(s): {', '.join(containers)}"

        if insights:
            pattern = insights[0]
            if isinstance(pattern, dict):
                return f"O SOFIA aprendeu um padrão recorrente: {pattern.get('insight', '')}"

        return "Contexto consolidado com sucesso. Faça uma pergunta operacional específica para eu trazer evidências detalhadas."


openai_service = OpenAIService()
