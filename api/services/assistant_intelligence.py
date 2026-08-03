from __future__ import annotations

from typing import Any, Dict, List


def classify_question(question: str) -> Dict[str, Any]:
    text = question.lower()
    is_investigation = any(token in text for token in ["por que", "qual a causa", "causa", "problema", "indispon", "lento", "quebrou", "down", "severity", "average", "avarege", "alerta", "trigger", "incident"])
    needs_zabbix = any(token in text for token in ["zabbix", "severity", "average", "avarege", "alerta", "trigger", "problema"])
    needs_knowledge = any(token in text for token in ["knowledge", "runbook", "doc", "historico", "incidente"])
    return {
        "kind": "investigation" if is_investigation else "conversation",
        "needs_zabbix": needs_zabbix,
        "needs_knowledge": needs_knowledge,
        "raw": question,
    }


def build_investigation_plan(question: str, modules: List[str], capabilities: Dict[str, List[str]], knowledge_hint: str) -> str:
    parts = [
        "Plano de investigação do SOFIA:",
        "1. Verificar contexto operacional no Zabbix e nos alertas ativos.",
        "2. Correlacionar métricas e eventos com o histórico de incidentes.",
        "3. Consultar Knowledge e runbooks para identificar causa provável.",
        "4. Responder com uma hipótese objetiva e próxima do estado real do ambiente.",
    ]
    if "zabbix" in modules:
        parts.append(f"Zabbix disponível: {', '.join(capabilities.get('zabbix', []))}.")
    if knowledge_hint:
        parts.append(f"Contexto encontrado: {knowledge_hint}")
    return "\n".join(parts)
