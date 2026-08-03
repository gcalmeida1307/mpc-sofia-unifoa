from __future__ import annotations

import json
from datetime import datetime, timezone

from ai.client import OpenAIResponsesClient
from ai.models import AIAnswerModel
from ai.planner import build_plan
from ai.prompts import SYSTEM_PROMPT
from context.builder import context_builder
from core.event_bus import event_bus
from services.openai_reasoner import has_openai_enabled
from services.openai_reasoner import has_openai_enabled


class OpenAIService:
    def __init__(self):
        self.client = OpenAIResponsesClient()

    def _looks_like_host_count(self, question: str) -> bool:
        q = question.lower()
        count_terms = ["quantos", "quantas", "quantidade", "total", "numero", "número"]
        host_terms = ["host", "hosts"]
        severity_terms = ["severity", "severidade", "average", "avg", "avarege", "avarage"]
        return any(term in q for term in count_terms) and any(term in q for term in host_terms) and not any(term in q for term in severity_terms)

    def answer(self, question: str) -> dict:
        event_bus.publish_sync(
            "ai.question.received",
            {"question": question, "generated_at": datetime.now(timezone.utc).isoformat()},
        )
        plan = build_plan(question)
        context = context_builder.build(question, plan)

        if self._looks_like_host_count(question):
            host_count = context.get("summary", {}).get("hosts", 0)
            answer = f"Você possui {host_count} host(s) cadastrados no Zabbix."
            result = AIAnswerModel(
                answer=answer,
                plan=plan,
                context=context,
                llm_used=False,
            )
            event_bus.publish_sync(
                "ai.answered",
                {
                    "question": question,
                    "answer": answer,
                    "llm_used": False,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            return result.model_dump()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "developer", "content": json.dumps(context, ensure_ascii=False)},
            {"role": "user", "content": question},
        ]

        llm_answer = self.client.ask(messages)
        if llm_answer:
            result = AIAnswerModel(
                answer=llm_answer.strip(),
                plan=plan,
                context=context,
                llm_used=True,
            )
            event_bus.publish_sync(
                "ai.answered",
                {
                    "question": question,
                    "answer": llm_answer.strip(),
                    "llm_used": True,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            return result.model_dump()

        # Deterministic fallback when OpenAI is unavailable.
        answer = self._fallback_answer(question, context)
        result = AIAnswerModel(
            answer=answer,
            plan=plan,
            context=context,
            llm_used=False,
        )
        event_bus.publish_sync(
            "ai.answered",
            {
                "question": question,
                "answer": answer,
                "llm_used": False,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return result.model_dump()

    def _fallback_answer(self, question: str, context: dict) -> str:
        tools = context.get("tools", {})
        insights = context.get("insights", {}) if isinstance(context.get("insights", {}), dict) else {}
        q = question.lower()

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
        if not has_openai_enabled() and not any(term in q for term in operational_terms):
            return (
                "Ainda não há um provedor de IA configurado neste servidor. "
                "Se você definir OPENAI_API_KEY (ou outro provedor equivalente), eu consigo responder como chat livre."
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
            for pattern in insights.get("patterns", [])[:2]:
                pattern_lines.append(pattern.get("insight", ""))
            if pattern_lines:
                return f"Encontrei {len(problems)} problema(s) ativo(s). Top: {'; '.join(top)}. Padrões aprendidos: {' | '.join(pattern_lines)}"
            return f"Encontrei {len(problems)} problema(s) ativo(s). Top: {'; '.join(top)}"

        if "docker.list_containers" in tools:
            containers = tools.get("docker.list_containers", {}).get("containers", [])
            if isinstance(containers, list):
                return f"Há {len(containers)} container(s): {', '.join(containers)}"

        if insights.get("patterns"):
            pattern = insights["patterns"][0]
            return f"O SOFIA aprendeu um padrão recorrente: {pattern.get('insight', '')}"

        return "Contexto consolidado com sucesso. Faça uma pergunta operacional específica para eu trazer evidências detalhadas."


openai_service = OpenAIService()
