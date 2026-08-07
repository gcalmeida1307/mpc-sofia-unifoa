# SOFIA — arquitetura de interface

## Objetivo

A interface deve apresentar uma decisão por vez, manter detalhes técnicos sob demanda e preservar a mesma experiência em tema claro e escuro. O frontend atual continua em HTML e JavaScript nativos para aproveitar as APIs FastAPI e o editor já funcional sem uma migração disruptiva.

## Navegação

- Desktop: sidebar agrupada e recolhível.
- Tablet: sidebar em formato drawer.
- Mobile: barra inferior para Executivo, Analytics, Ambiente e Conversar; **Mais** abre o restante.
- Links administrativos são montados apenas para administradores.
- O menu do usuário concentra perfil, tema, administração e logout.

## Design tokens

Novos componentes devem usar somente tokens semânticos definidos ao final de `static/styles.css`:

- superfícies: `--background`, `--surface-1`, `--surface-2`, `--surface-3`, `--surface-hover`;
- texto: `--text-primary`, `--text-secondary`, `--text-disabled`;
- estados: `--success`, `--info`, `--warning`, `--danger` e respectivas versões `-soft`;
- estrutura: `--border-subtle`, `--shadow`, `--focus-ring`.

Não adicionar hexadecimal de fundo, texto ou borda dentro de componentes novos.

## Hierarquia das páginas

- **Executivo:** saúde, mudanças, evolução, riscos e ação recomendada.
- **Analytics:** filtros, indicadores, distribuição, histórico e ranking.
- **Ambiente:** fontes, recursos, serviços e mudanças horárias.
- **Conversar:** resposta principal; fonte, confiança, gráficos e evidências sob demanda.
- **Inteligência:** Diário Cognitivo como visão inicial; agentes em uma aba secundária.
- **Conhecimento:** resumo do índice, fontes, cadastro e upload.
- **Automações:** templates, metadados do fluxo, catálogo, canvas, etapas e resultado.

## Automação

Templates disponíveis:

- incidente de rede;
- resumo da madrugada;
- risco de capacidade;
- relatório executivo;
- lentidão SQL.

Cada nó possui configuração em drawer. No bloco Zabbix, operação, período, escopo reconhecido e severidade mínima são persistidos e aplicados pelo executor. Durante a execução os nós passam visualmente por `queued`, `running`, `completed` ou `failed`.

## Ergonomia e acessibilidade

- controles principais com pelo menos 44 px;
- foco de teclado visível;
- informação importante nunca depende somente de cor;
- contraste específico para os dois temas;
- suporte a `prefers-reduced-motion`;
- editor completo preservado em desktop/tablet e navegável em telas menores;
- logs, JSON e evidências extensas ficam recolhidos até solicitação do usuário.

## Regra de evolução

Antes de criar uma tela nova, verificar se a informação pertence a uma página existente. Reutilizar painéis, estados e tokens. Mudanças de tema e responsividade devem ser validadas nos pontos de quebra de 440, 760, 900, 1050 e 1250 px.
