from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from connectors.zabbix import ZabbixConnector
from core.registry import registry
from services.docker_service import DockerService


class InfrastructureSnapshotService:
    def __init__(self):
        self._snapshot: dict[str, Any] | None = None

    def refresh(self) -> dict[str, Any]:
        snapshot: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "modules": registry.list_modules(),
            "capabilities": registry.get_snapshot().get("capabilities", {}),
            "zabbix": {},
            "docker": {},
        }

        try:
            connector = ZabbixConnector()
            snapshot["zabbix"] = {
                "host_count": connector.count_hosts(),
                "problem_summary": connector.get_problem_summary(limit=200),
                "top_problems": connector.list_active_problems(limit=10),
            }
        except Exception as exc:
            snapshot["zabbix"] = {"error": str(exc)}

        try:
            docker = DockerService()
            snapshot["docker"] = {
                "containers": docker.list_containers(),
            }
        except Exception as exc:
            snapshot["docker"] = {"error": str(exc)}

        self._snapshot = snapshot
        return snapshot

    def get(self) -> dict[str, Any]:
        if self._snapshot is None:
            return self.refresh()
        return self._snapshot


infrastructure_snapshot = InfrastructureSnapshotService()
