from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from services.postgres_store import postgres_store


RULESET_VERSION = "executive-health-v1"
SEVERITY_WEIGHT = {0: 0.1, 1: 0.25, 2: 0.75, 3: 1.5, 4: 3.0, 5: 5.0}
DOMAINS = {
    "Rede": ("switch", "access-point", "roteador", "router", "rede", "network"),
    "Servidores": ("servidor", "server", "hyperv", "windows", "linux"),
    "Telefonia": ("telefon", "voip", "pabx", "sip"),
    "Storage": ("storage", "san", "nas", "disk", "disco", "filesystem"),
    "Segurança": ("firewall", "security", "seguranca", "vpn", "auth"),
}
RISK_RULES = (
    ("broadcast", "Broadcast crescente", "Tráfego de difusão acima do padrão pode degradar todo o segmento.", "Verificar uplinks e possíveis loops", ["Identificar os equipamentos com maior recorrência", "Validar STP e loops nos uplinks", "Comparar o tráfego após a correção"]),
    ("backup", "Backup acima do normal", "A janela de backup está consumindo mais recurso ou tempo que o esperado.", "Validar duração e janela do backup", ["Confirmar o início e o fim do backup", "Comparar disco e rede no mesmo horário", "Reagendar ou limitar a carga se necessário"]),
    ("cpu", "CPU elevada", "Processamento elevado pode aumentar latência ou interromper serviços.", "Revisar os equipamentos mais afetados", ["Ordenar equipamentos por recorrência", "Identificar processo ou carga coincidente", "Acompanhar a CPU depois da intervenção"]),
    ("unavailable by icmp", "Equipamento sem resposta", "O monitoramento perdeu comunicação com um ou mais equipamentos.", "Validar energia, enlace e conectividade", ["Confirmar energia e conexão física", "Testar o caminho de rede", "Validar o retorno no Zabbix"]),
    ("link down", "Enlace indisponível", "Uma interface deixou de transportar tráfego e pode afetar usuários conectados.", "Verificar porta e equipamento conectado", ["Identificar porta e equipamento afetado", "Validar cabo, energia e estado administrativo", "Confirmar a recuperação no Zabbix"]),
    ("lower speed", "Porta operando abaixo da velocidade", "A porta negociou velocidade inferior ao padrão anterior.", "Validar cabo e negociação da porta", ["Verificar cabo e conectores", "Conferir velocidade e duplex nas duas pontas", "Observar erros após renegociar"]),
    ("memory", "Memória elevada", "Pouca memória disponível pode causar lentidão e encerramento de processos.", "Verificar consumo e processos recentes", ["Identificar os maiores consumidores", "Comparar com a linha de base", "Corrigir vazamento ou ajustar capacidade"]),
    ("disk", "Armazenamento sob pressão", "Espaço, latência ou fila de disco estão acima do nível esperado.", "Validar espaço, latência e fila de disco", ["Separar falta de espaço de lentidão", "Identificar carga ou rotina coincidente", "Liberar capacidade ou corrigir a origem"]),
    ("airtime", "Ponto de acesso instável", "O canal sem fio apresenta ocupação ou interferência elevada.", "Revisar interferência e ocupação de canal", ["Identificar os pontos de acesso afetados", "Comparar canais e vizinhança", "Ajustar canal ou potência e reavaliar"]),
)


