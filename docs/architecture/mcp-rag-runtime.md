# Runtime MCP, RAG e IA do SOFIA

## Fluxo operacional

1. O planejador classifica a pergunta e seleciona capabilities.
2. Perguntas sobre runbooks, base ou procedimentos Zabbix combinam `knowledge_lookup` e telemetria.
3. O contexto executa ferramentas de leitura, recupera evidencias da base local/Qdrant e memoria de aprendizado.
4. O chat tenta o LLM local dentro de um orcamento curto de latencia. Se ele nao responder, retorna uma resposta RAG factual com proximo passo seguro.
5. Ciclos periodicos atualizam snapshot, fontes de conhecimento e insights persistidos.

## MCP HTTP

Endpoint: `POST /mcp` com `Content-Type: application/json`.

Metodos suportados:

- `initialize`
- `ping`
- `tools/list`
- `tools/call`

Ferramentas de leitura:

- `sofia.platform.status`
- `sofia.infrastructure.summary`
- `sofia.knowledge.search
- sofia.zabbix.active_summary: resumo atual de hosts afetados, problemas ativos e severidades do Zabbix.`

O servidor MCP nao expoe acoes mutaveis. Operacoes de ingestao e administracao continuam protegidas pela API administrativa do SOFIA.

## Operacao do LLM

O default interativo e `qwen2.5:1.5b`, adequado ao servidor CPU atual. O modelo maior pode ser usado sob demanda, mas nao deve ser colocado como fallback automatico do chat, pois aumenta a fila de inferencia.

## Controlled tool selection

SOFIA exposes read-only MCP tools through tools/list. The internal planner selects
the smallest capability set from the user question and invokes the selected MCP tool
through the same JSON-RPC contract used by external clients. This keeps operational
data collection explicit, auditable and free of destructive actions by default.
