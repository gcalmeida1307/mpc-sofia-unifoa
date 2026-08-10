from pathlib import Path


STATIC = Path(__file__).resolve().parents[1] / "static"


def test_home_is_compact_and_does_not_render_audit_or_prompt_list():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert 'id="overall-health"' in html
    assert 'id="executive-devices"' in html
    assert 'id="risk-ranking"' in html
    assert 'id="risk-detail"' in html
    assert "Resumo operacional" in html
    assert "Evolução da saúde" in html
    assert "Movimento do ambiente" in html
    assert "Saúde por área" in html
    assert "Cinco maiores riscos" in html
    assert "Próxima ação" in html
    assert '/ui/analista.html' in html
    assert 'id="audit"' not in html
    assert 'id="training-prompts"' not in html


def test_operations_view_keeps_only_operational_status():
    html = (STATIC / "analista.html").read_text(encoding="utf-8")
    assert "Fontes do ambiente" in html
    assert 'id="operations-sources"' in html
    assert 'id="device-timeline"' in html
    assert 'id="training-count"' not in html
    assert 'id="provider-grid"' not in html
    script = (STATIC / "operations.js").read_text(encoding="utf-8")
    assert "Mudanças no ambiente" not in script
    executive_script = (STATIC / "executive.js").read_text(encoding="utf-8")
    assert "Investigar agora no Zabbix" in executive_script
    assert "Saúde calculada com alertas ativos e severidade" in executive_script


def test_management_contains_five_row_audit_table():
    html = (STATIC / "gestao.html").read_text(encoding="utf-8")
    script = (STATIC / "management.js").read_text(encoding="utf-8")
    assert '<thead>' in html and 'id="management-audit-body"' in html
    assert "/auth/admin/audit?limit=5" in script
    assert ".slice(0,5)" in script
    assert "Reenviar ativação" in script
    assert "Reconfigurar acesso" in script
    assert "invalidar senha e TOTP" in script
    assert "código de ativação foi enviado" in script
    assert "Desabilitar" in script
    assert "Reativar usuário" in script
    assert "data-disable" in script


def test_access_request_suggests_structured_available_usernames():
    html = (STATIC / "solicitar-acesso.html").read_text(encoding="utf-8")
    script = (STATIC / "access-request.js").read_text(encoding="utf-8")
    assert 'placeholder="nome.sobrenome"' in html
    assert "/auth/access-requests/username-options" in script
    assert "Sugestões disponíveis" in script
    assert "username.pattern" in script


def test_ux_architecture_has_analytics_intelligence_and_clean_automation():
    analytics = (STATIC / "analytics.html").read_text(encoding="utf-8")
    intelligence = (STATIC / "inteligencia.html").read_text(encoding="utf-8")
    automation = (STATIC / "automacao.html").read_text(encoding="utf-8")
    auth = (STATIC / "auth.js").read_text(encoding="utf-8")
    assert "O ambiente em gráficos" in analytics
    assert "Diário Cognitivo" in intelligence
    assert "Quem está trabalhando" in intelligence
    intelligence_script = (STATIC / "intelligence.js").read_text(encoding="utf-8")
    assert "JSON.stringify" not in intelligence_script
    assert "Prioriza incidentes" in intelligence_script
    assert "Entradas" in automation and "Processamento" in automation and "Saídas" in automation
    assert 'id="management-users"' not in automation
    assert "/ui/analytics.html" in auth
    assert "/ui/inteligencia.html" in auth
    styles = (STATIC / "styles.css").read_text(encoding="utf-8")
    assert "#connector-catalog.connector-lanes" in styles
    assert ".analytic-donut>.severity-legend" in styles


def test_chat_displays_operational_progress_without_exposing_internal_reasoning():
    html = (STATIC / "conversar.html").read_text(encoding="utf-8")
    assert 'id="answer-progress"' in html
    assert "Consultando fontes autorizadas" in html
    assert "raciocínio interno e dados sensíveis não são exibidos" in html


def test_design_system_applies_semantic_tokens_to_both_themes():
    styles = (STATIC / "styles.css").read_text(encoding="utf-8")
    for token in ["--background", "--surface-1", "--surface-2", "--surface-3", "--text-primary", "--text-secondary", "--border-subtle", "--success-soft", "--danger-soft"]:
        assert token in styles
    assert ':root[data-theme="light"]' in styles
    assert '.msg.assistant,.suggestion-chip' in styles
    assert '.connector-card,.connector-drag-ghost,.graph-node' in styles
    assert '@media(prefers-reduced-motion:reduce)' in styles


def test_product_navigation_chat_and_automation_are_progressively_disclosed():
    auth = (STATIC / "auth.js").read_text(encoding="utf-8")
    chat = (STATIC / "chat.js").read_text(encoding="utf-8")
    automation = (STATIC / "automation.js").read_text(encoding="utf-8")
    styles = (STATIC / "styles.css").read_text(encoding="utf-8")
    assert "nav-group" in auth and "mobile-nav" in auth and "nav-collapsed" in auth
    assert "localStorage.removeItem('sofia-nav-collapsed')" in auth
    assert "localStorage.setItem('sofia-nav-collapsed'" not in auth
    assert "aria-expanded" in auth and "setMenu" in auth
    assert "One predictable menu interaction" in styles
    assert "Ver evidências" in chat and "Mostrar gráficos" in chat
    assert "autoRun" in chat and "sofia-current-analysis" in chat
    assert "Investigar agora no Zabbix" in (STATIC / "executive.js").read_text(encoding="utf-8")
    assert "WORKFLOW_TEMPLATES" in automation and "node-drawer" in automation
    assert "Última madrugada (22h–06h)" in automation
    assert "config.operation" in automation and "graph-node.running" in styles
