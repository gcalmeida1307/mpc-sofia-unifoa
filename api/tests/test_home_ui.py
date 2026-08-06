from pathlib import Path


STATIC = Path(__file__).resolve().parents[1] / "static"


def test_home_is_compact_and_does_not_render_audit_or_prompt_list():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert 'id="overall-health"' in html
    assert 'id="executive-devices"' in html
    assert 'id="risk-ranking"' in html
    assert 'id="risk-detail"' in html
    assert '/ui/analista.html' in html
    assert 'id="audit"' not in html
    assert 'id="training-prompts"' not in html


def test_analyst_view_keeps_detailed_operational_status():
    html = (STATIC / "analista.html").read_text(encoding="utf-8")
    assert 'id="training-count"' in html
    assert 'id="device-timeline"' in html
    script = (STATIC / "app.js").read_text(encoding="utf-8")
    assert "Alertas que entraram" in script
    assert "Alertas resolvidos" in script
    assert "Dispositivos monitorados" in script
    executive_script = (STATIC / "executive.js").read_text(encoding="utf-8")
    assert "Investigar evidências no Zabbix" in executive_script


def test_management_contains_five_row_audit_table():
    html = (STATIC / "gestao.html").read_text(encoding="utf-8")
    script = (STATIC / "management.js").read_text(encoding="utf-8")
    assert '<thead>' in html and 'id="management-audit-body"' in html
    assert "/auth/admin/audit?limit=5" in script
    assert ".slice(0,5)" in script
