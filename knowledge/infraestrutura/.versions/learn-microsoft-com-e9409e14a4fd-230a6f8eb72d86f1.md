# Relatório de usuários arriscados - Microsoft Entra ID Protection | Microsoft Learn

Fonte: https://learn.microsoft.com/pt-br/entra/id-protection/concept-risky-user-report
Capturado em: 2026-09-14T12:05:07.852575+00:00
Páginas no domínio: 1

## Relatório de usuários arriscados - Microsoft Entra ID Protection | Microsoft Learn
URL: https://learn.microsoft.com/pt-br/entra/id-protection/concept-risky-user-report

Relatório de usuários arriscados - Microsoft Entra ID Protection | Microsoft Learn
Pular para o conteúdo principal
Ignorar a experiência de chat do Pergunte e aprenda
Não há mais suporte para esse navegador.
Atualize o Microsoft Edge para aproveitar os recursos, o suporte técnico e as atualizações de segurança mais recentes.
Baixar o Microsoft Edge
Mais informações sobre o Internet Explorer e o Microsoft Edge
Sumário
Sair do modo Editor
Pergunte e aprenda
Pergunte e aprenda
Modo de leitura
Sumário
Ler em inglês
Adicionar
Adicionar a Planos
Copiar Markdown
Imprimir
Observação
O acesso a essa página exige autorização. Você pode tentar
entrar
ou
alterar diretórios
.
O acesso a essa página exige autorização. Você pode tentar
alterar os diretórios
.
Relatório de usuários arriscados do Microsoft Entra ID Protection
Comentários
Neste artigo
Saber quais usuários estão em risco e
por que
eles estão em risco é uma responsabilidade fundamental dos administradores de segurança e identidade. O relatório de usuários arriscados no Microsoft Entra ID Protection fornece o relatório completo, juntamente com um resumo de dados de risco e uma linha do tempo de atividade.
O relatório de usuários arriscados também é integrado ao Agente de Gerenciamento de Riscos de Identidade (versão prévia) para sugestões e insights aprimorados do agente. Se você tiver o Agente de Gerenciamento de Riscos de Identidade habilitado, poderá alternar entre a exibição padrão e a exibição do agente do relatório.
Este artigo fornece uma visão geral das informações e ações disponíveis no relatório de usuários arriscados.
Pré-requisitos
Para acessar este relatório, você precisa:
Microsoft Entra ID Free, Microsoft Entra ID P1 para gerenciamento de dados limitados de usuários.
Licenças do Microsoft Entra ID P2 para acesso completo aos dados de usuário arriscados.
O Leitor de Segurança
e o
Operador de Segurança
são as funções menos privilegiadas necessárias para usar a
exibição padrão
do relatório.
O Administrador de Segurança
é necessário para usar a
exibição do agente
do relatório e acessar os recursos do Agente de Gerenciamento de Riscos de Identidade.
O Administrador de Usuários
é necessário para redefinir senhas.
Relatório de usuários arriscados
A exibição padrão do relatório de usuários arriscados contém três seções principais: o gráfico de resumo de usuários arriscados em cada nível, novos usuários arriscados por dia e a lista completa de usuários arriscados. Se você tiver o
Agente de Gerenciamento de Riscos de Identidade
ativado, poderá usar o modo de exibição
Agente
para ver sugestões e insights do agente.
A
porcentagem de usuários arriscados em cada gráfico de nível de risco
mostra uma representação visual do usuário e seus níveis de risco. Este resumo visual permite que você veja rapidamente o estado das coisas em sua organização. Passe o mouse sobre cada segmento do gráfico para ver a porcentagem de usuários em cada nível de risco.
O
novo gráfico de usuários arriscados por dia
mostra uma linha do tempo de quando usuários arriscados foram detectados em sua organização. O gráfico também indica se o risco foi corrigido pelo usuário ou por um administrador. Passe o mouse sobre qualquer ponto no gráfico para ver a divisão dos usuários arriscados e a atividade de correção.
A metade inferior do relatório contém a lista completa de usuários arriscados.
Selecione o nome de um usuário arriscado para ver seus detalhes de risco.
Marque a caixa de seleção ao lado de um ou mais usuários para tomar medidas, como confirmar o comprometimento ou descartar o risco.
Se as opções de ação estiverem desabilitadas, será necessário ter uma função com privilégios mais elevados. Para obter mais informações, consulte
o que é o Microsoft Entra ID Protection
.
Detalhes arriscados do usuário
Na página Detalhes do Usuário Arriscado, você pode executar ações como ignorar o risco ou redefinir a senha do usuário.
No
relatório de usuários arriscados
, selecione um usuário para exibir mais detalhes sobre seus eventos de risco e até mesmo tomar medidas sobre esse usuário.
Os detalhes incluem informações básicas sobre o usuário e uma linha do tempo das atividades de risco recentes. A seção
Linha do Tempo
fornece uma visão cronológica dos eventos de risco associados ao usuário. A linha do tempo mostra quando o risco foi detectado, o nível de risco e o tipo de risco detectado.
Para ver eventos de entrada de risco junto com eventos de usuário arriscados, selecione a caixa de seleção
Agregar sinais de risco por entradas arriscadas
.
Sinais de risco unificados
Microsoft Entra ID Protection correlaciona sinais de Microsoft Defender e outras fontes para fornecer sinais de risco unificados para detecções de risco do usuário. Essa funcionalidade calcula uma Pontuação de Risco de Identidade abrangente com base em vários sinais de identidade de toda a malha de identidade, incluindo contas vinculadas e conjuntos de contas.
Você pode exibir sinais de risco unificados na exibição padrão e no modo de exibição do agente do relatório de usuários arriscados. Selecione um usuário na lista para ver detalhes de cada conta vinculada associada a um usuário arriscado, ajudando você a entender o escopo completo do risco na identidade de um usuário. Quando a Pontuação de Risco de Identidade aumenta, a pontuação do Microsoft Entra também aumenta, o que pode disparar automaticamente suas políticas de Acesso Condicional baseadas em risco.
A Pontuação de Risco de Identidade aparece no contexto de um usuário selecionado do relatório de usuários arriscados. A pontuação, o resumo de riscos e os links para investigar mais são fornecidos para ajudá-lo a entender o risco e tomar as medidas apropriadas. Selecione o link
Exibir relatório completo no Microsoft Defender
para ver os sinais correlacionados no Microsoft Defender para Identidade e investigar o usuário arriscado mais detalhadamente.
Para obter detalhes completos sobre como o risco unificado funciona, os pré-requisitos, como habilitar o recurso e a solução de problemas, consulte
sinais de risco unificados em Microsoft Entra ID Protection
.
Adotar medidas em um usuário de risco
A ação no nível do usuário se aplica a todas as detecções atualmente associadas a esse usuário. Se os botões de ação estiverem desabilitados, será necessário ter uma função com privilégios mais elevados. Os administradores podem tomar medidas sobre os usuários e optar por:
Redefinir senha
– essa ação revoga as sessões atuais do usuário.
Confirmar usuário comprometido
- Essa ação é tomada em um verdadeiro positivo. O ID Protection define o risco do usuário como alto e adiciona uma nova detecção, o Usuário comprometido confirmado pelo administrador. O usuário é considerado suspeito até que as etapas de correção sejam tomadas.
Confirmar usuário seguro
- Essa ação é tomada em um falso positivo. Isso elimina o risco e as detecções desse usuário e o coloca no modo de aprendizado para reaprender as propriedades de uso. Você pode usar essa opção para marcar falsos positivos.
Ignorar o risco de usuário
- Essa ação é tomada em um risco de usuário positivo benigno. Esse risco do usuário que detectamos é real, mas não é malicioso como os de um teste de penetração conhecido. Daqui para frente, os usuários semelhantes devem continuar sendo avaliados quanto ao risco.
Bloquear o usuário
– Essa ação impede que um usuário entre se o invasor tiver acesso à senha ou capacidade de executar a MFA.
Investigar com o Microsoft 365 Defender
– Essa ação leva os administradores ao portal do Microsoft Defender para permitir que um administrador investigue mais.
Comentários
Esta página foi útil?
Sim
Não
Não
Precisa de ajuda com este tópico?
Quer experimentar o Pergunte e aprenda para esclarecer ou guiar você neste tópico?
Pergunte e aprenda
Pergunte e aprenda
Sugerir uma correção?
Recursos adicionais
Last updated on
2026-07-03
Neste artigo
Esta página foi útil?
Precisa de ajuda com este tópico?
Quer experimentar o Pergunte e aprenda para esclarecer ou guiar você neste tópico?
Pergunte e aprenda
Pergunte e aprenda
Sugerir uma correção?
pt-br
Suas escolhas de privacidade
Tema
Claro
Escuro
Alto contraste
Aviso de isenção de responsabilidade sobre a IA
Versões anteriores
Blog
Contribuir
Privacidade
Privacidade da Integridade do Consumidor
Termos de Uso
Marcas Comerciais
© Microsoft 2026
