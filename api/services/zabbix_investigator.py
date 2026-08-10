from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from ai.operational_query import normalize, related_problems
from connectors.zabbix import ZabbixConnector


QUERY_ALIASES = {
    "enlace indisponivel":"link down", "porta operando abaixo":"lower speed",
    "equipamento sem resposta":"unavailable icmp", "armazenamento sob pressao":"disk",
    "ponto de acesso instavel":"airtime", "cpu elevada":"cpu", "memoria elevada":"memory",
}
LOCAL_TIMEZONE=ZoneInfo("America/Sao_Paulo")


def _epoch(value: Any) -> str | None:
    try:return datetime.fromtimestamp(int(value),tz=timezone.utc).astimezone(LOCAL_TIMEZONE).isoformat()
    except (TypeError,ValueError,OSError):return None


def _entity_label(*values: str) -> str | None:
    corpus=" ".join(values)
    patterns=(r"(?i)interface\s+([^:()]+(?:/[^:() ]+)*)",r"(?i)port(?:a)?\s+([A-Za-z]*\d+(?:/\d+)*)",r'(?i)"([^"]+)"\s*\(')
    for pattern in patterns:
        match=re.search(pattern,corpus)
        if match:return match.group(1).strip()
    key_match=re.search(r"\[([^,\]]+)",corpus)
    return key_match.group(1).strip() if key_match else None


def _numeric_summary(samples: list[dict]) -> dict[str, Any] | None:
    parsed=[]
    for sample in samples:
        try:parsed.append((int(sample.get("clock")),float(sample.get("value"))))
        except (TypeError,ValueError):continue
    if not parsed:return None
    parsed.sort();values=[item[1] for item in parsed]
    state_changes=sum(1 for index in range(1,len(values)) if values[index]!=values[index-1])
    return {"samples":len(values),"first":values[0],"last":values[-1],"minimum":min(values),"maximum":max(values),"change":round(values[-1]-values[0],4),"state_changes":state_changes,"from":_epoch(parsed[0][0]),"to":_epoch(parsed[-1][0])}


def _interpreted_value(item: dict) -> str | None:
    key=str(item.get("key_","")).lower();value=str(item.get("lastvalue",""))
    if "ifoperstatus" in key:return {"1":"up","2":"down","3":"testing","4":"unknown","5":"dormant","6":"not present","7":"lower layer down"}.get(value)
    if "ifadminstatus" in key:return {"1":"up","2":"down","3":"testing"}.get(value)
    return None


class ZabbixInvestigator:
    def investigate(self, question: str, *, connector: ZabbixConnector | None = None, max_problems: int = 20, hours: int = 2, recurrence_days: int = 7) -> dict[str, Any]:
        connector=connector or ZabbixConnector();universe=connector.list_active_problems(limit=2000)
        normalized=normalize(question);search_question=question
        for source,target in QUERY_ALIASES.items():
            if source in normalized:search_question=f"{question} {target}"
        selected=related_problems(search_question,universe,limit=max(1,min(max_problems,50)))
        if not selected:
            selected=universe[:max(1,min(max_problems,50))]
        trigger_ids=sorted({str(item.get("objectid")) for item in selected if item.get("objectid")})
        triggers=connector.get_trigger_diagnostics(trigger_ids)
        item_ids=sorted({str(function.get("itemid")) for trigger in triggers.values() for function in (trigger.get("functions") or []) if function.get("itemid")})[:150]
        items=connector.get_items(item_ids);host_ids=sorted({str(ref.get("hostid")) for problem in selected for ref in (problem.get("host_refs") or []) if ref.get("hostid")})
        related_by_trigger: dict[str,list[str]]={}
        for problem in selected:
            trigger_id=str(problem.get("objectid") or "");trigger=triggers.get(trigger_id,{})
            direct=[items[str(function.get("itemid"))] for function in (trigger.get("functions") or []) if str(function.get("itemid")) in items]
            entity=_entity_label(str(problem.get("name", "")),*(str(item.get("name", "")) for item in direct),*(str(item.get("key_", "")) for item in direct))
            refs=problem.get("host_refs") or [];network_subject=any(token in normalize(str(problem.get("name",""))) for token in ("interface","porta","link","enlace"))
            if entity and refs and network_subject:
                related=connector.search_items([str(refs[0].get("hostid"))],entity,limit=100)
                entity_pattern=re.compile(rf"(?<!\d){re.escape(entity)}(?!\d)",re.IGNORECASE)
                related=[item for item in related if entity_pattern.search(f"{item.get('name','')} {item.get('key_','')}")]
                related_by_trigger[trigger_id]=[str(item.get("itemid")) for item in related if item.get("itemid")]
                for item in related:
                    if item.get("itemid"):items[str(item.get("itemid"))]=item
        hosts=connector.get_host_diagnostics(host_ids);history=connector.get_item_history(list(items.values()),hours=hours);recurrence=connector.count_trigger_recurrence(trigger_ids,days=recurrence_days)
        evidence=[];missing=set()
        for problem in selected:
            trigger_id=str(problem.get("objectid") or "");trigger=triggers.get(trigger_id,{})
            network_subject=any(token in normalize(str(problem.get("name",""))) for token in ("interface","porta","link","enlace"))
            selected_item_ids=[]
            for item_id in [str(function.get("itemid")) for function in (trigger.get("functions") or [])]+related_by_trigger.get(trigger_id,[]):
                if item_id in items and item_id not in selected_item_ids:selected_item_ids.append(item_id)
            trigger_items=[items[item_id] for item_id in selected_item_ids]
            entity=_entity_label(str(problem.get("name", "")),*(str(item.get("name", "")) for item in trigger_items),*(str(item.get("key_", "")) for item in trigger_items))
            item_evidence=[]
            for item in trigger_items:
                samples=history.get(str(item.get("itemid")),[])
                item_evidence.append({"itemid":item.get("itemid"),"name":item.get("name"),"key":item.get("key_"),"current_value":item.get("lastvalue"),"interpreted_value":_interpreted_value(item),"previous_value":item.get("prevvalue"),"units":item.get("units"),"last_collected_at":_epoch(item.get("lastclock")),"enabled":str(item.get("status","0"))=="0","supported":str(item.get("state","0"))=="0","error":item.get("error") or None,"history_summary":_numeric_summary(samples),"recent_samples":samples[-8:]})
            if not trigger_items:missing.add("A trigger não expôs itens de origem")
            if trigger_items and not any(history.get(str(item.get("itemid"))) for item in trigger_items):missing.add("Sem amostras históricas no período consultado")
            item_corpus=" ".join(f"{item.get('name','')} {item.get('key_','')}" for item in trigger_items).lower();coverage_gaps=[]
            if entity and network_subject:
                if "ifadminstatus" not in item_corpus:coverage_gaps.append("Estado administrativo da porta não coletado")
                if not any(token in item_corpus for token in ("lldp","cdp","neighbor")):coverage_gaps.append("Equipamento conectado não identificado por LLDP/CDP")
                if not any(token in item_corpus for token in ("error","crc")):coverage_gaps.append("Erros da interface não coletados")
                if not any(token in item_corpus for token in ("bits received","bits sent","octets")):coverage_gaps.append("Tráfego da interface não coletado")
                missing.update(coverage_gaps)
            refs=problem.get("host_refs") or [];host_detail=hosts.get(str(refs[0].get("hostid")),{}) if refs else {}
            evidence.append({"problem":problem.get("name"),"eventid":problem.get("eventid"),"triggerid":trigger_id,"severity":problem.get("severity_label"),"started_at":_epoch(problem.get("clock")),"entity":entity,"hosts":problem.get("hosts") or [],"groups":problem.get("groups") or [],"trigger":{"enabled":str(trigger.get("status","0"))=="0","state":trigger.get("state"),"last_change_at":_epoch(trigger.get("lastchange")),"operational_data":trigger.get("opdata") or None,"dependencies":trigger.get("dependencies") or [],"tags":trigger.get("tags") or []},"items":item_evidence,"host":{"description":host_detail.get("description") or None,"interfaces":host_detail.get("interfaces") or [],"inventory":host_detail.get("inventory") or {},"templates":[item.get("name") for item in (host_detail.get("parentTemplates") or [])]},"recurrence":{"days":recurrence_days,"occurrences":recurrence.get(trigger_id,0)},"data_coverage":{"complete":not coverage_gaps,"gaps":coverage_gaps}})
        return {"status":"completed","scope":{"question":question,"active_universe":len(universe),"selected_problems":len(selected),"trigger_count":len(triggers),"item_count":len(items),"host_count":len(hosts),"history_hours":hours,"recurrence_days":recurrence_days},"evidence":evidence,"missing_data":sorted(missing),"guardrails":{"read_only":True,"problem_limit":max_problems,"item_limit":150,"claude_calculates_evidence":False}}


