# Observabilidade

O endpoint administrativo `/api/admin/observability` expõe traces com hash da
pergunta, módulo, intenção, complexidade, router, retrieval, provider, modelo,
confiança, latência e status. Spans registram entendimento, plano, retrieval e
verificação. O Pipeline Explorer usa eventos persistidos por documento.

Perguntas e respostas não são armazenadas pelo trace. O `trace_id` retornado ao
cliente permite correlacionar uma execução sem expor seu conteúdo.

`GET /api/admin/evaluation` executa a verificação determinística de corpus e
recuperação para todos os módulos. A nota retornada é um smoke score de
disponibilidade, pipeline e evidência recuperada; não é uma avaliação
semântica final nem substitui revisão por especialistas.
