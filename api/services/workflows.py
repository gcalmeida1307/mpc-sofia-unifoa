from __future__ import annotations

from connectors.n8n import n8n_connector


def list_n8n_templates():
    return {
        "templates": [
            {
                "id": "incident-correlation",
                "webhook": "sofia-investigation",
                "description": "Recebe evento, consulta contexto e abre plano de ação.",
                "payload_example": {
                    "incident": "lab-12-down",
                    "source": "zabbix",
                    "priority": "high",
                },
            },
            {
                "id": "auto-remediation",
                "webhook": "sofia-remediation",
                "description": "Dispara esteira de mitigação e comunicação.",
                "payload_example": {
                    "incident": "sql-latency",
                    "action": "restart-service",
                    "notify": ["teams", "email"],
                },
            },
        ]
    }


def list_workflows():
    return {
        "workflows": [
            {
                "id": "host-down",
                "name": "Host caiu",
                "steps": [
                    "Consultar Zabbix",
                    "Consultar documentação",
                    "Consultar histórico",
                    "Sugerir solução",
                    "Executar script",
                    "Enviar Teams",
                ],
            }
        ]
    }


def run_workflow(workflow_id: str, event: dict):
    return {
        "workflow_id": workflow_id,
        "status": "planned",
        "event": event,
        "execution": {
            "phase": "consulta",
            "actions": [
                "Zabbix: coletar evidências",
                "Knowledge: recuperar contexto da falha",
                "Workflow: sugerir mitigação",
                "Marketplace: verificar ferramenta necessária",
            ],
        },
        "message": "Fluxo recebido para orquestração de resposta operacional.",
    }


def run_n8n_workflow(webhook_name: str, event: dict):
    payload = {
        "source": "sofia",
        "webhook": webhook_name,
        "event": event,
    }
    try:
        response = n8n_connector.trigger_webhook(webhook_name, payload)
        return {
            "status": "triggered",
            "webhook": webhook_name,
            "response": response,
        }
    except Exception as exc:
        return {
            "status": "error",
            "webhook": webhook_name,
            "error": str(exc),
        }
