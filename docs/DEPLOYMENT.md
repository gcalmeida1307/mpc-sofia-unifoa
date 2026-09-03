# Implantação local

1. Crie/valide `.venv` e instale `requirements.txt`.
2. Configure `.env` sem versionar secrets.
3. Execute `pnpm dev:network` para frontend em `5174` na rede interna e
   `pnpm api:network` para a API em `8787`, ou use `start-local.ps1`.
4. Para produção, sirva o build atrás de TLS e restrinja a porta da API à rede
   interna.

PostgreSQL é usado pelo runtime no schema isolado `sofia_runtime` quando
`SOFIA_POSTGRES_URL` ou `DATABASE_URL` autentica corretamente; a migration
`migrations/001_knowledge_expansion.sql` permanece como referência para o
provisionamento institucional. SQLite local (`data/knowledge_expansion.sqlite3`)
é o fallback explícito para desenvolvimento/offline. Valide o backend em
`/api/capabilities` ou no Pipeline Explorer; nunca coloque a senha no código.
