def get_marketplace_catalog():
    return {
        "platform": "SOFIA Marketplace",
        "modules": [
            {
                "name": "Redis",
                "category": "cache",
                "status": "available",
            },
            {
                "name": "PostgreSQL",
                "category": "database",
                "status": "available",
            },
            {
                "name": "Grafana",
                "category": "observability",
                "status": "available",
            },
            {
                "name": "Prometheus",
                "category": "monitoring",
                "status": "available",
            },
            {
                "name": "Qdrant",
                "category": "vector-search",
                "status": "available",
            },
            {
                "name": "n8n",
                "category": "automation",
                "status": "available",
            },
            {
                "name": "MinIO",
                "category": "object-storage",
                "status": "available",
            },
            {
                "name": "RabbitMQ",
                "category": "messaging",
                "status": "available",
            },
        ],
    }


def install_module(module_name: str, version: str | None = None):
    return {
        "status": "planned",
        "module_name": module_name,
        "version": version,
        "actions": [
            "backup",
            "update compose",
            "start container",
            "register module",
            "expose MCP tools",
            "document installation",
        ],
        "message": f"Solicitação recebida para instalar {module_name} pelo marketplace.",
    }
