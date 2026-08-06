from services.zabbix_investigator import ZabbixInvestigator, format_investigation
from ai.critic import critic_engine


class FakeConnector:
    def __init__(self): self.calls=[]
    def list_active_problems(self,limit):
        self.calls.append("problems")
        return [{"eventid":"10","objectid":"20","name":"HP Switch: Interface 13(): Link down","severity_label":"Average","severity":"3","clock":"1786000000","hosts":["sw-1"],"groups":["Switches"],"host_refs":[{"hostid":"30","name":"sw-1","groups":["Switches"]}]}]
    def get_trigger_diagnostics(self,ids):
        self.calls.append("triggers");return {"20":{"triggerid":"20","status":"0","state":"0","lastchange":"1786000000","functions":[{"itemid":"40","function":"last","parameter":""}],"dependencies":[],"tags":[{"tag":"scope","value":"network"}]}}
    def get_items(self,ids):
        self.calls.append("items");return {"40":{"itemid":"40","hostid":"30","name":"Interface 13: Operational status","key_":"ifOperStatus[13]","lastvalue":"2","prevvalue":"1","lastclock":"1786000100","units":"","value_type":"3","status":"0","state":"0","error":""}}
    def search_items(self,host_ids,text,limit):
        self.calls.append("related_items");return []
    def get_host_diagnostics(self,ids):
        self.calls.append("hosts");return {"30":{"description":"Switch de acesso","interfaces":[{"ip":"192.0.2.10","available":"1"}],"inventory":{},"parentTemplates":[{"name":"HP Enterprise Switch"}]}}
    def get_item_history(self,items,hours):
        self.calls.append("history");return {"40":[{"clock":"1785999900","value":"1"},{"clock":"1786000100","value":"2"}]}
    def count_trigger_recurrence(self,ids,days):
        self.calls.append("recurrence");return {"20":3}


def test_investigator_walks_full_zabbix_evidence_chain():
    connector=FakeConnector();result=ZabbixInvestigator().investigate("Como resolver enlace indisponível?",connector=connector)
    assert connector.calls==["problems","triggers","items","related_items","hosts","history","recurrence"]
    evidence=result["evidence"][0]
    assert evidence["entity"]=="13"
    assert evidence["items"][0]["current_value"]=="2"
    assert evidence["items"][0]["history_summary"]["change"]==1.0
    assert evidence["recurrence"]["occurrences"]==3
    assert result["guardrails"]["read_only"] is True
    answer=format_investigation(result)
    assert "componente 13" in answer and "3 ocorrência(s)" in answer


def test_investigator_supports_operating_system_metrics():
    connector=FakeConnector()
    connector.list_active_problems=lambda limit:[{"eventid":"11","objectid":"21","name":"Windows: CPU utilization high","severity_label":"High","severity":"4","clock":"1786000000","hosts":["srv-1"],"groups":["Servidores"],"host_refs":[{"hostid":"31","name":"srv-1","groups":["Servidores"]}]}]
    connector.get_trigger_diagnostics=lambda ids:{"21":{"status":"0","functions":[{"itemid":"41"}]}}
    connector.get_items=lambda ids:{"41":{"itemid":"41","name":"CPU utilization","key_":"system.cpu.util","lastvalue":"95","prevvalue":"80","lastclock":"1786000100","units":"%","value_type":"0","status":"0","state":"0"}}
    connector.search_items=lambda host_ids,text,limit:[]
    connector.get_host_diagnostics=lambda ids:{"31":{"interfaces":[],"inventory":{},"parentTemplates":[{"name":"Windows"}]}}
    connector.get_item_history=lambda items,hours:{"41":[{"clock":"1785999900","value":"80"},{"clock":"1786000100","value":"95"}]}
    connector.count_trigger_recurrence=lambda ids,days:{"21":2}
    result=ZabbixInvestigator().investigate("Investigue CPU elevada no servidor",connector=connector)
    item=result["evidence"][0]["items"][0]
    assert item["name"]=="CPU utilization" and item["history_summary"]["maximum"]==95.0


def test_critic_allows_detailed_evidence_report_for_investigation():
    result=critic_engine.evaluate("investigue",{"intent":"incident_analysis","tools":["zabbix.investigate"]},{},"evidência "*500)
    assert result["approved"] is True
