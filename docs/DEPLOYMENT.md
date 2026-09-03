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
provisionamento institucional. Para produção, configure:

```env
SOFIA_STORAGE_MODE=production
SOFIA_POSTGRES_URL=postgresql://usuario:senha@servidor:5432/sofia
SOFIA_ENCRYPTION_KEY=<chave-forte-fora-do-repositorio>
```

Nesse modo, o sistema falha fechado se o PostgreSQL não estiver disponível e
o Production Gate não libera a implantação enquanto os stores obrigatórios
não estiverem migrados. SQLite local (`data/knowledge_expansion.sqlite3`) é
permitido apenas com `SOFIA_STORAGE_MODE=developer`, para desenvolvimento ou
operação offline explicitamente assumida. Valide o backend em
`/api/capabilities`, `/api/health` ou no Pipeline Explorer; nunca coloque a
senha no código.
