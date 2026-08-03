# SOFIA Core + OpenAI Responses API (Treinamento)

## Visao arquitetural
O SOFIA nao embute o ChatGPT como produto; ele usa modelo da OpenAI como motor de raciocinio.

Fluxo recomendado:

Pergunta -> Planner Engine -> Context Engine -> Reasoning Engine -> OpenAI Responses API -> Critic Engine -> Resposta

## Principio central
- O SOFIA conhece a infraestrutura.
- A OpenAI nao acessa Zabbix/Docker diretamente.
- O SOFIA entrega contexto estruturado para o modelo.

## Modulo AI implementado
Estrutura criada em `api/ai/`:
- `client.py`: cliente da Responses API (`/v1/responses`).
- `planner.py`: decide tools/capabilities por intencao.
- `reasoning.py`: define objetivo, restricoes e estrategia da resposta antes da chamada ao modelo.
- `critic.py`: valida a resposta candidata (consistencia, tamanho e aderencia ao contexto).
- `prompts.py`: prompt de sistema operacional.
- `tools.py`: adaptadores para Zabbix, Docker, Knowledge, Marketplace, Registry.
- `service.py`: orchestrator `OpenAIService` com pipeline Planner -> Context -> Reasoning -> OpenAI -> Critic.

## Camada de aprendizado
Estrutura criada em `api/learning/` e `api/context/`:
- `learning/service.py`: extrai recorrencias, classifica familias e persiste insights.
- `context/infrastructure.py`: snapshot com cache e refresh periodico.
- `context/builder.py`: consolida tools + insights em um JSON unico.

## Cognitive Engine (estado atual)
Pipeline atual do SOFIA:

Pergunta -> Planner -> Context Object -> Reasoning -> OpenAI -> Critic -> Resposta

Componentes:
- `ai/planner.py`: infere intent e capabilities; delega tools ao `CapabilityResolver`.
- `core/capability_resolver.py`: resolve capabilities para tools via Registry.
- `context/builder.py`: monta `Context` unificado com `snapshot`, `knowledge`, `insights`, `history`, `evidence` e `risks`.
- `ai/reasoning.py`: gera objetivo, justificativa, recomendacoes e restricoes antes da chamada ao modelo.
- `ai/critic.py`: valida consistencia da resposta, calcula `confidence` e aplica revisao quando necessario.
- `ai/tools.py`: executa tools com trilha de evidencia (duracao, sucesso, rollback hint).

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
4. Passar toda resposta candidata pelo Critic antes de responder ao usuario.
5. Tratar fallback sem derrubar o endpoint.
6. Expor mesma capability para REST + MCP + Dashboard.
7. Persistir padroes recorrentes como insights, nao apenas como historico bruto.

## Proximos passos recomendados
1. Adicionar scheduler de snapshot (30-60s) desacoplado da pergunta do usuario.
2. Evoluir intent `host_analysis` para analise temporal de 30 dias por grupo.
3. Persistir trilha de `evidence`/`tool trace` em tabela dedicada para auditoria.
4. Expor painel de metricas da IA (latencia, confidence, custo, precision).
5. Criar permissao por role para tools destrutivas.
