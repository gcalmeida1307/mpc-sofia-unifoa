# GUIA COMPLETO - SOFIA

Este documento consolida, em um unico lugar, o funcionamento do SOFIA.
A documentacao por assunto continua valida e recomendada para aprofundamento.

Para instalação, atualização, validação, backup e segurança operacional, siga primeiro o [Runbook operacional](RUNBOOK_OPERACIONAL.md).

## 1. O que e o SOFIA

SOFIA e uma plataforma operacional orientada a contexto para infraestrutura.
Nao e apenas um chatbot. O objetivo e atuar como um nucleo de decisao e orquestracao.

Principios:
- Core-first: toda entrada passa pelo Core.
- Context before action: primeiro consolidar evidencia, depois agir.
- Modularidade por contrato: modulos padronizados, baixo acoplamento.
- Event-driven: eventos desacoplam produtores e consumidores.
- AI as reasoning engine: IA raciocina com contexto, nao consulta conectores diretamente.

## 2. Arquitetura unificada

Fluxo cognitivo implementado:

Pergunta -> Planner -> Context -> Reasoning -> OpenAI/fallback -> Critic -> Resposta -> Learning

Fluxo autonomo implementado:

Scheduler -> Snapshot -> Learning -> Insight -> Dashboard

Arquitetura macro:

- Canais de entrada: Dashboard, REST, MCP.
- Core: lifecycle, registry, event bus, seguranca, schedulers.
- Context Engine: consolida snapshot, tools, riscos, historico, knowledge.
- AI Engine: planner, hypothesis engine, agent runtime, reasoning, critic, learning loop.
- Providers/Modulos: Zabbix, Docker, Knowledge, Marketplace, Workflow, N8N, SSH.
- Persistencia: PostgreSQL (auditoria, snapshots, metricas e ciclos).
- Memoria semantica: Qdrant (com fallback local).

## 3. Estrutura principal do projeto

- api/main.py: entrypoint da aplicacao.
- api/core/: kernel (application, registry, event bus, schedulers, bootstrap).
- api/context/: snapshot e construcao de contexto.
- api/ai/: pipeline cognitivo e ferramentas de IA.
- api/routes/: endpoints REST.
- api/services/: persistencia, integracoes e utilitarios.
- api/static/: dashboard web.
- docs/: documentacao por assunto.

## 4. Modulos e capacidades

Modulos registrados no Core:
- zabbix
- docker
- knowledge
- marketplace
- workflow
- n8n
- ssh

Capacidades-chave:
- host_count
- host_analysis
- incident_analysis
- network_investigation
- security_investigation
- capacity_investigation
- docker_observe
- docker_restart
- marketplace_browse
- knowledge_lookup
- workflow_lookup
- registry_snapshot
- learning_insights

## 5. Pipeline de IA (estado atual)

### 5.1 Planner
- Classifica intencao e capacidades.
- Ordena capacidades por politica adaptativa (weights aprendidos).
- Resolve tools via capability resolver + registry.

### 5.2 Agent Runtime
Seleciona agente especialista para o caso:
- Operations Agent
- Infrastructure Agent
- Security Agent
- Database Agent
- Network Agent
- Developer Agent
- Learning Agent
- Automation Agent

Cada agente possui:
- objetivos
- playbooks
- memoria de dominio
- orcamento de tools
- foco de critic

### 5.3 Hypothesis Engine
- Recebe sintoma/pergunta.
- Gera hipoteses por dominio (network/security/capacity/general).
- Prioriza por score de confianca e custo de verificacao.
- Define evidencia esperada e ferramentas de verificacao.

### 5.4 Context Builder
Consolida:
- snapshot de infraestrutura
- saida das tools
- riscos
- historico
- insights de aprendizado
- agente selecionado
- hipotese selecionada

### 5.5 Reasoning
- Define objetivo operacional.
- Gera recomendacoes acionaveis.
- Incorpora hipotese prioritaria no plano de acao.

### 5.6 Claude/Ollama
- Usa Anthropic Claude por `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` e `ANTHROPIC_MAX_TOKENS`.
- Usa prompt caching quando aplicável para reduzir latência e consumo.
- Em indisponibilidade, erro ou falta de crédito, usa Ollama como fallback local.

### 5.7 Critic
- Valida consistencia da resposta.
- Ajusta confianca.
- Pode revisar resposta automaticamente.

### 5.8 Learning Loop
Pos-resposta, executa:
- registrar decisao + evidencias + resultado
- gerar insight candidato
- atualizar indice de knowledge/memoria
- atualizar pesos do planner

## 6. Rotina autonoma de investigacao

Watchers continuos:
- infra watcher
- security watcher
- capacity watcher

Quando detecta anomalia:
- abre investigacao
- roda hypothesis engine
- persiste evidencia e resumo
- publica evento de investigacao
- expoe no dashboard

## 7. Persistencia e auditoria (PostgreSQL)

Tabelas principais:
- assistant_messages
- assistant_insights
- infra_snapshots
- tool_execution_audit
- ai_response_metrics
- ai_hypothesis_runs
- ai_learning_cycles
- planner_policy_weights
- autonomous_investigations

Objetivo:
- rastreabilidade de resposta
- evidencia auditavel
- analise temporal
- melhoria continua do roteamento

## 8. Endpoints essenciais

### 8.1 Core e observabilidade
- GET /core/kernel
- GET /core/registry
- GET /core/settings
- GET /security/validate

### 8.2 IA e assistente
- POST /ai/ask
- POST /assistant/ask

### 8.3 Contexto e aprendizado
- GET /context/snapshot
- GET /context/build?query=...
- POST /learning/train
- GET /learning/insights

