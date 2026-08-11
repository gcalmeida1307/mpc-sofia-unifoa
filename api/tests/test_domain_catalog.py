import pytest

from services.domain_catalog import DeclarativeDomainCatalog, THEMES


def test_manifest_builds_operational_domain_contract():
    manifest=DeclarativeDomainCatalog._manifest({"domain_id":"medicina","display_name":"Medicina","description":"Protocolos","purpose":"Apoiar decisões clínicas baseadas em protocolos.","entities":["paciente","protocolo"],"metrics":["adesão"],"source_url":"https://docs.example.org/medicina","refresh_seconds":86400})
    assert manifest["routes"]["search"]=="/domains/medicina/search"
    assert manifest["permissions"]==["medicina.read","medicina.manage"]
    assert manifest["knowledge_collection"]["id"]=="medicina.knowledge"
    assert manifest["source"]["allowed_domains"]==["docs.example.org"]
    assert manifest["experience"]["navigation"][0]["page"]=="overview"
    assert manifest["experience"]["pages"]["records"]["template"]=="entity_list"
    assert manifest["experience"]["branding"]["preset"]=="ocean"


@pytest.mark.parametrize("domain_id",["Zabbix","core","x","financeiro_geral","../rh"])
def test_manifest_rejects_unsafe_or_reserved_domain_ids(domain_id):
    with pytest.raises(ValueError):DeclarativeDomainCatalog._manifest({"domain_id":domain_id,"display_name":"Teste","purpose":"Objetivo suficientemente descritivo."})


def test_domain_experience_accepts_only_curated_accessible_themes():
    assert {"ocean","clinical","amber","violet","emerald","indigo"}<=set(THEMES)
    with pytest.raises(ValueError,match="Tema visual inválido"):
        DeclarativeDomainCatalog._manifest({"domain_id":"medicina","display_name":"Medicina","purpose":"Apoiar decisões clínicas baseadas em evidências.","theme":"custom-css"})
