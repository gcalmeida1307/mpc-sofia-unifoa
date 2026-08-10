from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from services.behavior_patterns import BehaviorPatternAnalyzer


def _snapshot(at, active=True):
    problems=[]
    if active:problems=[{"name":"HP Switch: Interface 13(): Link down","hosts":["SW-ADMIN-01"],"groups":["ADMINISTRATIVO","Switches"]}]
    return {"generated_at":at.isoformat(),"payload":{"zabbix":{"problems":problems}}}


def test_analyzer_recognizes_recurring_out_of_hours_routine():
    timezone=ZoneInfo("America/Sao_Paulo");start=datetime(2026,8,1,tzinfo=timezone);snapshots=[]
    for day in range(5):
        for hour in range(24):snapshots.append(_snapshot(start+timedelta(days=day,hours=hour),active=hour>=18 or hour<8))
    patterns=BehaviorPatternAnalyzer().analyze(snapshots,min_samples=12)
    assert len(patterns)==1
    assert patterns[0]["host"]=="SW-ADMIN-01"
    assert patterns[0]["entity"]=="13"
    assert patterns[0]["classification"]=="rotina administrativa provável"
    assert patterns[0]["night_down_rate"]==1
    assert patterns[0]["business_down_rate"]==0
    assert patterns[0]["confidence"]>=.9


def test_analyzer_does_not_label_random_business_failure_as_routine():
    timezone=ZoneInfo("America/Sao_Paulo");start=datetime(2026,8,1,tzinfo=timezone);snapshots=[]
    for day in range(5):
        for hour in range(24):snapshots.append(_snapshot(start+timedelta(days=day,hours=hour),active=hour in {10,14,20}))
    assert BehaviorPatternAnalyzer().analyze(snapshots,min_samples=12)==[]
