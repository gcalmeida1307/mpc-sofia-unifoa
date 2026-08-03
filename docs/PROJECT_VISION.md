# PROJECT_VISION - SOFIA

## 1) Objetivo do SOFIA

O SOFIA e um copiloto operacional para ambientes de infraestrutura e operacoes.

Objetivo central:
- Ser o Kernel de decisao e orquestracao do ecossistema.
- Unificar interfaces (Dashboard, REST, MCP, CLI) em um unico Core.
- Transformar dados operacionais em contexto confiavel para acao.
- Usar IA como motor de raciocinio, sem acoplamento direto com conectores.

Resultado esperado:
- Menos acoplamento entre componentes.
- Mais consistencia de resposta em qualquer canal.
- Evolucao modular sem reescrever o sistema inteiro.

---

## 2) Arquitetura

Arquitetura alvo (Kernel-centric):

```text
               Dashboard
                    |
 REST ---------------|
 MCP ----------------|
 CLI ----------------|
                    v
               SOFIA CORE
                    |
   +----------------+----------------+
   |                |                |
   v                v                v
 Registry      Context Engine     Event Bus
   |                |                |
   +---------+------+--------+-------+
             |               |
             v               v
        Modules/Tools    Handlers/Agents
             |
   +---------+---------+---------+---------+
   |         |         |         |         |
   v         v         v         v         v
 Docker    Zabbix  Knowledge    SSH      Others
```

Principio estrutural:
- Toda entrada conversa com o Core.
- Modulos nao se acoplam entre si de forma direta.
- Integracoes externas sao adaptadores plugados no Core.

---

## 3) Epicos

### Epico 1 - Kernel Foundation
- Application como ponto unico de entrada.
- Lifecycle de startup/shutdown.
- Registry/Container para dependencia unica.
- Settings centralizado por dominio.

### Epico 2 - Modular Platform
- Contrato BaseModule para todos os modulos.
- Registro de capabilities e health por modulo.
- Descoberta de modulos para Dashboard, REST e MCP.

### Epico 3 - Event-Driven Core
- EventBus com publish/subscribe.
- Eventos operacionais padrao (host.down, host.recovered, etc.).
- Reacao desacoplada por handlers (planner, workflow, auditoria, memoria).

### Epico 4 - Intelligence Layer
- Context Engine consolidando ferramentas e estado.
- Planner para selecionar tools por intencao/custo.
- OpenAIService usando contexto estruturado.
- Aprendizado persistido com memoria operacional.

### Epico 5 - Governance and Safety
- ACL por tool/capability.
- Auditoria de acoes e trilha de decisao.
- Politicas para operacoes destrutivas.

---

## 4) Principios

1. Core-first
- O Core e a espinha dorsal do sistema.

2. Modularidade por contrato
- Todo modulo implementa o mesmo contrato de ciclo de vida e capacidades.

3. Event-driven
- Integracoes publicam eventos; consumidores reagem sem acoplamento.

4. Context before action
- Decisao passa por contexto consolidado antes de executar qualquer acao.

5. AI as reasoning engine
- IA raciocina sobre contexto; nao acessa conectores diretamente.

6. Backward compatibility com evolucao progressiva
- Migracoes devem preservar endpoints e operacao existente.

7. Observabilidade e seguranca
- Estado do kernel, configuracao mascarada, trilhas de evento e auditoria.

---

## 5) Como os modulos se comunicam

Modelo oficial:
- Modulo A nao chama Modulo B diretamente.
- Modulo A publica evento no EventBus.
- Core distribui para handlers/subscribers.
- Se necessario, o Core resolve dependencias via Registry.

Fluxo exemplo (incidente):
1. Snapshot detecta host indisponivel.
2. Publica `host.down` no EventBus.
3. Planner/Workflow/Auditoria recebem o evento.
4. Context Engine consolida evidencias.
5. OpenAIService propoe plano.
6. Workflow executa automacao aprovada.

Beneficio:
- Isolamento de falhas.
- Menor acoplamento.
- Maior escalabilidade funcional.

---

## 6) Papel da OpenAI

A OpenAI e o motor de raciocinio do SOFIA, nao a dona do contexto.

Responsabilidades:
- Interpretar perguntas e contexto consolidado.
- Produzir explicacao, plano de acao e proximos passos.
- Operar por interface padrao do OpenAIService.

Nao responsabilidades:
- Nao acessar Zabbix, Docker, SSH ou banco diretamente.
- Nao decidir fora dos dados fornecidos pelo Context Engine.

Contrato pratico:
- Pergunta -> Planner -> Tools/Context -> OpenAI -> Resposta/Plano.

---

## 7) Papel do MCP

O MCP e a camada de exposicao de capacidades do Core para clientes/agentes externos.

Responsabilidades:
- Expor tools padronizadas a partir do registry.
- Reusar o mesmo contrato de capacidades do Core.
- Permitir consumo seguro e governado das funcoes do SOFIA.

Beneficio:
- Uma unica fonte de verdade para tools (REST, Dashboard, MCP, CLI).
- Menos duplicacao de logica de integracao.

---

## 8) Roadmap

### Fase 0 - Estado atual (baseline)
- Application + lifecycle no Core.
- Registry com services centrais.
- EventBus inicial e primeiros handlers.
- Snapshot publicando eventos de host.
- Endpoint de observabilidade de kernel e settings.

### Fase 1 - Consolidacao de modulos
- Mover chamadas diretas para resolucao via registry/container.
- Completar contrato BaseModule em todos os modulos.
- Health/readiness por modulo com status agregado.

### Fase 2 - Eventos operacionais completos
- Catalogo de eventos padrao (infra, workflow, ai, seguranca).
- Replay/auditoria de eventos.
- EventBus persistente opcional para escala horizontal.

### Fase 3 - Inteligencia orientada a contexto
- Planner com score de risco/custo/latencia.
- Context Engine com janelas historicas e correlacao temporal.
- Aprendizado com memoria semantica e insights versionados.

### Fase 4 - Governanca e operacao enterprise
- ACL por capability (viewer/operator/admin).
- Trilha de aprovacao para acoes destrutivas.
- Observabilidade completa (metricas, logs, tracing, SLO).

---

## 9) Definicao de pronto (DoD) por evolucao

Uma entrega e considerada pronta quando:
- Mantem compatibilidade com endpoints existentes.
- Nao viola o principio Core-first.
- Evita acoplamento direto entre modulos.
- Atualiza documentacao e contratos de arquitetura.
- Inclui validacao de execucao no ambiente do SOFIA.
