from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import re
from threading import Lock
from typing import Any
from zoneinfo import ZoneInfo

from services.postgres_store import postgres_store


DOWN_TOKENS = ("link down", "unavailable", "indispon", "offline", "not responding")
ENTITY_PATTERNS = (
    re.compile(r"(?i)interface\s+([^:()]+(?:/[^:() ]+)*)"),
    re.compile(r"(?i)port(?:a)?\s+([A-Za-z]*\d+(?:/\d+)*)"),
)


class BehaviorPatternAnalyzer:
    """Detect schedules from persisted observations without delegating calculations to an LLM."""

    def __init__(self, domain_id: str = "infrastructure", timezone_name: str = "America/Sao_Paulo"):
        self.domain_id = domain_id
        self.timezone = ZoneInfo(timezone_name)
        self._last_run: datetime | None = None
        self._cache: list[dict[str, Any]] = []
        self._lock = Lock()

    @staticmethod
    def _entity(problem: dict[str, Any]) -> str:
        text = str(problem.get("name") or "")
        for pattern in ENTITY_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        return text[:100] or "indisponibilidade"

    def analyze(self, snapshots: list[dict[str, Any]], min_samples: int = 24) -> list[dict[str, Any]]:
        records: dict[tuple[str, str], dict[str, Any]] = defaultdict(
            lambda: {"down": [0] * 24, "seen": [0] * 24, "days": set(), "groups": set(), "examples": []}
        )
        ordered = sorted(snapshots, key=lambda item: str(item.get("generated_at") or ""))
        all_keys: set[tuple[str, str]] = set();parsed: list[tuple[datetime, list[dict[str, Any]]]] = []
        for snapshot in ordered:
            try: at = datetime.fromisoformat(str(snapshot.get("generated_at"))).astimezone(self.timezone)
            except (TypeError, ValueError): continue
            problems = ((snapshot.get("payload") or {}).get("zabbix") or {}).get("problems") or [];scoped=[]
            for problem in problems:
                if not any(token in str(problem.get("name") or "").lower() for token in DOWN_TOKENS): continue
                entity=self._entity(problem)
                for host in problem.get("hosts") or []:
                    key=(str(host),entity);all_keys.add(key);scoped.append({"key":key,"problem":problem})
            parsed.append((at,scoped))
        for at,scoped in parsed:
            active={item["key"] for item in scoped}
            for key in all_keys:
                records[key]["seen"][at.hour]+=1
                if key in active:records[key]["down"][at.hour]+=1;records[key]["days"].add(at.date().isoformat())
            for item in scoped:
                record=records[item["key"]];record["groups"].update(item["problem"].get("groups") or [])
                if len(record["examples"])<3:record["examples"].append(str(item["problem"].get("name") or ""))
        patterns=[];night_hours=tuple(range(18,24))+tuple(range(0,8));business_hours=tuple(range(8,18))
        for (host,entity),data in records.items():
            night_seen=sum(data["seen"][h] for h in night_hours);night_down=sum(data["down"][h] for h in night_hours)
            business_seen=sum(data["seen"][h] for h in business_hours);business_down=sum(data["down"][h] for h in business_hours)
            if night_seen<min_samples or business_seen<max(6,min_samples//4) or len(data["days"])<3:continue
            night_rate=night_down/night_seen;business_rate=business_down/business_seen
            if night_rate<.55 or business_rate>.30 or night_rate-business_rate<.40:continue
            confidence=round(min(.99,.55+(night_rate-business_rate)*.35+min(len(data["days"]),10)*.02),2)
            likely_admin=any(token in " ".join(data["groups"]).lower() for token in ("admin","jurid","rh","finance","secretar","portaria"))
            patterns.append({"id":sha256(f"{host}|{entity}|night_schedule".encode()).hexdigest()[:16],"kind":"scheduled_availability","host":host,"entity":entity,"classification":"rotina administrativa provável" if likely_admin else "rotina programada provável","summary":f"{host} · {entity} fica indisponível predominantemente fora do horário comercial e retorna durante o expediente.","night_down_rate":round(night_rate,3),"business_down_rate":round(business_rate,3),"observed_days":len(data["days"]),"samples":night_seen+business_seen,"confidence":confidence,"groups":sorted(data["groups"]),"evidence":data["examples"],"recommended_action":"Validar com o responsável se o desligamento é intencional; se confirmado, criar janela de manutenção ou dependência para reduzir falso positivo sem ocultar falhas fora do padrão.","deviation_rule":"Alertar quando não retornar no início do expediente ou cair durante o horário comercial."})
        return sorted(patterns,key=lambda item:(item["confidence"],item["observed_days"]),reverse=True)

    def run_cycle(self, force: bool = False) -> dict[str, Any]:
        with self._lock:
            now=datetime.now(timezone.utc)
            if not force and self._last_run and now-self._last_run<timedelta(hours=1):return {"status":"not_due","patterns":self._cache,"next_cycle":(self._last_run+timedelta(hours=1)).isoformat()}
            snapshots=postgres_store.get_sampled_snapshots(self.domain_id,scan_limit=2200,stride=5);self._cache=self.analyze(snapshots);self._last_run=now
            for pattern in self._cache[:50]:postgres_store.save_insight(pattern["id"],"behavior.scheduled_availability",pattern["summary"],pattern)
            return {"status":"completed","patterns":self._cache,"snapshot_count":len(snapshots),"generated_at":now.isoformat()}

    def patterns(self, force: bool = False) -> dict[str, Any]:return self.run_cycle(force=force or not self._cache)


behavior_pattern_analyzer=BehaviorPatternAnalyzer()
