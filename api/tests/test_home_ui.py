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
    assert "domain-access-dialog" in script and "domain-role-list" in script
    assert "Escolha o papel para" not in script
    assert "input[name=\"domain-role\"]:checked" in script
    access_styles=(STATIC / "management-access.css").read_text(encoding="utf-8")
    assert ".domain-role-option" in access_styles and "::backdrop" in access_styles


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


def test_knowledge_page_can_install_declarative_domains():
    html=(STATIC / "base.html").read_text(encoding="utf-8")
    script=(STATIC / "base.js").read_text(encoding="utf-8")
    assert 'id="domain-form"' in html and "Criar módulo operacional" in html
    assert "Entidades principais" in html and "Indicadores importantes" in html
    assert "'/domains'" in script and "permissions" in script and "routes.search" in script
    assert 'id="domain-theme"' in script and "identidade visual" in script


def test_shell_renders_domain_experiences_instead_of_fixed_domain_pages():
    auth=(STATIC / "auth.js").read_text(encoding="utf-8")
    html=(STATIC / "domain.html").read_text(encoding="utf-8")
    workspace=(STATIC / "domain-workspace.js").read_text(encoding="utf-8")
    styles=(STATIC / "domain-shell.css").read_text(encoding="utf-8")
    assert "/domains/experience/catalog" in auth and "domain-switcher" in auth
    assert 'id="domain-navigation"' in html and 'id="domain-page"' in html
    for template in ["executive_overview","entity_list","analytics","knowledge"]:assert template in workspace
    assert "suggested_questions" in workspace and "/ui/conversar.html?q=" in workspace
    assert "--domain-accent" in styles and "--domain-secondary" in styles


def test_chat_displays_operational_progress_without_exposing_internal_reasoning():
    html = (STATIC / "conversar.html").read_text(encoding="utf-8")
    script = (STATIC / "chat.js").read_text(encoding="utf-8")
    assert 'id="answer-progress"' in html
    assert "Consultando dados" in html
    assert "sem expor dados sensíveis" in html
    assert 'id="chat-welcome"' in html and 'id="starter-prompts"' in html
    assert 'data-mode="Investigue"' in html and "Contexto pronto" in script
    assert 'id="clear-conversation"' in html
    assert "temporal_context" in script and "conversationHistory" in script


def test_timeline_uses_progressive_detail_and_period_visualization():
    html = (STATIC / "timeline.html").read_text(encoding="utf-8")
    script = (STATIC / "timeline.js").read_text(encoding="utf-8")
    assert 'id="timeline-chart"' in html
    assert 'id="timeline-search"' in html and 'id="level-filters"' in html
    assert "Mostrar mais" in script and "Investigar este episódio" in script
    assert "não causalidade" in script
    assert "eventEntities" in script and "ids.has(item.from)&&ids.has(item.to)" in script


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
    assert "Abrir análise visual" in chat
    assert "sofia-chat-history" in chat and "autoRun" in chat
    assert "analysis_entries" in chat and "conversation-analysis" in chat
    assert "Mostrar gráficos desta análise" not in chat and "Ver evidências" not in chat
    assert "Investigar agora no Zabbix" in (STATIC / "executive.js").read_text(encoding="utf-8")
    assert "WORKFLOW_TEMPLATES" in automation and "node-drawer" in automation
    assert "Última madrugada (22h–06h)" in automation
    assert "config.operation" in automation and "graph-node.running" in styles
