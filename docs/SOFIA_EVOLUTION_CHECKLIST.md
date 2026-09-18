# Checklist de evolução do SOFIA

Este checklist é o registro operacional da implementação do plano de evolução.
Uma etapa só muda para `TESTADO` depois de uma execução verificável dos testes.
`PENDENTE` significa que há trabalho restante; `BLOQUEADO` significa que depende
de requisito externo, contrato de cliente ou validação especializada.

## Baseline

- [x] Inventário do núcleo atual e dos contratos existentes — `TESTADO`
- [x] Baseline antes da mudança — `TESTADO`: 136 testes passaram
- [x] Regressão completa após a implementação — `TESTADO`: 159 testes passaram em 5m49s (suíte isolada do runtime externo; testes do planner habilitam a simulação explicitamente)

## Fase 1 — qualidade da recuperação e versionamento

- [x] Busca lexical e densa em paralelo com fusão RRF — `IMPLEMENTADO`
- [x] Termos exatos continuam com busca literal determinística — `TESTADO` na regressão existente
- [x] Autoencoder retirado do ranking e identificado apenas como diagnóstico — `IMPLEMENTADO`
- [x] Índice preparado em staging — `IMPLEMENTADO`
- [x] Ponteiro ativo publicado atomicamente — `IMPLEMENTADO`
- [x] Rollback para versão anterior — `TESTADO`
- [x] Testes de RRF, staging, publicação e rollback — `TESTADO`: suíte específica passou

## Fase 2 — avaliação e resiliência

- [ ] Casos dourados por módulo com expectativa de fonte e evidência — `PARCIAL`: 5/10 casos revisados; os 5 restantes continuam rascunho. Os 5 casos revisados passam após alinhar o caso de governança aos termos efetivamente presentes na fonte.
- [x] Gate determinístico de casos dourados — `IMPLEMENTADO` e bloqueia rascunhos
- [x] Fila persistente com tentativas, lease e backoff — `IMPLEMENTADO`
- [x] Recuperação de jobs após reinício — `IMPLEMENTADO`: jobs pendentes são reidratados pelo worker, respeitando `available_at`
- [x] Circuit breaker por provider — `IMPLEMENTADO`
- [x] Fallback controlado para evidência estática — `TESTADO` pela regressão do orquestrador
- [x] Testes de fila e circuit breaker — `TESTADO`: suíte específica passou com 17 testes

## Fase 2.1 — interpretação semântica local

- [x] Ollama local como interpretador auxiliar antes da recuperação — `IMPLEMENTADO`
- [x] Ollama sem acesso ao corpus e sem autoridade para alterar rota, módulo ou permissões — `TESTADO`
- [x] Vocabulário semântico bounded e fallback determinístico sem contaminar a busca — `TESTADO`
- [x] Cache em memória por digest da consulta, sem persistir pergunta bruta — `TESTADO`
- [x] Circuit breaker do interpretador local para evitar repetir timeout em sequência — `IMPLEMENTADO`
- [x] Síntese final somente após retrieval + Evidence Judge quando o planner local participar — `TESTADO`
- [ ] Smoke test do modelo Ollama configurado — `PENDENTE`: o endpoint local está online, mas `qwen3.5:4b` não respondeu em até 30s nesta máquina; o fallback determinístico foi exercitado e passou.

## Fase 3 — privacidade e melhoria controlada

- [x] Sanitização em camadas com dicionário de entidades — `IMPLEMENTADO`
- [x] Feedback isolado como candidato de avaliação — `IMPLEMENTADO`
- [x] Candidato não entra automaticamente na base autoritativa — `TESTADO`
- [x] Revisão explícita antes de promover candidato — `IMPLEMENTADO`: endpoint de revisão mantém aprovação separada da base
- [x] Testes de não vazamento e promoção — `TESTADO`: candidato metadata-only não cria arquivo nem altera corpus

## Fase 4 — interoperabilidade sob demanda

- [x] Isolamento e namespace FHIR R4 — `IMPLEMENTADO`
- [x] Capability Statement para R4 — `TESTADO` com rotas legadas preservadas
- [ ] Escopo HL7 v2 por cliente — `BLOQUEADO`: faltam mensagens e requisitos do integrador
- [ ] Escopo TISS por cliente — `BLOQUEADO`: faltam transações e requisitos do integrador
- [x] Testes de contrato FHIR R4 — `TESTADO`: namespace R4 e rotas legadas presentes

## Critério de encerramento

- [ ] Todos os itens implementáveis passam nos testes de regressão — `PENDENTE`: código implementado passou; cobertura aprovada ainda não abrange todos os módulos
- [x] Nenhuma fase é declarada concluída com testes falhando — `TESTADO`
- [x] Itens bloqueados têm requisito de entrada e decisão registrada — `TESTADO`: HL7 v2/TISS aguardam contrato de integração

## Resultado da validação real

- Suíte completa: `159 passed, 4 warnings` em 5m49s.
- Lint global: `ruff check api tests` passou.
- Build frontend: `pnpm build` passou.
- Runtime Ollama: endpoint `/api/tags` respondeu; geração de `qwen3.5:4b` excedeu 30s e permaneceu em fallback local.
- Gate dourado: `5/5` casos revisados passam com `100%`; publicação global permanece `BLOQUEADA` até haver casos aprovados para todos os módulos e corpus para `secretaria`.
- Bloqueios reais: 5 módulos têm casos ainda em rascunho e `secretaria` não possui corpus local.
- Escopo conversacional: pedidos concretos fora do domínio ativo são bloqueados antes do provider e não recebem resposta gerada como se pertencessem ao módulo.
