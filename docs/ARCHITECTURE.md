# Arquitetura do SOFIA

## Visão geral

```text
Browser responsivo
       │ contratos HTTP
       ▼
FastAPI + adaptador MCP (allowlist)
       │
       ├── CORE: intenção → complexidade → plano → contexto → resposta → verificação
       ├── Domain Contracts: política, vocabulário, fontes, skills e tools por módulo
       ├── Knowledge: ingestão → OCR/extração → qualidade → artifacts → chunks → índice
       ├── Providers: Ollama / Gemini / Claude / OpenAI via interface comum
       ├── Insights/Neural/Monte Carlo: análise de apoio, sem transformar correlação em fato
       └── PostgreSQL em schema isolado + SQLite fallback explícito
```

O CORE não contém regras clínicas ou jurídicas exclusivas. Essas regras são
descritas pelo contrato em `api/domains.py`; o retrieval mantém o filtro de
módulo e a autorização antes de montar o contexto.

## Decisões

- O modo local é a autoridade padrão. Providers externos só recebem contexto
  minimizado quando a política permitir.
- O reranker combina cobertura lexical, BM25-like, TF-IDF e embedding neural
  local do Ollama quando o índice do módulo está pronto; sem o modelo neural,
  a busca continua funcional com o caminho determinístico.
- A expansão e os embeddings são persistidos por módulo e processados em fila
  sequencial. PostgreSQL é o backend primário quando as credenciais validam;
  SQLite é apenas fallback operacional, nunca uma troca silenciosa de fonte.
- O pipeline é persistente, por documento e reprocessável. Falha em um arquivo
  não interrompe os demais.
- Dados operacionais de observabilidade são armazenados sem pergunta/resposta
  brutas; conteúdos clínicos não entram nas estatísticas.
