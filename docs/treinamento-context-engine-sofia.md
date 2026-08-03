# Treinamento SOFIA Core - Context Engine com Zabbix

## Objetivo
Este material treina o time para operar o SOFIA com arquitetura orientada a contexto, evitando acoplamento direto da IA a cada ferramenta de infraestrutura.

## Problema que esta arquitetura resolve
Evitar o desenho fraco:

IA -> Zabbix API

e adotar o desenho escalavel:

IA -> Context Engine -> Infrastructure Snapshot -> Conectores (Zabbix, Docker, etc)

## Componentes
1. Infrastructure Snapshot Service
- Consolida estado operacional da infraestrutura.
- Fonte atual: Zabbix (hosts/problemas) e Docker (containers).
- Endpoint: `GET /context/snapshot`.
- Atualizacao: on-demand hoje; pode virar job periodico (30-60s).

2. Planner
- Interpreta pergunta e define capacidades necessarias para responder.
- Exemplo de capacidades: `zabbix.problems`, `docker.list_containers`, `n8n.trigger_webhook`.

3. Context Builder
- Junta `snapshot + knowledge + plano` para formar contexto consistente da resposta.
- Endpoint: `GET /context/build?query=...`.

## Fluxo recomendado
1. Usuario pergunta.
2. Planner classifica intencao.
3. Context Builder coleta snapshot consolidado.
4. Knowledge traz runbook e procedimento.
5. Assistente responde com evidencia + acao sugerida.
6. Se necessario, n8n executa workflow.

## Exemplo de pergunta
"quando eu olho o grupo switches, quais possuem problema agora?"

Resposta esperada:
- total de problemas no grupo;
- top problemas com severidade;
- hosts afetados;
- proxima acao tecnica.

## Endpoints de operacao
- `POST /assistant/ask`
- `GET /context/snapshot`
- `GET /context/build?query=quais+hosts+estao+com+average`
- `GET /security/validate`
- `POST /workflows/n8n/run`

## Validacao de seguranca
O backend aplica headers:
- HSTS
- CSP
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy

Checklist:
1. Confirmar endpoint `GET /security/validate`.
2. Garantir TLS no proxy reverso (Nginx/Traefik/Caddy).
3. Manter segredos em variaveis de ambiente (ex.: `OPENAI_API_KEY`).

## Identidade no chat
- Sem conta/logon: chat mostra `You`.
- Com nome salvo pelo usuario: chat mostra o nome informado.

## Como testar agora
```bash
cd /opt/sofia

docker compose up -d --build

curl -sS http://127.0.0.1:8080/security/validate

curl -sS "http://127.0.0.1:8080/context/build?query=quais%20problemas%20no%20grupo%20switches"

curl -sS -X POST http://127.0.0.1:8080/assistant/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"quantos módulos de marketplace eu possuo?"}'
```

## Proximo passo recomendado
- Agendar refresh de snapshot (30s) em tarefa periodica.
- Salvar snapshot no PostgreSQL para auditoria temporal.
- Adicionar conectores para VMware/Proxmox/Grafana no mesmo padrao.
