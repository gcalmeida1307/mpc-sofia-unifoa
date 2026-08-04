import requests

from config.settings import settings


class ZabbixConnector:
    def __init__(self):
        self.token = None

    def login(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": settings.ZABBIX_USER,
                "password": settings.ZABBIX_PASSWORD,
            },
            "id": 1,
        }
        response = requests.post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        self.token = data["result"]
        return self.token

    def get_hosts(self, groupids: list[str] | None = None):
        if not self.token:
            self.login()

        params = {
            "output": ["hostid", "host", "name"],
            "selectInterfaces": ["ip"],
        }
        if groupids:
            params["groupids"] = groupids
        payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": params,
            "auth": self.token,
            "id": 2,
        }
        response = requests.post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        return data.get("result", [])

    def count_hosts(self):
        return len(self.get_hosts())

    def count_hosts_in_group(self, group_name: str) -> int:
        groupids = self.find_hostgroup_ids(group_name)
        return len(self.get_hosts(groupids=groupids)) if groupids else 0

    def get_active_problems(self, limit: int = 100, groupids: list[str] | None = None):
        if not self.token:
            self.login()

        params = {
            "output": ["eventid", "name", "severity", "clock", "objectid"],
            "recent": True,
            "sortfield": ["eventid"],
            "sortorder": "DESC",
            "limit": limit,
        }
        if groupids:
            params["groupids"] = groupids

        payload = {
            "jsonrpc": "2.0",
            "method": "problem.get",
            "params": params,
            "auth": self.token,
            "id": 3,
        }
        response = requests.post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        return data.get("result", [])

    def get_hosts_for_triggers(self, trigger_ids: list[str]):
        if not trigger_ids:
            return {}
        if not self.token:
            self.login()

        payload = {
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "output": ["triggerid"],
                "triggerids": trigger_ids,
                "selectHosts": ["hostid", "host", "name"],
            },
            "auth": self.token,
            "id": 4,
        }
        response = requests.post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])

        mapping = {}
        for item in data.get("result", []):
            mapping[str(item.get("triggerid"))] = item.get("hosts", [])
        return mapping

    def get_groups_for_hostids(self, host_ids: list[str]):
        if not host_ids:
            return {}
        if not self.token:
            self.login()

        payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid"],
                "hostids": host_ids,
                "selectGroups": ["groupid", "name"],
            },
            "auth": self.token,
            "id": 6,
        }
        response = requests.post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])

        mapping = {}
        for host in data.get("result", []):
            hid = str(host.get("hostid"))
            groups = host.get("groups", []) or []
            mapping[hid] = [group.get("name", "") for group in groups if group.get("name")]
        return mapping

    def find_hostgroup_ids(self, group_name: str):
        if not self.token:
            self.login()

        payload = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": ["groupid", "name"],
                "search": {"name": group_name},
                "searchByAny": True,
            },
            "auth": self.token,
            "id": 5,
        }
        response = requests.post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        return [str(item.get("groupid")) for item in data.get("result", []) if item.get("groupid")]

    def get_problem_summary(self, limit: int = 200):
        problems = self.get_active_problems(limit=limit)
        host_ids = set()
        severity_buckets = {str(level): 0 for level in range(6)}
        trigger_ids = [str(problem.get("objectid")) for problem in problems if problem.get("objectid")]
        trigger_hosts = self.get_hosts_for_triggers(trigger_ids)

        for problem in problems:
            severity = str(problem.get("severity", "0"))
            if severity in severity_buckets:
                severity_buckets[severity] += 1
            for host in trigger_hosts.get(str(problem.get("objectid")), []):
                host_id = host.get("hostid")
                if host_id:
                    host_ids.add(host_id)

        return {
            "total_problems": len(problems),
            "affected_hosts": len(host_ids),
            "severity_buckets": severity_buckets,
        }

    def list_active_problems(self, limit: int = 10, group_name: str | None = None):
        groupids = None
        if group_name:
            groupids = self.find_hostgroup_ids(group_name)
            if not groupids:
                return []

        problems = self.get_active_problems(limit=limit, groupids=groupids)
        trigger_ids = [str(problem.get("objectid")) for problem in problems if problem.get("objectid")]
        trigger_hosts = self.get_hosts_for_triggers(trigger_ids)
        host_ids = sorted(
            {
                str(host.get("hostid"))
                for hosts in trigger_hosts.values()
                for host in hosts
                if host.get("hostid")
            }
        )
        host_groups = self.get_groups_for_hostids(host_ids)

        severity_map = {
            "0": "Not classified",
            "1": "Information",
            "2": "Warning",
            "3": "Average",
            "4": "High",
            "5": "Disaster",
        }

        enriched = []
        for problem in problems:
            hosts = trigger_hosts.get(str(problem.get("objectid")), [])
            host_names = [host.get("name", "") for host in hosts if host.get("name")]
            groups = sorted(
                {
                    group_name_item
                    for host in hosts
                    for group_name_item in host_groups.get(str(host.get("hostid")), [])
                }
            )
            severity = str(problem.get("severity", "0"))
            enriched.append(
                {
                    "eventid": problem.get("eventid"),
                    "name": problem.get("name"),
                    "severity": severity,
                    "severity_label": severity_map.get(severity, severity),
                    "group_filter": group_name,
                    "hosts": host_names,
                    "groups": groups,
                }
            )

        return enriched
