# Desenvolvimento

Use a `.venv` do projeto para testes: `\.venv\Scripts\python.exe -m pytest -q`.
Antes de alterar retrieval, ingestão ou providers, execute o baseline e depois
Ruff, compileall e `pnpm build`. Não adicione regras de um módulo no CORE;
altere o contrato do domínio e acrescente um caso de avaliação.

O frontend consome `/api/modules`, `/api/capabilities`, `/api/chat`, upload e
os endpoints administrativos autenticados. Dados novos devem ser exibidos
com estados reais, não com placeholders de processamento.
