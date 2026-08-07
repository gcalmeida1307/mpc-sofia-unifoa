from pathlib import Path


STATIC = Path(__file__).resolve().parents[1] / "static"


def read(name: str) -> str:
    return (STATIC / name).read_text(encoding="utf-8")


def test_login_has_only_the_login_task_and_links_to_other_flows():
    html = read("login.html")
    assert 'id="login-form"' in html
    assert 'id="setup-form"' not in html
    assert 'id="access-form"' not in html
    assert '/ui/primeiro-acesso.html' in html
    assert '/ui/solicitar-acesso.html' in html
    assert '/ui/recuperar-senha.html' in html


def test_first_access_is_a_guided_passwordless_activation():
    html = read("primeiro-acesso.html")
    script = read("onboarding.js")
    assert "Sua conta começa sem senha" in html
    assert "Google Authenticator" in html
    assert 'id="totp-qr"' in html
    assert 'data-step="1"' in html and 'data-step="3"' in html
    assert "/auth/first-access/start" in script
    assert "/auth/first-access/complete" in script


def test_access_request_and_recovery_are_independent_pages():
    request = read("solicitar-acesso.html")
    recovery = read("recuperar-senha.html")
    assert 'id="access-email"' in request
    assert 'id="access-form"' in request
    assert 'id="reset-form"' in recovery
    assert "administrador precisa autorizar" in recovery


def test_authentication_pages_offer_persistent_light_and_dark_themes():
    theme = read("theme.js")
    for page in ("login.html", "primeiro-acesso.html", "solicitar-acesso.html", "recuperar-senha.html"):
        html = read(page)
        assert 'data-theme-toggle' in html
        assert '/ui/theme.js' in html
    assert "prefers-color-scheme: light" in theme
    assert "sofia-theme" in theme
    authenticated_theme = read("auth.js")
    assert "Usar tema claro" in authenticated_theme
    assert "Usar tema escuro" in authenticated_theme
