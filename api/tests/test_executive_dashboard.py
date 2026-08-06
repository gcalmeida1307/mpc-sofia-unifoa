from services import executive_dashboard as executive


def snapshot(hosts, problems):
    return {"generated_at":"2026-08-06T12:00:00+00:00","summary":{"hosts":hosts,"problems":len(problems)},"payload":{"zabbix":{"problems":problems}}}


def problem(eventid, name, severity, host, groups):
    return {"eventid":eventid,"name":name,"severity":str(severity),"hosts":[host],"groups":groups}


def test_executive_contract_is_deterministic_and_auditable(monkeypatch):
    old = snapshot(233, [problem("old", "CPU high", 3, "srv-1", ["Servidores"])])
    current = snapshot(234, [
        problem("1", "Broadcast traffic high", 4, "sw-1", ["Switches"]),
        problem("2", "Unavailable by ICMP ping", 3, "sw-2", ["Switches"]),
    ])
    monkeypatch.setattr(executive, "_load_reference_snapshots", lambda: (current, old, old))
    monkeypatch.setattr(executive, "_history", lambda: [{"at":"2026-08-06T12:00:00+00:00","score":95}])

    result = executive.executive_summary()

    assert result["view"] == "executive"
    assert result["ruleset"] == "executive-health-v1"
    assert result["devices"] == {"total":234,"delta":1}
    assert result["changes"] == {"new_alerts":2,"new_devices":1,"resolved":1,"critical_incidents":1}
    assert result["top_risks"][0].keys() == {"title","impact","confidence","recommended_action"}
    assert result["top_risks"][0]["title"] == "Broadcast crescente"
    detail = result["risk_details"]["Broadcast crescente"]
    assert detail["affected_assets"] == ["sw-1"]
    assert len(detail["treatment"]) == 3
    assert detail["description"]


def test_static_device_count_stays_out_of_timeline_change(monkeypatch):
    current = snapshot(234, [])
    previous = snapshot(234, [])
    monkeypatch.setattr(executive, "_load_reference_snapshots", lambda: (current, previous, previous))
    monkeypatch.setattr(executive, "_history", lambda: [])
    result = executive.executive_summary()
    assert result["devices"]["delta"] == 0
    assert result["changes"]["new_devices"] == 0
