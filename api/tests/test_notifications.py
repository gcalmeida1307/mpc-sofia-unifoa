from services.notifications import EmailNotifier


def test_activation_email_targets_user_and_contains_required_steps(monkeypatch):
    captured = {}
    notifier = EmailNotifier()

    def fake_send(recipients, subject, body):
        captured.update(recipients=recipients, subject=subject, body=body)
        return True

    monkeypatch.setattr(notifier, "send", fake_send)
    assert notifier.notify_account_activation(
        "Pessoa@Empresa.com", "nome.sobrenome", "Nome Sobrenome", "temporary-token"
    )
    assert captured["recipients"] == ["Pessoa@Empresa.com"]
    assert "acesso aprovado" in captured["subject"]
    assert "nome.sobrenome" in captured["body"]
    assert "Google Authenticator" in captured["body"]
    assert "temporary-token" in captured["body"]
