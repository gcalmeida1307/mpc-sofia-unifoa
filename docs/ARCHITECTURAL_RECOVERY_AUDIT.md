# Auditoria de recuperação arquitetural

## Escopo

Esta auditoria aplica a missão de recuperação arquitetural: preservar APIs,
interface e corpus existentes, remover decisões duplicadas e impedir que uma
alteração pontual em um domínio vire uma regra global. O objetivo é deixar o
fluxo documental generalizável para qualquer módulo, sem criar correções
específicas para assédio, gripe, Zabbix, horas extras ou outro caso isolado.

## Fluxo efetivo

```text
entrada HTTP
  -> contexto de sessão limitado (não é conhecimento)
  -> route_query / QueryPlan único
  -> gate de escopo e autorização
  -> interpretação semântica auxiliar (Ollama, sem autoridade de roteamento)
  -> seleção de fontes do módulo ativo
  -> retrieval lexical + semântico
  -> Evidence Judge / cobertura por fonte
  -> Context Package agrupado por documento e localização
  -> composição local ou LLM
  -> verificação + critic
  -> resposta e trilha de auditoria
  -> fila de expansão somente se a consulta documental ficou sem evidência
```

O `QueryPlan` determinístico é a autoridade da execução. O interpretador
semântico pode enriquecer vocabulário, mas não pode trocar intenção, módulo,
coleção, necessidade de recuperação ou estratégia.

## Primeiro ponto de perda identificado

Antes desta revisão, o plano era reconstruído em pontos diferentes: a rota era
classificada na orquestração, a memória reclassificava a pergunta e o pacote
de contexto podia classificá-la novamente. Isso permitia que uma etapa posterior
mudasse silenciosamente a tarefa original. O fluxo principal agora cria um
plano, passa o mesmo plano para memória e contexto e registra a estratégia nele.

O segundo ponto de perda era a ingestão: unidades estruturais eram novamente
fundidas apenas pelo limite de caracteres. Artigos, títulos e seções podiam
chegar ao índice como um bloco sem hierarquia. A ingestão agora mantém fronteiras
estruturais e grava a seção no metadado do chunk.

O terceiro ponto de perda era a fronteira de aprendizado: o endpoint persistia
`record_search_topic` antes de saber se a mensagem era conversa ou se a base já
respondia. Saudações, respostas encontradas e perguntas em andamento podiam
entrar na fila de expansão como se fossem lacunas de conhecimento. O registro
agora ocorre somente depois da resposta, quando `evidence_found` é falso e o
`ContextPackage` confirma uma tarefa documental. O histórico da sessão é
limitado a seis turnos e 8.000 caracteres por requisição; ele não é indexado,
aprendido nem persistido como corpus.

## Estratégias de execução

O contrato de consulta reconhece, de forma validada:

- `FACT_LOOKUP` — fato ou trecho localizado;
- `DOCUMENT_SUMMARY` — resumo de um documento ou conjunto de seções;
- `MULTI_DOCUMENT_SYNTHESIS` — síntese entre fontes explicitamente relacionadas;
- `CONCEPT_COMPARISON` — comparação de conceitos;
- `MULTI_HOP` — pergunta com mais de uma etapa de evidência;
- `STRUCTURED_DATA` — consulta determinística em CSV/XLSX e dados tipados;
- `RCA_INVESTIGATION` — investigação de causa-raiz.

Valores desconhecidos recebidos por clientes legados voltam para
`FACT_LOOKUP`, em vez de derrubar a execução ou permitir uma rota arbitrária.

## Classificação das partes existentes

| Parte | Decisão | Motivo |
|---|---|---|
| `QueryPlan` e `route_query` | Manter e fortalecer | Contrato determinístico de execução. |
| `semantic_planner` | Refatorar | Auxiliar a interpretação; não pode ser um segundo roteador. |
| `context_engine` | Refatorar | Receber o plano já criado; fallback permanece apenas para chamadas legadas. |
| ingestão estrutural | Refatorar | Preservar artigo, cláusula, seção, página e linhas. |
| retrieval híbrido e Evidence Judge | Manter/refatorar | Julgar aderência e cobertura, não apenas sobreposição de termos. |
| `domain_packages` | Manter | Selecionar fontes por módulo e política. |
| handlers locais de casos conhecidos | Manter temporariamente | Compatibilidade/regressão; não são o caminho de generalização. Novas exceções não devem ser adicionadas. |
| `server.py` e `orchestration.py` | Refatorar incrementalmente | Ainda concentram responsabilidades; a remoção segura exige testes por fatia, não reescrita. |
| `response_policy` e `session_context` | Adicionar | Centralizam a fronteira evidência → geração e impedem crescimento da conversa na orquestração. |
| RCA/grafo/learning | Manter como camadas superiores | Não podem substituir ingestão, retrieval ou evidência. |

## Garantias e limites

- O módulo ativo continua sendo a fronteira padrão de fontes.
- Fonte explicitamente nomeada pelo usuário pode ser procurada dentro do módulo
  ativo, mas não autoriza misturar outro módulo silenciosamente.
- Conversa direta não dispara retrieval.
- Conversa direta não entra na fila de expansão; somente uma tarefa documental
  sem evidência pode ser registrada como demanda de conhecimento.
- O provider externo/local nunca recebe uma resposta como se fosse evidência:
  com evidência aprovada, sintetiza o pacote local; sem evidência, a orientação
  é separada e rotulada, sujeita às políticas LGPD/FHIR.
- Dados estruturados seguem rota própria; não são tratados apenas como texto.
- PDFs e imagens dependem de extração validada; página ruim não pode ser
  anunciada como corpus plenamente pronto.
- Ausência, evidência rejeitada e falha de verificação são estados distintos na
  trilha de execução.
- Feedback não altera conhecimento de produção sem avaliação e publicação
  versionada.

## Validação realizada nesta etapa

Foi incluído um corpus cego com nomes fictícios e sem termos de domínio:

1. fato localizado em documento desconhecido;
2. resumo com seções estruturais;
3. plano de comparação;
4. plano multi-hop e RCA.

Esses casos evitam que a suíte passe apenas porque reconhece palavras de
Direito, Medicina ou Infraestrutura. A suíte completa permanece obrigatória
antes de declarar a recuperação concluída.
