from pathlib import Path


STATIC = Path(__file__).resolve().parents[1] / "static"


def test_home_is_compact_and_does_not_render_audit_or_prompt_list():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert 'id="training-count"' in html
    assert 'id="knowledge-count"' in html
    assert 'id="training-status"' in html
    assert 'id="device-timeline"' in html
    assert 'id="audit"' not in html
    assert 'id="training-prompts"' not in html


def test_management_contains_five_row_audit_table():
    html = (STATIC / "gestao.html").read_text(encoding="utf-8")
    script = (STATIC / "management.js").read_text(encoding="utf-8")
    assert '<thead>' in html and 'id="management-audit-body"' in html
    assert "/auth/admin/audit?limit=5" in script
    assert ".slice(0,5)" in script
