# Experience Intelligence

O SOFIA separa estado, investigação, história e administração.

## Fluxo temporal

1. Snapshots de um domínio são normalizados em `domain_events`.
2. Cada evento mantém origem, entidades, evidência, confiança e um nível: `observed`, `correlated`, `inferred` ou `learned`.
3. `domain_event_relations` registra relações auditáveis sem transformar hipótese em fato.
4. A API `/timeline/{domain_id}` agrupa eventos próximos em episódios nas janelas de 15 minutos a 7 dias.

## Experiências

- Executivo: estado, risco e decisão.
- Investigação: evidências, gráficos e causa/consequência.
- Linha do Tempo: sequência, relações e aprendizado.
- Administração: tecnologia interna, usuários, papéis, auditoria e saúde técnica.

## Acesso por domínio

O papel global controla a plataforma. `domain_memberships` associa usuário, domínio, papel e escopo/unidade. `domain_roles` contém a hierarquia e capabilities. Alterar uma associação revoga as sessões ativas.

## IA com revisão humana

Claude ou Ollama pode propor nome, entidades, métricas, tema, perguntas e hierarquia. A proposta não grava dados. Um administrador revisa o formulário e somente a submissão explícita instala o domínio. Guardrails de saúde e emprego são acrescentadas às propostas relevantes.

## Respostas ricas

Além do texto, o contrato `presentation` pode entregar indicadores, gráfico, timeline, entidades e ações. Os valores vêm das evidências coletadas; o provedor de linguagem não calcula indicadores operacionais.