zabbix_investigator=ZabbixInvestigator()


def format_investigation(result: dict[str, Any]) -> str:
    scope=result.get("scope",{});evidence=result.get("evidence",[]) or []
    if not evidence:return "A investigação não encontrou problemas ativos relacionados no Zabbix."
    recurring=sum(1 for entry in evidence if int((entry.get('recurrence') or {}).get('occurrences',0) or 0)>1)
    lines=["Conclusão",f"O Zabbix confirmou {scope.get('selected_problems',0)} problema(s) em {scope.get('host_count',0)} equipamento(s). {recurring} ocorrência(s) são recorrentes no período analisado.","", "Evidências prioritárias"]
    for entry in evidence[:5]:
        host=", ".join(entry.get("hosts",[]) or []) or "equipamento não identificado";entity=f" · componente {entry.get('entity')}" if entry.get("entity") else ""
        items=entry.get("items",[]) or []
        recurrence=(entry.get("recurrence") or {}).get("occurrences",0)
        lines.append(f"- {host}{entity}: {entry.get('problem')} · desde {entry.get('started_at') or 'horário não informado'} · {recurrence} ocorrência(s) em {entry.get('recurrence',{}).get('days',7)} dias")
        preferred=[item for item in items if any(token in str(item.get("name","")).lower() for token in ("operational status","speed","bits received","bits sent","error","discard","cpu","memory","disk","service"))][:3]
        for item in preferred:
            label=item.get("name") or item.get("key") or "Item";unit=item.get("units") or "";interpreted=f" ({item.get('interpreted_value')})" if item.get("interpreted_value") else ""
            history=item.get("history_summary") or {};history_note=f"; {history.get('samples')} amostras e {history.get('state_changes',0)} mudança(s)" if history else "; sem histórico"
            lines.append(f"  - {label}: {item.get('current_value')} {unit}{interpreted}{history_note}".rstrip())
    lines.extend(["", "Tendência", "- Recorrência detectada; priorize equipamentos com mais de uma ocorrência. " if recurring else "- Não há recorrência suficiente para afirmar tendência; continue coletando amostras."])
    missing=result.get("missing_data",[]) or []
    if missing:lines.extend(["", "Limites", "- "+"; ".join(missing)+"."])
    lines.extend(["", "Próxima ação", "1. Abra o equipamento com maior recorrência e valide o componente e os valores destacados.", "2. Não atribua cabo, energia ou core quando a coleta não comprovar essa causa.", "3. Depois da intervenção, confirme normalização e ausência de nova ocorrência no Zabbix."])
    return "\n".join(lines)
