import pytest

from services.domain_catalog import DeclarativeDomainCatalog


def test_manifest_builds_operational_domain_contract():
    manifest=DeclarativeDomainCatalog._manifest({"domain_id":"medicina","display_name":"Medicina","description":"Protocolos","purpose":"Apoiar decisões clínicas baseadas em protocolos.","entities":["paciente","protocolo"],"metrics":["adesão"],"source_url":"https://docs.example.org/medicina","refresh_seconds":86400})
    assert manifest["routes"]["search"]=="/domains/medicina/search"
    assert manifest["permissions"]==["medicina.read","medicina.manage"]
    assert manifest["knowledge_collection"]["id"]=="medicina.knowledge"
    assert manifest["source"]["allowed_domains"]==["docs.example.org"]


@pytest.mark.parametrize("domain_id",["Zabbix","core","x","financeiro_geral","../rh"])
def test_manifest_rejects_unsafe_or_reserved_domain_ids(domain_id):
    with pytest.raises(ValueError):DeclarativeDomainCatalog._manifest({"domain_id":domain_id,"display_name":"Teste","purpose":"Objetivo suficientemente descritivo."})
