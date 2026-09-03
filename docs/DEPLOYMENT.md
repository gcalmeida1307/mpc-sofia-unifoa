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

Depois de trocar o backend, migre os stores locais uma única vez. A rotina é
idempotente, cifra os campos sensíveis antes da gravação e preserva os SQLite
como fonte de recuperação:

```powershell
.\.venv\Scripts\python.exe scripts\migrate_operational_stores.py
```

Reinicie a API e confirme em `/api/health` que `mode` é
`production-primary` e que `local_scope_pending_migration` está vazio. O
endpoint também lista as tabelas ausentes sem mostrar a senha da conexão.

Nesse modo, o sistema falha fechado se o PostgreSQL não estiver disponível e
o Production Gate não libera a implantação enquanto os stores obrigatórios
não estiverem migrados. Os stores de autenticação, FHIR, integrações, insights,
auditoria, analytics e observabilidade usam PostgreSQL; SQLite local é
permitido apenas com `SOFIA_STORAGE_MODE=developer`, para desenvolvimento ou
operação offline explicitamente assumida. Valide o backend em
`/api/capabilities`, `/api/health` ou no Pipeline Explorer; nunca coloque a
senha no código.

## Gate de produção

O `Production Gate` não é um indicador decorativo. Antes de liberar a
plataforma, execute o canário operacional e depois consulte o gate como
administrador:

```powershell
.\.venv\Scripts\python.exe scripts\run_readiness_canary.py
```

O resultado só pode ser `release_allowed: true` quando todos os módulos com
corpus tiverem os dez níveis prontos, cada caso dourado estiver revisado e
referenciar suas fontes esperadas, o armazenamento estiver saudável, a chave
de criptografia existir e não houver documento em quarentena. Um módulo sem
documentos, como `secretaria` enquanto seu corpus não for fornecido, bloqueia
o gate por desenho; não é convertido artificialmente em 100%.

Para fechar os níveis neurais, `SOFIA_EMBEDDING_MAX_CHUNKS` deve cobrir todos
os chunks dos módulos que serão publicados. Em uma máquina sem GPU, mantenha o
processamento sequencial e aumente o limite gradualmente; índice parcial é
visível no Explorer e não é tratado como cobertura integral.