### 8.4 Engine e painel
- GET /engine/ai/metrics
- GET /engine/ai/panel
- GET /engine/evidence/audit
- GET /engine/temporal/groups
- GET /engine/agents/status
- GET /engine/investigations/recent
- GET /engine/intelligence/summary

## 9. Dashboard (UI)

O dashboard mostra:
- status de modulos e capacidades
- metricas de IA
- tendencias por grupo (30 dias)
- auditoria de tools
- investigacoes autonomas recentes
- agentes especialistas
- chat operacional

Comportamentos implementados:
- scroll spy no menu por secao
- carregamento resiliente por widget (safe load)
- tolerancia a falha parcial de endpoint

## 10. Configuracao (.env local)

Variaveis principais:
- ANTHROPIC_API_KEY
- ANTHROPIC_MODEL
- ANTHROPIC_MAX_TOKENS
- OLLAMA_BASE_URL
- OLLAMA_MODEL
- SNAPSHOT_INTERVAL_SECONDS
- AUTONOMOUS_INVESTIGATION_INTERVAL_SECONDS
- AI_METRICS_WINDOW_HOURS
- REQUEST_RATE_LIMIT_PER_MINUTE
- SECURITY_ADMIN_API_KEY
- SECURITY_MFA_TOTP_SECRET
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- ZABBIX_URL
- ZABBIX_USER
- ZABBIX_PASSWORD

O `.env` não é versionado. Se Claude estiver sem crédito ou indisponível, a SOFIA continua operando com Ollama e respostas determinísticas quando aplicável.

## 11. Seguranca

Implementacoes atuais:
- headers de seguranca no backend
- protecao de endpoints criticos por chave admin
- TOTP opcional para acoes sensiveis
- rate limit de endpoints de IA
- PostgreSQL com politica SCRAM e configuracao hardening

Pontos de producao:
- TLS em proxy reverso
- senha forte de banco
- firewall restritivo
- segredos fora do codigo

## 12. Operacao rapida

Subir stack:

```bash
cd /opt/sofia
docker compose up -d --build
```

Validar kernel:

```bash
curl -sS http://127.0.0.1:8080/core/kernel
```

Validar IA:

```bash
curl -sS -X POST http://127.0.0.1:8080/ai/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Switches estao lentos com picos de broadcast. O que investigar?"}'
```

Validar painel:

```bash
curl -sS "http://127.0.0.1:8080/engine/ai/panel?hours=24"
```

## 13. Troubleshooting rapido

1. Chat sem resposta natural
- Verificar OPENAI_API_KEY.
- Verificar quota/billing da conta OpenAI.
- Verificar se llm_used=true em /ai/ask.

2. Frontend nao carrega completo
- Verificar /ui e /ui/app.js (status 200).
- Verificar /engine/ai/panel e /core/registry.
- A UI suporta carga parcial e deve continuar funcional.

3. Dados de Zabbix ausentes
- Revisar ZABBIX_URL, ZABBIX_USER, ZABBIX_PASSWORD.
- Verificar conectividade do container.

4. Persistencia vazia
- Verificar postgres e credenciais.
- Verificar readiness do servico.

## 14. O que ja esta tangivel hoje

- Investigacao por hipotese com confianca e custo de verificacao.
- Aprendizado pos-resposta persistido.
- Ajuste adaptativo de politica do planner.
- Watchers autonomos abrindo investigacao.
- Painel com sinais de inteligencia (hipoteses, aprendizado, investigacoes).
- Auditoria formal de execucao e metricas de IA.

## 15. Documentacao por assunto (mantida)

Este guia consolida tudo, mas os documentos detalhados seguem ativos:
- visao e direcao de produto
- contrato de arquitetura
- operacao do assistente
- treinamento de context engine
- treinamento OpenAI + cognitive engine
- hardening de seguranca
- docs de modulos (Docker, Zabbix)

Use este arquivo como guia principal e os demais como referencia de profundidade.

## 16. Prioridades Operacionais (Epic 2.5)

### Prioridade zero
- Garantir caminho padrao com IA ativa: llm_used=true.
- Ordem recomendada de providers:
  1) OpenAI (quando quota/billing ativos)
  2) Ollama (fallback local/remoto)
  3) fallback deterministico (ultimo recurso)

### Prioridade 1
- Transformar o Hypothesis Engine de regras para hibrido com LLM:
  - LLM propõe hipoteses
  - Planner e tools validam
  - Critic aprova/refuta com evidencia

### Prioridade 2
- Executor paralelo de tools por plano, com coleta de evidencias unificada.

### Prioridade 3
- Evoluir Knowledge de busca simples para retriever + ranking + resumo consolidado.

### Prioridade 4
- Respostas com autoavaliacao explicita:
  - quais evidencias embasaram
  - confianca
  - por que essa acao foi recomendada

### Prioridade 5
- Evoluir de Learning para Experience:
  - lembrar casos similares de longo prazo
  - reutilizar conclusoes historicas no contexto atual

### Prioridade 6
- Operacao proativa de ponta a ponta:
  - observar
  - levantar hipotese
  - investigar
  - concluir
  - abrir chamado/notificar
  - publicar no dashboard

## 17. Configuracao de Multi-IA (OpenAI + Ollama)

Variaveis adicionais:
- OLLAMA_BASE_URL
- OLLAMA_MODEL
- OLLAMA_API_KEY
- OLLAMA_MODE (native ou openai)

Comportamento:
- O SOFIA tenta OpenAI primeiro.
- Se OpenAI falhar (quota/erro/rede), tenta Ollama automaticamente.
- Apenas se ambos falharem, aplica fallback deterministico.

Validacao recomendada:
- Executar POST /ai/ask.
- Confirmar campos:
  - llm_used=true
  - llm_provider=openai ou ollama