def _problems(snapshot: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not snapshot:
        return []
    value = (snapshot.get("payload") or {}).get("zabbix", {}).get("problems", [])
    return value if isinstance(value, list) else []


def _summary(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    value = (snapshot or {}).get("summary", {})
    return value if isinstance(value, dict) else {}


def _score(problems: list[dict[str, Any]], capacity: int) -> int:
    penalty = sum(SEVERITY_WEIGHT.get(int(item.get("severity", 0) or 0), 0.1) for item in problems)
    return max(0, min(100, round(100 - (penalty / max(capacity, 10)) * 4)))


def _domain_for(problem: dict[str, Any]) -> str | None:
    corpus = " ".join([str(problem.get("name", "")), *map(str, problem.get("groups", []) or [])]).lower()
    for name, tokens in DOMAINS.items():
        if any(token in corpus for token in tokens):
            return name
    return None


def _domain_scores(problems: list[dict[str, Any]], hosts: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for problem in problems:
        domain = _domain_for(problem)
        if domain:
            grouped[domain].append(problem)
    return [{"name":name,"score":_score(grouped[name],hosts),"active_risks":len(grouped[name])} for name in DOMAINS]


def _risk_family(problem: dict[str, Any]) -> tuple[str, str, str, list[str]] | None:
    name = str(problem.get("name", "")).lower()
    for token, title, description, action, treatment in RISK_RULES:
        if token in name:
            return title, description, action, treatment
    return None


def _top_risks(problems: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, Any]] = {}
    for problem in problems:
        family = _risk_family(problem)
        if not family:
            continue
        title, description, action, treatment = family
        entry = grouped.setdefault(title, {"title":title,"description":description,"recommended_action":action,"treatment":treatment,"hosts":set(),"groups":set(),"severities":defaultdict(int),"weight":0.0,"count":0})
        entry["hosts"].update(map(str, problem.get("hosts", []) or []));entry["groups"].update(map(str, problem.get("groups", []) or []))
        severity=int(problem.get("severity",0) or 0);entry["severities"][severity]+=1
        entry["weight"] += SEVERITY_WEIGHT.get(severity, 0.1);entry["count"] += 1
    ranked = sorted(grouped.values(), key=lambda item:(item["weight"],item["count"]), reverse=True)[:5]
    result = [];details = {}
    for item in ranked:
        affected = len(item["hosts"])
        impact = f"{affected} equipamento(s) afetado(s)" if affected else "Impacto ainda não identificado"
        result.append({"title":item["title"],"impact":impact,"confidence":min(98,72+item["count"]*3),"recommended_action":item["recommended_action"]})
        details[item["title"]] = {"description":item["description"],"occurrences":item["count"],"affected_assets":sorted(item["hosts"])[:12],"additional_assets":max(0,len(item["hosts"])-12),"areas":sorted(group for group in item["groups"] if group != "Global")[:6],"severity_distribution":dict(item["severities"]),"treatment":item["treatment"]}
    return result, details


def _load_reference_snapshots() -> tuple[dict | None, dict | None, dict | None]:
    try:
        with postgres_store._connect() as conn:
            current = conn.execute("SELECT generated_at,summary,payload FROM infra_snapshots ORDER BY generated_at DESC LIMIT 1").fetchone()
            previous_hour = conn.execute("SELECT generated_at,summary,payload FROM infra_snapshots WHERE generated_at <= NOW()-INTERVAL '1 hour' ORDER BY generated_at DESC LIMIT 1").fetchone()
            previous_day = conn.execute("SELECT generated_at,summary,payload FROM infra_snapshots WHERE generated_at <= NOW()-INTERVAL '24 hours' ORDER BY generated_at DESC LIMIT 1").fetchone()
        def convert(row): return {"generated_at":row[0].isoformat(),"summary":row[1],"payload":row[2]} if row else None
        return convert(current), convert(previous_hour), convert(previous_day)
    except Exception:
        recent = postgres_store.get_recent_snapshots(2)
        return (recent[0] if recent else None, recent[1] if len(recent)>1 else None, None)


def _history(hours: int = 12) -> list[dict[str, Any]]:
    try:
        with postgres_store._connect() as conn:
            rows = conn.execute("""SELECT DISTINCT ON (date_trunc('hour',generated_at)) generated_at,summary,payload
                FROM infra_snapshots WHERE generated_at>=NOW()-(%s||' hours')::interval
                ORDER BY date_trunc('hour',generated_at),generated_at DESC""",(str(hours),)).fetchall()
        return [{"at":row[0].isoformat(),"score":_score(_problems({"payload":row[2]}),int((row[1] or {}).get("hosts",0) or 0))} for row in rows]
    except Exception:
        return []


def executive_summary() -> dict[str, Any]:
    current, previous_hour, previous_day = _load_reference_snapshots()
    summary = _summary(current);problems = _problems(current);hosts = int(summary.get("hosts",0) or 0)
    health = _score(problems, hosts);day_score = _score(_problems(previous_day),int(_summary(previous_day).get("hosts",hosts) or hosts)) if previous_day else health
    hour_problems = _problems(previous_hour);current_ids={str(item.get("eventid")) for item in problems};previous_ids={str(item.get("eventid")) for item in hour_problems}
    new_alerts=len(current_ids-previous_ids);resolved=len(previous_ids-current_ids)
    previous_hosts=int(_summary(previous_hour).get("hosts",hosts) or hosts) if previous_hour else hosts
    risks,risk_details=_top_risks(problems)
    delta=health-day_score
    return {
        "view":"executive","generated_at":datetime.now(timezone.utc).isoformat(),"ruleset":RULESET_VERSION,
        "health":{"overall":health,"trend":"stable" if abs(delta)<2 else "improving" if delta>0 else "declining","delta_vs_previous":delta},
        "devices":{"total":hosts,"delta":hosts-previous_hosts},
        "domains":_domain_scores(problems,hosts),"top_risks":risks,"risk_details":risk_details,
        "changes":{"new_alerts":new_alerts,"new_devices":max(0,hosts-previous_hosts),"resolved":resolved,"critical_incidents":sum(1 for item in problems if int(item.get("severity",0) or 0)>=4)},
        "recommended_action":risks[0]["recommended_action"] if risks else "Manter o acompanhamento do ambiente",
        "history":_history(),
    }
