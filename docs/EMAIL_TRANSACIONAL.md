# E-mail transacional da SOFIA

A SOFIA envia apenas mensagens operacionais: solicitação de acesso, ativação aprovada e redefinição de senha. Não use uma conta pessoal nem execute um SMTP público neste servidor.

## Arquitetura recomendada

1. Registrar ou usar um domínio institucional.
2. Criar um subdomínio exclusivo, como `avisos.exemplo.com`, para isolar a reputação de envio.
3. Contratar um provedor transacional SMTP.
4. Publicar no DNS os registros SPF e DKIM fornecidos pelo provedor.
5. Iniciar DMARC com monitoramento (`p=none`) e endurecer a política depois de validar os relatórios.
6. Manter a API key exclusivamente no `.env` local.

## Variáveis locais

```dotenv
SMTP_HOST=smtp.provedor.example
SMTP_PORT=587
SMTP_USER=usuario-fornecido
SMTP_PASSWORD=segredo-fornecido
SMTP_FROM=SOFIA <acesso@avisos.exemplo.com>
SMTP_STARTTLS=true
ADMIN_NOTIFICATION_EMAIL=administrador@exemplo.com
```

Depois de alterar o `.env`, reconstruir apenas a API:

```bash
docker compose up -d --build sofia-api
```

## Comportamento seguro

- Se o envio de ativação funcionar, o token não volta para o navegador do administrador.
- Se SMTP estiver indisponível, a interface apresenta uma cópia emergencial para entrega por canal seguro.
- Reenviar ativação invalida o código anterior.
- Enquanto SMTP estiver indisponível, um administrador autenticado recebe uma cópia única do código para entrega por canal seguro.
- Para uma conta ativa que perdeu senha ou TOTP, `Reconfigurar acesso` revoga sessões, invalida as credenciais anteriores e exige novo Primeiro acesso.
- Um administrador não pode reconfigurar a própria conta; outro administrador deve executar a recuperação.
- Senhas, hashes e segredos TOTP nunca são enviados por e-mail.
