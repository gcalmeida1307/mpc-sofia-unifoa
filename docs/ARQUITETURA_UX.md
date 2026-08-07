# Arquitetura de experiência da SOFIA

A interface apresenta a mesma plataforma em níveis de leitura diferentes, sem duplicar a lógica operacional.

| Área | Pergunta respondida | Público principal |
|---|---|---|
| Executivo | Como está o ambiente e qual é a prioridade? | Gestores e usuários |
| Analytics | Como saúde, riscos e severidades se distribuem no tempo? | Gestores e analistas |
| Operações | Quais fontes e serviços estão disponíveis? | Analistas |
| Conversar | O que os dados autorizados respondem à minha pergunta? | Todos os usuários |
| Inteligência | O que foi lido, aprendido e persistido? | Administradores |
| Conhecimento | Quais fontes e documentos alimentam o RAG? | Administradores |
| Automações | De onde vêm os dados, como são processados e qual saída é gerada? | Administradores |
| Administração | Quem acessa, quem aguarda aprovação e o que foi auditado? | Administradores |

## Regras de apresentação

- Números operacionais vêm das APIs da SOFIA; o frontend apenas renderiza.
- Claude pode explicar evidências, mas não calcula saúde ou severidade.
- O Diário Cognitivo exibe ciclos e insights persistidos, nunca uma alegação genérica de “treinamento”.
- O progresso do chat informa estágios operacionais sem expor raciocínio interno ou dados sensíveis.
- O editor organiza conectores em Entradas, Processamento e Saídas, mantendo o grafo técnico disponível.
