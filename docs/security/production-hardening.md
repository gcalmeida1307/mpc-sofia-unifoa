# SOFIA Production Hardening

## 1. Network exposure
- Services in compose are bound to localhost by default.
- Keep reverse proxy in front of API and terminate TLS there.
- HSTS só é emitido pela aplicação em requisições HTTPS; o header não cria TLS.
- Para borda pública, configure DNS, `SOFIA_PUBLIC_HOST` e `TLS_CONTACT_EMAIL` e execute `docker compose -f docker-compose.yml -f docker-compose.edge.yml up -d`.
- O Caddy obtém e renova certificados automaticamente. Firewall/WAF deve permitir apenas 80/443 e a porta 8080 deve ser limitada à rede administrativa.

## 2. PostgreSQL hardening
Implemented in compose and config files:
- SCRAM-SHA-256 auth required for local/host connections.
- Dedicated hardened config in postgres/conf/postgresql.conf.
- Dedicated pg_hba policy in postgres/conf/pg_hba.conf.
- Healthcheck enabled for service readiness.

### Mandatory production actions
- Set a strong POSTGRES_PASSWORD in environment.
- Restrict host firewall access to port 5432.
- Use encrypted disk for postgres_data volume.

## 3. Admin operations protection
SOFIA supports API key and optional TOTP for critical write endpoints.

Environment:
- SECURITY_ADMIN_API_KEY
- SECURITY_MFA_TOTP_SECRET

Protected write endpoints:
- /marketplace/install
- /workflows/run
- /workflows/n8n/run
- /engine/ingest

Headers:
- x-sofia-admin-key
- x-sofia-otp (if TOTP enabled)

## 4. About PostgreSQL 2FA
Native PostgreSQL inside this container stack does not provide built-in TOTP out of the box.
Recommended approach:
- enforce TOTP at access layer (VPN/SSO bastion/proxy), and
- use SOFIA endpoint-level TOTP for critical platform actions.

## 5. Runtime validation
Use:
- GET /security/validate
- GET /core/kernel
- GET /engine/ai/metrics
- GET /engine/evidence/audit

## 6. Knowledge Hub e autorização

- URLs cadastradas passam por proteção SSRF e validação de cada redirecionamento.
- Redes privadas, loopback, link-local e URLs com credenciais são recusadas.
- A autorização é validada por capability em cada superfície protegida; negativas são auditadas.
- Consulte `docs/architecture/hardening-and-performance.md` para o contrato e as métricas.

## 7. Sessão, navegador e uploads

- A sessão atual usa token Bearer no header, não cookie; por isso flags `HttpOnly/SameSite` e CSRF de cookie não se aplicam ao contrato atual. O risco principal é XSS, mitigado por CSP e renderização textual. Uma futura migração para cookie deverá adotar `Secure`, `HttpOnly`, `SameSite=Strict` e token CSRF.
- CORS não é habilitado: navegadores permanecem em mesma origem por padrão.
- Uploads aceitam apenas TXT, Markdown, PDF e DOCX, com limite de 10 MB, além do limite global de request.
- Endpoints de login, recuperação, ativação e solicitação possuem rate limiting; falhas de autenticação são auditadas.
- Recuperação MFA permanece administrativa e auditável enquanto SMTP não estiver disponível.
