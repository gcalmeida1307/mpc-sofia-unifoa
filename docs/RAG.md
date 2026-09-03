# Retrieval aumentado

O retrieval executa filtro físico pelo módulo e, quando pedido, seleção por
nome de arquivo. Depois calcula cobertura lexical e uma pontuação BM25-like,
similaridade vetorial TF-IDF local e reranking por intenção. Evidência abaixo
do gate não é enviada ao provider.

Resumo de documento seleciona representantes explicativos por fonte. Perguntas
comparativas preservam fontes de papéis diferentes. Perguntas clínicas usam
preferência por guidance clínico; CID/ICD é vocabulário de classificação, não
evidência automática para diagnóstico.
