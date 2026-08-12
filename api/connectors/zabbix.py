import requests
import time
from datetime import datetime, timedelta, timezone

from config.settings import settings
from core.observability import INTEGRATION_LATENCY, INTEGRATION_REQUESTS


class ZabbixConnector:
    _circuit_failures = 0
    _circuit_open_until = 0.0

    def __init__(self):
        self.token = None

    def _post(self, url: str, **kwargs):
        timeout = kwargs.pop("timeout", settings.REQUEST_TIMEOUT)
        if time.monotonic() < self.__class__._circuit_open_until:
            INTEGRATION_REQUESTS.labels(integration="zabbix", operation="jsonrpc", status="circuit_open").inc()
            raise requests.ConnectionError("Zabbix temporariamente indisponível; circuito aberto")
        started = time.perf_counter()
        last_error: Exception | None = None
        try:
            for attempt in range(2):
                try:
                    response = requests.post(url, timeout=timeout, **kwargs)
                    if response.status_code >= 500 and attempt == 0:
                        time.sleep(0.08)
                        continue
                    response.raise_for_status()
                    self.__class__._circuit_failures = 0
                    INTEGRATION_REQUESTS.labels(integration="zabbix", operation="jsonrpc", status="success").inc()
                    return response
                except requests.RequestException as exc:
                    last_error = exc
                    # A timeout already consumed the configured budget. Retrying it
                    # synchronously would double chat latency; the next snapshot
                    # cycle is the safe retry boundary.
                    break
            self.__class__._circuit_failures += 1
            if self.__class__._circuit_failures >= 3:
                self.__class__._circuit_open_until = time.monotonic() + 20
            INTEGRATION_REQUESTS.labels(integration="zabbix", operation="jsonrpc", status="failure").inc()
            raise last_error or requests.ConnectionError("Falha no Zabbix")
        finally:
            INTEGRATION_LATENCY.labels(integration="zabbix", operation="jsonrpc").observe(time.perf_counter() - started)

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
        response = self._post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        self.token = data["result"]
        return self.token

    def _api_call(self, method: str, params: dict, request_id: int = 90):
        if not self.token:
            self.login()
        payload = {"jsonrpc":"2.0","method":method,"params":params,"auth":self.token,"id":request_id}
        response = self._post(settings.ZABBIX_URL, json=payload, timeout=settings.REQUEST_TIMEOUT)
        data=response.json()
        if "error" in data:
            raise Exception(data["error"])
        return data.get("result", [])

    def get_trigger_diagnostics(self, trigger_ids: list[str]) -> dict[str, dict]:
        if not trigger_ids:
            return {}
        rows=self._api_call("trigger.get", {
            "triggerids":sorted(set(trigger_ids)),
            "output":["triggerid","description","expression","priority","status","state","value","lastchange","opdata","comments","url"],
            "selectFunctions":["itemid","function","parameter"],
            "selectDependencies":["triggerid","description","status","value"],
            "selectHosts":["hostid","host","name"],
            "selectTags":["tag","value"],
        },91)
        return {str(row.get("triggerid")):row for row in rows}

    def get_items(self, item_ids: list[str]) -> dict[str, dict]:
        if not item_ids:
            return {}
        rows=self._api_call("item.get", {
            "itemids":sorted(set(item_ids)),
            "output":["itemid","hostid","name","key_","lastvalue","prevvalue","lastclock","units","value_type","status","state","error","delay","history","trends"],
            "selectHosts":["hostid","host","name"],
            "selectValueMap":["mappings"],
        },92)
        return {str(row.get("itemid")):row for row in rows}

    def search_items(self, host_ids: list[str], text: str, limit: int = 100) -> list[dict]:
        if not host_ids or not text.strip():
            return []
        return self._api_call("item.get", {"hostids":sorted(set(host_ids)),"output":["itemid","hostid","name","key_","lastvalue","prevvalue","lastclock","units","value_type","status","state","error"],"search":{"name":text.strip(),"key_":text.strip()},"searchByAny":True,"sortfield":"name","limit":max(1,min(limit,300))},99)

    def get_item_history(self, items: list[dict], *, hours: int = 2, limit: int = 1200) -> dict[str, list[dict]]:
        grouped: dict[int,list[str]]={}
        for item in items:
            grouped.setdefault(int(item.get("value_type",0) or 0),[]).append(str(item.get("itemid")))
        result: dict[str,list[dict]]={}
        time_from=int((datetime.now(timezone.utc)-timedelta(hours=max(1,min(hours,24)))).timestamp())
        for value_type,itemids in grouped.items():
            rows=self._api_call("history.get", {"history":value_type,"itemids":itemids,"time_from":time_from,"sortfield":"clock","sortorder":"ASC","limit":limit,"output":"extend"},93+value_type)
            for row in rows:
                result.setdefault(str(row.get("itemid")),[]).append({"clock":row.get("clock"),"value":row.get("value"),"ns":row.get("ns")})
        return result

    def get_host_diagnostics(self, host_ids: list[str]) -> dict[str, dict]:
        if not host_ids:
            return {}
        rows=self._api_call("host.get", {"hostids":sorted(set(host_ids)),"output":["hostid","host","name","status","description"],"selectInterfaces":["interfaceid","type","ip","dns","port","main","available","error"],"selectInventory":"extend","selectParentTemplates":["templateid","name"],"selectTags":["tag","value"]},100)
        return {str(row.get("hostid")):row for row in rows}

    def count_trigger_recurrence(self, trigger_ids: list[str], days: int = 7) -> dict[str, int]:
        if not trigger_ids:
            return {}
        rows=self._api_call("event.get", {"source":0,"object":0,"objectids":sorted(set(trigger_ids)),"value":1,"time_from":int((datetime.now(timezone.utc)-timedelta(days=max(1,min(days,30)))).timestamp()),"output":["objectid"],"limit":10000},110)
        counts: dict[str,int]={}
        for row in rows:
            key=str(row.get("objectid"));counts[key]=counts.get(key,0)+1
        return counts

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
        response = self._post(
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
        response = self._post(
            settings.ZABBIX_URL,
            json=payload,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        return data.get("result", [])

    def get_trigger_events(self, days: int, limit: int = 5000, groupids: list[str] | None = None):
        if not self.token:
            self.login()
        params = {
            "output": ["eventid", "name", "severity", "clock", "objectid", "value"],
            "source": 0, "object": 0, "value": 1,
            "time_from": int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp()),
            "sortfield": ["clock"], "sortorder": "DESC", "limit": limit,
        }
        if groupids:
            params["groupids"] = groupids
        payload = {"jsonrpc":"2.0","method":"event.get","params":params,"auth":self.token,"id":7}
        response = self._post(settings.ZABBIX_URL, json=payload, timeout=settings.REQUEST_TIMEOUT)
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
        response = self._post(
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
        response = self._post(
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
        response = self._post(
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
            host_refs = [
                {
                    "hostid": str(host.get("hostid", "")),
                    "name": host.get("name") or host.get("host") or "",
                    "groups": host_groups.get(str(host.get("hostid")), []),
                }
                for host in hosts
                if host.get("hostid")
            ]
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
                    "objectid": problem.get("objectid"),
                    "name": problem.get("name"),
                    "severity": severity,
                    "severity_label": severity_map.get(severity, severity),
                    "clock": problem.get("clock"),
                    "group_filter": group_name,
                    "hosts": host_names,
                    "host_refs": host_refs,
                    "groups": groups,
                }
            )

        return enriched

    def list_trigger_events(self, days: int = 7, limit: int = 5000, group_name: str | None = None):
        groupids = self.find_hostgroup_ids(group_name) if group_name else None
        if group_name and not groupids:
            return []
        events = self.get_trigger_events(days=days, limit=limit, groupids=groupids)
        trigger_ids = sorted({str(event.get("objectid")) for event in events if event.get("objectid")})
        trigger_hosts = self.get_hosts_for_triggers(trigger_ids)
        host_ids = sorted({str(host.get("hostid")) for hosts in trigger_hosts.values() for host in hosts if host.get("hostid")})
        host_groups = self.get_groups_for_hostids(host_ids)
        severity_map = {"0":"Not classified","1":"Information","2":"Warning","3":"Average","4":"High","5":"Disaster"}
        enriched = []
        for event in events:
            hosts = trigger_hosts.get(str(event.get("objectid")), [])
            refs = [{"hostid":str(host.get("hostid", "")),"name":host.get("name") or host.get("host") or "",
                     "groups":host_groups.get(str(host.get("hostid")), [])} for host in hosts if host.get("hostid")]
            groups = sorted({group for ref in refs for group in ref["groups"]})
            severity = str(event.get("severity", "0"))
            enriched.append({"eventid":event.get("eventid"),"objectid":event.get("objectid"),"name":event.get("name"),
                "severity":severity,"severity_label":severity_map.get(severity,severity),"clock":event.get("clock"),
                "hosts":[ref["name"] for ref in refs],"host_refs":refs,"groups":groups,"historical":True})
        return enriched

    def list_groups(self, limit: int = 200) -> list[dict]:
        if not self.token:
            self.login()
        payload = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {"output": ["groupid", "name"], "selectHosts": ["hostid"], "sortfield": "name", "limit": limit},
            "auth": self.token,
            "id": 20,
        }
        response = self._post(settings.ZABBIX_URL, json=payload, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        return [{"groupid": str(item.get("groupid")), "name": item.get("name", ""), "hosts": len(item.get("hosts", []) or [])} for item in data.get("result", [])]

    def create_group(self, name: str) -> dict:
        if not self.token:
            self.login()
        payload = {
            "jsonrpc": "2.0",
            "method": "hostgroup.create",
            "params": [{"name": name}],
            "auth": self.token,
            "id": 21,
        }
        response = self._post(settings.ZABBIX_URL, json=payload, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise Exception(data["error"])
        return {"name": name, "groupids": data.get("result", {}).get("groupids", [])}
