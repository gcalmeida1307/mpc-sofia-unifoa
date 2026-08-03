# SOFIA - Operacao do Assistente

## Objetivo
Este documento descreve como manter o assistente do SOFIA funcionando com respostas estaveis em JSON, com evidencias de Zabbix e automacao via n8n.

## O que foi corrigido
- Erro de JSON no frontend (`Internal Server Error` em texto puro) ao consultar o endpoint `POST /assistant/ask`.
- Causa raiz: ordenacao do fallback local em `vector_store.search()` quebrava quando havia empate de score.
- Correcao aplicada:
  - `api/services/vector_store.py`: sort com `key=lambda row: row[0]`.
  - `api/routes/assistant.py`: fallback de memoria protegido por `try/except`.

## Comportamento esperado
- O endpoint `POST /assistant/ask` deve sempre retornar JSON valido.
- Perguntas de Zabbix como:
  - "Quais problemas sao listados no zabbix agora?"
  - "quando eu olho o grupo switches, quais possuem problema agora?"
  devem retornar dados reais de problemas ativos, com severidade e hosts.

## Endpoints principais
- `POST /assistant/ask`: pergunta ao assistente.
- `GET /engine/memory/status`: status de memoria (PostgreSQL e Qdrant).
- `GET /engine/history`: historico de mensagens.
- `GET /workflows/n8n/templates`: templates de workflow n8n.
- `POST /workflows/n8n/run`: dispara webhook do n8n.

## Como validar rapido
```bash
cd /opt/sofia

docker compose up -d --build

curl -sS -X POST http://127.0.0.1:8080/assistant/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"quantos modulos de marktplace eu possuo?"}'

curl -sS -X POST http://127.0.0.1:8080/assistant/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Quais problemas sao listados no zabbix agora?"}'

curl -sS -X POST http://127.0.0.1:8080/assistant/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"quando eu olho o grupo switches, quais possuem problema agora?"}'
```

## OpenAI (opcional)
Para respostas mais naturais com base em evidencias:
- Configure `OPENAI_API_KEY`.
- Opcional: `OPENAI_MODEL` (padrao `gpt-4o-mini`).

`docker-compose.yml` ja aceita:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

## n8n (uso pratico)
1. Criar webhook no n8n, por exemplo: `sofia-investigation`.
2. Disparar pelo SOFIA:
```bash
curl -sS -X POST http://127.0.0.1:8080/workflows/n8n/run \
  -H 'Content-Type: application/json' \
  -d '{"webhook":"sofia-investigation","event":{"incident":"lab-12-down","priority":"high"}}'
```
3. No n8n, encadear consulta de APIs (Zabbix/Grafana/SQL) e notificacoes (Teams/Jira/email).

## Troubleshooting
### Erro: `Unexpected token 'I', "Internal S"...`
- Causa: backend retornou erro 500 em texto puro.
- Acao:
  1. Verificar logs: `docker logs --tail 200 sofia_api`
  2. Rebuild: `docker compose up -d --build`
  3. Revalidar `POST /assistant/ask`.

### Webhook n8n retorna 404
- Workflow/webhook nao existe ou nao esta ativo.
- Criar/ativar workflow no n8n com o mesmo path do webhook.

## Observacao
Mesmo sem OpenAI, o assistente segue funcional com respostas baseadas em dados reais de Zabbix e contexto do SOFIA.
