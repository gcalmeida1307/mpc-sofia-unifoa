# Avaliação e regressão

`tests/evals/manifest.json` lista os 11 módulos e as categorias mínimas: simples,
documento, inexistente, comparação, evidência insuficiente/contraditória,
fora do domínio, prompt injection, permissão, complexidade, resumo, entidades,
relações e tool routing.

O teste canário em `tests/test_canary_pipeline.py` percorre uma fonte controlada
até READY e então consulta o RAG. O baseline atual antes desta rodada era 31
testes; a contagem final deve ser obtida executando a suíte, sem números
inventados.

## Production Gate

O gate de produção combina os dez níveis de prontidão de cada módulo com
armazenamento primário, criptografia, quarentena e regressão. Ele é estrito:

- `tests/evals/manifest.json` separa casos `reviewed: true` dos casos em rascunho;
- uma pergunta que espera evidência precisa declarar `expected_sources`;
- um caso de `insufficient_evidence` valida justamente a ausência de evidência;
- módulos com corpus, mas sem caso revisado, e módulos sem corpus aparecem como
  bloqueios próprios;
- o score mede recuperação e aderência documental, não inventa qualidade da
  redação de uma LLM.

Para validar a parte operacional sem persistir perguntas ou respostas, execute:

```powershell
.\.venv\Scripts\python.exe scripts\run_readiness_canary.py
```

Depois, use `GET /api/admin/production-gate` ou o botão **Production Gate** no
Pipeline Explorer. O canário fecha a presença de telemetria; ele não substitui
uma revisão humana dos casos dourados.
