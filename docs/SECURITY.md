# Segurança e privacidade

Controles implementados: sessões rotativas, RBAC por módulo, endpoint de
estatísticas restrito a `AG000001`, minimização/redação antes de providers
externos, validação de extensão e tamanho no upload, quarentena de fontes
inválidas, allowlist de tools, validação de caminho no reprocessamento, crawler
com limite de páginas/profundidade, proteção contra prompt injection em
capturas públicas e autorização durante o retrieval.

O sistema é preparado para LGPD e para uso controlado de dados FHIR, mas não é
declarado legalmente “compliant” sem revisão institucional, base legal,
controles de retenção, gestão de acesso, TLS e auditoria formal.

Com `SOFIA_ENCRYPTION_KEY`, os campos de identidade, tokens de autenticação,
segredos 2FA, payloads FHIR, payloads de integrações e evidências de insights
são cifrados pela aplicação antes de serem persistidos no PostgreSQL. Isso
complementa — e não substitui — criptografia de disco, TLS, backup protegido e
gestão de chaves.

Gaps operacionais: TLS deve ser terminado por proxy/rede interna; secrets devem
ser fornecidos por ambiente/secret manager; PostgreSQL precisa ser provisionado
e migrado; backup, restauração e retenção precisam ser definidos pelo operador.
