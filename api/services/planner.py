from __future__ import annotations


def build_plan(question: str) -> dict:
    q = question.lower()
    steps = []
    capabilities = []

    if any(token in q for token in ["problema", "alerta", "indispon", "severity", "zabbix"]):
        steps.extend([
            "Ler snapshot de problemas e hosts no Zabbix.",
            "Filtrar por grupo/severidade quando informado.",
            "Cruzar com runbook e histórico para sugerir ação.",
        ])
        capabilities.extend(["zabbix.problems", "knowledge.search"])

    if any(token in q for token in ["docker", "container"]):
        steps.append("Ler snapshot de containers e status no Docker.")
        capabilities.append("docker.list_containers")

    if any(token in q for token in ["n8n", "workflow", "automacao", "automação"]):
        steps.append("Sugerir ou disparar workflow de investigação no n8n.")
        capabilities.append("n8n.trigger_webhook")

    if not steps:
        steps.append("Responder com base no contexto consolidado do snapshot e knowledge.")

    return {
        "intent": "operational-investigation",
        "steps": steps,
        "capabilities": sorted(set(capabilities)),
    }
