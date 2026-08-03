# Contrato Interno de Arquitetura - SOFIA

## Objetivo
Definir o contrato interno padrao para que Dashboard, REST, MCP e OpenAIService usem a mesma espinha dorsal.

## Principio
- OpenAIService nao chama conectores de infraestrutura diretamente.
- OpenAIService chama somente Context Engine.
- Context Engine orquestra providers e retorna JSON consolidado.

## Diagrama
```text
Dashboard / MCP / REST
          |
          v
    OpenAIService
          |
          v
    Context Engine
          |
   +------+--------+--------+
   |      |        |        |
   v      v        v        v
Zabbix  Docker  Knowledge Registry
          |
          v
     Context JSON
          |
          v
 OpenAI Responses API
          |
          v
Resposta + Plano de acao
```

## Estrutura de pacotes
```text
api/
├── ai/
│   ├── service.py
│   ├── client.py
│   ├── planner.py
│   ├── prompts.py
│   ├── models.py
│   └── tools.py
├── context/
│   ├── builder.py
│   ├── infrastructure.py
│   ├── knowledge.py
│   └── registry.py
```

## Contrato do Planner
Entrada: `question: str`

Saida:
```json
{
  "intent": "operational-assistant",
  "tools": ["zabbix.list_problems", "registry.snapshot"],
  "needs_llm_reasoning": true
}
```

## Contrato do Context Builder
Entrada:
- `question`
- `plan`

Saida:
```json
{
  "summary": {
    "hosts": 234,
    "problems": 20,
    "containers": 0,
    "modules": 6
  },
  "question": "quando eu olho o grupo switches, quais possuem problema agora?",
  "plan": {"...": "..."},
  "tools": {"...": "..."}
}
```

## Contrato da Camada de Aprendizado
Entrada:
- Snapshot atual da infraestrutura.
- Historico recente de mensagens.
- Relevancia documental do Knowledge.

Saida:
- `summary`: estado consolidado.
- `patterns`: recorrencias detectadas.
- `top_hosts`: hosts com maior reincidencia.
- `knowledge_hits`: documentos que reforcam a analise.
- Persistencia em `assistant_insights`.

Exemplo de padrao:
```json
{
  "family": "network-switch-l2",
  "signal": "Recurring layer-2 / switch issues",
  "count": 18,
  "insight": "Ha recorrencia de eventos de switch/link/speed. Vale verificar uplinks, VLANs e cabos antes de atuar em cima do sintoma."
}
```

## Contrato do OpenAI Client
- Responsabilidade unica: chamar `POST /v1/responses`.
- Nao conhece Zabbix, Docker ou regras de negocio.

## SnapshotService
- Objetivo: evitar consultas completas em toda pergunta.
- Frequencia recomendada: 30-60s.
- Fonte atual: Zabbix + Docker.

## ToolExecutor
- Entrada: lista de tools do Planner.
- Saida: mapa `tool_name -> output`.
- Responsavel por padronizar execucao dos providers.

## Regras de seguranca
- Segredos apenas por variavel de ambiente.
- Headers de seguranca habilitados no backend.
- Operacoes destrutivas exigem controle de permissao em etapa futura.

## Roadmap imediato
1. Persistir snapshots historicos em PostgreSQL.
2. Adicionar providers de Grafana/VMware/Proxmox.
3. Adicionar ACL por tool (viewer/operator/admin).
4. Permitir que Planner selecione tools por custo/latencia.
5. Persistir e versionar aprendizados de operacao como uma base viva de insights.