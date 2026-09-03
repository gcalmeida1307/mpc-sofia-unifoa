# Avaliação e regressão

`tests/evals/manifest.json` lista os 11 módulos e as categorias mínimas: simples,
documento, inexistente, comparação, evidência insuficiente/contraditória,
fora do domínio, prompt injection, permissão, complexidade, resumo, entidades,
relações e tool routing.

O teste canário em `tests/test_canary_pipeline.py` percorre uma fonte controlada
até READY e então consulta o RAG. O baseline atual antes desta rodada era 31
testes; a contagem final deve ser obtida executando a suíte, sem números
inventados.
