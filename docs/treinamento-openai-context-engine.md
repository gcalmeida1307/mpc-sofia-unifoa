# SOFIA Core + OpenAI Responses API (Treinamento)

## Visao arquitetural
O SOFIA nao embute o ChatGPT como produto; ele usa modelo da OpenAI como motor de raciocinio.

Fluxo recomendado:

Pergunta -> Planner Engine -> Context Engine -> OpenAI Responses API -> Plano de acao -> Dashboard/REST/MCP

## Principio central
- O SOFIA conhece a infraestrutura.
- A OpenAI nao acessa Zabbix/Docker diretamente.
- O SOFIA entrega contexto estruturado para o modelo.

## Modulo AI implementado
Estrutura criada em `api/ai/`:
- `client.py`: cliente da Responses API (`/v1/responses`).
- `planner.py`: decide tools/capabilities por intencao.
- `context.py`: executa tools e monta contexto unico.
- `prompts.py`: prompt de sistema operacional.
- `memory.py`: agrega historico e memoria semantica.
- `tools.py`: adaptadores para Zabbix, Docker, Knowledge, Marketplace, Registry.
- `service.py`: orchestrator `OpenAIService`.

## Camada de aprendizado
Estrutura criada em `api/learning/` e `api/context/`:
- `learning/service.py`: extrai recorrencias, classifica familias e persiste insights.
- `context/infrastructure.py`: snapshot com cache e refresh periodico.
- `context/builder.py`: consolida tools + insights em um JSON unico.

O objetivo e transformar observacoes repetidas em conhecimento operacional reutilizavel.

## Endpoints
- `POST /ai/ask`: executa OpenAIService diretamente.
- `POST /assistant/ask`: usa OpenAIService para perguntas operacionais e fallback local se necessario.
- `GET /context/build?query=...`: inspeção do contexto consolidado.
- `GET /context/snapshot`: snapshot de infraestrutura.

## Configuracao
Variaveis de ambiente:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (padrao: `gpt-5`)

Exemplo:
```bash
export OPENAI_API_KEY="<sua-chave>"
export OPENAI_MODEL="gpt-5"
```

## Como testar
```bash
cd /opt/sofia

docker compose up -d --build

curl -sS -X POST http://127.0.0.1:8080/ai/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Quais hosts estao dando mais problema agora?"}'

curl -sS -X POST http://127.0.0.1:8080/assistant/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"quando eu olho o grupo switches, quais possuem problema agora?"}'
```

## Boas praticas
1. Nao pedir para o modelo "ler o Zabbix".
2. Sempre montar contexto JSON consolidado no SOFIA.
3. Planejar tools via Planner antes da chamada ao modelo.
4. Tratar fallback sem derrubar o endpoint.
5. Expor mesma capability para REST + MCP + Dashboard.
6. Persistir padroes recorrentes como insights, nao apenas como historico bruto.

## Proximos passos recomendados
1. Adicionar scheduler de snapshot (30-60s).
2. Persistir snapshots historicos no PostgreSQL.
3. Evoluir Planner com score de prioridade e risco.
4. Adicionar tools de VMware/Proxmox/Grafana.
5. Criar permissao por role para tools destrutivas.
