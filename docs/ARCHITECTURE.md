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
       └── PostgreSQL em schema isolado + SQLite somente em desenvolvimento
```

O CORE não contém regras clínicas ou jurídicas exclusivas. Cada módulo possui
um pacote de domínio isolado em `api/domain_packages/`, com política, seleção
de fontes e critérios de recuperação próprios. O retrieval mantém o filtro de
módulo e a autorização antes de montar o contexto.

O caminho de uma pergunta é deliberadamente verificável:

```text
Percepção → Roteamento → Planejamento → Recuperação híbrida
          → Evidence Judge → Raciocínio → Crítica → Entrega
```

O Evidence Judge registra evidências aceitas, rejeitadas e conflitos; o
harness executa um segundo passe limitado quando a primeira recuperação não
é suficiente. A resposta nunca é liberada como “10/10” por aparência: o
Production Gate bloqueia publicação quando qualidade, segurança, storage,
corpus ou regressão não atendem aos critérios.

## Decisões

- O modo local é a autoridade padrão. Providers externos só recebem contexto
  minimizado quando a política permitir e não substituem a evidência local.
- O reranker combina cobertura lexical, BM25-like, TF-IDF e embedding neural
  local do Ollama quando o índice do módulo está pronto; sem o modelo neural,
  a busca continua funcional com o caminho determinístico.
- A expansão e os embeddings são persistidos por módulo e processados em fila
  sequencial. PostgreSQL é o backend primário quando as credenciais validam;
  em `SOFIA_STORAGE_MODE=production`, qualquer falha de conexão bloqueia o
  fluxo em vez de cair silenciosamente para SQLite. SQLite permanece somente
  para desenvolvimento/offline explícito.
- O pipeline é persistente, por documento e reprocessável. Falha em um arquivo
  não interrompe os demais.
- Cada documento produz extração/OCR, score de qualidade, artefatos de
  conhecimento, chunks, embeddings, relações, índice e validação; artefatos
  insuficientes ficam pendentes/quarentenados.
- O grafo semântico persiste relações observadas entre conceitos e documentos;
  coocorrência não é apresentada como causalidade. A rede neural é um apoio
  de adaptação/representação, não uma autorização para inventar fatos.
- Dados operacionais de observabilidade são armazenados sem pergunta/resposta
  brutas; conteúdos clínicos não entram nas estatísticas. A coleta usa hash
  não reversível, módulo, modelo, latência, confiança, fontes e feedback.
