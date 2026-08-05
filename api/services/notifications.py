from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage


class EmailNotifier:
    @staticmethod
    def configured() -> bool:
        return bool(os.getenv("SMTP_HOST", "").strip() and os.getenv("SMTP_FROM", "").strip())

    def send(self, recipients: list[str], subject: str, body: str) -> bool:
        recipients = sorted({email.strip().lower() for email in recipients if email and "@" in email})
        if not recipients or not self.configured():
            return False
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = os.environ["SMTP_FROM"].strip()
        message["To"] = ", ".join(recipients)
        message.set_content(body)
        host = os.environ["SMTP_HOST"].strip()
        port = int(os.getenv("SMTP_PORT", "587"))
        username = os.getenv("SMTP_USER", "").strip()
        password = os.getenv("SMTP_PASSWORD", "")
        use_tls = os.getenv("SMTP_STARTTLS", "true").lower() in {"1", "true", "yes", "on"}
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            if use_tls:
                smtp.starttls(context=context)
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
        return True

    def notify_access_request(self, recipients: list[str], username: str, display_name: str, email: str, reason: str) -> bool:
        return self.send(
            recipients,
            f"SOFIA: nova solicitacao de acesso - {username}",
            f"Uma nova solicitacao aguarda aprovacao.\n\nNome: {display_name}\nUsuario: {username}\nE-mail: {email}\nMotivo: {reason or 'Nao informado'}\n\nAcesse Gestao da plataforma para revisar.",
        )

    def notify_password_reset(self, recipient: str, username: str, token: str) -> bool:
        return self.send(
            [recipient],
            "SOFIA: redefinicao de senha autorizada",
            f"O administrador autorizou a redefinicao da senha de {username}.\n\nToken temporario: {token}\n\nUse o token, uma nova senha e seu codigo TOTP na tela de login. O token expira em 30 minutos e pode ser usado uma unica vez.",
        )


email_notifier = EmailNotifier()
