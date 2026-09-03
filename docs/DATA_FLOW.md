# Fluxo de dados

```text
pergunta → redação operacional para métricas → classificação de domínio
         → retrieval autorizado → ContextPackage → provider autorizado
         → verificação → resposta + fontes + trace_id

arquivo/link → RECEIVED → EXTRACTION/OCR → QUALITY_CHECK → MARKDOWN_READY
             → UNDERSTANDING → CHUNKING → EMBEDDING → RELATING → INDEXING
             → VALIDATING → READY
```

O mapa de redação externo existe apenas em memória durante uma requisição. A
resposta pode ser reidratada localmente por marcadores controlados, mas o mapa
não é persistido.
