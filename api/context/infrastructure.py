from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from time import perf_counter
from typing import Any

from config.settings import settings
from connectors.zabbix import ZabbixConnector
from core.event_bus import event_bus
from services.docker_service import DockerService
from services.postgres_store import postgres_store
from core.observability import SNAPSHOT_AGE, SNAPSHOT_DURATION


def _extract_group_name(question: str) -> str | None:
    q = question.lower()
    prd_match = re.search(r"\bprd\d+(?:-[a-z0-9_ -]+)?", q)
    if prd_match:
        return prd_match.group(0).strip()
    if "grupo " not in q:
        return None
    tail = q.split("grupo ", 1)[1]
    separators = [",", "?", ".", " no zabbix", " agora", " quais", " possui", " tem", " existem"]
    for sep in separators:
        if sep in tail:
            tail = tail.split(sep, 1)[0]
    group = tail.strip()
    return group or None


class SnapshotService:
    def __init__(self, refresh_seconds: int | None = None):
        self.refresh_seconds = int(refresh_seconds or settings.SNAPSHOT_INTERVAL_SECONDS)
        self._snapshot: dict[str, Any] | None = None
        self._last_refresh: datetime | None = None
        self._last_down_hosts: set[str] = set()

    @staticmethod
    def _detect_down_hosts(problems: list[dict[str, Any]]) -> set[str]:
        down_tokens = ["down", "unavailable", "link down", "indispon", "offline"]
        hosts: set[str] = set()
        for problem in problems:
            name = str(problem.get("name", "")).lower()
            if not any(token in name for token in down_tokens):
                continue
            for host in problem.get("hosts", []) or []:
                host_name = str(host).strip()
                if host_name:
                    hosts.add(host_name)
        return hosts

    def _publish_transitions(self, down_hosts: set[str], generated_at: str, total_problems: int) -> None:
        new_down = sorted(down_hosts - self._last_down_hosts)
        recovered = sorted(self._last_down_hosts - down_hosts)
        for host in new_down:
            event_bus.publish_sync(
                "host.down",
                {"host": host, "generated_at": generated_at, "problem_count": total_problems},
            )
        for host in recovered:
            event_bus.publish_sync(
                "host.recovered",
                {"host": host, "generated_at": generated_at, "problem_count": total_problems},
            )
        self._last_down_hosts = down_hosts

    def _is_stale(self) -> bool:
        if self._snapshot is None or self._last_refresh is None:
            return True
        return datetime.now(timezone.utc) - self._last_refresh > timedelta(seconds=self.refresh_seconds)

    def refresh(self) -> dict[str, Any]:
        started = perf_counter()
        snapshot: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "zabbix": {},
            "docker": {},
        }

        try:
            connector = ZabbixConnector()
            summary = connector.get_problem_summary(limit=2000)
            # Persist the same operational universe used by the summary so hourly
            # comparisons are not distorted by a rotating top-200 window.
            problems = connector.list_active_problems(limit=2000)
            down_hosts = self._detect_down_hosts(problems)
            group_summary = self._group_problem_summary(problems)
            snapshot["zabbix"] = {
                "host_count": connector.count_hosts(),
                "problem_summary": summary,
                "problems": problems,
                "down_hosts": sorted(down_hosts),
                "group_summary": group_summary,
            }
            self._publish_transitions(
                down_hosts=down_hosts,
                generated_at=snapshot["generated_at"],
                total_problems=len(problems),
            )
        except Exception as exc:
            snapshot["zabbix"] = {"error": str(exc), "problems": []}

        try:
            containers = DockerService().list_containers()
            if isinstance(containers, list):
                snapshot["docker"] = {
                    "containers": containers,
                    "container_count": len(containers),
                }
            else:
                snapshot["docker"] = {"containers": [], "error": containers}
        except Exception as exc:
            snapshot["docker"] = {"containers": [], "error": str(exc)}

        self._snapshot = snapshot
        self._last_refresh = datetime.now(timezone.utc)

        self._persist_snapshot(snapshot)
        SNAPSHOT_DURATION.observe(perf_counter() - started)
        SNAPSHOT_AGE.set(0)
        return snapshot

    @staticmethod
    def _group_problem_summary(problems: list[dict[str, Any]]) -> list[dict[str, Any]]:
        totals: dict[str, int] = {}
        for problem in problems:
            for group in problem.get("groups", []) or []:
                totals[group] = totals.get(group, 0) + 1
        ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
        return [{"group": group, "occurrences": count} for group, count in ranked[:20]]

    @staticmethod
    def _persist_snapshot(snapshot: dict[str, Any]) -> None:
        zabbix = snapshot.get("zabbix", {}) if isinstance(snapshot.get("zabbix", {}), dict) else {}
        docker = snapshot.get("docker", {}) if isinstance(snapshot.get("docker", {}), dict) else {}
        summary = {
            "hosts": zabbix.get("host_count", 0),
            "problems": int((zabbix.get("problem_summary", {}) or {}).get("total_problems", len(zabbix.get("problems", []) or [])) or 0),
            "containers": docker.get("container_count", 0),
            "groups": len(zabbix.get("group_summary", []) or []),
        }
        postgres_store.save_snapshot(domain_id="infrastructure", snapshot=snapshot, summary=summary)

    def get(self, force_refresh: bool = False) -> dict[str, Any]:
        if force_refresh or self._is_stale():
            return self.refresh()
        if self._last_refresh:
            SNAPSHOT_AGE.set(max(0, (datetime.now(timezone.utc) - self._last_refresh).total_seconds()))
        return self._snapshot or self.refresh()


class InfrastructureProvider:
    def __init__(self, service: SnapshotService):
        self.service = service

    def execute(self, tool_name: str, question: str) -> dict[str, Any]:
        snapshot = self.service.get()

        if tool_name == "zabbix.count_hosts":
            group_name = _extract_group_name(question)
            if group_name:
                return {"host_count": ZabbixConnector().count_hosts_in_group(group_name), "group": group_name}
            return {"host_count": snapshot.get("zabbix", {}).get("host_count", 0)}

        if tool_name == "zabbix.list_problems":
            group_name = _extract_group_name(question)
            problems = snapshot.get("zabbix", {}).get("problems", [])
            if group_name:
                connector = ZabbixConnector()
                problems = connector.list_active_problems(limit=200, group_name=group_name)
            return {
                "group": group_name,
                "summary": snapshot.get("zabbix", {}).get("problem_summary", {}),
                "problems": problems,
            }

        if tool_name == "docker.list_containers":
            return {
                "containers": snapshot.get("docker", {}).get("containers", []),
                "container_count": snapshot.get("docker", {}).get("container_count", 0),
            }

        return {"error": f"unsupported infrastructure tool: {tool_name}"}


snapshot_service = SnapshotService()
infrastructure_provider = InfrastructureProvider(snapshot_service)
