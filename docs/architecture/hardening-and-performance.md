# Hardening e performance do SOFIA

Este incremento consolida controles que devem permanecer na camada da aplicação. O MCP continua expondo contratos de ferramentas; autorização, política e decisão operacional permanecem fora dele.

## Fluxo operacional

```text
Fonte (Zabbix/Docker)
  -> snapshot compartilhado com TTL
  -> contexto, dashboard, investigação, analytics e automações
  -> resposta com fontes e modo de execução explícitos
```

Uma pergunta determinística usa dados locais/snapshot. Claude é acionado para interpretação ou explicação e o Ollama permanece como fallback. A resposta informa `sources_used`, `response_mode` e `degraded` para que caminhos diferentes não pareçam equivalentes.

## Autorização por capacidade

As rotas são protegidas por capacidades, além da autenticação:

- `dashboard.read`
- `assistant.ask`
- `zabbix.read`
- `workflow.execute`
- `knowledge.manage`
- `intelligence.manage`
- `platform.manage`

Os perfis persistidos atuais continuam compatíveis: `user` recebe somente consulta/chat e `admin` recebe todas as capacidades. A API `/auth/me` publica as capacidades efetivas para a interface. Negativas são auditadas.

## Proteção SSRF do Knowledge Hub

Antes de cada requisição e de cada redirecionamento, a URL é resolvida novamente. São bloqueados:

- loopback e redes privadas;
- link-local, incluindo metadados de nuvem;
- endereços reservados, multicast e não especificados;
- URLs com credenciais embutidas;
- esquemas diferentes de HTTP/HTTPS;
- domínios fora de `allowed_domains`, quando configurado.

Fontes internas legítimas devem ser publicadas por um proxy HTTPS controlado. Não desabilite essa validação para alcançar IPs internos.

## Resiliência e desempenho

- O snapshot central evita consultas integrais repetidas ao Zabbix.
- O cliente Zabbix usa timeout, uma repetição curta para falhas transitórias e circuito de 20 segundos após falhas consecutivas.
- A ingestão RAG só recalcula embeddings quando o conteúdo da página mudou.
- O compilador de workflows é independente do armazenamento e rejeita ciclos, arestas duplicadas e referências inválidas.
- Índices cobrem datas, status, ferramenta, tipo e assinatura nas tabelas de maior crescimento.
- Na inicialização, a retenção remove snapshots acima de 30 dias e telemetria/auditoria operacional acima de 90 dias. Usuários e conhecimento nunca são removidos por essa rotina.

Processamento pesado poderá migrar para uma fila quando medições demonstrarem saturação. Redis/Celery não são requisitos antes disso.

## Métricas Prometheus

Além de CPU, memória, disco e PostgreSQL, `/metrics` publica:

- `sofia_http_requests_total`
- `sofia_http_request_duration_seconds`
- `sofia_integration_requests_total`
- `sofia_integration_request_duration_seconds`
- `sofia_llm_requests_total`
- `sofia_llm_tokens_total`
- `sofia_workflow_runs_total`
- `sofia_snapshot_duration_seconds`
- `sofia_snapshot_age_seconds`

Alertas recomendados: aumento do p95 HTTP, circuito Zabbix aberto, falhas de workflow, crescimento de modo degradado e snapshot com idade superior a duas vezes o intervalo configurado.
