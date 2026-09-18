# Manual Completo do Zabbix 6.0 | PDF | Rede de computadores | Rede mundial de computadores

Fonte: https://pt.scribd.com/document/855576618/Zabbix-Documentation-6-0-Pt
Capturado em: 2026-09-10T14:53:56.555058+00:00
Páginas no domínio: 10

## Manual Completo do Zabbix 6.0 | PDF | Rede de computadores | Rede mundial de computadores
URL: https://pt.scribd.com/document/855576618/Zabbix-Documentation-6-0-Pt

Manual Completo do Zabbix 6.0 | PDF | Rede de computadores | Rede mundial de computadores
Pular para o conteúdo principal
Abrir o menu de navegação
Fechar sugestões
Pesquisar
Pesquisar
pt
Change Language,
Português
Mudar o idioma
,
Português
Carregar
Fazer login
Fazer login
0 notas
0% acharam este documento útil (0 voto)
28 visualizações
1.847 páginas
Manual Completo do Zabbix 6.0
O documento é a documentação do Zabbix 6.0, datada de 21 de novembro de 2023, que inclui uma introdução ao software, suas funcionalidades e uma visão geral. Ele detalha as atualizações e novidades de várias versões do Zabbix, além de fornecer informações sobre instalação, definições e processos relacionados. A documentação é estruturada em seções que abordam desde a instalação até problemas conhecidos.
Enviado por
yuri kaizer
Título e descrição aprimorados por IA
Direitos autorais
© All Rights Reserved
Levamos muito a sério os direitos de conteúdo. Se você suspeita que este conteúdo é seu,
reivindique-o aqui
.
Formatos disponíveis
Baixe no formato PDF, TXT ou leia on-line no Scribd
Baixar
Salvar
Salvar Zabbix Documentation 6.0.Pt para ler mais tarde
Compartilhar
0%
0% acharam este documento útil, Marcar esse documento como útil
0%
0% acharam que esse documento não foi útil, Marcar esse documento como não foi útil
Imprimir
Incorporar
Relatório
0 notas
0% acharam este documento útil (0 voto)
28 visualizações
1.847 páginas
Manual Completo do Zabbix 6.0
O documento é a documentação do Zabbix 6.0, datada de 21 de novembro de 2023, que inclui uma introdução ao software, suas funcionalidades e uma visão geral. Ele detalha as atualizações e novidades de várias versões do Zabbix, além de fornecer informações sobre instalação, definições e processos relacionados. A documentação é estruturada em seções que abordam desde a instalação até problemas conhecidos.
Enviado por
yuri kaizer
Título e descrição aprimorados por IA
Direitos autorais
© All Rights Reserved
Levamos muito a sério os direitos de conteúdo. Se você suspeita que este conteúdo é seu,
reivindique-o aqui
.
Formatos disponíveis
Baixe no formato PDF, TXT ou leia on-line no Scribd
Ir para itens anteriores
Baixar
Salvar
Salvar Zabbix Documentation 6.0.Pt para ler mais tarde
Compartilhar
0%
0% acharam este documento útil, Marcar esse documento como útil
0%
0% acharam que esse documento não foi útil, Marcar esse documento como não foi útil
Imprimir
Incorporar
Relatório
Ir para os próximos itens
Baixar
Salvar Zabbix Documentation 6.0.Pt para ler mais tarde
Compartilhar
Mais opções
Tela inteira
Documentation 6.
ZABBIX
21.11.2023
Contents
Manual do Zabbix 5
Copyright notice . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
1. Introdução . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
1 Estrutura do manual . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5
2 O que é o Zabbix . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
3 Funcionalidades do Zabbix . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
4 Visão geral do Zabbix . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
5 O que há de novo no Zabbix 6.0.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
6 O que há de novo no Zabbix 6.0.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
6 O que há de novo no Zabbix 6.0.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
7 What’s new in Zabbix 6.0.2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
8 O que há de novo no Zabbix 6.0.3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
9 What’s new in Zabbix 6.0.4 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
10 O que há de novo no Zabbix 6.0.5 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
11 O que há de novo no Zabbix 6.0.6 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22
12 O que há de novo no Zabbix 6.0.7 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
13 O que há de novo no Zabbix 6.0.8 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
14 O que há de novo no Zabbix 6.0.9 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
15 O que há de novo no Zabbix 6.0.10 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
16 O que há de novo no Zabbix 6.0.11 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
17 O que há de novo no Zabbix 6.0.12 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
18 O que há de novo na Zabbix 6.0.13 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
19 O que há de novo no Zabbix 6.0.14 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
20 O que há de novo no Zabbix 6.0.15 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
21 O que há de novo no Zabbix 6.0.16 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
22 O que há de novo no Zabbix 6.0.17 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
23 What’s new in Zabbix 6.0.18 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
25 What’s new in Zabbix 6.0.20 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
26 What’s new in Zabbix 6.0.21 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29
27 O que há de novo no Zabbix 6.0.22 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29
28 What’s new in Zabbix 6.0.23 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30
29 What’s new in Zabbix 6.0.24 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30
2. Definições . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31
3. Processos Zabbix . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
2 Servidor . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
3 Agent 2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 39
3 Agente . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 42
4 Proxy . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45
5 Java gateway . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 47
6 Sender . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51
7 Get . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52
8 JS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 52
9 Serviço Web . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53
4. Instalação . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53
1 Obtendo o Zabbix . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53
2 Requisitos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 54
3 Instalação a partir do código-fonte . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66
4 Instalação via pacote . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 76
5 Instalação por containers . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 90
6 Instalação da interface web . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 98
1
7 Procedimento de atualização . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 106
8 Problemas conhecidos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 116
10 Notas de atualização para 6.0.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 121
11 Notas de atualização para 6.0.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 123
12 Notas de atualização para 6.0.2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
13 Notas de atualização para 6.0.3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
14 Notas de atualização para 6.0.4 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
15 Notas de atualização para 6.0.5 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
16 Notas de atualização para 6.0.6 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
17 Notas de atualização para 6.0.7 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
18 Notas de atualização para 6.0.8 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
19 Notas de atualização para 6.0.9 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 124
20 Notas atualizadas para 6.0.10 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125
21 Notas atualizações para 6.0.11 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125
22 Upgrade notas para 6.0.12 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125
23 Notas de atualização para 6.0.13 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 125
24 Notas de upgrade para 6.0.14 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126
25 Notas de atualização para 6.0.15 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126
26 Notas de atualização para 6.0.16 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126
27 Notas sobre a atualização para 6.0.17 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126
28 Notas de atualização para 6.0.18 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
29 Upgrade notas para 6.0.19 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
30 Notas de atualização para 6.0.20 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
31 Notas de atualização para 6.0.21 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
32 Notas de atualização para 6.0.22 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
33 Notas de atualização para 6.0.23 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
5. Início rápido . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128
1 Autenticando e configurando usuário . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 128
2 Novo host . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 132
3 Novo item . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 134
4 Novo gatilho (trigger) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 136
5 Recebendo notificação de problema . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 137
6 Novo modelo (template) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
6. Aplicação Zabbix . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 143
7. Configuração . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 146
1 Hosts e grupos de hosts . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 155
2 Itens . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 163
3 Gatilhos (triggers) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 521
4 Eventos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 538
5 Correlação de evento . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 542
6 Marcação . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 549
7 Visualização . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 552
8 Modelos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 582
9 Modelos prontos para uso . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 583
10 Notificações sobre eventos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 589
11 Macros . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 641
12 Usuários e grupos de usuários . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 652
13 Armazenamento de segredos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 660
14 Scheduled reports . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 661
8. Monitoramento de serviço . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 665
1 Árvore de serviços . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 665
2 Ações de serviço . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 669
3 SLA . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 670
4 Exemplo Setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 671
9. Monitoramento web . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 677
1 Itens de monitoramento web . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 686
2 Cenário real de Monitoramento Web . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 688
10. Monitoramento de máquina virtual . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 696
1 Campos de chave de descoberta de máquina virtual . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 701
11. Manutenção . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 706
12. Expressões regulares . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 711
13. Reconhecimento do problema . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 717
14. Configuração exportação/importação . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 719
2
1 Grupos de anfitriões . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 721
2 Templates . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 721
4 Mapas de rede . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 738
5 Tipos de mídia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 744
3 Descoberta de baixo nível . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 759
16 Monitoração distribuída . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 812
Proxies . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 812
17. Criptografia . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 815
1 Usando certificados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 821
2 Usando chaves pré-compartilhadas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 828
3 Solução de problemas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 830
18. Interface da Web . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 833
1 Menu . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 833
2 Seções de front-end . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 834
3 Configurações do usuário . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 993
4 Pesquisa global . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 997
5 Modo de manutenção de front-end . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 999
6 Parâmetros da página . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1000
7 Definições . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1001
8 Criando seu próprio tema . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1002
9 Modo de depuração . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1002
10 Cookies usados pelo Zabbix . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1003
11 Time zones . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1003
13 Redefinindo senha . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1004
19 API . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1005
referência do método . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1009
Apêndice 1. Comentário de referência . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1529
Apêndice 2. Mudanças de 5.4 para 6.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1534
Mudanças na API do Zabbix na versão 6.0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1538
20. Módulos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1540
3 Configuração do processo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1590
4 Protocolos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1682
5 Itens . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1707
6 Supported functions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1733
7 Macros . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1813
8 Símbolos de unidade . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1824
9 Sintaxe do período de tempo . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1825
10 Execução de comandos . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1826
11 Compatibilidade de versões . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1827
14 Tratamento de erros do banco de dados . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1827
14 Upgrade de monitoramento de serviço . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1828
15 Biblioteca de links dinâmicos do remetente Zabbix para Windows . . . . . . . . . . . . . . . . . . . . . . . . . 1828
18 Agente vs agente 2 comparação . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1829
18 Outros problemas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1830
Páginas de manual do Zabbix 1831
zabbix_agent2 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1831
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1831
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1831
Descrição . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1831
OPÇÕES . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1832
ARQUIVOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1832
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1832
AUTOR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1832
Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1832
zabbix_agentd . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1833
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1833
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1833
DESCRIÇÃO . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1833
OPÇÕES . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1833
ARQUIVOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1834
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1834
AUTOR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1834
3
Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1834
zabbix_get . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1834
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1835
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1835
DESCRIÇÃO . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1835
Opções . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1835
EXEMPLOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1836
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1836
Índice . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1836
Índice . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1836
zabbix_js . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1837
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1837
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1837
DESCRIPTION . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1837
OPÇÕES . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1837
EXEMPLOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1837
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1837
Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1838
zabbix_proxy . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1838
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1838
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1838
DESCRIÇÃO . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1838
OPÇÕES . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1838
ARQUIVOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1839
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1839
AUTOR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1839
Índice . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1839
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1840
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1840
DESCRIÇÃO . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1840
OPÇÕES . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1840
STATUS DE SAÍDA . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1842
EXEMPLOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1842
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1843
Autor . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1843
Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1843
zabbix_server . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1844
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1844
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1844
DESCRIÇÃO . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1844
OPÇÕES . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1844
ARQUIVOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1845
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1845
AUTOR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1845
Index . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1845
zabbix_web_service . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
NOME . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
SINOPSE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
DESCRIÇÃO . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
OPÇÕES . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
ARQUIVOS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
VEJA TAMBÉM . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
AUTOR . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
Índice . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 1846
4
Manual do Zabbix
Bem vindo ao Manual do usuário do software Zabbix. Estas páginas são criadas para ajudar os usuários a gerenciar com sucesso
suas tarefas de monitoramento com o Zabbix, das simples às mais complexas.
Copyright notice
Zabbix documentation is NOT distributed under a GPL license. Use of Zabbix documentation is subject to the following terms:
You may create a printed copy of this documentation solely for your own personal use. Conversion to other formats is allowed as
long as the actual content is not altered or edited in any way. You shall not publish or distribute this documentation in any form or on
any media, except if you distribute the documentation in a manner similar to how Zabbix disseminates it (that is, electronically for
download on a Zabbix web site) or on a USB or similar medium, provided however that the documentation is disseminated together
with the software on the same medium. Any other use, such as any dissemination of printed copies or use of this documentation,
in whole or in part, in another publication, requires the prior written consent from an authorized representative of Zabbix. Zabbix
reserves any and all rights to this documentation not expressly granted above.
1. Introdução
Por favor utilize a barra lateral para acessar o conteúdo na seção de Introdução.
1 Estrutura do manual
Estrutura
O conteúdo deste manual é dividido em seções e subseções para fornecer fácil acesso a assuntos de interesse em particular.
Quando você navega até seções específicas, certifique-se de que você expanda as pastas da seção para revelar o conteúdo
completo do que está incluso nas subseções e páginas individuais.
Associação cruzada entre páginas de conteúdo relacionado é fornecida tanto quanto possível de modo a garantir que informações
relevantes não passem despercebidas pelos usuários.
Seções
Introdução fornece informações gerais sobre o software Zabbix atual. A leitura desta seção deve supri-lo com boas razões para
escolher o Zabbix.
Conceitos do Zabbix explica a terminologia usada no Zabbix e provê detalhes sobre os seus componentes.
Instalação e Início rápido devem ajudá-lo a começar com o Zabbix. A seção Zabbix appliance é uma alternativa para ter uma prova
rápida de como é usar o Zabbix.
Configuração é uma das maiores e mais importantes seções neste manual. Ela contém muita recomendação essencial sobre como
configurar o Zabbix para monitorar seu ambiente, desde a configuração de hosts para obtenção de dados essenciais à visualização
de dados, configuração de notificações e comandos remotos a serem executados em caso de problemas.
Serviços de TI detalha como usar o Zabbix para uma visão geral de alto nível do seu ambiente de monitoramento.
Monitoramento web deve ajudá-lo a aprender como monitorar a disponibilidade de sites web.
Monitoramento de máquina virtual apresenta como configurar o monitoramento de ambiente VMware.
Manutenção, Expressões regulares, Reconhecimento de evento e Exportação/Importação XML são seções adicionais que revelam
como usar estes vários aspectos do software Zabbix.
Descoberta contém instruções para configuração de descoberta automática de dispositivos de rede, agentes ativos, sistemas de
arquivo, interfaces de rede, etc.
Monitoramento distribuído lida com as possibilidades de uso do Zabbix em ambientes maiores e mais complexos.
Criptografia ajuda na explicação das possibilidades de criptografia de comunicações entre componentes do Zabbix.
Interface web contém informações específicas para uso da interface web do Zabbix.
API apresenta detalhes de operação com a API do Zabbix.
Listas detalhadas de informações técnicas estão inclusas nos Apêndices. Ali é onde você também encontrará uma seção de FAQ
(perguntas frequentes).
5
2 O que é o Zabbix
Visão geral
O Zabbix foi criado por Alexei Vladishev, e atualmente é, ativamente, desenvolvido e suportado por Zabbix SIA.
O Zabbix é uma solução de nível enterprise, de código aberto e com suporte a monitoração distribuída.
O Zabbix é um software que monitora numerosos parâmetros de rede, a saúde e integridade de servidores, máquinas virtuais,
aplicações, serviços, banco de dados, websites, a nuvem e muito mais. O Zabbix usa um mecanismo flexível de notificação que
permite aos usuários configurar alertas baseados em e-mail para praticamente qualquer evento. Isso permite uma resposta rápida
para problemas do servidor. O Zabbix oferece um excelente recurso de relatórios e visualização de dados baseados em dados
armazenados. Isso torna o Zabbix ideal para gerenciamento de capacidade.
O Zabbix suporta tanto ”pooling” quanto ”trapping”. Todos os relatórios e estatísticas, bem como os parâmetros de configuração
são acessados através de um frontend baseado web. Um frontend baseado na web garante que o status de sua rede e a integridade
de seus servidores podem ser avaliadas a partir de qualquer localização. Devidamente configurado, o Zabbix pode desempenhar
um papel importante no monitoramento da infraestrutura de TI. Isto é igualmente verdadeiro para pequenas organizações com
poucos servidores e para grandes empresas com milhares de servidores.
O Zabbix é gratuito. Zabbix é escrito e distribuído sob a GPL General Public License versão 2. Isso significa que seu código fonte
é distribuído gratuitamente e disponível para o público em geral.
Commercial support está disponível e fornecido pela Zabbix Company e seus parceiros em todo o mundo.
Aprenda mais sobre Zabbix features.
Usuários do Zabbix
Muitas organizações de diferentes tamanhos ao redor do mundo confiam no Zabbix como a plataforma principal de monitoramento.
3 Funcionalidades do Zabbix
Visão geral
O Zabbix é uma solução de monitoramento de rede altamente integrada, oferecendo uma variedade de funcionalidades em um
único pacote.
Coleta de dados
• verificações de disponibilidade e performance
• suporte para monitoramento SNMP (ambos trapping e polling), IPMI, JMX, VMware
• verificações customizadas
• coleta de dados desejados em intervalos customizados
• executado pelo Server/Proxy e pelos agentes
Definições de limite (threshold) flexíveis
• você pode definir limites de problema muito flexíveis, chamados gatilhos, referenciando valores do banco de dados de
backend
Alertas altamente configuráveis
• o envio de notificações pode ser customizado para o planejamento de escalação, destinatário, tipo de mídia
• notificações podem ser tornadas significantes e úteis usando variáveis de macro
• ações automáticas incluem comandos remotos
Gráfico em tempo real
• itens monitorados são imediatamente lançados em gráfico usando a funcionalidade nativa de criação de gráficos
Capacidades de monitoramento web
• O Zabbix pode seguir um caminho de cliques de mouse simulado em um site web e verificar pela funcionalidade e tempo
de resposta
Opções de visualização extensivas
• habilidade de criar gráficos customizados que podem combinar múltiplos itens em uma única visualização
• mapas de rede
6
• apresentação em uma visão estilo dashboard
• relatórios
• visualização de alto nível (negócio) de recursos monitorados
Armazenamento de dados históricos
• dados armazenados em um banco de dados
• histórico configurável
• procedimento de limpeza (housekeeping) nativo
Configuração fácil
• adiciona dispositivos monitorados como hosts
• hosts são selecionados para monitoramento, uma vez que no banco de dados
• aplicar modelos ao dispositivos monitorados
Uso de modelos
• agrupamento de verificações em modelos
• modelos podem herdar outros modelos
Descoberta de rede
• descoberta automática de dispositivos de rede
• autoregistro de agente
• descoberta de sistemas de arquivo, interfaces de rede e OIDs SNMP
Interface web rápida
• um frontend baseado em web com PHP
• acessível de qualquer lugar
• você pode navegar com o mouse
• log de auditoria
API Zabbix
• a API fornece uma interface programável para o Zabbix para manipulações em massa, integração de softwares de terceiros
e outros propósitos.
Sistema de permissões
• autenticação de usuário segura
• certos usuários podem ser limitados a certas visualizações
Agente com funcionalidade completa e facilmente extensível
• implementado nos alvos monitorados
• pode ser implementado em ambos Linux e Windows
Daemons binários
• escritos em C, para performance e pequena pegada de memória
• facilmente portável
Pronto para ambientes complexos
• monitoramento remoto facilitado usando um Zabbix Proxy
4 Visão geral do Zabbix
Arquitetura
O Zabbix consiste de vários componentes de software importantes. Suas responsabilidades estão resumidas abaixo.
Server
O Zabbix server é o componente central para o qual os agentes reportam informações de disponibilidade e integridade e estatís-
ticas. O Server é o repositório central no qual todas as configurações, estatísticas e dados operacionais são armazenados.
Armazenamento banco de dados
Todas as informações de configuração assim como os dados coletados pelo Zabbix são armazenados em um banco de dados.
Interface web
7
Para fácil acesso ao Zabbix de qualquer lugar e de qualquer plataforma, a interface baseada em web é oferecida. A interface
é parte do Zabbix Server, e usualmente (mas não necessariamente) é executada na mesma máquina física na qual está sendo
executado o Server.
Proxy
O Zabbix proxy pode coletar dados de performance e disponibilidade em nome do Zabbix Server. Um proxy é uma parte opcional
da implementação do Zabbix; no entanto, ele pode ser de grande benefício para distribuir a carga de um único Zabbix Server.
Agent
Os Zabbix Agents são implementados nos alvos de monitoramento para monitorar ativamente os recursos locais e aplicações e
disponibilizar os dados coletados para o Zabbix Server. Desde o Zabbix 4.4, há dois tipos de agente disponíveis: o Zabbix Agent
(leve, suportado em muitas plataformas, escrito em C) e o Zabbix Agent2 (extra-flexível, facilmente extensível com plugins, escrito
em Go).
Fluxo de dados
Em adição é importante voltar um passo atrás e dar uma olhada geral no fluxo de dados dentro do Zabbix. De modo a criar um
item que colete dados você deve primeiro criar um host. Indo para o outro lado do espectro do Zabbix você deve primeiro ter um
item para criar um gatilho. Você deve ter um gatilho para criar uma ação. Portanto se você quiser receber um alerta de que sua
carga de CPU está muito alta no Servidor X você deve primeiro criar uma entrada de host para o Servidor X seguido por um item
para monitoramento de sua CPU, e então um gatilho que é ativado se a CPU estiver muito alta, seguida de uma ação que envia
um e-mail para você. Ainda que isto possa parecer um monte de passos, com o uso de modelos realmente não é. No entanto,
devido a este desenho é possível criar uma configuração muito flexível.
5 O que há de novo no Zabbix 6.0.0
Veja breaking changes para esta versão.
Cluster de alta disponibilidade para o servidor Zabbix
A nova versão vem com uma solução nativa de alta disponibilidade para o Servidor Zabbix.
A solução consiste em várias instâncias ou nós do zabbix_server, onde apenas um nó pode estar ativo (funcionando) por vez,
enquanto outros nós estão em standby, prontos para assumir o controle caso o nó atual seja interrompido ou falhe ou falhar.
Veja também: Cluster de alta disponibilidade.
Monitoramento de serviços atualizado
Foram feitas várias atualizações no monitoramento de serviços. O monitoramento de serviços oferece uma visão de alto nível da
infraestrutura monitorada no Zabbix.
**Mapeamento baseado em tags de serviços para problemas
A disponibilidade de services nas versões anteriores do Zabbix dependia de triggers e de seus estados. Na na nova versão, isso
foi substituído por um mapeamento baseado em tags para problemas o respectivo serviço.
Na configuração do serviço, as dependências rígidas e flexíveis não existem mais. Em vez disso, um serviço pode ter vários
serviços principais.
Menu de serviços
Agora há um novo menu Serviços no Zabbix, com quatro seções de menu:
• Services - para visão geral e configuração do serviço (movido de Monitoramento -> Serviços)
• Service actions - para ações de serviço (novo tipo de ação) tipo)
• SLA - para configurar SLAs
• SLA report - para relatórios de SLA (também disponível como widget de painel)
8
Observe que não existe mais uma seção separada para a configuração do serviço (anteriormente em Configuração → Serviços).
**Regras de cálculo e propagação de status
Há novas regras de cálculo de status e regras adicionais flexíveis para calcular o status de um serviço pai com base nos status e
no peso dos filhos diretos. Agora também é possível definir regras flexíveis para propagar o status de um serviço status de serviço
para serviços pai.
Permissões
As permissões flexíveis para serviços foram implementadas em função do usuário nível. O acesso de leitura-escrita ou somente
leitura pode ser concedido a todos, a nenhum ou a serviços selecionados (com base no nome ou nas tags).
**Análise da causa raiz
Uma nova coluna Causa raiz lista os problemas subjacentes que afetam direta ou indiretamente o status do serviço.
Se você clicar no nome do problema, poderá ver mais detalhes sobre ele em Monitoramento → Problemas.
**Alerta sobre mudança de status do serviço
Agora é possível receber alertas automatizados sobre alterações no status do serviço, semelhantes aos alertas sobre alterações
no status do trigger mudanças.
Uma nova funcionalidade service action foi adicionada, semelhante a outras ações no Zabbix. As ações de serviço podem incluir
etapas para operações de problema, recuperação e atualização relacionadas a serviços. É possível é possível configurar dois
tipos de ações: enviar uma mensagem para os destinatários especificados e executar um comando remoto no servidor Zabbix no
servidor Zabbix. Da mesma forma que as ações de acionamento, as ações de serviço suportam problemas escalonamento.
Novos modelos de mensagem Service, Service recovery e Service update foram adicionados a media types e devem ser definidos
para permitir o envio correto de notificações para ações de serviço.
**Clonagem de serviços
Os serviços agora podem ser clonados. O botão Clone foi adicionado ao formulário de configuração de um serviço. Quando um
serviço é clonado, seus links pai são preservados, enquanto os links filho não são.
Chaves primárias
As chaves primárias agora são usadas em todas as tabelas, inclusive nas tabelas de histórico, em novas instalações.
Não há atualização automática para chaves primárias nas instalações existentes. As instruções para uma atualização manual
das tabelas de histórico para chaves primárias em instalações pré-existentes estão disponíveis em MySQL/MariaDB, PostgreSQL,
TimescaleDB v1 e v2, e Oracle.
9
Widgets Vários widgets de painel foram adicionados na nova versão.
Principais hosts
Um widget Top hosts foi adicionado aos widgets do painel. Esse widget foi projetado para substituir o widget Data overview (Visão
geral dos dados) que agora está obsoleto.
O widget Top hosts permite criar tabelas personalizadas para a visão geral dos dados, o que é útil para relatórios do tipo Top N e
relatórios de progresso de barras úteis para o planejamento de capacidade.
Para obter mais informações, consulte Widget Top hosts.
Valor do item
Um widget Item value foi adicionado aos widgets do painel.
Esse tipo de widget é útil para exibir valores de itens individuais com destaque. São possíveis diferentes estilos visuais de exibição
possíveis:
Para obter mais informações, consulte Item value widget.
Macros Novas macros
Agora há suporte para novas macros para depuração de expressões de acionamento e ações internas.
As macros de depuração de expressões simplificam o processo de depuração de expressões de acionamento:
• {[Link]}, {[Link]} - resolvem para uma expressão de aciona-
mento ou recuperação parcialmente parcialmente avaliada ou expressão de recuperação, em que somente as funções são
aplicadas;
• {[Link]<1-9>}, {[Link]<1-9>} - resolvem para os resultados da enésima função baseada
em item no momento do do evento.
As macros para ações internas contêm o motivo pelo qual um item, uma regra LLD ou um trigger deixou de ser suportado:
• {[Link]} - para notificações internas baseadas em itens;
• {[Link]} - para notificações internas baseadas em regras LLD;
• {[Link]} - para notificações internas baseadas em triggeres.
10
Para obter mais detalhes, consulte Macros Suportadas.
Macros simples substituídas por macros de expressão
Uma nova sintaxe de expressão para triggers e itens calculados foi introduzida em [Zabbix 5.4] ([Link]
No entanto, a sintaxe antiga ainda permaneceu em uso nas macros simples. Na nova versão, a funcionalidade das macros simples
foi transferida para as macros de expressão e a nova sintaxe de expressão é usada. Consulte a comparação abaixo para obter
detalhes sobre a alteração:
No Zabbix 6.0 Antes do Zabbix 6.0
{?avg(/host/key,1h)} {host:[Link](1h)}
Exemplo de uma macro de expressão na nova Exemplo de uma macro simples nas versões anteriores.
versão.
As macros simples existentes serão convertidas em macros de expressão durante a atualização. O escopo das macros de expressão
abrange o mesmo que era oferecido pelas macros simples. Portanto, as macros de expressão podem ser usadas em:
• notificações e comandos de problemas
• notificações e comandos de atualização de problemas
• rótulos de elementos do mapa
• rótulos de links de mapas
• rótulos de formas de mapas
• nomes de gráficos
Macros posicionais não são mais suportadas
O suporte a macros posicionais no nome do item ($1, $2...$9), obsoleto desde o Zabbix 4.0, foi totalmente removido.
Não há mais suporte para macros de usuário no nome do item
O suporte a macros de usuário em nomes de itens (incluindo nomes de regras de descoberta), obsoleto desde o Zabbix 4.0, foi
totalmente removido.
Processamento em massa para métricas do Prometheus
O processamento em massa de itens dependentes foi introduzido na fila de pré-processamento para melhorar o desempenho da
recuperação de métricas do Prometheus.
Consulte Prometheus checks para obter mais detalhes.
Processamento de resultados para o padrão Prometheus
Uma etapa de padrão do Prometheus no pré-processamento pode produzir um resultado em que várias linhas são correspondidas.
Para lidar com essa situação, um novo parâmetro no processamento de resultados foi adicionado à etapa de pré-processamento
do padrão Prometheus que permite agregar os dados de várias linhas correspondentes, introduzindo funções como soma, mínimo,
máximo, média e contagem.
Funções Funções para histogramas do Prometheus
Há algum tempo é possível coletar métricas do Prometheus no Zabbix mas é difícil trabalhar com algumas das métricas. Especifi-
camente, as métricas do tipo histograma podem ser apresentadas no Zabbix como vários itens com os mesmos nomes de chave,
mas com parâmetros diferentes. No entanto, mesmo que esses itens estejam logicamente relacionados e representem os mes-
mos dados, tem sido difícil analisar os dados coletados sem funções especializadas. Para cobrir essa lacuna de funcionalidade na
nova versão, as funções rate() e histogram_quantile() que produzem o mesmo resultado que suas contrapartes PromQL, foram
adicionadas.
Outras novas adições para complementar essa funcionalidade são as funções bucket_rate_foreach() e as funções bucket_percentile().
Para obter mais informações, consulte:
• Funções de histórico (consulte rate())
• Funções de agregação (consulte histograma_quantile(), bucket_percentile())
• Funções Foreach (consulte bucket_rate_foreach())
Mudança monotônica
Agora é possível verificar se há aumento ou diminuição monotônica nos valores dos itens usando as novas monoinc() ou mon-
odec() funções de histórico.
Contagem de alterações
11
Uma nova função de histórico changecount() foi adicionada, permitindo contar o número de alterações entre valores adjacentes.
A função suporta três modos diferentes para contar todas as alterações, somente diminuições ou somente aumentos. Por exemplo,
ela pode ser usada para rastrear alterações no número de usuários ou no número de diminuições no tempo de atividade do sistema.
Contagem de entidades
Novas funções foram adicionadas para simplificar a contagem de hosts, itens ou valores valores específicos, retornados por funções
foreach.
Funções de agregação:
• count - número total de valores em uma matriz retornada por uma função foreach (retorna um número inteiro);
• item_count - número total de itens atualmente habilitados que correspondem aos critérios de filtro (retorna um número
inteiro).
Função foreach:
• exists_foreach - número de itens ativados no momento que correspondem aos critérios de filtro (retorna uma matriz).
Detecção de anomalias
O Zabbix 5.2 introduziu novas funções de tendência úteis para o monitoramento da linha de base. No entanto, elas ainda exigem
a definição de limites (por exemplo, verificar se o tráfego da Web em setembro de 2021 é menos e 2x maior em comparação com
setembro de 2020). Existem casos de uso em que esses limites são difíceis de definir. Por exemplo, o tráfego da Web de um site
novo, mas altamente popular pode crescer organicamente muitas vezes em um ano, mas a taxa de crescimento é desconhecida.
No entanto, um pico repentino de tráfego devido a um ataque DDOS deve gerar um alerta independentemente do crescimento
orgânico do tráfego.
Os algoritmos de detecção de anomalias fazem exatamente isso: encontram dados que não parecem normais (outliers) em um
contexto de outros valores.
Foi adicionada uma nova função de tendência trendstl() que usa o método de ”decomposição para calcular a taxa de anomalia.
Ela divide uma única sequência de série temporal em três outras sequências:
• sequência de tendências que contém apenas grandes alterações nos dados originais (por exemplo, o tráfego do site mostra
crescimento)
• sequência de estação que contém apenas alterações sazonais (por exemplo, menos tráfego no site no verão e mais no
outono)
• sequência restante, que contém apenas valores residuais que não podem ser interpretados como partes da tendência ou
da estação
A detecção de anomalias funciona com a sequência restante e verifica se há valores que estão muito distantes da maioria dos
valores restantes. ”Longe” significa que o valor absoluto da sequência restante é N vezes maior do que o desvio padrão ou médio
ou desvio médio.
Funções String
String function concat agora permite concatenar mais de dois parâmetros. Essa função pode ser usada para combinar cadeias de
caracteres e valores em diferentes combinações ou anexar dois ou mais valores uns aos outros. Os tipos de dados também são
compatíveis.
12
Itens Seleção automatizada de tipos
O formulário de configuração do item agora sugere automaticamente o tipo de informação correspondente, se a chave do item
selecionado retornar dados apenas do tipo específico (por exemplo, o item log[] requer Type of information: Log). O parâmetro
Type of information agora está localizado sob o parâmetro Key na guia Item principal e é duplicado na guia na guia Preprocessing
se pelo menos uma etapa de pré-processamento for especificada. Se o Zabbix detectar uma possível incompatibilidade entre o
tipo de informação e chave selecionados, um ícone de aviso será exibido ao lado do campo Tipo de informação.
Itens do agente
Vários novos itens foram adicionados ao agente/agente 2 do Zabbix:
• [Link] - retorna metadados do host
• [Link] - retorna o número de descritores de arquivos abertos
• [Link][] - retorna o número de soquetes TCP que correspondem aos parâmetros
• [Link][] - retorna o número de soquetes UDP que correspondem aos parâmetros
• [Link][] - retorna a lista de arquivos de diretório como JSON
• [Link][] - retorna informações sobre um arquivo como JSON
• [Link][] - retorna a propriedade de um arquivo
• [Link][] - retorna uma cadeia de 4 dígitos contendo número octal com permissões Unix
Além disso:
• [Link][] agora suporta um segundo parâmetro mode (crc32, md5, sha256)
• [Link][] agora oferece suporte a um segundo parâmetro mode (bytes ou lines)
• [Link] e [Link] agora retornam uma macro {#FSLABEL} no Windows (com nomes de volumes)
Para obter mais detalhes, consulte agent items.
Itens calculados
Os itens calculados agora suportam não apenas informações numéricas, mas também dos tipos texto, log e caracteres.
Recarregamento de parâmetros do usuário sem reinicialização do agente
Os parâmetros do usuário agora podem ser recarregados do arquivo de configuração sem reiniciar o agente. Para fazer isso,
execute a nova opção de controle de tempo de execução userparameter_reload opção de controle de tempo de execução, por
exemplo:
zabbix_agentd -R userparameter_reload
ou
zabbix_agent2 -R userparameter_reload
UserParameter é a única opção de configuração do agente que será recarregada com esse comando.
Controles de tempo de execução em sistemas operacionais baseados em BSD
Anteriormente, as opções de controle de tempo de execução do Zabbix Server e do Zabbix Proxy não eram suportadas em sistemas
baseados em BSD. A alteração do método de método de transferência de comandos em tempo de execução permitiu eliminar essa
limitação. Agora, a maioria dos comandos é compatível com em FreeBSD, NetBSD, OpenBSD e outros sistemas operacionais da
família *BSD.
Para obter a lista exata, consulte Controle de tempo de execução para Zabbix server ou proxy.
Plug-ins do Zabbix Agent 2
**Carregador de plug-in externo
Anteriormente, os plug-ins só podiam ser compilados no Zabbix Agent 2, o que exigia a recompilação do agente toda vez que
você precisasse alterar o conjunto de plug-ins disponíveis. Agora, com a adição do carregador de plug-ins externo, os plug-ins
não precisam ser integrados diretamente ao agente 2 e podem ser adicionados como complementos externos separados (plug-ins
carregáveis), facilitando assim o processo de criação de plug-ins adicionais para coletar novas métricas de monitoramento.
A introdução de plug-ins carregáveis causou as seguintes alterações nos parâmetros de configuração:
• o parâmetro Plugins.<PluginName>.Path foi movido para Plugins.<PluginName>.[Link].
• o parâmetro Plugins.<PluginName>.Capacity, embora ainda suportado, foi descontinuado; use Plugins.<PluginName>.[Link]
Requisitos de senha
Os requisitos personalizados de complexidade de senha agora podem ser fornecidos para o Zabbix interno (/manual/web_interface/frontend_se
Para evitar que os usuários do Zabbix definam senhas fracas, é possível impor as seguintes restrições:
• Definir o comprimento mínimo da senha.
13
• Exigir que a senha contenha uma combinação de letras maiúsculas e letras maiúsculas e minúsculas, dígitos e/ou caracteres
especiais.
• Proibir o uso das senhas mais comuns e fáceis de adivinhar.
Bancos de dados Para criar a melhor experiência para o usuário e garantir o melhor desempenho do Zabbix em vários ambientes
de produção, o suporte a algumas versões mais antigas de bancos de dados foi abandonado. Isso se aplica principalmente às
versões de banco de dados que estão chegando ao fim de sua vida útil e versões com problemas não corrigidos que podem
interferir no desempenho normal.
A partir do Zabbix 6.0, as seguintes versões de banco de dados são oficialmente suportadas:
• MySQL/Percona 8.0.X
• MariaDB 10.5.X - 10.6.X
• PostgreSQL 13.X - 14.X
• Oracle 19c - 21c
• TimescaleDB 2.0.1-2.3
• SQLite 3.3.5-3.34.X
Por padrão, o Zabbix Server e o proxy não serão iniciados se uma versão de banco de dados não suportada for detectada. Agora
é possível, embora não seja recomendado, agora é possível desativar a verificação da versão do banco de dados modificando o
parâmetro de configuração AllowUnsupportedDBVersions do o server ou proxy.
suporte utf8mb4 para MySQL
a codificação utf8mb4 com agrupamento utf8mb4_bin agora é suportada para instalações do Zabbix com o banco de dados
MySQL/MariaDB.
Anteriormente, apenas a codificação utf8 era suportada, o que no MySQL significa codificação utf8mb3 e, portanto, suporta apenas
um subconjunto de caracteres UTF-8 adequados. Na nova versão, o suporte a utf8mb4 foi adicionado com suporte para full
Conjunto de caracteres UTF-8. As instalações antigas que usam utf8mb3 são mantidas intactas e podem continuar usando essa
codificação.
Consulte também as instruções sobre a execução da conversão utf8mb4 após a atualização para a versão 6.0.
Processos Tempo limite do Zabbix get e do Zabbix sender
Os utilitários Zabbix get e Zabbix sender agora suportam um parâmetro -t <seconds> ou --timeout <seconds> de tempo
limite. O intervalo válido é:
• 1-30 segundos para o Zabbix get (padrão: 30 segundos)
• 1-300 segundos para o Zabbix sender (padrão: 60 segundos)
Funcionalidade estendida do gateway SNMP
O gateway SNMP agora pode fornecer informações sobre triggeres em um estado problemático e revelar informações sobre o host
nos detalhes do trigger
Além disso, agora é possível limitar a taxa de traps de SNMP enviados pelo gateway de SNMP.
A lista de OIDs suportados foi ampliada com um novo OID .10 para uma lista delimitada por vírgulas de nomes de host de triggeres.
Novos parâmetros foram adicionados ao arquivo de configuração do gateway SNMP:
• ProblemBaseOID - OID da tabela de triggeres de problemas;
• ProblemMinSeverity - gravidade mínima, os triggeres com gravidade inferior não serão incluídos;
• ProblemHideAck - se especificado, somente os triggeres com problemas não reconhecidos serão incluídos;
• ProblemTagFilter - se especificado, somente os triggeres com o nome de tag especificado serão incluídos;
• TrapTimer - se definido, o Zabbix não enviará mais do que um trap de maior severidade em um determinado período de
tempo.
Para obter detalhes, consulte [Zabbix SNMP Gateway] ([Link]
Conteúdo compactado no monitoramento da Web
A capacidade de lidar com conteúdo compactado foi adicionada ao Zabbix Web do Zabbix. Todos os formatos de codificação
suportados por libcurl são suportados.
Pré-processamento Linguagem de consulta do Prometheus
O pré-processamento do Zabbix Prometheus query language agora suporta dois operadores adicionais de correspondência de
rótulos:
• != -- seleciona rótulos que não são iguais à string fornecida;
14
• !~ -- seleciona rótulos que não correspondem à cadeia de caracteres fornecida string fornecida.
Métodos JavaScript
Os métodos HTTP PATCH, HEAD, OPTIONS, TRACE e CONNECT foram adicionados ao mecanismo JavaScript. Além disso, o mecan-
ismo agora permite enviar solicitações de métodos HTTP personalizados com o novo método JS [Link].
Veja também: Objetos JavaScript adicionais.
Registro de auditoria
**Registros
O log de auditoria agora contém registros sobre todas as alterações de configuração para todos os objetos do Zabbix, incluindo
alterações que ocorreram como resultado da execução de uma regra LLD, uma ação de descoberta de rede, uma ação de au-
torregistro ou uma execução de script. Anteriormente, as alterações de configuração iniciadas a partir do Zabbix Server, por
exemplo, como resultado da execução de uma regra de descoberta, não eram registradas. Agora, essas modificações de objeto
serão armazenadas como registros de auditoria atribuídos ao usuário System.
**Filtro de registro
Foi adicionada uma funcionalidade para filtrar registros pela operação de front-end que causou essas entradas. Se vários registros
de log tiverem sido criados como resultado de uma única operação, por exemplo, vincular/desvincular um modelo, esses registros
terão o mesmo Recordset ID.
**Configurações de auditoria
Novo seção Audit log foi adicionada ao menu Administration→General, permitindo ativar ou desativar o registro de auditoria. As
configurações de manutenção para auditoria, anteriormente localizadas na seção Housekeeper, também foram movidas para a
nova seção Log de auditoria.
Suporte ao PCRE2
O suporte ao PCRE2 foi adicionado e os pacotes de instalação do Zabbix para RHEL 7 e mais recentes, SLES (todas as versões),
Debian 9 e mais recentes, Ubuntu 16.04 e mais recentes foram atualizados para usar o PCRE2. O PCRE ainda é suportado, mas
o Zabbix só pode ser compilado com uma das bibliotecas PCRE ou PCRE2, ambas não podem ser usadas ao mesmo tempo ao
mesmo tempo.
Processamento separado para verificações de ODBC
O processamento de verificações de ODBC foi transferido dos processos regulares de sondagem para processos separados de servi-
dor/proxy sondadores de ODBC. Essa alteração permite limitar o número de conexões ao banco de dados criadas pelos processos
de sondagem. Anteriormente, as verificações de ODBC eram executadas por pollers regulares, que também trabalham com itens
do agente Zabbix, verificações SSH etc.
Um novo parâmetro de configuração StartODBCPollers foi adicionado ao Zabbix nos arquivos de configuração do Zabbix server e
proxy.
Você pode usar o item interno zabbix[process,<type>] para monitorar a carga dos pollers ODBC.
Integrações de webhooks
Está disponível uma nova integração que permite usar o tipo de mídia webhook para criar Github issues das notificações do Zabbix
.
Modelos (Templates) Novos modelos oficiais estão disponíveis para monitoramento.
Kubernetes
• *Nós do Kubernetes por HTTP
• *Estado do cluster do Kubernetes por HTTP
• *Servidor de API do Kubernetes por HTTP
• *Gerenciador de controle do Kubernetes por HTTP
• *Agendador do Kubernetes por HTTP
• *Kubelet do Kubernetes por HTTP
Para ativar o monitoramento do Kubernetes, você precisa usar a nova ferramenta Zabbix Helm Chart, que instala o proxy Zabbix
e os agentes Zabbix no cluster do Kubernetes.
Para saber mais sobre a configuração de modelos, consulte HTTP template operation.
Mikrotik
• MikroTik <device model> SNMP - 53 novos modelos específicos para monitorar vários modelos de roteadores e switches
MikroTik roteadores e switches ethernet, consulte [lista completa] ([Link]
15
• Mikrotik SNMP - um modelo genérico para monitorar dispositivos MikroTik.
Você pode obter esses modelos:
• Em Configuration → Templates em novas instalações;
• Ao atualizar a partir de versões anteriores, os modelos mais recentes podem ser baixados do [Zabbix Git repository]
([Link] e importados manualmente para o Zabbix na seção
Configuration → Templates. Se já existir um modelo com o mesmo nome , verifique a opção Delete missing antes de im-
portar para obter uma importação limpa. Dessa forma, os itens que foram excluídos do modelo atualizado serão removidos
(observe que o histórico dos itens excluídos será perdido)
Notificações Links de modelos mais visíveis
Para tornar a vinculação de modelos mais visível, agora ela é colocada na primeira guia dos formulários de configuração de host,
protótipo de host e modelo e nos formulários de atualização em massa de host/template.
Consequentemente, uma guia separada para vinculação de modelos foi removida de todos os respectivos formulários.
Em um desenvolvimento relacionado, na configuração do protótipo de host, os campos para a seleção do protótipo do grupo de
host/grupo de host também foram movidos de uma guia separada para uma guia separada também foram movidos de uma guia
separada para a primeira guia.
Transferência de comandos em tempo de execução
Os comandos de tempo de execução do Zabbix Server e do proxy agora são enviados via socket em vez de sinais Unix. Essa
alteração permitiu melhorar a experiência do usuário ao trabalhar com opções de controle de tempo de execução:
• Os resultados da execução do comando agora são impressos no console.
• É possível enviar parâmetros de entrada mais longos, como o nome do nó HA em vez do número do nó.
Front-end Geomap
Um novo widget de mapa geográfico para os painéis foi introduzido, oferecendo uma maneira de exibir hosts em mapas geográficos.
Para obter mais informações, consulte o Geomap dashboard widget e mapas geográficos.
16
Subfiltro nos dados mais recentes
Um subfiltro foi adicionado à seção Latest data. O subfiltro é útil para o acesso rápido, com um clique, a grupos de itens relaciona-
dos.
O subfiltro mostra links clicáveis que permitem filtrar itens com base em uma entidade comum: o host, o nome da tag ou o valor
da tag. Assim que a entidade é clicada, os itens são imediatamente filtrados.
Para obter mais detalhes, consulte a seção latest data.
Melhorias na usabilidade de gráficos personalizados
A página de gráficos em Monitoring → Hosts → Graphs recebeu vários aprimoramentos de usabilidade:
• Não há mais um limite de 20 gráficos na página
• Foi adicionado um subfiltro que permite selecionar rapidamente grupos de gráficos relacionados com base em uma tag ou
valor de tag comum
• Gráficos simples para o host podem ser exibidos juntamente com gráficos personalizados
Para obter mais detalhes, consulte a página graph.
Criação de hosts a partir do monitoramento
Agora também é possível criar novos hosts a partir de Monitoramento → Hosts.
O botão Create host está disponível para usuários Admin e Super Admin.
Edição de host como pop-up
O formulário para criação e edição de host agora é aberto em uma janela modal (pop-up) em Configuration → Hosts, Monitoring →
Hosts e em qualquer página, onde houver um menu de host ou outro link direto para a configuração do host configuração.
Os links diretos para a página de edição do host ainda funcionam e estão abrindo a página de edição do host em página inteira
página de edição do host em página inteira.
Melhor navegação entre a configuração do item e os dados mais recentes
17
Um novo menu de contexto para itens foi introduzido em Latest data, permitindo acessar a configuração do item e os gráficos
disponíveis configuração do item e os gráficos disponíveis:
Por outro lado, um novo menu de contexto foi introduzido na seção lista de itens no menu de configuração que permite acessar
os dados mais recentes do item e outras opções úteis:
Esse menu substitui a opção do assistente nas versões anteriores. Um menu semelhante foi também foi introduzido para itens de
modelo e item prototypes.
Notificação sobre escalonamentos cancelados
Ao configurar [operações de ação] (/manual/config/notifications/action/operation#configuring-an-operation), agora é possível pos-
sível cancelar as notificações sobre escalonamentos cancelados desmarcando a caixa de seleção da opção correspondente.
Monitoring → Dados mais recentes atualizados
Foram feitos vários aprimoramentos na seção Dados mais recentes:
• O tempo desde a última verificação (por exemplo, 1m 20s) agora é exibido em vez do tempo de execução do último item.
• Passar o mouse sobre o último valor de um item mostrará o valor bruto sem unidades ou mapeamento de valor aplicado.
• Se um host estiver em manutenção, um ícone de chave inglesa laranja ficará visível ao lado do nome do host.
Monitoramento → Visão geral removida
A seção Visão geral no menu Monitoramento foi completamente removida. A mesma funcionalidade ainda pode ser acessada
usando os painéis Data overview e Trigger overview dashboard widgets.
Diversos
• O tamanho máximo do campo foi aumentado para os seguintes campos:
– Item preprocessing parameters
18
– Tipo de mídia mensagem
• O idioma padrão da interface web do Zabbix foi alterado de Inglês britânico para inglês americano. O suporte ao inglês
britânico foi abandonado.
• O link Share no menu principal foi substituído por um link Integrations que leva à página Integrações no site da Site do
Zabbix.
• Se a interface web do Zabbix for aberta em um dos idiomas disponíveis no site do Zabbix, ao clicar no link Integrations, o
usuário poderá acessar a página Integrations no site do Zabbix disponíveis no site do Zabbix, ao clicar no link Integrations,
será aberta a página Integrations no idioma apropriado. Para todos os outros idiomas, incluindo o inglês, a página de
Integrações será aberta em inglês.
• Uma expressão personalizada, usada em action configuration para calcular as condições, agora pode ter até 1024 caracteres
(antes era 255).
• A seção Monitoramento->Hosts agora mostra o link para a tela de problemas do host, mesmo que nenhum problema esteja
aberto no momento.
Mudanças significativas Registro de auditoria
Para implementar as alterações na [funcionalidade de registro de auditoria] (#audit-log), a estrutura de banco de dados existente
anteriormente teve de ser reformulada. Durante a atualização, as tabelas de banco de dados auditlog e auditlog_details
serão substituídas pela nova tabela auditlog com um formato diferente. **Os registros de log de auditoria existentes serão
excluídos
Verificação de versões de BD compatíveis
Zabbix server e proxy agora verificarão a versão do banco de dados versão do banco de dados antes da inicialização e não iniciarão
se a versão estiver fora do intervalo suportado estiver fora do intervalo suportado. Para obter mais detalhes, consulte databases.
Suporte ao PCRE2
O Zabix agora suporta PCRE e PCRE2. Os pacotes Zabbix para RHEL 7 e mais recentes, SLES (todas as versões), Debian 9 e
mais recentes, Ubuntu 16.04 e mais recentes foram atualizados para compilar com PCRE2 em vez de PCRE. Ao compilar a partir
de fontes, os usuários podem optar por especificar o sinalizador ”--with-libpcre” ou ”--with-libpcre2”. Se estiver atualizando uma
instalação existente, a alteração do PCRE para PCRE2 pode fazer com que algumas expressões regulares se comportem de forma
diferente - consulte Problemas conhecidos para obter detalhes.
**Arquivos de configuração separados
Cada plug-in do Zabbix Agent 2 agora tem um arquivo de configuração separado (/manual/appendix/config/zabbix_agent2_plugins).
Por padrão, esses arquivos estão localizados no diretório ./zabbix_agent2.d/plugins.d/. O caminho é especificado no
parâmetro Include do arquivo de configuração do agente 2 e pode ser relativo ao diretório zabbix_agent2.conf ou zab-
bix_agent2.[Link].
Monitoramento da linha de base
O conjunto de opções de monitoramento de linha de base disponíveis foi ampliado com as duas novas funções baselinedev e
baselinewma.
• Baselinedev - compara o último período de dados com os mesmos períodos de dados nas estações anteriores e retorna o
número de desvios;
• baselinewma - calcula a linha de base calculando a média dos dados do mesmo período de tempo em vários períodos de
tempo iguais (”temporadas”) usando o algoritmo de média móvel ponderada.
No contexto dessas funções, o termo ”estação” refere-se a um período de tempo configurável, que pode ser de horas, dias,
semanas, meses ou anos, meses ou anos. A duração de uma temporada e o número de temporadas a serem analisadas são
definidos nos parâmetros da função.
Consulte history functions para obter mais informações.
6 O que há de novo no Zabbix 6.0.1
Agente Zabbix 2 itens
• Suporte nativo para os items [Link] e [Link] foi adicionado. Esses itens, usados com o agente Zabbix 2, agora
suportam o processamento de cheques simultâneos. No Windows, endereços IP DNS personalizados são permitidos no
parâmetro ip, os parâmetros timeout e count não são mais ignorados.
• [Link] e [Link] items/manual/config/items/itemtypes/zabbix_agent/zabbix_agent2#s.m.a.r.t.),
compatível com S.M.A.R.T. plugin, foram atualizados e agora retornam o valor da macro {#DISKTYPE} em letras minúsculas.
19
Discovery of disabled systemd units It is now also possible to discover disabled systemd units using the [Link]
item key, supported by Zabbix agent 2. Note that to have items and triggers created from prototypes for disabled systemd units, it
may be necessary to adjust (or remove) prohibiting LLD filters for the {#[Link]} and {#[Link]} macros.
For more details, see Discovery of systemd services.
SNI support in encrypted connections
Encrypted TCP connections between Zabbix agent and Zabbix server or proxy now support SNI.
SourceIP support in LDAP simple checks SourceIP support has been added to LDAP simple checks. Note that with OpenLDAP,
version 2.6.1 or above is required.
6 O que há de novo no Zabbix 6.0.1
Aggregate functions The count_foreach function now returns ’0’ for a matching item in the array, if no data are present for
the item or the data do not match the filter. Previously such items would be ignored (no data added to the aggregation).
TimescaleDB 2.11 support Support for TimescaleDB version 2.11 is now available.
Configurable TLS and connection parameters in MQTT plugin The MQTT plugin for Zabbix agent 2 now provides additional
configuration options, which can be defined in the plugin configuration file as named session or default parameters:
• Connection-related parameters: broker URL, topic, username, and password;
• TLS encryption parameters: location of the top-level CA(s) certificate, MQTT certificate or certificate chain, private key.
All of the new parameters are optional.
JavaScript preprocessing The heap limit for scripts has been upped from 64 to 512 megabytes.
Supported platforms Support for Debian 12 (Bookworm) has been added, and official packages are available for download on
Zabbix website.
7 What’s new in Zabbix 6.0.2
Zabbix agent 2 active check configuration
A new optional configuration parameter ForceActiveChecksOnStart has been added to Zabbix agent 2. Setting the parameter
to ForceActiveChecksOnStart=1 will ensure item data for active checks is collected immediately upon Zabbix agent restart,
except for items with Scheduling update interval. Otherwise, the first data collection after an agent restart will happen at random
time, which is less than item update interval, to prevent spikes in resource usage.
It is also possible to set this option only for a specific plugin by using Plugins.<PluginName>.[Link]
(for example, [Link]=1). If set, a plugin-level parameter will override the
global setting.
JMX monitoring The template Generic Java JMX now contains discovery rules for low-level discovery of memory pools and
garbage collectors.
Keyboard navigation Keyboard control has been implemented for info icons in the frontend. Thus it is now possible to focus on
info icons, and open the hints, using the keyboard.
8 O que há de novo no Zabbix 6.0.3
Métricas PostgreSQL
Um novo item foi adicionado ao plugin do PostgreSQL para o agente Zabbix 2. A métrica [Link] é utilizada para monitorar
o tempo de execução das consultas.
20
Templates
Um novo template OpenWeatherMap by HTTP agora está disponível, permitindo monitorar o OpenWeatherMap via HTTP. Ver HTTP
template operation para configurações.
As mudanças abaixo foram feitas nos templates existentes:
• Nos templates Windows services pelo Zabbix agent, Windows services pelo Zabbix agent active, Windows pelo Zabbix agent,
Windows pelo Zabbix agent active {$[Link].NOT_MATCHES} o valor da macro foi atualizado para filtrar uma lista
de serviços.
• O template PostgreSQL by Zabbix agent 2 agora verificará o número de consultas lentas e irá gerar um problema se a
quantidade exceder um limite estabelecido.
Você pode obter esses templates:
• Em Configuration → Templates em novas instalações;
• Se você estiver atualizado a partir de versões anteriores, você pode baixar os novos templates pelo Zabbix Git repository
ou encontrá-los no diretório zabbix/templates da versão mais recente do Zabbix. Em seguida, enquanto estiver em Config-
uration → Templates você pode importá-los manualmente no Zabbix.
9 What’s new in Zabbix 6.0.4
Text data for Top hosts widget It is now possible to select items with any type of information (including Character, Text, and
Log) in the Top hosts widget. For example, it is now possible to use this widget to display the versions of Zabbix agents running
on each host.
OpenSSL 3.0 support OpenSSL 3.0.x is now supported. Note that this change does not affect frontend encryption (which uses its
own openssl-php package) and Java gateway JMX encrypted connections to monitoring targets (which uses its own Java encrypted
libraries).
Templates New templates are available: - TrueNAS SNMP - monitoring of TrueNAS storage OS by SNMP - Proxmox VE by HTTP -
see setup instructions for HTTP templates
You can get these templates:
• In Configuration → Templates in new installations;
• If you are upgrading from previous versions, you can download new templates from Zabbix Git repository or find them in
the templates directory of the downloaded latest Zabbix version. Then, while in Configuration → Templates you can import
them manually into Zabbix.
GLPi integration A new GLPi integration is available allowing to use the webhook media type to create problems in GLPi Assis-
tance section based on Zabbix problem notifications.
S.M.A.R.T. monitoring Smart plugin, supported for Zabbix agent 2, now provides more efficient disk discovery and allows
returning information about a specific disk, instead of all discovered disks. Zabbix agent 2 items [Link] and
[Link] have been updated. The templates SMART by Zabbix agent 2 and SMART by Zabbix agent 2 (active) have also
been modified to incorporate the new functionality.
10 O que há de novo no Zabbix 6.0.5
Templates New templates are available:
• CockroachDB by HTTP
• Envoy Proxy by HTTP
See setup instructions for HTTP templates.
You can get these templates:
• In Configuration → Templates in new installations;
21
• If you are upgrading from previous versions, you can download new templates from Zabbix Git repository or find them in
the templates directory of the downloaded latest Zabbix version. Then, while in Configuration → Templates you can import
them manually into Zabbix.
Handling of NaN values in Prometheus preprocessing There is a new behavior for handling (skipping) NaN values. So, if a
dataset consists of valid numeric values and NaNs, then NaN values are skipped and:
• ’avg’, ’max’, ’min’, ’sum’ return a result that is calculated from the valid values
• ’count’ returns the number of valid values
If all values in a dataset are NaNs then ’avg’, ’max’, ’min’, and ’sum’ return a ”no data (at least one value is required)” error, while
’count’ returns 0.
Previously, if NaN was the first value in a dataset then:
• ’avg’, ’max’, ’min’, ’sum’ returned a ”Value ”NAN” of type ”string” is not suitable for
value type ”Numeric (float)”” error
• ’count’ returned the number of values (including NaN values)
Also previously, if NaN was not the first value in a dataset then:
• ’avg’, ’sum’ returned a ”Value ”NAN” of type ”string” is not suitable for
value type ”Numeric (float)”” error
• ’max’ returned the maximum of values until the first NaN was encountered
• ’min’ returned the minimum of values until the first NaN was encountered
• ’count’ returned the number of values (including NaN values)
Latest data link for hosts shows numbers The latest data link for hosts in Monitoring -> Hosts now shows the number of
items with latest data.
Frontend languages German and Vietnamese languages are now enabled in the frontend.
Expandable lists in latest data subfilter Expandable lists have been introduced in the latest data subfilter:
• For each entity group (e.g. tags, hosts) 10 rows of entities are now displayed. If there are more entities, a three-dot icon
is displayed at the end; if you click on it the list will be expanded to a maximum of 1000 entries (the value of SUBFIL-
TER_VALUES_PER_GROUP in frontend definitions). Previously a non-expandable maximum of 100 entries was the limit.
• In the list of Tag values 10 rows of tag names are now displayed. If there are more tag names with values, a three-dot
icon is displayed at the bottom; if you click on it the list will be expanded to a maximum of 200 tag names. Previously, a
non-expandable maximum of 20 rows with tag names was the limit.
For each tag name 10 rows of values are displayed (expandable to 1000 entries (the value of SUBFILTER_VALUES_PER_GROUP in
frontend definitions))
Audit log filter Multiple actions now can be selected in the audit log filter in Reports -> Audit:
This is useful to see all related actions (for example, successful and failed logins into the frontend) in the audit list.
11 O que há de novo no Zabbix 6.0.6
22
Suporte PHP 8 Agora, PHP 8.0 e 8.1 são suportados.
Suporte MariaDB 10.7 Agora, a maior versão suportada para Maria DB é 10.7.X.
Plugin carregável MongoDB O MongoDB plugin não faz mais parte do Zabbix agent 2 e agora está disponível como um plugin
carregável. A lista de versões suportadas do MongoDB foram estendidas para 2.6-5.3.
A funcionalidade e o conjunto de itens items suportados não foram alterados.
Templates Novos templates
Novos templates estão disponíveis:
• HPE MSA 2040 armazenado por HTTP
• HPE MSA 2060 armazenado por HTTP
• HPE Primera por HTTP
Veja as instruções de configuração para HTTP templates.
Você pode acessar esses templates:
• Em Configuration → Templates em novas instalações;
• Se você estiver atualizando a partir de versões anteriores, você consegue baixar os novos templates do Zabbix em Git
repository ou encontrá-los no diretório zabbix/templates da versão mais recente baixada do Zabbix. Em seguida, enquanto
em Configuration → Templates, você pode importá-los manualmente no Zabbix.
Alteração no ExpressMS messenger webhook API A versão API foi alterada para v4 no ExpressMS messenger webhook.
12 O que há de novo no Zabbix 6.0.7
Suporte MariaDB 10.8 Agora, a maior versão suportada para Maria DB é 10.8.X.
Suporte TimescaleDB 2.6 Agora, a maior versão suportada para TimescaleDB é 2.6.
Templates Novos templates
Um novo template HPE Synergy por HTTP está disponível.
Veja as instruções da configuração para HTTP templates.
Você consegue acessar esse template:
• Em Configuration → Templates em novas instalações;
• Se você estiver atualizando a partir de versões anteriores, você pode baixar os novos templates de Zabbix em Git reposi-
tory ou encontrá-los no diretório zabbix/templates da versão mais recente baixada do Zabbix. Em seguida, enquanto em
Configuration → Templates, você pode importá-los manualmente no Zabbix.
Templates atualizados
O template PostgreSQL Agent 2 foi atualizado. Uma trigger para detectar falhas no checksum foi adicionada ao item Dbstat do
PostgreSQL Agent 2 template.
Você consegue acessar esse template:
• Em Configuration → Templates em novas instalações;
• Se você estiver atualizando a partir de versões anteriores, você consegue baixar os novos templates do repositório do Zabbix
Git repository ou encontrá-los templates no diretório da versão mais recente baixada do Zabbix. Em seguida, enquanto
em Configuration → Templates, você pode importá-los manualmente no Zabbix.
13 O que há de novo no Zabbix 6.0.8
Mês abreviado com letra maiúscula Agora, um ”mês” é abreviado com letra maiúscula ”M” no frontend. Anteriormente, era
abreviado com letra minúscula ”m”, sobrepondo a abreviação do minuto.
23
Suporte TimescaleDB 2.7 Agora, a versão maior suportada para TimescaleDB é 2.7.
Templates Um novo template OPNsense por SNMP template está disponível.
Você pode acessar esse template:
• Em Configuration → Templates em novas instalações;
• Se você estiver atualizando a partir de versões anteriores, você pode pode baixar novos templates do Zabbix em Git repos-
itory]([Link] ou encontrá-los no diretório da versão mais re-
cente baixada do Zabbix. Em seguida, enquanto em Configuration → Templates, você pode importá-los manualmente no
Zabbix.
Pacotes RHEL renomeados Os pacotes RHEL foram renomeados, adicionando uma palavra ”release” no nome:
Naming Nome do pacote
Old zabbix-agent-6.0.7-1.el9.x86_64.rpm
New zabbix-agent-6.0.8-release1.el9.x86_64.rpm
Não há nenhuma mudança funcional associada a essa alteração. Isso é nessário como preparação para fornecer pacotes da versão
menor (ou seja, 6.0.x) de candidatos a lançamento, esperados para começar com o 6.0.9. A mudança do nome garantirá que,
para alguém que tenha tanto os repositórios estáveis e instáveis habilitados no seu sistema, as atualizações de repositório sejam
recebidas na ordem correta. Essa mudança no nome é somente para pacotes RHEL.
14 O que há de novo no Zabbix 6.0.9
Macros de expressão Agora, os macros {[Link]<1-9>} são suportados dentro dos expression macros.
Pacotes Os scripts SQL foram movidos do diretório /usr/share/doc para /usr/share nos pacotes Zabbix.
15 O que há de novo no Zabbix 6.0.10
Filter settings remembered
In several Monitoring pages (Problems, Hosts, Latest data) the current filter settings are now remembered in the user profile. When
the user opens the page again, the filter settings will have stayed the same.
Additionally, the marking of a changed (but not saved) favorite filter is now a green dot next to the filter name, instead of the filter
name in italics.
Suporte TimescaleDB 2.8 A maior versão suportada para TimescaleDB agora é de 2.8.
Suporte PostgreSQL 15 Agora o PostgreSQL 15 é suportado. Perceba que o TimescaleDB ainda não suporta PostgreSQL 15.
Possibilidade de construir Zabbix agent 2 offline O Zabbix agent 2 agora pode ser construído offline. O tarball de origem
agora inclui o diretório src/go/vendor, que deve verificar que a golang não é obrigada a baixar os módulos de dependência
automaticamente. É possível atualizar os últimos módulos manualmente, usando os comandos go mod tidy ou go get .
PostgreSQL plugin loadable The PostgreSQL plugin is now loadable in Zabbix agent 2 (previously built-in).
See also: PostgreSQL loadable plugin repository
Frontend Miscellaneous
• Warnings about incorrect housekeeping configuration for TimescaleDB are now displayed if history or trend tables contain
compressed chunks, but Override item history period or Override item trend period options are disabled. For more informa-
tion, see TimescaleDB setup.
24
16 O que há de novo no Zabbix 6.0.11
Reportando sistemas de arquivo com inodes igual a zero Os itens do agente [Link] agora são capazes de reportar
sistemas de arquivo com contagem de inodes igual a zero, o que pode ser o caso para sistemas de arquivo com inodes dinâmicos.
(por exemplo: btrfs).
Ainda, agora os itens [Link] não se tornarão não suportados em casos como, modo configurado ’pfree’ ou ’pused’. Em
vez disso, os valores de pfree/pused para tais arquivos serão reportados como e ”100” e ”0”, respectivamente.
Consultas utilizadas da API Consultas de banco de dados da API, usadas ao pesquisar por nomes nas tabelas hosts e items,
foram otimizadas e agora serão processadas de forma mais eficiente.
17 O que há de novo no Zabbix 6.0.12
Melhoria de desempenho nos sincronizadores de histórico O desempenho de sincronizadores de histórico foi aprimorado
pela introdução de uma nova trava de leitura e escrita. Isso reduz o travamento entre os sincronizadores de histórico, trappers e
proxy poller, usando uma trava de leitura compartilhada ao acessar o cache de configuração. A nova trava pode ser bloqueada
somente para escrita pelo sincronizador de configuração que realiza a recarga do cache de configuração.
18 O que há de novo na Zabbix 6.0.13
Alterações (breaking changes) Versão de plugins carregáveis
Loadable plugins para o Zabbix agente 2 agora é utilizado o mesmo sistema de versionamento do próprio Zabbix. As seguintes
alterações foram feitas:
• MongoDB 1.2.0 -> MongoDB 6.0.13
• PostgreSQL 1.2.1 -> PostgreSQL 6.0.13
Esses plugins são compatíveis com qualquer versão secundária do Zabbix 6.0.
Observe que o repositório de fonte para cada puglin agora contém um branch dedicado release/6.0 branch (anteriormente, havia
apenas o branch master).
Suporte MariaDB 10.10 A versão máxima suportada para MariaDB agora é 10.10.X.
Importação de configuração Anteriormente, o processo de importação falharia devido a uma icompatibilidade de UUID de uma
entidade importável (grupo host, item, graph, etc.). Por exemplo, não era possível importar o grupo host se algum grupo host já
tivesse um mesmo nome existente no host.
Na nova versão, a importação falhará por causa de uma incompatibilidade de UUID; em vez disso, a entidade será correspondida
pelos critérios de singularidade, como o ID da entidade. A entidade será importada, e o UUID será atualizado para o UUID da
entidade importada.
Outra melhoria, ao remover o vínculo do template (a opção Excluir ausentes para o vínculo do template) através do template
importado ou host, as entidades herdadas não são mais removidas (o template fica desvinculado, não desvinculado e limpo), a
menos que essas entidades estejam ausentes no arquivo de importação entidades e a opção Excluir ausentes para a entidade
específica esteja marcada.
Devido a essa mudança, a opção de mensagem de alerta ao marcar a opção Excluir ausentes para o vínculo do template, não será
mais exibida.
Consultar tablespaces separadas em bancos de dados Oracle com Zabbix agent 2 O seguinte Zabbix agent 2 items,
suportados para o plugin do Oracle, agora possuem parâmetros opcionais adicionais:
• [Link][<existingParameters>,<diskgroup>]
• [Link][<existingParameters>,<destination>]
• [Link][<existingParameters>,<database>]
• [Link][<existingParameters>,<database>]
25
• [Link][<existingParameters>,<tablespace>,<type>]
Esses parâmetros permitem consultar instanciadas separadas de dados específicos, ao invés de todos os dados, melhorando assim
o desempenho.
Recuperar informação adicional com docker.container_info[] O docker.container_info[] Zabbix agent 2 item agora
suporta a opção de recuperar informações de nível baixo de forma parcial (short) ou recuperar informações de forma completa
sobre um Docker container.
Comandos de tempo de execução do para profiling Os comandos de tempo de execução para profilling foram adicionados
ao Zabbix server e ao Zabbix proxy.
• prof_enable - habilitar profiling
• prof_disable - desabilitar profiling
O Profiling por ser habilitado pelo processo server/proxy. Profilling habilitados fornecem detalhes de todo rwlocks/mutexes pela
função nome.
Veja também:
• Zabbix server runtime commands
• Zabbix proxy runtime commands
Função HMAC para JavaScript Uma nova função foi adicionada ao mecanismo JavaScript permitindo retornar um hash HMAC:
• hmac('<hash type>',key,string)
Essa função é util em casos em que é necessário um código de autenticação de mensagem baseado em hash (HMAC) para assinar
solicitações. Os tipos de hash MD5 e SHA256 são suportados, e. g.:
• hmac('md5',key,string)
• hmac('sha256',key,string)
Templates Novos templates estão disponíveis:
• AWS EC2 via HTTP
• AWS via HTTP
• Instância AWS RDS via HTTP
• Bucket AWS S3 via HTTP
• Azure via HTTP
• Servidor Control-M via HTTP
• Gerenciador empresarial Control-M via HTTP
• Veeam Backup Geranciador empresarial via HTTP
• Veeam Backup e Replication via HTTP
Veja instruções de setup para HTTP templates.
O template Oracle by Zabbix agent 2 foi atualizado (itens estáticos múltiplos removidos; múltiplos itens prototypes adicionados)
de acordo ao a mudança realizada Zabbix agent 2 items.
Para mais informações sobre atualizações, veja Template changes.
Você tem acesso a esses templates em:
• Em Configuração → Templates em nova instalações;
• se você está atualizando pelas versões anteriores, você pode fazer download dos novos templates pelo Zabbix Git repository
ou encontrar eles no diretório de downloads da última versão da Zabbix. Depois, enquanto estiver na Configuração →
Templates, você pode importá-los manualmente no Zabbix.
Suporte TimescaleDB 2.9 A versão máxima suportada para TimescaleDB agora é 2.9.
Integrações do Webhook Um novo tipo de mídiaLINE agora está disponível, permitindo o uso da funcionalidade webhook para
enviar notificações sobre eventos do Zabbix para o mensageiro LINE.
Idiomas Frontend Idiomas como Catalão e Romeno agora estão habilitadas no frontend.
26
Biblioteca Golang para atualização do Windows A biblioteca Golang usada pelo Zabbix agent 2 em conjunto com os plug-
ins MongoDB ou PostgreSQL para monitorar Windows agora é [Link]/Microsoft/go-winio, versão 0.6.0 (anteriormente
[Link]/natefinch/npipe). Veja também Golang libraries, MongoDB plugin dependencies, e PostgreSQL plugin depen-
dencies.
Aumento do limite de descritores de arquivos abertos para Zabbix agent 2 The system service file shipped in Zabbix
agent 2 packages now declares the open file descriptor limit of 8196. Anteriormente, o limite do sistema padrão de 1024 foi
utilizado. O novo limite é suficiente para a configuração padrão Zabbix agent 2. Se você tem uma configuração não padre
do agent 2 configuration, por exemplo use plugins adicionais ou recursos estendidos, esse limite pode precisar ser aumentado
manualmente futuramente. Nesse caso, ajuste o parâmetro LimitNOFILE no arquivo de unidade do sistema.
19 O que há de novo no Zabbix 6.0.14
Plugins carregáveis Conexão plugin Encrypted MongoDB
O plugin MongoDB agora oferece suporte à criptografia TLS ao se conectar ao MongoDB utilizando sessões nomeadas. O plugin
atualizado (Plugin MongoDB 1.2.1) está incluído nos pacotes oficiais do Zabbix a partir da versão Zabbix 6.0.14. Observe que o
MongoDB é um plugin carregável e pode ser instalado separadamente a partir dos pacotes ou de fontes. O plugin funcionará com
qualquer versão inferior do Zabbix 6.0. Para mais detalhes, ver MongoDB plugin.
Suporte PHP Agora, a maior versão suportada para PHP é 8.2.
Limites para objetos JavaScript no pré-processamento Os seguintes limites para JavaScript objects no pré-processamento
foram inseridos:
• O tamanho total de todas as mensagens que pode ser carregado com o método log() foi limitado para 8MB por execução
de script.
• A inicialização de múltiplos objetos HttpRequest foi limitada a 10 por execução de script.
• O tamanho total do comprimento dos campos de cabeçalho que podem ser adicionados a um único objeto HttpRequest
com o método addHeader() foi limitado a 128 Kbytes (caracteres especiais e nomes de cabeçalho estão incluídos).
20 O que há de novo no Zabbix 6.0.15
MariaDB 10.11 support A versão máxima supported version para MariaDB agora é 10.11.X.
Suporte TimescaleDB 2.10 O máximo supported version para TimescaleDB agora é 2.10.
Opções de conexão para Oracle plugin O Oracle plugin, suportado para Zabbix agent 2, agora permite especificar a opção
de login as sysdba, as sysoper, ou as sysasm. A opção pode ser adicionada tanto parâmetro chave de item do usuário
quanto ao parâmetro de configuração do puglin. [Link].<SessionName>. Usuário do formato user as sysdba
(a opção de login é case-insensitive; não deve contem um espaço final.
Assinando dados usando RS256 A nova função do Java Script sign(hash,key,data) foi implementada permitindo o uso
do algoritmo de criptografia RS256 para calcular a assinatura. Para mais detalhes ver: Additional JavaScript objects.
21 O que há de novo no Zabbix 6.0.16
Otimização de sincronização de configuração para Oracle
Para instalação do Zabbix com Oracle, agora é possível alterar manualmente os tipos de campo de item e pré-processamento de
item de nclob para nvarchar2 aplicando um patch de banco de dados .
22 O que há de novo no Zabbix 6.0.17
27
Integrações Webhook Um novo tipo de mídia Webhook webhook foi adicionado para enviar notificações do Zabbix para o
Event-Driven Ansible.
Misturar parâmetros da chave do item e da sessão em plugins do Zabbix agent 2 Agora, o Zabbix agent 2 permite a
substituição dos parâmetros named session, especificando os novos valores nos parâmetros da chave do item. Anteriormente,
os usuários precisavam selecionar se preferiam fornecer os valores da string de conexão em uma sessão nomeada ou em uma
chave do item. Se as sessões nomeadas fossem usadas, os parâmetros relacionados à chave do item precisavam estar vazios.
Agora, quando usamos sessões nomeadas, somente o primeiro parâmetro (geralmente, uma URI) deve ser especificado na sessão
nomeada, enquanto outros parâmetros podem ser definidos na sessão nomeada ou na chave do item.
O suporte a HTML na atribuição do Geomap foi removido Agora, o texto de atribuição para o Geomap dashboard widget
pode somente conter um texto simples; o suporte para HTML foi removido.
Nas configurações Geographical maps da Administração→ Sessão geral, o campo Atribuição somente estará visível quando o Tile
provider estiver configurado como Outro.
23 What’s new in Zabbix 6.0.18
Items docker.container_stats
The docker.container_stats item on Zabbix agent 2 now also returns a pids_stats property with the current number of pro-
cesses/threads on the container.
Cleaner configuration export YAML files generated during Zabbix entity configuration export no longer contain empty lines
between entities in an array, which makes such files shorter and more convenient to work with. See Configuration export/import
section for updated export examples.
UTF-8 BOM in configuration import Configuration import now supports files with a UTF-8 byte-order mark (BOM).
Cosmos DB monitoring The template Azure by HTTP now also works with Azure Cosmos DB for MongoDB.
You can get this template:
• In Configuration → Templates in new installations.
• If you are upgrading from previous versions, you can download this template from Zabbix Git repository or find it in the
zabbix/templates directory of the downloaded latest Zabbix version. Then, while in Configuration → Templates you can
import it manually into Zabbix.
Proxy history housekeeping The limitation on the amount of outdated information deleted from the proxy database per proxy
history housekeeping cycle has been removed.
Previously the housekeeper deleted only no more than 4 times the HousekeepingFrequency hours of outdated information. For
example, if HousekeepingFrequency was set to ”1”, no more than 4 hours of outdated information (starting from the oldest
entry) was deleted. In cases when a proxy would constantly receive data older than set in ProxyOfflineBuffer, this could result
in excessive data accumulation.
Now this limitation has been removed, providing a more effective proxy history housekeeping solution.
A new template Google Cloud Platform by HTTP (GCP by HTTP) is available.
Default values for Zabbix agent 2 Zabbix agent 2 plugins now allow to define default values for connecting to monitoring
targets in the configuration file. If no value is specified in an item key or a named session, the plugin will use the value defined in
Plugins.<PluginName>.Default.<Parameter> -
the corresponding default parameter. New parameters have the structure
for example, [Link]=tcp://localhost:27017. See for more info:
• Configuring plugins
• Plugin configuration file parameters
25 What’s new in Zabbix 6.0.20
28
Templates A new template AWS ECS Cluster by HTTP (along with its Serverless Cluster version) is available.
You can get this template:
• In Configuration → Templates in new installations;
• If you are upgrading from previous versions, you can download new templates from Zabbix Git repository or find them in
the zabbix/templates directory of the downloaded latest Zabbix version. Then, while in Configuration → Templates you can
import them manually into Zabbix.
Frontend Spellcheck disabled in non-descriptive text areas
Spellcheck has been disabled for the text areas in which non-descriptive text is entered, such as scripts, expressions, macro values,
etc.
Miscellaneous Database TLS connection for MySQL on SLES 12
The packages for server/proxy installation on SUSE Linux Enterprise Server version 12 are now built using MariaDB Connector/C
library, thus enabling the encryption of connection to MySQL using the DBTLSConnect parameter. The supported encryption values
are ”required” and ”verify_full”.
26 What’s new in Zabbix 6.0.21
MySQL 8.1 support
The maximum supported version for MySQL is now 8.1.X.
MariaDB 11.0 support
The maximum supported version for MariaDB is now 11.0.X.
Log file monitoring
For log[], logrt[], [Link][], [Link][] items, regular expression runtime errors are now logged in the Zabbix
agent log file. See more details.
Items New item for Zabbix agent 2
A new item has been added to MySQL plugin for Zabbix agent 2. This new item, [Link], can be used for executing
custom MySQL queries.
Templates New template is available:
• AWS Cost Explorer by HTTP
You can get this template:
• In Configuration → Templates in new installations;
• If you are upgrading from previous versions, you can download new templates from Zabbix Git repository or find them in
the zabbix/templates directory of the downloaded latest Zabbix version. Then, while in Configuration → Templates you can
import them manually into Zabbix.
Notifications Webhook integrations
New webhook media type for pushing Zabbix notifications to Mantis Bug Tracker has been added.
Installation Support for ARM64/AArch64
ARM64/AArch64 installation packages are now available for Debian, RHEL 8, 9 and its derivatives, as well as SLES/OpenSUSE Leap
15.
27 O que há de novo no Zabbix 6.0.22
Funções agregadas
Agora, a função last_foreach também é suportada nas seguintes funções agregadas aggregate functions: kurtosis, mad, skew-
ness, stddevpop, stddevsamp, sumofsquares, varpop, e varsamp.
29
Limite do valor de retorno
O limite do valor de retorno para receber o dado de fontes externas (como de scripts ou outros programas) foi aumentado para
16MB. Isso afeta:
• Itens Agent [Link][] e [Link][]
• Verificações de agentes personalizados definidos em user parameters
• SSH agent, External check, e itens Script
• Remote commands
Templates Novos templates estão disponíveis:
• Acronis Cyber Protect Cloud by HTTP
• HashiCorp Nomad by HTTP
• MantisBT by HTTP
Você pode obter esses templates:
• Em Configuração → Templates em novas instalações;
• Se você estiver atualizando a partir de versões anteriores, você pode baixar os novos templates de Zabbix Git repository ou
encontrá-los no diretório de últimos acessos zabbix/templates. Em seguida, enquanto em Configuration → Templates você
pode importá-los manualmente para o Zabbix.
28 What’s new in Zabbix 6.0.23
Databases Supported versions
PostgreSQL 16 and MariaDB 11.1 are now supported.
Plugins New item for PostgreSQL Zabbix agent 2 plugin
New item, [Link], has been added to PostgreSQL Zabbix agent 2 plugin. This item is used for returning the PostgreSQL
version.
Templates New templates
New template is available:
• Nextcloud by HTTP
You can get this template:
• In Configuration → Templates in new installations;
• If you are upgrading from previous versions, you can download new templates from Zabbix Git repository or find them in
the zabbix/templates directory of the downloaded latest Zabbix version. Then, while in Configuration → Templates you can
import them manually into Zabbix.
Updated templates
PostgreSQL by ODBC and PostgreSQL by Zabbix agent 2 templates now include the item and trigger for monitoring PostgreSQL
version.
Frontend Miscellaneous
The Clear history button located in Configuration → Hosts → Items has been renamed Clear history and trends to more accurately
describe its function, which is the same as the Clear history and trends button in the item configuration form.
In trigger action configuration, the condition type Trigger name has been renamed Event name to better describe its function. Note
that by default, the event name matches the trigger name unless a custom event name is specified in trigger configuration.
29 What’s new in Zabbix 6.0.24
Databases TimescaleDB 2.12 support
Support for TimescaleDB version 2.12 is now available.
30
Plugins New item in Zabbix agent 2 plugin
The item for returning the database server version is now available in MongoDB plugin ([Link]).
Templates New templates
New template is available:
• HPE iLO by HTTP
You can get this template:
• In Configuration → Templates in new installations;
• If you are upgrading from previous versions, you can download new templates from Zabbix Git repository or find them in
the zabbix/templates directory of the downloaded latest Zabbix version. Then, while in Configuration → Templates, you can
import them manually into Zabbix.
Updated templates
Integration with OpenShift has been added to Kubernetes cluster state by HTTP template.
2. Definições
Visual geral Nesta seção você pode aprender o significado de alguns termos comumente usados no Zabbix.
Definições host
- um dispositivo ligado à rede que você queira monitorar, com IP/DNS.
grupo de host
- um agrupamento lógico de hosts; ele pode conter hosts e modelos. Hosts e modelos dentro de um grupo de host não são
de nenhuma forma associados um ao outro. Grupos de host são usados quando garantindo direitos de acesso aos hosts para
diferentes grupos de usuário.
item
- um fragmento de dado em especial que você queira receber de um host, uma métrica de dados.
pré-processamento de valor
- *uma transformação de um valor de métrica recebido antes de salvá-lo no banco de dados.
gatilho
- uma expressão lógica que define um limite (threshold) de problema e é usado para ”avaliar” os dados recebidos em itens.
Quando os dados recebidos estão acima do limite, os gatilhos vão do estado ’Ok’ para ’Problema’. Quando os dados recebidos
estão abaixo do limite, os gatilhos se mantêm/retornam para um estado ’Ok’.
evento
- uma ocorrência única de algo que mereça atenção tal como um gatilho mudando de estado ou um autoregistro de de-
scoberta/agente acontecendo.
etiqueta de evento
- um marcador pré-definido para o evento. Ela pode ser usada na correlação de evento, granulação de permissão, etc.
correlação de evento
- um método de correlação de problemas às suas soluções flexivelmente e precisamente.
Por exemplo, você pode definir que um problema reportado por um gatilho pode ser solucionado por outro gatilho, que pode até
mesmo usar método de coleta de dados diferente.
problema
- um gatilho que está em estado de ”Problema”.
atualização de problema
- opções de gerenciamento de problema fornecidas pelo Zabbix, tais como adição de comentário, reconhecimento, mudança de
severidade ou encerrar manualmente.
31
ação
- meios pré-definidos de reagir a um evento.
Uma ação consiste de operações (p.e. enviando uma notificação) e condições (quando a operação é executada)
escalação
- um cenário customizado para execução de operações dentro de uma ação; uma sequência de envio de notificações/execução de
comandos remotos.
mídia
- um meio de entrega de notificações; canal de entrega.
notificação
- uma mensagem sobre algum evento enviada para um usuário através do canal de mídia escolhido.
comando remoto
- um comando pré-definido que é automaticamente executado em um host monitorado diante de alguma condição.
modelo (template)
- um conjunto de entidades (itens, gatilhos, gráficos, regras de descoberta de baixo-nível, cenários web) prontas para serem
aplicadas a um ou vários hosts.
A função dos modelos é acelerar a implementação de tarefas de monitoramento em um host; também tornar mais fácil a aplicação
de mudanças em massa às tarefas de monitoramento. Modelos são associados diretamente a hosts individualmente.
cenário web
- uma ou várias requisições HTTP para verificar a disponibilidade de um site web.
frontend
- a interface web fornecida com o Zabbix.
dashboard
- seção customizável da interface web exibindo resumos e visualizações de informações importantes em unidades visuais chamadas
widgets.
widget
- unidade visual exibindo informações de um certo tipo e origem (um sumário, um mapa, um gráfico, o relógio, etc), usado no
dashboard.
Zabbix API
- A API do Zabbix permite usar o protocolo JSON RPC para criar, atualizar e buscar objetos Zabbix (como hosts, itens, gráficos e
outros) ou executar quaisquer outras tarefas customizadas.
Zabbix Server
- um processo central do software Zabbix que executa monitoramento, interage com os Zabbix Proxies e Agents, calcula gatilhos,
envia notificações; um repositório central de dados.
Zabbix Proxy
- um processo que pode coletar dados em nome do Zabbix Server, tirando um pouco da carga de processamento do Server.
Zabbix Agent
- um processo implementado nos alvos de monitoramento para monitorar ativamente os recursos e aplicações locais.
Zabbix Agent 2
- uma nova geração do Zabbix Agent para monitorar ativamente recursos e aplicações locais, permitindo usar plugins customizados
para monitoramento.
Attention:
Pelo fato de o Zabbix Agent 2 compartilhar muita funcionalidade com o Zabbix Agent, o termo ”Zabbix Agent” na docu-
mentação se aplica a ambos - Zabbix Agent e Zabbix Agent 2, se o comportamento funcional é o mesmo. O Zabbix Agent
2 é especificamente nomeado apenas se sua funcionalidade for diferente.
criptografia
32
- suporte de comunicações criptografadas entre componentes Zabbix (Server, Proxy, Agent, utilitários zabbix_sender e zabbix_get)
usando o protocolo Transport Layer Security (TLS).
descoberta de rede
- descoberta automatizada de dispositivos de rede.
descoberta de baixo-nível
- descoberta automatizada de entidades de baixo-nível em um dispositivo em particular (p.e. sistemas de arquivo, interfaces de
rede, etc.).
regra de descoberta de baixo-nível
- conjunto de definições para descoberta automatizada de entidades de baixo-nível em um dispositivo.
protótipo de item
- uma métrica com certos parâmetros como variáveis, pronta para descoberta de baixo-nível. Após a descoberta de baixo-nível as
variáveis são automaticamente substituídas com os parâmetros reais descobertos e a métrica automaticamente inicia a coleta de
dados.
protótipo de gatilho
- um gatilho com certos parâmetros como variáveis, pronto para descoberta de baixo-nível. Após a descoberta de baixo-nível as
variáveis são automaticamente substituídas com os parâmetros reais descobertos e a métrica automaticamente inicia a coleta de
dados.
Protótipos de algumas outras entidades do Zabbix estão também em uso na descoberta de baixo-nível - protótipos de gráfico,
protótipos de host, protótipos de grupo de host.
autoregistro de agente
- processo automatizado através do qual um Zabbix Agent a si mesmo é registrado como um host e começa a monitorar.
3. Processos Zabbix
Por favor use a barra lateral para acessar o conteúdo na seção de processo do Zabbix.
2 Servidor
Visão geral
O Zabbix Server é o componente central da solução.
O servidor gerencia a coleta e recebimento de dados, calcula o estado das triggers, envia notificações aos usuários. Ele é o
componente para o qual os agentes e proxies enviam dados sobre a disponibilidade, performance e integridade dos sistemas
monitorados. O servidor também pode executar por sí só verificações remotas nos dispositivos monitorados, estas verificações
ocorrem quando se utiliza itens do tipo ”verificação simples”.
O servidor gerencia o repositório central de configuração, estatísticas e armazenamento de dados operacionais, é ele quem irá
alertar os administradores quando os incidentes ocorrerem.
As funcionalidades básicas de uma solução de monitoração baseada em Zabbix é distribuida em três componentes: Zabbix Server,
interface web e banco de dados (SGDB).
Todas as informações de configuração da monitoração são armazenadas no banco de dados, tanto o Servidor quanto a Interface
Web do Zabbix interagem com o SGBD. Por exemplo, quando você utiliza a interface web (ou a API) para adicionar itens, eles são
salvos em uma tabela do SGDB. Em paralelo a isso o Zabbix Server, uma vez a cada minuto, irá buscar, na tabela de itens, a lista
de itens que deverão ser monitorados. É por isso que pode demorar até dois minutos para que uma modificação feita na Interface
Web comece a produzir efeitos na tela de dados recentes.
Processo do Servidor
O Zabbix Server é executado como um processo de segundo plano (daemon). O exemplo abaixo demonstra uma das formas de
inicia-lo:
shell> cd sbin
shell> ./zabbix_server
33
Você pode utilizar alguns parâmetros com o Zabbix Server:
-c --config <arquivo> caminho absoluto (completo) para o arquivo de configuração (o padrão é /et
-R --runtime-control <opção> executa funções administrativas
-h --help apresenta o help de parâmetros
-V --version apresenta o número de versão
Note:
O controle em tempo de execução não é suportado em OpenBSD e em NetBSD.
Exemplos de linha de comando com parâmetros:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf
shell> zabbix_server --help
shell> zabbix_server -V
Controle em tempo de execução
Opções do controle em tempo de execução:
Opção Descrição Objetivo
config_cache_reload Atualiza o cache de configuração. O comando é
ignorado se o cache já estiver atualizado.
log_level_increase[=<alvo>] Aumenta o nível de log, afeta todos os processos pid - Identificador do processo (1 a
se o alvo não for especificado. 65535)
tipo do processo - Restringe a
todos os processos de determinado
tipo (Ex.: poller)
tipo do processo,N - Restringe a
determinado processo de um tipo
específico (Ex.: poller,3)
log_level_decrease[=<alvo>] Reduz o nível de log, afeta todos os processos se
o alvo não for especificado.
O PID do processo a se modificar o nível de log deverá estar entre 1 e 65535. Em ambientes com muitos processos a modificação
poderá ser feita em um processo específico.
Exemplo de utilização do controle em tempo de execução para recarregar o cache de configuração do Zabbix Server:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R config_cache_reload
Exemplos de utilização do controle em tempo de execução para modificar o nível de log:
Aumenta o nível de log de todos os processos:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_increase
Aumenta o nível de log do segundo processo de pooler:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_increase=poller,2
Aumenta o nível de log do processo com PID 1234:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_increase=1234
Diminui o nível de log de todos os processos do pooler HTTP:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_decrease="http poller"
Inicie manualmente
Se o acima não funcionar você terá que iniciar manualmente. Encontre o caminho para o binário do zabbix_server e execute:
shell> zabbix_server
Você pode usar os seguintes parâmetros de linha de comando com o Zabbix server:
-c --config <file> caminho para o arquivo de configuração (o padrão é /usr/local/etc/zabbix_s
-f --foreground executa o Zabbix Server ao fundo (foreground)
-R --runtime-control <option> realiza funções administrativas
-h --help apresenta esta ajuda
-V --version exibe número de versão
34
Exemplos de execução do Zabbix Server com parâmetros de linha de comando:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf
shell> zabbix_server --help
shell> zabbix_server -V
Controle em tempo de execução
Opções de controle em tempo de execução:
Opção Descrição Alvo
config_cache_reload Recarrega o cache de configuração. Ignorado se o cache
atualmente está sendo carregado.
diaginfo[=<target>] Reúne informações de diagnóstico no arquivo de log do historycache - estatísticas de
Server. cache de histórico
valuecache - estatísticas de
cache de valor
preprocessing - estatísticas
de gerenciados de
pré-processamento
alerting - estatísticas de
gerenciador de alerta
lld - estatísticas de
gerenciador de LLD
locks - lista de mutexes (é
vazio em sistemas **BSD*)
ha_status Registra (log) o estado do cluster de alta disponibilidade
(HA).
ha_remove_node=target Remove o nó de alta disponibilidade (HA) especificado target - número do nó na lista
pelo seu número listado. (pode ser obtido pela
Note que nós ativos/em espera não podem ser execução de ha_status)
removidos.
ha_set_failover_delay=delay Configura atraso de recuperação de falha (failover) de
alta disponibilidade (HA).
Sufixos de tempo são suportados, p.e. 10s, 1m.
secrets_reload Recarrega segredos do Vault.
service_cache_reload Recarrega o cache do gerenciador de serviço.
snmp_cache_reload Recarrega cache SNMP, limpa as propriedades SNMP
(engine time, engine boots, engine id, credentials) para
todos os hosts.
housekeeper_execute Inicia procedimento de housekeeping. Ignorado se o
procedimento de housekeeping está atualmente em
progresso.
trigger_housekeeper_execute Inicia o procedimento de gatilho de housekeeping.
Ignorado se o procedimento de gatilho de housekeeping
está atualmente em progresso.
log_level_increase[=<target>] Aumenta nível de log, afeta todos os processos se alvo process type - Todos os
não for especificado. processos do tipo especificado
Não suportado nos sistemas **BSD*. (p.e., poller)
Veja todos os tipos de
processo do Server.
process type,N - Tipo e
número do processo (p.e.,
poller,3)
pid - Identificador do processo
(1 até 65535). Para valores
maiores especifique alvo como
’process type,N’.
log_level_decrease[=<target>] Diminui nível de log, afeta todos os processos se alvo
não for especificado.
Não suportado nos sistemas **BSD*.
Exemplo de utilização de controle em tempo de execução para recarregar o cache de configuração do Server:
35
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R config_cache_reload
Exemplo de utilização de controle em tempo de execução para reunir informação de diagnóstico:
Reúne todas as informações de diagnóstico disponíveis no arquivo de log do Server:
shell> zabbix_server -R diaginfo
Reúne estatísticas de cache de histórico no arquivo de log do Server:
shell> zabbix_server -R diaginfo=historycache
Exemplo de utilização de controle em tempo de execução para recarregar cache SNMP:
shell> zabbix_server -R snmp_cache_reload
Exemplo de utilização de controle em tempo de execução para execução de gatilho de housekeeper:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R housekeeper_execute
Exemplo de utilização de controle em tempo de execução para alterar nível de log:
Aumenta nível de log de todos os processos:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_increase
Aumenta o nível de log do segundo processo de poller:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_increase=poller,2
Aumenta nível de log do processo com PID 1234:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_increase=1234
Diminui o nível de log de todos os processos de poller http:
shell> zabbix_server -c /usr/local/etc/zabbix_server.conf -R log_level_decrease="http poller"
Exemplo de configuração de atraso de failover HA para o mínimo de 10 segundos:
shell> zabbix_server -R ha_set_failover_delay=10s
Scripts de inicialização
Os scripts são utilizados para iniciar automaticamente os processos do Zabbix Server durante o processo de inicialização e final-
ização da máquina. Tais scripts podem ser localizados no diretório misc/init.d do código fonte da solução.
Plataformas suportadas
Devido aos requisitos de segurança e a natureza de missão crítica do funcionamento do Zabbix Server, o UNIX é o único sistema
operacional que pode entregar de forma consistente o desempenho, tolerância a falhas e resiliência necessários. O Zabbix opera
como uma das soluções líderes de mercado.
O Zabbix Server é testado nas seguintes plataformas:
• Linux
• Solaris
• AIX
• HP-UX
• Mac OS X
• FreeBSD
• OpenBSD
• NetBSD
• SCO Open Server
• Tru64/OSF1
Note:
O Zabbix pode funcionar em outros sistemas operacionais baseados no UNIX.
Start-up scripts
The scripts are used to automatically start/stop Zabbix processes during system’s start-up/shutdown. The scripts are located under
directory misc/init.d.
Server process types
• alert manager - alert queue manager
• alert syncer - alert DB writer
36
• alerter - process for sending notifications
• availability manager - process for host availability updates
• configuration syncer - process for managing in-memory cache of configuration data
• discoverer - process for discovery of devices
• escalator - process for escalation of actions
• history poller - process for handling calculated, aggregated and internal checks requiring a database connection
• history syncer - history DB writer
• housekeeper - process for removal of old historical data
• http poller - web monitoring poller
• icmp pinger - poller for icmpping checks
• ipmi manager - IPMI poller manager
• ipmi poller - poller for IPMI checks
• java poller - poller for Java checks
• lld manager - manager process of low-level discovery tasks
• lld worker - worker process of low-level discovery tasks
• poller - normal poller for passive checks
• preprocessing manager - manager of preprocessing tasks
• preprocessing worker - process for data preprocessing
• problem housekeeper - process for removing problems of deleted triggers
• proxy poller - poller for passive proxies
• report manager- manager of scheduled report generation tasks
• report writer - process for generating scheduled reports
• self-monitoring - process for collecting internal server statistics
• snmp trapper - trapper for SNMP traps
• task manager - process for remote execution of tasks requested by other components (e.g. close problem, acknowledge
problem, check item value now, remote command functionality)
• timer - timer for processing maintenances
• trapper - trapper for active checks, traps, proxy communication
• unreachable poller - poller for unreachable devices
• vmware collector - VMware data collector responsible for data gathering from VMware services
The server log file can be used to observe these process types.
Various types of Zabbix server processes can be monitored using the zabbix[process,<type>,<mode>,<state>] internal item.
Supported platforms
Due to the security requirements and mission-critical nature of server operation, UNIX is the only operating system that can
consistently deliver the necessary performance, fault tolerance and resilience. Zabbix operates on market leading versions.
Zabbix server is tested on the following platforms:
• Linux
• Solaris
• AIX
• HP-UX
• Mac OS X
• FreeBSD
• OpenBSD
• NetBSD
• SCO Open Server
• Tru64/OSF1
Note:
Zabbix may work on other Unix-like operating systems as well.
Locale
Note that the server requires a UTF-8 locale so that some textual items can be interpreted correctly. Most modern Unix-like systems
have a UTF-8 locale as default, however, there are some systems where that may need to be set specifically.
1 Cluster de alta disponibilidade
Visão geral
37
O modo de alta disponibilidade oferece proteção contra falhas de software/hardware para o Zabbix Server e permite minimizar o
tempo de parada durante manutenções de software/hardware.
O cluster de alta disponibilidade (HA) é uma solução opcional (opt-in) e é suportada para Zabbix Server. A solução de HA nativa é
projetada para ser simples de usar, funcionará entre sites e não possui requisitos específicos para os bancos de dados que o Zabbix
reconhece. Os usuários são livres para utilizar a solução de HA nativa do Zabbix, ou uma solução de HA de terceiros, dependendo
do que melhor atende as necessidades de alta disponibilidade em seus ambientes.
A solução consiste de múltiplas instâncias ou nós do zabbix_server. Cada nó:
• é configurado separadamente (arquivo de configuração, scripts, criptografia, exportação de dados)
• usa o mesmo banco de dados
• possui vários modos: ativo, em espera, indisponível, parado
Apenas um nó pode estar ativo (trabalhando) por vez. Os nós em espera não fazem coleta de dados, processamento ou outras
atividades regulares do Server; eles não esperam por comunicação nas portas; eles têm conexões mínimas com o banco de dados.
Ambos os nós ativos e em espera atualizam seus horários de último acesso a cada 5 segundos. Cada nó em espera monitora o
horário do último acesso do nó ativo. Se horário do último acesso do nó ativo estiver acima de ’atraso de recuperação de falha’
segundos, o nó em espera torna a si o nó ativo e associa o estado de ’indisponível’ ao nó anteriormente ativo.
O nó ativo monitora sua própria conectividade de banco de dados - se for perdida por mais do que atraso de recuperação
de falha - 5 segundos, ele deve parar todo o processamento e alterar para o modo de espera. O nó ativo também monitora o
estado dos nós em espera - se o horário do último acesso de um nó em espera for maior do que ’atraso de recuperação de falha’
segundos, o nó em espera recebe o estado de ’indisponível’.
O atraso de recuperação de falha é configurável, com o valor mínimo sendo de 10 segundos.
Os nós são projetados para serem compatíveis entre versões secundárias (minor) do Zabbix.
Habilitando cluster HA
Configurações do Server
Para transformar qualquer Zabbix Server de um servidor isolado (standalone) em um nó de cluster HA, especifique o parâmetro
HANodeName (nome do nó) na configuração do Server.
O parâmetro de endereço do nó NodeAddress (endereço:porta), se configurado, deve ser usado pelo Frontend do nó ativo, sobre-
screvendo o valor presente no [Link].
Preparing frontend
Make sure that Zabbix server address:__SOFIA_PII_1__
Zabbix frontend will autodetect the active node by reading settings from the nodes table in Zabbix database. Node address of the
active node will be used as the Zabbix server address.
Configuração do Proxy
Para habilitar conexões à múltiplos Servers em um ambiente de alta disponibilidade, liste os endereços de nó de HA no parâmetro
Server do Proxy, separados por ponto-e-vírgula.
Configurações do Agent
Para habilitar conexões à múltiplos Servers em um ambiente de alta disponibilidade, liste os endereços de nó de HA no parâmetro
ServerActive do agente, separados por ponto-e-vírgula.
Failover to standby node
Zabbix will fail over to another node automatically if the active node stops. There must be at least one node in standby status for
the failover to happen.
How fast will the failover be? All nodes update their last access time (and status, if it is changed) every 5 seconds. So:
• If the active node shuts down and manages to report its status as ”shut down”, another node will take over within 5 seconds.
• If the active node shuts down/becomes unavailable without being able to update its status, standby nodes will wait for the
failover delay + 5 seconds to take over
The failover delay is configurable, with the supported range between 10 seconds and 15 minutes (one minute by default). To
change the failover delay, you may run:
zabbix_server -R ha_set_failover_delay=5m
Gerenciando um cluster HA
O estado atual do cluster HA pode ser gerenciado usando as opções de controle em tempo de execução dedicadas:
38
• ha_status - registra o estado do cluster HA no log do Zabbix Server;
• ha_remove_node=alvo - remove um nó HA identificado por seu <alvo> - número do nó na lista (o número pode ser obtido
do resultado da execução de ha_status). Note que nós ativos/em espera não podem ser removidos.
• ha_set_failover_delay=atraso - configure o atraso de recuperação de falha de HA (sufixos de tempo são suportados, p.e.
10s, 1m)
O estado de um nó pode ser monitorado:
• em Relatórios → Informação do sistema
• no widget de dashboard Informação de sistema
• usando a opção de controle em tempo de execução ha_status do Server (veja acima).
O item interno zabbix[cluster,discovery,nodes] pode ser usado para descoberta de nó, pois ele retorna um JSON com
informações de nós de alta disponibilidade.
Desabilitando um cluster HA
Para desabilitar um cluster de alta disponibilidade:
• faça cópia de backup dos arquivos de configuração
• pare os nós em espera
• remova o parâmetro HANodeName do servidor primário ativo
• reinicie o servidor primário (ele iniciará em modo isolado (standalone))
######Detalhes da implementação
O cluster de alta disponibilidade (HA) é uma solução opcional e é suportada pelo Zabbix server. A solução nativa de HA está
designada para ser simples de usar, funcionará em todos os sites e não tem requisitos específicos para o banco de dados que
o Zabbix reconhece. Os usuário são livres para usar a solução de HA nativa do Zabbix, ou uma solução de HA de terceiros,
dependendo do que irá atender melhor os requisitos de alta disponibilidade em seu ambiente.
A solução consiste de múltiplas instâncias do zabbix_server ou nós. Cada nó:
• é configurado separadamente
• usa o mesmo banco de dados
• pode ter vários modos: ativo, espera, indisponível, parado
Apenas um nó pode estar ativo (trabalhando) por vez. Um nó de espera executa apenas o processo gerenciador do HA. Um nó
de espera não realiza a coleta de dados, processamento ou outras atividades regulares do servidor; eles não escutam nas portas;
eles tem conexões mínimas com o banco de dados.
Ambos os nós ativos e em espera atualizam sua última hora de acesso a cada 5 segundos. Cada nó em espera monitora o último
horário de acesso do nó ativo. Se a última hora de acesso do nó ativo for maior que o ’atraso de failover’ em segundos, o nó de
espera muda para ser o nó ativo e atribui o status de ’indisponível’ para o nó ativo anteriormente.
O nó ativo monitora sua própria conectividade com o banco de dados - se ela for perdida por mais de ’failover delay -5’ segundos,
ele deve parar todos os processos e mudar para o modo de espera. O nó ativo também monitora o status dos nós em espera -
se o último horário de acesso do nó de espera for maior que o ’failover delay’ em segundos, o nó em espera muda o status para
’indisponível’.
3 Agent 2
Visão geral
O Zabbix Agent 2 é uma nova geração do agente Zabbix e pode ser usado no lugar do Zabbix Agent. O Zabbix Agent 2 foi
desenvolvido para:
• reduzir o número de conexões TCP
• fornecer concorrência aprimorada de verificações
• ser facilmente extensível com plugins. Um plugin deve ser capaz de:
– fornecer verificações triviais consistindo de apenas poucas linhas simples de código
– fornecer verificações complexas consistindo de scripts de longa execução e aquisição de dados isolada com envio
periódico dos dados de volta
• ser uma substituição opcional para o Zabbix Agent (em que ele suporta todas as funcionalidades anteriores)
O Agent 2 é escrito em Go (com algum código em C reutilizado do Zabbix Agent). Um ambiente Go configurado com uma versão
de Go atualmente suportada é necessário para compilar o Zabbix Agent 2.
39
O Agent 2 não possui suporte nativo a execução com deamon (daemonization) no Linux; ele pode ser executado como um serviço
do Windows.
Verificações passivas funcionam de forma similar ao Zabbix Agent. As verificações ativas suportam intervalos agendados/flexíveis
e concorrência de verificação em um Server ativo.
Concorrência de verificação
Verificações de diferentes plugins podem ser executadas de forma concorrente. O número de verificações concorrentes dentro de
um plugin é limitada pela configuração de capacidade do plugin. Cada plugin pode ter uma configuração de capacidade fixada
em código (sendo 100 o padrão) que pode ser diminuída usando a configuração Plugins.<Plugin name>.Capacity=N no
parâmetro de configuração Plugins.
Veja também: Orientações para desenvolvimento de plugin.
Plataformas suportadas
O Agent 2 é suportado pelas plataformas Linux e Windows.
Se instalando a partir dos pacotes, o Agent 2 é suportado em:
• RHEL/CentOS 6, 7, 8
• SLES 15 SP1+
• Debian 9, 10
• Ubuntu 18.04, 20.04
No Windows o Agent 2 é suportado em:
• Windows Server 2008 R2 e mais recente
• Windows 7 e mais recente
Instalação
O Zabbix Agent 2 está disponível em pacotes pré-compilados. Para compilar o Zabbix Agent 2 a partir dos fontes você tem que
especificar a opção de configuração --enable-agent2.
Opções
Os seguintes parâmetros de linha de comando podem ser usados com o Zabbix Agent 2:
Parâmetro Descrição
-c --config <arquivo-configuração> Caminho para o arquivo de configuração.
Você pode usar esta opção para informar um arquivo de
configuração que não é o arquivo padrão.
No UNIX, o padrão é /usr/local/etc/zabbix_agent2.conf ou como
configurado pelas variáveis de tempo de compilação
--sysconfdir ou --prefix
-f --foreground Executa o agente ao fundo (foreground) (padrão: true
(verdadeiro)).
-p --print Apresenta itens conhecidos e sai.
Nota: Para retornar os resultados de parâmetro do usuário
também, você deve especificar o arquivo de configuração (caso
ele não esteja na localização padrão).
-t --test <item key> Testa o item especificado e sai.
Nota: Para retornar os resultados de parâmetro do usuário
também, você deve especificar o arquivo de configuração (caso
ele não esteja na localização padrão).
-h --help Apresenta informações de ajuda e sai.
-v --verbose Apresenta informações de depuração (debugging). Use esta
opção com as marcações -p e -t.
-V --version Apresenta o número de versão do agente e sai.
-R --runtime-control <option> Executa funções administrativas. Veja controle em tempo de
execução.
Exemplos específicos de utilização de parâmetros de linha de comando:
• apresenta todos os itens nativos com valores
• testa um parâmetro de usuário com a chave ”[Link]” definida no arquivo de configuração especificado
40
shell> zabbix_agent2 --print
shell> zabbix_agent2 -t "[Link]" -c /etc/zabbix/zabbix_agentd.conf
Controle em tempo de execução (runtime)
O controle em tempo de execução fornece algumas opções para controle remoto.
Opção Descrição
log_level_increase Aumenta nível de log.
log_level_decrease Diminui nível de log.
metrics Lista de métricas disponíveis.
version Exibe versão do agente.
userparameter_reload Recarrega parâmetros de usuário do arquivo de configuração atual.
Note que o UserParameter é única opção de configuração do agente que será
recarregada.
help Exibe informações de ajuda sobre controle em tempo de execução.
Exemplos:
• aumentando o nível de log para o Agent 2
• apresenta opções de controle em tempo de execução
shell> zabbix_agent2 -R log_level_increase
shell> zabbix_agent2 -R help
Arquivo de configuração
Os parâmetros de configuração do Agent 2 são predominantemente compatíveis com o Zabbix Agent com algumas exceções.
Novos parâmetros Descrição
ControlSocket O caminho para o socket de controle em tempo de
execução. O Agent 2 usa um socket de controle para
comandos em tempo de execução.
EnablePersistentBuffer, Estes parâmetros são usados para configurar o
PersistentBufferFile, armazenamento persistente no Agent 2 para itens
PersistentBufferPeriod ativos.
Plugins Plugins podem ter seus próprios parâmetros, no
Plugins.<Nome do
formato
plugin>.<Parâmetro>=<valor>. Um parâmetro
de plugin comum é Capacity (capacidade),
configurando o limite de verificações que podem ser
executadas ao mesmo tempo.
StatusPort A porta na qual o Agent 2 aguardará comunicação
(listening) para requisições de estado HTTP e
exibição de uma lista de plugins configurados e
alguns parâmetros internos
Parâmetros descontinuados Descrição
AllowRoot, User Não suportado porque operação como daemon
(daemonization) não é suportada.
LoadModule, LoadModulePath Módulos carregáveis não são suportados.
StartAgents Este parâmetro era usado no Zabbix Agent para
aumentar a concorrência de verificações passivas ou
desabilitá-los. No Agent 2, a concorrência é
configurada no nível do plugin e pode ser limitada
por uma configuração de capacidade. Considerando
que desabilitar verificações passivas não é
atualmente suportado.
HostInterface, HostInterfaceItem Não suportado ainda.
Para mais detalhes veja as opções do arquivo de configuração para zabbix_agent2.
Códigos de saída
A partir da versão 4.4.8 o Zabbix Agent 2 também pode ser compilado com versões mais antigas do OpenSSL (1.0.1, 1.0.2).
41
Neste caso o Zabbix oferece mutexes para travamento no OpenSSL. Se um travamento ou destravamento mutex falhar então uma
mensagem de erro é apresentada na saída de erro padrão (STDERR) e o Agent 2 sai com código de erro 2 ou 3, respectivamente.
3 Agente
Visão geral
O agente Zabbix é instalado no dispositivo alvo da monitoração. Possui capacidade de monitorar de monitorar ativamente os
recursos e aplicações locais (discos e partições, memória, estatísticas do processador, etc).
O agente concentra as informações locais sobre o dispositivo monitorado para posterior envio ao servidor ou proxy Zabbix (depen-
dendo da configuração). Em caso de falhas (como um disco cheio ou a interrupção de um processo) o servidor Zabbix pode alertar
ativamente os administradores do ambiente sobre o ocorrido.
Os agentes Zabbix são extremamente eficientes pois utilizam chamadas nativas do sistema operacional para obter as informações
estatísticas.
Verificações passivas e ativas
Os agentes Zabbix podem executar verificações passivas ou ativas.
Em uma verificação passiva o agente responde à uma requisição de informações. O servidor ou o proxy Zabbix requisitam o dado
toda vez que é necessário (uso de CPU, memória, disco, etc), o agente responde com o resultado do teste solicitado.
O processo de verificação ativa requer um processamento mais complexo. O agente precisa primeiro receber a lista de itens a
monitorar e o intervalo entre coletas pretendido. Esta informação vem do servidor Zabbix através de requisições periódicas do
agente.
A verificação ativa permite que o agente continue executando o perfil de monitoração mesmo quando o servidor Zabbix está
indisponível, enviando posteriormente e de forma retroativa o resultado dos testes.
A definição se a verificação deve ocorrer de forma passiva ou ativa é configurada através do tipo do item, na interface web do
Zabbix. Um agente Zabbix pode processar itens do tipo ’Agente Zabbix’ ou ”Agente Zabbix (ativo)”.
Plataformas suportadas
O agente Zabbix é suportado por:
• Linux
• IBM AIX
• FreeBSD
• NetBSD
• OpenBSD
• HP-UX
• Mac OS X
• Solaris: 9, 10, 11
• Windows: 2000, Server 2003, XP, Vista, Server 2008, 7
Instalação
Veja as instruções de instalação para o agente.
Attention:
Em geral os agentes 32bits do Zabbix conseguirão ser executados em ambientes 64bits, mas em alguns casos poderá
ocorrer falha.
Instalação
Veja instalação de pacotes localpara instruções sobre como instalar o agente Zabbix como pacote.
Veja instruções alternativas para instalação manual caso não queira instalar via pacotes.
::: Aviso importante Em geral, Agentes Zabbix 32bit irão funcionar com sistemas 64bit , mas podem falhar em alguns casos. :::
Controle em tempo de execução
Opções de controle em tempo de execução:
42
Opção Descrição Alvo
log_level_increase[=<alvo>] Aumenta o nível de log, afeta todos os processos se o alvo pid - Identificador do
não for especificado. processo (1 a 65535)
tipo do processo -
Restringe a todos os
processos de
determinado tipo
(Ex.: poller)
tipo do processo,N
- Restringe a
determinado
processo de um tipo
específico (Ex.:
poller,3)
log_level_decrease[=<alvo>] Reduz o nível de log, afeta todos os processos se o alvo
não for especificado.
O PID do processo a se modificar o nível de log deverá estar entre 1 e 65535. Em ambientes com muitos processos a modificação
poderá ser feita em um processo específico.
Exemplo de utilização do controle em tempo de execução para modificar o nível de log:
Increase log level of all processes:
shell> zabbix_agentd -c /usr/local/etc/zabbix_agentd.conf -R log_level_increase
Aumenta o nível de log do segundo processo do ouvinte (listener):
shell> zabbix_agentd -c /usr/local/etc/zabbix_agentd.conf -R log_level_increase=listener,2
Aumenta o nível de log do processo com PID 1234:
shell> zabbix_agentd -c /usr/local/etc/zabbix_agentd.conf -R log_level_increase=1234
Reduz o nível de log de todas os processos de verificação ativa:
shell> zabbix_agentd -c /usr/local/etc/zabbix_agentd.conf -R log_level_decrease="active checks"
Processo de usuário
O agente Zabbix foi desenhado para ser executado como um processo “não-root”. Ele pode ser executado com a permissão do
usuário que o iniciou. Neste cenário ele irá executar sem nenhum problema.
Se você tentar inicia-lo com o usuário ’root’, ele alternará seu permissionamento de execução para o usuário ’zabbix’, que deverá
existir em seu ambiente. Você só poderá rodar o Servidor Zabbix como ’root’ se modificar o parâmetro ’AllowRoot’ no arquivo de
configuração.
Agent em sistemas Windows
O Zabbix Agent no Windows é executado como um Serviço do Windows.
Executando o agente em ambiente Microsoft Windows
Veja o manual do agente no Windows para detalhes sobre como instalar, configurar e executar o agente neste sistema operacional.
Sintaxe de linha de comando do agente no Windows:
zabbix_agentd.exe [-c arquivo-de-configuração]
zabbix_agentd.exe [-c arquivo-de-configuração] -p
zabbix_agentd.exe [-c arquivo-de-configuração] -t chave-do-item
zabbix_agentd.exe [-c arquivo-de-configuração] -i [-m]
zabbix_agentd.exe [-c arquivo-de-configuração] -d [-m]
zabbix_agentd.exe [-c arquivo-de-configuração] -s [-m]
zabbix_agentd.exe [-c arquivo-de-configuração] -x [-m]
zabbix_agentd.exe -h
zabbix_agentd.exe -V
Os parâmetros a seguir podem ser utilizados.
Options:
-c --config <arquivo> caminho absoluto (completo) para o arquivo de configuração (o padrão é c
-h --help apresenta o help de parâmetros
43
-V --version apresenta o número de versão
-p --print apresenta todos os itens (chaves) possíveis
-t --test <chave do item> testa um item específico e retorna o resultado
Functions:
-i --install Instala o serviço do agente Zabbix
-d --uninstall Desinstala o serviço do agente Zabbis
-s --start Inicia o serviço do agente Zabbix
-x --stop Finaliza o serviço do agente Zabbix
-m --multiple-agents Nome do serviço com o hostname
Arquivo de configuração
Veja o manual do arquivo de configuração para detalhes de opções de configuração do agente Zabbix no Windows.
Códigos de saída
Antes da versão 2.2 do Zabbix o agente retornava 0 em caso de sucesso e 255 em caso de falha. A partir desta versão o agente
passou a retornar 0 para sucesso e 1 para falha.
Runtime control
With runtime control options you may change the log level of agent processes.
Option Description Target
log_level_increase[=<target>] Increase log level. Target can be specified as:
If target is not specified, all processes are affected. process type - all processes
of specified type (e.g., listener)
See all agent process types.
process type,N - process
type and number (e.g.,
listener,3)
pid - process identifier (1 to
65535). For larger values
specify target as
’process-type,N’.
log_level_decrease[=<target>] Decrease log level.
If target is not specified, all processes are affected.
userparameter_reload Reload user parameters from the current configuration
file.
Note that UserParameter is the only agent configuration
option that will be reloaded.
Examples:
• increasing log level of all processes
• increasing log level of the third listener process
• increasing log level of process with PID 1234
• decreasing log level of all active check processes
shell> zabbix_agentd -R log_level_increase
shell> zabbix_agentd -R log_level_increase=listener,3
shell> zabbix_agentd -R log_level_increase=1234
shell> zabbix_agentd -R log_level_decrease="active checks"
Note:
Runtime control is not supported on OpenBSD, NetBSD and Windows.
Agent process types
• active checks - process for performing active checks
• collector - process for data collection
• listener - process for listening to passive checks
The agent log file can be used to observe these process types.
Process user
44
Zabbix agent on UNIX is designed to run as a non-root user. It will run as whatever non-root user it is started as. So you can run
agent as any non-root user without any issues.
If you will try to run it as ’root’, it will switch to a hardcoded ’zabbix’ user, which must be present on your system. You can only run
agent as ’root’ if you modify the ’AllowRoot’ parameter in the agent configuration file accordingly.
Configuration file
For details on configuring Zabbix agent see the configuration file options for zabbix_agentd or Windows agent.
Locale
Note that the agent requires a UTF-8 locale so that some textual agent items can return the expected content. Most modern
Unix-like systems have a UTF-8 locale as default, however, there are some systems where that may need to be set specifically.
Exit code
Before version 2.2 Zabbix agent returned 0 in case of successful exit and 255 in case of failure. Starting from version 2.2 and
higher Zabbix agent returns 0 in case of successful exit and 1 in case of failure.
4 Proxy
Visão geral
O Zabbix Proxy é um processo que pode receber dados de um ou mais dispositivos monitorados e enviar ao Zabbix Server,
basicamente ele funciona em nome do Zabbix Server (na visão do agente monitorado o Proxy passa a ser o Zabbix Server). Todo
os dados recebidos são armazenados temporariamente (buferizados), transferidos ao Zabbix Server que o Zabbix Proxy pertencer,
sendo excluídos na sequência do armazenamento temporário do Proxy.
A utilização deste componente é opcional, mas normalmente é muito benéfica pois distribui a carga de monitoração normalmente
atribuída ao Zabbix Server. Se toda a coleta de dados for feita através de Proxies o uso de CPU e de I/O no servidor responsável
pelo Zabbix Server reduz significativamente.
O Zabbix Proxy é a solução ideal para a monitoração centralizada de localidades geograficamente dispersas e para redes gerenci-
adas remotamente.
O Zabbix Proxy requer um banco de dados em separado (normalmente um SQLite).
Attention:
Observe que o Proxy suporta SQLite, MySQL e PostgreSQL. O uso de Oracle ou IBM DB2 neste componente é uma escolha
com riscos e limitações seus, exemplos podem ser encontrados em retorno de valores regras de autobusca.
Veja também: Usando Proxies em ambientes distribuídos
Processo do Proxy
O Zabbix Proxy é executado como um processo de background (Daemon). O proxy pode ser iniciado ao executar:
shell> cd sbin
shell> ./zabbix_proxy
Você pode utilizar alguns parâmetros com o Zabbix Proxy:
-c --config <arquivo> caminho absoluto (completo) para o arquivo de configuração (o padrão é /et
-R --runtime-control <opção> executa funções administrativas
-h --help apresenta o help de parâmetros
-V --version apresenta o número de versão
Note:
O controle em tempo de execução não é suportado em OpenBSD e em NetBSD.
Exemplos de linha de comando com parâmetros:
shell> zabbix_proxy -c /usr/local/etc/zabbix_proxy.conf
shell> zabbix_proxy --help
shell> zabbix_proxy -V
45
Se instalado como pacote
Zabbix proxy roda como um processo em segundo plano. O proxy pode ser iniciado executando: service zabbix-proxy start
Isso funcionará na maioria dos sistemas GNU/Linux. Em alguns sistemas você pode necessitar executar:
/etc/init.d/zabbix-proxy start
De forma semelhante, para parar/reiniciar/ver status do Zabbix proxy, utilize os seguintes comandos:
service zabbix-proxy stop service zabbix-proxy restart service zabbix-proxy status
Processo de usuário
O Zabbix Proxy foi desenhado para ser executado como um processo ”não-root”. Ele pode ser executado com a permissão do
usuário que o iniciou. Neste cenário ele irá executar sem nenhum problema.
Se você tentar inicia-lo com o usuário ’root’, ele irá alternar seu permissionamento de execução para o usuário ’zabbix’, que deverá
existir em seu ambiente. Você só poderá rodar o Zabbix Proxy como ’root’ se modificar o parâmetro ’AllowRoot’ no arquivo de
configuração.
Arquivo de configuração
Veja as opções do arquivo de configuração para detalhes sobre sua configuração.
Scripts de inicialização
Os scripts são utilizados para iniciar automaticamente os processos do Zabbix Proxy durante o processo de inicialização e finaliza-
ção da máquina. Atualmente (29/11/15) estes scripts não vem junto com o código fonte da solução mas são facilmente obtidos
através da cópia e edição dos scripts do Zabbix Server localizados no diretório misc/init.d do código fonte da solução.
Plataformas suportadas
Devido aos requisitos de segurança e a natureza de missão crítica do funcionamento do Zabbix Proxy, o UNIX é o único sistema
operacional que pode entregar de forma consistente o desempenho, tolerância a falhas e resiliência necessários. O Zabbix opera
como uma das soluções líderes de mercado.
O Zabbix Proxy é testado nas seguintes plataformas:
• Linux
• Solaris
• AIX
• HP-UX
• Mac OS X
• FreeBSD
• OpenBSD
• NetBSD
• SCO Open Server
• Tru64/OSF1
Note:
O Zabbix pode funcionar em outros sistemas operacionais baseados no UNIX.
Proxy process types
• availability manager - process for host availability updates
• configuration syncer - process for managing in-memory cache of configuration data
• data sender - proxy data sender
• discoverer - process for discovery of devices
• heartbeat sender - proxy heartbeat sender
• history poller - process for handling calculated, aggregated and internal checks requiring a database connection
• history syncer - history DB writer
• housekeeper - process for removal of old historical data
• http poller - web monitoring poller
• icmp pinger - poller for icmpping checks
• ipmi manager - IPMI poller manager
• ipmi poller - poller for IPMI checks
• java poller - poller for Java checks
• poller - normal poller for passive checks
• preprocessing manager - manager of preprocessing tasks
• preprocessing worker - process for data preprocessing
46
• self-monitoring - process for collecting internal server statistics
• snmp trapper - trapper for SNMP traps
• task manager - process for remote execution of tasks requested by other components (e.g. close problem, acknowledge
problem, check item value now, remote command functionality)
• trapper - trapper for active checks, traps, proxy communication
• unreachable poller - poller for unreachable devices
• vmware collector - VMware data collector responsible for data gathering from VMware services
The proxy log file can be used to observe these process types.
Various types of Zabbix proxy processes can be monitored using the zabbix[process,<type>,<mode>,<state>] internal item.
Supported platforms
Zabbix proxy runs on the same list of server#supported platforms as Zabbix server.
Locale
Note that the proxy requires a UTF-8 locale so that some textual items can be interpreted correctly. Most modern Unix-like systems
have a UTF-8 locale as default, however, there are some systems where that may need to be set specifically.
5 Java gateway
Visão geral
O Zabbix 2.0 inovou com o suporte nativo ao monitoramento de aplicações Java através de JMX, este suporte foi adicionado através
do componente ”Zabbix Java Gateway”. Ele é um processo de background (daemon) escrito em Java. Quando o Zabbix Server
precisa coletar um item (dado) através de um contador JMX em um host, ele solicita ao Zabbix Java Gateway, que utiliza a API de
gerência JMX para requisitar da aplicação o dado de interesse. A aplicação não precisa de softwares adicionais, apenas necessita
ter sido iniciada com a opção -[Link] no momento de sua inicialização (linha de comando).
O Zabbix Java Gateway aceita conexões oriundas do Zabbix Server e do Zabbix Proxy e só pode ser utilizado como um ”proxy
passivo”. Ao contrário do que ocorre com um Zabbix Proxy o Zabbix Java Gateway pode estar atrás de outro proxy (um Zabbix
Proxy). O acesso a cada Zabbix Java Gateway é configurado diretamente no arquivo de configuração do Zabbix Server ou do Zabbix
Proxy e só pode existir um Zabbix Java Gateway por Zabbix Server ou Zabbix Proxy. Se você precisar de ter mais de um Zabbix
Java Gateway em um mesmo ambiente da solução Zabbix você precisará configurar um novo Zabbix Proxy para cada Zabbix Java
Gateway. Se um host possuir itens do tipo JMX agent e itens de outros tipos, apenas os itens do tipo JMX agent serão solicitados
ao Zabbix Java Gateway.
O Zabbix Java Gateway não faz cache de nenhum valor coletado.
O Zabbix Server ou Zabbix Proxy tem um processo específico para se conectar ao Zabbix Java Gateway, controlado pela opção
StartJavaPollers. Internamente o Zabbix Java Gateway inicia múltiplas threads, controladas pela opção START_POLLERS. No
lado do servidor, se a conexão demorar mais do que o limite em segundos da opção Timeout, a requisição será terminada
(abortada), mas o Zabbix Java Gateway continuará aguardando pela coleta do contador JMX. Para resolver isso, desde o Zabbix
2.0.15, Zabbix 2.2.10 e Zabbix 2.4.5 foi adicionada a opção TIMEOUT no Zabbix Java Gateway que permite definir o tempo máximo
para as operações remotas do JMX.
O Zabbix Server ou o Zabbix Proxy irá agrupar as requisições em uma única requisição JMX, sempre que possível (é afetado pelos
intervalos entre coletas), e enviar para o Zabbix Java Gateway em uma única conexão visando obter melhor performance.
É recomendável configurar a opção StartJavaPollers com valor menor ou igual à opção START_POLLERS, de outra forma existirão
situações onde não existirão trheads disponíveis para atender às requisições.
A sessão abaixo descreve como obter e como executar o Zabbix Java Gateway, como configurar o Zabbix Server (ou Zabbix Proxy)
para usar o Zabbix Java Gateway para monitoração JMX, e como configurar os itens do Zabbix em sua interface web para coletar
um contador JMX específico.
When an item has to be updated over Java gateway, Zabbix server or proxy will connect to the Java gateway and request the value,
which Java gateway in turn retrieves and passes back to the server or proxy. As such, Java gateway does not cache any values.
Zabbix server or proxy has a specific type of processes that connect to Java gateway, controlled by the option StartJavaPollers.
Internally, Java gateway starts multiple threads, controlled by the START_POLLERS option. On the server side, if a connection
takes more than Timeout seconds, it will be terminated, but Java gateway might still be busy retrieving value from the JMX counter.
To solve this, there is the TIMEOUT option in Java gateway that allows to set timeout for JMX network operations.
Zabbix server or proxy will try to pool requests to a single JMX target together as much as possible (affected by item intervals) and
send them to the Java gateway in a single connection for better performance.
47
It is suggested to have StartJavaPollers less than or equal to START_POLLERS, otherwise there might be situations when no
threads are available in the Java gateway to service incoming requests; in such a case Java gateway uses ThreadPoolExecu-
[Link], meaning that the main thread will service the incoming request and temporarilylabel will not accept any
new requests.
If you are trying to monitor Wildfly-based Java applications with Zabbix Java gateway, please install the latest [Link]
available on the Wildfly download page.
Obtendo o gateway Java
Você pode instalar o gateway Java a partir das fontes ou pacotes baixado do Zabbix website.
Usando os links abaixo, você pode acessar informações sobre como obter e executar Zabbix Java gateway, como configurar o
servidor Zabbix (ou proxy Zabbix) para utilizr Zabbix Java gateway para monitoramento JMX, e como configurar os items Zabbix
com contadores correspondentes ao JMX .
Instalação a partir de Instruções Instruções
Fontes Instalação Configuração
pacotes RHEL/CentOS Instalação Configuração
pacotes Debian/Ubuntu Instalação Configuração
1 Setup from sources
Visão geral
SeInstalado a partir de fontes, as seguintes informações irão ajudá-lo a configurar Zabbix Java gateway.
Overview of files
If you obtained Java gateway from sources, you should have ended up with a collection of shell scripts, JAR and configuration files
under $PREFIX/sbin/zabbix_java. The role of these files is summarized below.
bin/zabbix-java-gateway-$[Link]
Java gateway JAR file itself.
lib/[Link]
lib/[Link]
lib/[Link]
lib/android-json-4.3_r3.[Link]
Dependencies of Java gateway: Logback, SLF4J, and Android JSON library.
lib/[Link]
lib/[Link]
Configuration files for Logback.
[Link]
[Link]
Convenience scripts for starting and stopping Java gateway.
[Link]
Configuration file that is sourced by startup and shutdown scripts above.
Configuring and running Java gateway
By default, Java gateway listens on port 10052. If you plan on running Java gateway on a different port, you can specify that in
[Link] script. See the description of Java gateway configuration file for how to specify this and other options.
Warning:
Port 10052 is not IANA registered.
Once you are comfortable with the settings, you can start Java gateway by running the startup script:
$ ./[Link]
Likewise, once you no longer need Java gateway, run the shutdown script to stop it:
$ ./[Link]
48
Note that unlike server or proxy, Java gateway is lightweight and does not need a database.
Configuring server for use with Java gateway
With Java gateway up and running, you have to tell Zabbix server where to find Zabbix Java gateway. This is done by specifying
JavaGateway and JavaGatewayPort parameters in the server configuration file. If the host on which JMX application is running is
monitored by Zabbix proxy, then you specify the connection parameters in the proxy configuration file instead.
JavaGateway=[Link]
JavaGatewayPort=10052
By default, server does not start any processes related to JMX monitoring. If you wish to use it, however, you have to specify the
number of pre-forked instances of Java pollers. You do this in the same way you specify regular pollers and trappers.
StartJavaPollers=5
Do not forget to restart server or proxy, once you are done with configuring them.
Debugging Java gateway
In case there are any problems with Java gateway or an error message that you see about an item in the frontend is not descriptive
enough, you might wish to take a look at Java gateway log file.
By default, Java gateway logs its activities into /tmp/zabbix_java.log file with log level ”info”. Sometimes that information is not
enough and there is a need for information at log level ”debug”. In order to increase logging level, modify file lib/[Link] and
change the level attribute of <root> tag to ”debug”:
<root level="debug">
<appender-ref ref="FILE" />
</root>
Note that unlike Zabbix server or Zabbix proxy, there is no need to restart Zabbix Java gateway after changing [Link] file -
changes in [Link] will be picked up automatically. When you are done with debugging, you can return the logging level to
”info”.
If you wish to log to a different file or a completely different medium like database, adjust [Link] file to meet your needs.
See Logback Manual for more details.
Sometimes for debugging purposes it is useful to start Java gateway as a console application rather than a daemon. To do that,
comment out PID_FILE variable in [Link]. If PID_FILE is omitted, [Link] script starts Java gateway as a console application
and makes Logback use lib/[Link] file instead, which not only logs to console, but has logging level ”debug” enabled
as well.
Finally, note that since Java gateway uses SLF4J for logging, you can replace Logback with the framework of your choice by placing
an appropriate JAR file in lib directory. See SLF4J Manual for more details.
JMX monitoring
See JMX monitoring page for more details.
2 Configuração a partir de pacotes RHEL
Visão geral
Se você tiver instalado installed a partir de pacotes RHEL, a informação seguinte te ajudará na configuração do Zabbix Java
gateway.
Configurar e executar Java gateway
Os parâmetros de configuração do Java gateway do Zabbix podem ser ajustados no arquivo:
/etc/zabbix/zabbix_java_gateway.conf
Para mais detalhes, ver configuração do Java gateway do Zabbix parameters.
Para iniciar o Java gateway do Zabbix:
service zabbix-java-gateway restart
Para iniciar o Java gateway do Zabbix automaticamente na inicialização:
RHEL 7 e depois:
systemctl enable zabbix-java-gateway
RHEL anterior à versão 7:
49
chkconfig --level 12345 zabbix-java-gateway on
Configurar o servidor para uso com Java gateway
Com o Java gateway instalado e rodando, você precisa informar ao servidor Zabbix onde encontrar o Java gateway Zabbix. Isso
é feito especificando os parâmetros JavaGateway e JavaGatewayPort na configuração do servidor server configuration file. Se o
host na qual a aplicação JMX estiver em execução e estiver sendo monitorado pelo Zabbix proxy, então você deve especificar os
parâmetros de conexão na configuração proxy configuration file.
JavaGateway=[Link]
JavaGatewayPort=10052
Por padrão, o servidor não inicia nenhum processo relacionado ao monitoramento JMX. Contudo, caso você deseje usá-lo, você
deve espeficiar o número de instâncias pre-forked do Java pollers. Você faz isso da mesma forma que você específica os pollers e
trappers regulares.
StartJavaPollers=5
Não esqueça de reiniciar o servidor ou proxy depois de terminar de configurá-los.
Debugar Java gateway
O arquivo de registo do Zabbix Java gateway é:
/var/log/zabbix/zabbix_java_gateway.log
Se você deseja aumentar o registro, edite o arquivo:
/etc/zabbix/zabbix_java_gateway_logback.xml
e mude level="info" para ”debug” ou até mesmo ”trace” (para solução detalhada):
<configuration scan="true" scanPeriod="15 seconds">
[...]
<root level="info">
<appender-ref ref="FILE" />
</root>
</configuration>
Monitorar JMX
Ver página JMX monitoring para mais detalhes.
3 Setup from Debian/Ubuntu packages
Visão geral
Se Instalação via pacotes Debian/Ubuntu , tas seguintes informações irão ajudá-lo a configurando o Zabbix Java gateway.
Configuring and running Java gateway
Java gateway configuration may be tuned in the file:
/etc/zabbix/zabbix_java_gateway.conf
For more details, see Zabbix Java gateway configuration parameters.
To start Zabbix Java gateway:
# service zabbix-java-gateway restart
To automatically start Zabbix Java gateway on boot:
# systemctl enable zabbix-java-gateway
Configuring server for use with Java gateway
With Java gateway up and running, you have to tell Zabbix server where to find Zabbix Java gateway. This is done by specifying
JavaGateway and JavaGatewayPort parameters in the server configuration file. If the host on which JMX application is running is
monitored by Zabbix proxy, then you specify the connection parameters in the proxy configuration file instead.
JavaGateway=[Link]
JavaGatewayPort=10052
50
By default, server does not start any processes related to JMX monitoring. If you wish to use it, however, you have to specify the
number of pre-forked instances of Java pollers. You do this in the same way you specify regular pollers and trappers.
StartJavaPollers=5
Do not forget to restart server or proxy, once you are done with configuring them.
Debugging Java gateway
Zabbix Java gateway log file is:
/var/log/zabbix/zabbix_java_gateway.log
If you like to increase the logging, edit the file:
/etc/zabbix/zabbix_java_gateway_logback.xml
and change level="info" to ”debug” or even ”trace” (for deep troubleshooting):
<configuration scan="true" scanPeriod="15 seconds">
[...]
<root level="info">
<appender-ref ref="FILE" />
</root>
</configuration>
JMX monitoring
See JMX monitoring page for more details.
6 Sender
Visão geral
O Zabbix Sender é um utilitário de linha de comando que pode ser usado para enviar dados de performance ao Zabbix Server para
processamento.
O utilitário é comumente usado em scripts de usuário de longa execução para envio periódico de dados de disponibilidade e
performance.
Para envio de resultados diretamente para o Zabbix Server ou Proxy, um item do tipo gatilho deve ser configurado.
Executando o Zabbix Sender
Um exemplo de execução do Zabbix Sender no UNIX:
shell> cd bin
shell> ./zabbix_sender -z zabbix -s "Linux DB3" -k [Link] -o 43
onde:
• z - host do Zabbix Server (endereço IP também pode ser usado)
• s - nome técnico do host monitorado (como registrado no Zabbix Frontend (interface web))
• k - chave de item
• o - valor para envio
Attention:
Opções que contêm espaços em branco, devem ser quotadas com aspas duplas.
O Zabbix Sender pode ser usado para enviar múltiplos valores a partir de um arquivo de entrada. Consulte a página principal do
Zabbix Sender para mais informações.
Se um arquivo de configuração é especificado, o Zabbix Sender usa todos os endereços definidos no parâmetro de configuração
ServerActive do agente para o envio de dados. Se o envio para um destes endereços falhar, o Sender tenta enviar para os outros
endereços. Se o envio de um conjunto de dados falhar para um endereço, o conjunto seguinte não é enviado para este endereço.
O Zabbix Sender aceita strings com codificação UTF-8 (para ambos os sistemas baseados em UNIX e Windows) sem ’byte order
mark (BOM)’ em primeiro no arquivo.
Zabbix Sender no Windows pode ser executado de forma similar:
51
zabbix_sender.exe [options]
Desde o Zabbix 1.8.4, os cenários de envio em tempo real do zabbix_sender foram aperfeiçoados para reunir múltiplos valores
passados a ele em sucessão próxima e enviá-los para o Server em uma única conexão. Um valor que não esteja distante mais do
que 0.2 segundos do valor anterior pode ser colocado na mesma pilha, mas o tempo máximo de agrupamento (pooling) ainda é
de 1 segundo.
Note:
O Zabbix Sender terminará se um parâmetro inválido (não seguindo a notação parâmetro=valor) estiver presente no
arquivos de configuração especificado.
7 Get
Visão geral
O Zabbix Get é um utilitário de linha de comando que pode ser usado para se comunicar com o Zabbix Agent e recuperar uma
informação requerida do agente.
Este utilitário é comumente utilizado para resolução de problemas nos Zabbix Agents.
Execução do Zabbix Get
Um exemplo de execução do Zabbix Get em UNIX para obter do agente o valor de carga de processador:
shell> cd bin
shell> ./zabbix_get -s [Link] -p 10050 -k [Link][all,avg1]
Um outro exemplo de execução do Zabbix Get para captura de uma string de um website:
shell> cd bin
shell> ./zabbix_get -s [Link] -p 10050 -k "[Link][[Link],,,\"USA: ([a-zA-Z0-9.-]+)\
Note que a chave de item aqui contém um espaço então aspas são usadas para destacar a chave do item no shell. As aspas não
fazem parte da chave do item; Elas serão removidas pelo shell e não será passadas para o Zabbix Agent.
O Zabbix Get aceita os seguintes parâmetros de linha de comando:
-s --host <nome do host ou IP> Especifica nome de host ou endereço IP de um host.
-p --port <número de porta> Especifica o número de porta do agente em execução no host. Padrão é 10
-I --source-address <endereço IP Especifica endereço IP de origem.
-t --timeout <segundos> Especifica limite de tempo (timeout). Intervalo válido: 1-30 segundos (
-k --key <chave do item> Especifica chave de item da qual obter valor.
-h --help Apresenta esta ajuda.
-V --version Exibe número da versão.
Veja também a página principal do Zabbix Get para mais informações.
O Zabbix Get no Windows pode ser executado de forma similar a:
zabbix_get.exe [options]
8 JS
Visão geral
O zabbix_js é um utilitário de linha de comando que pode ser usado para teste de script embutido.
Este utilitário executará um script de usuário com um parâmetro de string e apresentará os resultados. Os scripts são executados
usando o mecanismo embutido Zabbix Scripting.
No caso de erros de compilação ou execução o zabbix_js apresentará o erro na saída stderr e sairá com código 1.
Utilização
zabbix_js -s arquivo-script -p param-entrada [-l nível-log] [-t tempo-limite]
zabbix_js -s arquivo-script -i arquivo-entrada [-l nível-log] [-t tempo-limite]
zabbix_js -h
52
zabbix_js -V
O zabbix_js aceita os seguintes parâmetros de linha de comando:
-s, --script arquivo-script Especifica o nome de arquivo do script a executar. Se '-' for especifi
-i, --input input-file Especifica o nome de arquivo do parâmetro de entrada. Se '-' for espec
-p, --param input-param Especifica o parâmetro de entrada.
-l, --loglevel log-level Especifica o nível de log.
-t, --timeout timeout Especifica o tempo limite em segundos.
-h, --help Exibe informação de ajuda.
-V, --version Exibe o número de versão.
Exemplo:
zabbix_js -s [Link] -p exemplo
9 Serviço Web
Visão Geral
O serviço web Zabbix é um processo que é usado para comunicação com serviços web externos. Atualmente, o serviço web Zabbix
é usado para gerar e enviar relatórios programados com planos para adicionar funcionalidade no futuro.
O servidor Zabbix se conecta ao serviço web via HTTP(S). O serviço web do Zabbix que o Google Chrome seja instalado no mesmo
host; em alguns distribuições o serviço também pode funcionar com o Chromium (consulte dúvidas frequentes) .
Instalação
O serviço web Zabbix está disponível em pacotes Zabbix pré-compilados disponível para download em Zabbix site. Para compilar
Zabbix web serviço de fontes, especifique a opção de configuração --enable-webservice.
Veja também:
• Opções de arquivo de configuração para zabbix_web_service;
• Configurando relatórios programadoss
4. Instalação
Por favor, utilize a barra lateral para acessar o conteúdo disponível na seção de Instalação.
1 Obtendo o Zabbix
Visão geral
Há quatro formas de obter o Zabbix:
• Instale-o através dos pacotes de distribuição
• Baixe o arquivo fonte mais recente e o compile você mesmo
• Instale a partir dos contêineres
• Baixe a aplicação virtual
Para baixar os pacotes de distribuição mais recentes, fontes pré-compilados ou a aplicação virtual, acesse a página de download
do Zabbix, onde links diretos para as versões mais recentes são disponilizados.
Obtendo código fonte do Zabbix
Há várias maneiras de obter o código fonte do Zabbix:
• Você pode baixar as versões estáveis publicadas no site oficial da Zabbix
• Você pode baixar compilações noturnas da página oficial do desenvolvedor Zabbix
• Você pode obter a versão de desenvolvimento mais recente no repositório de códigos do Git:
– A principal localização do repositório completo está em [Link]
– As versões Master e demais publicações suportadas também são espelhadas para o Github em [Link]
zabbix/zabbix
53
Um cliente Git deve ser instalado para clonar o repositório. O pacote do cliente de linha de comando oficial é comumente chamado
git nas distribuições. Para instalar, por exemplo, no Debian/Ubuntu, execute:
sudo apt-get update
sudo apt-get install git
Para pegar todo o código do Zabbix, mude para o diretório onde você deseja gravar o código e execute:
git clone [Link]
2 Requisitos
Hardware
Memória
O Zabbix requer memória física e de disco. A quantidade de memória de disco necessária obviamente depende do número de
hosts e parâmetros que estão sendo monitorados. Se você planeja manter um longo histórico de parâmetros monitorados, deve
pensar em pelo menos alguns gigabytes para ter espaço suficiente para armazenar o histórico no banco de dados. Cada processo
do Zabbix daemon requer várias conexões ao servidor de banco de dados. A quantidade de memória alocada para a conexão
depende da configuração do mecanismo de banco de dados.
Note:
Quanto mais memória física você tiver, mais rápido o banco de dados (e, portanto, o Zabbix) funcionará.
CPU
O Zabbix e, especialmente, o banco de dados do Zabbix pode requerer recursos de CPU significativos dependendo do número de
parâmetros monitorados e o mecanismo de banco de dados selecionada.
Outro hardware
A porta de comunicação serial e o modem serial GSM são necessários para utilizar o suporte de notificação por SMS no Zabbix. O
conversor USB para serial também funcionará.
Examples of hardware configuration
The table provides examples of hardware configuration, assuming a Linux/BSD/Unix platform.
These are size and hardware configuration examples to start with. Each Zabbix installation is unique. Make sure to benchmark the
performance of your Zabbix system in a staging or development environment, so that you can fully understand your requirements
before deploying the Zabbix installation to its production environment.
Monitored Memory
1 2
Installation size metrics CPU/vCPU cores (GiB) Database Amazon EC2
Small 1 000 2 8 MySQL Server, [Link]/[Link]
Percona Server,
MariaDB Server,
PostgreSQL
Medium 10 000 4 16 MySQL Server, [Link]/[Link]
Percona Server,
MariaDB Server,
PostgreSQL
Large 100 000 16 64 MySQL Server, m6i.4xlarge/m6g.4xlarge
Percona Server,
MariaDB Server,
PostgreSQL,
Oracle
Very large 1 000 000 32 96 MySQL Server, m6i.8xlarge/m6g.8xlarge
Percona Server,
MariaDB Server,
PostgreSQL,
Oracle
54
1 2
1 metric = 1 item + 1 trigger + 1 graph<br> Example with Amazon general purpose EC2 instances, using ARM64 or x86_64
architecture, a proper instance type like Compute/Memory/Storage optimised should be selected during Zabbix installation evalu-
ation and testing before installing in its production environment.
Note:
Actual configuration depends on the number of active items and refresh rates very much (see database size section of this
page for details). It is highly recommended to run the database on a separate box for large installations.
Plataformas suportadas
Devido a requisitos de segurança e a natureza crítica do servidor de monitoramento, o UNIX é o único sistema operacional que
consegue fornecer consistentemente a performance, tolerância a falhas e resiliência necessárias. O Zabbix opera em versões
líderes de mercado.
Os componentes do Zabbix estão disponíveis e foram testados para as seguintes plataformas:
Plataforma Servidor Agente Agente2
Linux x x x
IBM AIX x x -
FreeBSD x x -
NetBSD x x -
OpenBSD x x -
HP-UX x x -
Mac OS X x x -
Solaris x x -
Windows - x x
Note:
O servidor Zabbix/agente Zabbix pode funcionar em outros sistemas operacionais baseados em Unix. O agente Zabbix é
suportado em todos os Windows versão desktop e versões de servidor desde o XP.
Attention:
O Zabbix desabilita os core dumps se compilado com criptografia e não inicia se o sistema não permitir a desativação dos
core dumps.
Software necessário
O Zabbix é construído em torno de servidores web modernos, principais mecanismos de banco de dados e linguagem de progra-
mação PHP.
Third-party external surrounding software
Mandatory requirements are needed always. Optional requirements are needed for the support of the specific function.
Mandatory Supported
Software status versions Comments
MySQL/Percona One of 8.0.X Required if MySQL (or Percona) is used as Zabbix backend database.
InnoDB engine is required. We recommend using the MariaDB
Connector/C library for building server/proxy.
MariaDB 10.5.00- InnoDB engine is required. We recommend using the MariaDB
10.8.X Connector/C library for building server/proxy.
Oracle 19c - 21c Required if Oracle is used as Zabbix backend database.
PostgreSQL 13.0-14.X Required if PostgreSQL is used as Zabbix backend database.
TimescaleDB for 2.0.1-2.7 Required if TimescaleDB is used as a PostgreSQL database
PostgreSQL extension. Make sure to install TimescaleDB Community Edition,
which supports compression.
SQLite Optional 3.3.5- SQLite is only supported with Zabbix proxies. Required if SQLite is
3.34.X used as Zabbix proxy database.
smartmontools 7.1 or later Required for Zabbix agent 2.
who Required for the user count plugin.
dpkg Required for the [Link] plugin.
pkgtool Required for the [Link] plugin.
55
Mandatory Supported
Software status versions Comments
rpm Required for the [Link] plugin.
pacman Required for the [Link] plugin.
Note:
Although Zabbix can work with databases available in the operating systems, for the best experience, we recommend
using databases installed from the official database developer repositories.
Frontend
A largura mínima de tela suportada para o frontend Zabbix é 1200px.
Software Versão Comentários
Apache 1.3.12 ou posterior
PHP 7.2.5 ou posterior O PHP 8.0 não é suportado.
Extensões do PHP
gd 2.0.28 ou posterior A extensão PHP GD deve suportar
imagens PNG (--with-png-dir), JPEG
(--with-jpeg-dir) e FreeType 2
(--with-freetype-dir).
bcmath php-bcmath (--enable-bcmath)
ctype php-ctype (--enable-ctype)
libXML 2.6.15 ou posterior php-xml, se fornecido como um pacote
separado pelo distribuidor.
xmlreader php-xmlreader, se fornecido como um
pacote separado pelo distribuidor.
xmlwriter php-xmlwriter, se fornecido como um
pacote separado pelo distribuidor.
session php-session, se fornecido como um
pacote separado pelo distribuidor.
sockets php-net-socket (--enable-sockets).
Necessário para suporte ao script de
usuário.
mbstring php-mbstring (--enable-mbstring)
gettext php-gettext (--with-gettext). Necessário
para que as traduções funcionem.
ldap php-ldap. Necessário somente se a
autenticação por LDAP for utilizada no
frontend.
openssl php-openssl. Necessário somente se a
autenticação por SAML for utilizada no
frontend.
mysqli Necessário se o MySQL for utilizado como
banco de dados no backend do Zabbix.
oci8 Necessário se o Oracle for utilizado como
banco de dados no backend do Zabbix.
pgsql Necessário se o PostgreSQL for utilizado
como banco de dados no backend do
Zabbix.
Note:
O Zabbix também pode funcionar em versões anteriores do Apache, MySQL, Oracle e PostgreSQL.
Attention:
Para outras fontes além do padrão DejaVu, a função do PHP imagerotate pode ser necessária. Se estiver ausente, essas
fontes podem ser renderizadas incorretamente quando um gráfico é exibido. Esta função só está disponível se o PHP for
compilado com GD empacotado, o que não é o caso no Debian e outros distribuições.
56
Navegador da web no lado do cliente
Os Cookies e o JavaScript devem estar habilitados.
As últimas versões estáveis do Google Chrome, Mozilla Firefox, Microsoft Edge, Apple Safari e Opera são suportadas.
Warning:
A política de mesma origem para os IFrames é implementada, o que significa que o Zabbix não pode ser inserido em
frames em domínio diferente.
Ainda assim, as páginas colocadas em um frame do Zabbix terão acesso ao Zabbix frontend (através
de JavaScript) se a página que é inserida no frame e o frontend do Zabbix estiverem no mesmo
domínio. [Link]
Uma página como se inserida nos dashboards em
[Link] terá o total acesso JS ao Zabbix.
Servidor
Requisitos obrigatórios são necessários sempre. Os requisitos opcionais são necessários para o suporte da função específica.
Requisito Status Descrição
libpcre Obrigatório A biblioteca PCRE é necessária para suporte
ao Perl Compatible Regular Expression (PCRE).
A nomenclatura pode diferir dependendo da
distribuição GNU/Linux, por exemplo ’libpcre3’
ou ’libpcre1’. PCRE v8.x e PCRE2 v10.x (do
Zabbix 6.0.0) são suportados.
libevent Necessário para suporte de métrica em massa
e monitoramento de IPMI. Versão 1.4 ou
superior.
Observe que para o proxy Zabbix este
requisito é opcional; é necessário para
suporte de monitoramento IPMI.
libpthread Required for mutex and read-write lock
support.
zlib Necessário para o suporte a compressão.
OpenIPMI Optional Necessário para suporte IPMI.
libssh2 or libssh Necessário para SSH checks. Versão 1.0 ou
superior (libssh2); 0.6.0 ou superior (libssh).
libssh é suportado desde o Zabbix 4.4.6.
fping Necessário para ICMP ping items.
libcurl Necessário para monitoramento web,
monitoramento VMware, autenticação SMTP,
[Link].* items do agente Zabbix, itens
do agente HTTP e Elasticsearch (se utilizado).
Recomendado versão 7.28.0 ou superior.
Requisitos da versão do Libcurl:
- Autenticação SMTP: versão 7.20.0 ou superior
- Elasticsearch: versão 7.28.0 ou superior
libxml2 Necessário para monitoramento VMware e
pré-processamento XML XPath.
net-snmp Necessário para suporte SNMP. Versão 5.3.0
ou superior.
GnuTLS, OpenSSL ou LibreSSL Necessário ao utilizar encryption.
Agente
57
Requisito Status Descrição
libpcre Obrigatório A biblioteca PCRE é obrigatória para suporte
ao Perl Compatible Regular Expression (PCRE).
A nomenclatura pode diferir dependendo da
distribuição GNU/Linux, por exemplo ’libpcre3’
ou ’libpcre1’. PCRE [Link] PCRE2 v10.x (do
Zabbix 6.0.0) são suportados.
GnuTLS, OpenSSL ou LibreSSL Opcional Necessário ao utilizar encryption.
Em sistemas Microsoft Windows é necessário
OpenSSL 1.1.1 ou posterior.
Note:
A partir da versão 5.0.3, o agente Zabbix não funcionará em plataformas AIX inferior as versões 6.1 TL07 / AIX 7.1 TL01.
Agent 2
Requisito Status Descrição
libpcre Obrigatório A biblioteca PCRE é obrigatória para suporte
ao Perl Compatible Regular Expression (PCRE).
A nomenclatura pode diferir dependendo da
distribuição GNU/Linux, por exemplo ’libpcre3’
ou ’libpcre1’. PCRE [Link] PCRE2 v10.x (do
Zabbix 6.0.0) são suportados.
OpenSSL Opcional Necessário ao usar criptografia.
OpenSSL 1.0.1 ou posterior é necessário em
plataformas UNIX.
A biblioteca OpenSSL deve ter o suporte PSK
ativado. O LibreSSL não é suportado.
Nos sistemas Microsoft Windows, o OpenSSL
1.1.1 ou posterior é necessário.
Java gateway
Se você obteve o Zabbix do repositório de origem ou de um arquivo, então as dependências necessárias já estão incluídas na
árvore de origem.
Se você obteve o Zabbix do pacote de sua distribuição, então as dependências necessárias já são fornecidas pelo sistema de
empacotamento.
Em ambos os casos acima, o software está pronto para ser usado e não há downloads são necessários.
Se, no entanto, você deseja fornecer suas versões dessas dependências (por exemplo, se você estiver preparando um pacote para
alguns distribuição), abaixo está a lista de versões de biblioteca que o gateway Java é conhecido por trabalhar. O Zabbix pode
funcionar com outras versões destes bibliotecas também.
A tabela a seguir lista os arquivos JAR que estão atualmente empacotados com Java gateway no código original:
Biblioteca Licença Site Comentários
[Link] EPL 1.0, LGPL 2.1 [Link] Testado com 0.9.27, 1.0.13,
1.1.1 e 1.2.3.
[Link] EPL 1.0, LGPL 2.1 [Link] Testado com 0.9.27, 1.0.13,
1.1.1 e 1.2.3.
[Link] Licença MIT [Link] Testado com 1.6.1, 1.6.6, 1.7.6
e 1.7.30.
android-json-4.3_r3.[Link] Licença Apache 2.0 https: Testado com 2.3.3_r1.1 e
//[Link]. 4.3_r3.1. Verifique
com/platform/libcore/+/ src/zabbix_java/lib/README
master/json para instruções de criação de
arquivo JAR.
58
O Java gateway pode ser construído pode ser construído usando Oracle Java ou código aberto OpenJDK (versão 1.6 ou mais recente).
Os pacotes fornecidos pelo Zabbix são compilados usando o OpenJDK. A tabela abaixo fornece informações sobre as versões do
OpenJDK usadas para construir pacotes Zabbix por distribuição:
Distribuição Versão do OpenJDK
RHEL/CentOS 8 1.8.0
RHEL/CentOS 7 1.8.0
SLES 15 11.0.4
SLES 12 1.8.0
Debian 10 11.0.8
Ubuntu 20.04 11.0.8
Ubuntu 18.04 11.0.8
Default port numbers
The following list of open ports per component is applicable for default configuration:
Zabbix component Port number Protocol Type of connection
Zabbix agent 10050 TCP on demand
Zabbix agent 2 10050 TCP on demand
Zabbix server 10051 TCP on demand
Zabbix proxy 10051 TCP on demand
Zabbix Java gateway 10052 TCP on demand
Zabbix web service 10053 TCP on demand
Zabbix frontend 80 HTTP on demand
443 HTTPS on demand
Zabbix trapper 10051 TCP on demand
Note:
The port numbers should be open in firewall to enable Zabbix communications. Outgoing TCP connections usually do not
require explicit firewall settings.
Tamanho do banco de dados
Os dados de configuração do Zabbix requerem uma quantidade fixa de espaço em disco e não crescem muito.
O tamanho do banco de dados Zabbix depende principalmente dessas variáveis, que definem a quantidade de dados históricos
armazenados:
• Números de valores processados por segundo
Este é o número médio de novos valores que o servidor Zabbix recebe a cada segundo. Por exemplo, se tivermos 3.000 itens para
monitoramento com uma taxa de atualização de 60 segundos, o número de valores por segundo será calculado como 3.000/60 =
50.
Isso significa que 50 novos valores são adicionados ao banco de dados Zabbix a cada segundo.
• Configuração do Housekeeper para o histórico
Zabbix mantém valores por um período fixo de tempo, normalmente várias semanas ou meses. Cada novo valor requer uma certa
quantidade de espaço em disco para dados e índice.
Então, se quisermos manter 30 dias de histórico e recebermos 50 valores por segundo, o número total de valores será em torno
de (30*24*3600)* 50 = 129.600.000, ou cerca de 130M de valores.
Dependendo do mecanismo de banco de dados usado, tipo de valores recebidos (reais, inteiros, strings, arquivos de log, etc), o
espaço em disco para manter um único valor pode variar de 40 bytes a centenas de bytes. Normalmente é cerca de 90 bytes
2
por valor para itens numéricos . No nosso caso, significa que 130M de valores exigirão 130M * 90 bytes = 10.9GB de espaço em
disco.
Note:
O tamanho dos items do tipo texto/log é impossível de ser previsto com exatidão, mas você esperar em torno de 500 bytes
por valor.
59
• Configuração do Housekeeper para a estatística
O Zabbix mantém um conjunto de valores máximo/min/médio/contagem de 1 hora para cada item na tabela trends. Os dados
são usados para tendências e gráficos de longos períodos. O período de uma hora não pode ser personalizado.
O banco de dados do Zabbix, dependendo do tipo do banco de dados, requer cerca de 90 bytes para cada total. Suponha que
gostaríamos de manter os dados de estatística por 5 anos. Os valores para 3.000 itens exigirão 3.000*24*365* 90 = 2,2 GB por
ano ou 11 GB por 5 anos.
• Configuração do Housekeeper para os eventos
1
Cada evento Zabbix requer aproximadamente 250 bytes de espaço em disco . É difícil estimar o número de eventos gerados
diariamente pelo Zabbix. Na pior das hipóteses, podemos assumir que o Zabbix gera um evento por segundo.
Para cada evento de recuperação, é criado um registro event_recovery. Normalmente a maioria dos eventos serão recuperados
para que possamos assumir um registro de event_recovery por evento. Isso significa 80 bytes adicionais por evento.
1
Opcionalmente, os eventos podem ter tags, cada registro de tag requer aproximadamente 100 bytes de espaço em disco . O
número de tags por evento (#tags) depende da configuração. Portanto, cada um precisará de mais #tags * 100 bytes de espaço
em disco.
Isso significa que se quisermos manter 3 anos de eventos, isso exigiria 3*365*24*3600* (250+80+#tags*100) = ~30GB+#tags*100B
2
disco espaço .
Note:
1
Mais quando tiver nomes de eventos não ASCII, tags e valores.
2
As aproximações de tamanho são baseadas no MySQL e podem ser diferentes para outros bancos de dados.
A tabela contém fórmulas que podem ser usadas para calcular o espaço em disco necessário para o sistema Zabbix:
Parâmetro Fórmula para o espaço em disco necessário (em bytes)
Configuração do Tamanho fixo. Normalmente 10MB ou menos.
Zabbix
Histórico dias*(itens/intervalo de atualização)*24*3600*bytes
itens : número de itens
dias : número de dias para manter o histórico
intervalo de atualização : intervalo de atualização médio para os itens
bytes : número de bytes necessário para manter um valor, depende do mecanismo de banco de
dados, normalmente ~90 bytes.
Estatísticas dias*(itens/3600)*24*3600*bytes
itens : número de itens
dias : número de dias para manter o histórico
bytes : número de bytes necessário para manter um valor estatístico, depende do mecanismo de
banco de dados, normalmente ~90 bytes.
Eventos dias*eventos*24*3600*bytes
eventos : número de eventos por segundo. Um (1) evento por segundo no pior cenário.
dias : número de dias para manter o histórico
bytes : número de bytes necessários para manter um valor estatístico, depende do mecanismo de
banco de dados, normalmente ~330 + número médio de tags por evento * 100 bytes.
Assim, o espaço total em disco necessário pode ser calculado como:
Configuração + Histórico + Estatísticas + Eventos
O espaço em disco NÃO será usado imediatamente após a instalação do Zabbix. O tamanho do banco de dados aumentará e
depois parará de crescer em algum ponto, o que depende das configurações do Housekeeper.
Sincronização de tempo
É muito importante ter a hora exata do sistema no servidor no qual o Zabbix está em execução. O ntpd é o daemon mais popular
que sincroniza a hora do host com a hora de outras máquinas. Isso é fortemente recomendado para manter a hora do sistema
sincronizada em todos os sistemas nos quais os componentes do Zabbix estão sendo executados.
1 Plugins
Por favor utilize a barra lateral para acessar o conteúdo na seção do Plugin.
60
1 Dependências do plugin PostgreSQL
Visão geral
As bibliotecas necessárias para o plugin PostgreSQL carregável estão listada nesta página.
Bibliotecas Go
Status
obri- Versão
Requirement gatório mínima Descrição
[Link]/ap/plugin-
Sim 1.X.X Biblioteca de suporte própria do Zabbix. Principalmente para plugins.
support
[Link]/jackc/pgx/v4 4.17.2 PostgreSQL driver.
[Link]/omeid/go- 0.0.1 Armazenamento incorporável de key-string mapeado em sistemas de
yarn arquivos.
1
[Link]/jackc/chunkreader
Indireto 2.0.1
[Link]/jackc/pgconn 1.13.0
[Link]/jackc/pgio 1.0.0
[Link]/jackc/pgpassfile 1.0.0
[Link]/jackc/pgproto3 2.3.1
[Link]/jackc/pgservicefile 0.0.0
[Link]/jackc/pgtype 1.12.0
[Link]/jackc/puddle 1.3.0
[Link]/Microsoft/go- 0.6.0 Pacote necessário para plugin PostgreSQL no Windows.
winio
[Link]/x/crypto 0.0.0
[Link]/x/sys 0.0.0
[Link]/x/text 0.3.7
1
”Indireto” significa que é usado em umas das bibliotecas que o agente utiliza. Isso é necessário, já que o Zabbix utiliza a biblioteca
que usa o pacote.
2 Dependências do plugin MongoDB
Visão geral
As bibliotecas necessárias para o plugin carregável MongoDB, estão listadas nesta página.
Bibliotecas Go
Status
obri- Versão
Requerimento gatório mínima Descrição
[Link]/ap/plugin-
Sim 1.X.X Biblioteca de suporte própria do Zabbix. Principalmente para plugins.
support
[Link]/mongo- 1.7.6 Bloqueios nomeados read/write, sincronização de acesso.
driver
1
[Link]/go- Indirect 1.8.0 Pacote necessário para o plugin MongoDB é mongo-driver lib.
stack/stack
[Link]/golang/snappy 0.0.1 Pacote necessário para o plugin MongoDB é mongo-driver lib.
[Link]/klauspost/compress 1.13.6 Pacote necessário para o plugin MongoDB é mongo-driver lib.
[Link]/Microsoft/go- 0.6.0 Pacote necessário para o plugin MongoDB é mongo-driver lib.
winio
[Link]/pkg/errors 0.9.1 Pacote necessário para o plugin MongoDB é mongo-driver lib.
[Link]/xdg- 1.0.0 Pacote necessário para o plugin MongoDB é mongo-driver lib.
go/pbkdf2
[Link]/xdg- 1.0.2 Pacote necessário para o plugin MongoDB é mongo-driver lib.
go/scram
[Link]/xdg- 1.0.2 Pacote necessário para o plugin MongoDB é mongo-driver lib.
go/stringprep
[Link]/youmark/pkcs8 0.0.0 Pacote necessário para o plugin MongoDB é mongo-driver lib.
61
Status
obri- Versão
Requerimento gatório mínima Descrição
[Link]/x/crypto 0.0.0 Pacote necessário para o plugin MongoDB é mongo-driver lib.
[Link]/x/sync 0.0.0 Pacote necessário para o plugin MongoDB é mongo-driver lib.
[Link]/x/sys 0.0.0 Pacote necessário para o plugin MongoDB é mongo-driver lib.
[Link]/x/text 0.3.7 Pacote necessário para o plugin MongoDB é mongo-driver lib.
1
”Indirect” significa que é usado em uma das bibliotecas que o agente utiliza. É necessário, pois o Zabbix utiliza a biblioteca que
utiliza os pacotes.
Best practices for secure Zabbix setup
Visão geral
Esta seção contém boas práticas que devem ser observadas de modo a configurar o Zabbix de uma forma segura.
As práticas contidas aqui não são necessárias para o funcionamento do Zabbix. Elas são recomendadas para uma melhor segurança
do sistema.
Access control
Princípio do menor privilégio
O princípio do menor privilégio deve ser usado todo o tempo no Zabbix. Este princípio implica que contas de usuário (no Zabbix
Frontend) ou usuários de processo (para Zabbix Server/Proxy ou Agent) tenham apenas aqueles privilégios essenciais para executar
as funções pretendidas. Em outras palavras, contas de usuário devem fornecer o mínimo de privilégios possível, durante todo o
tempo.
Attention:
Fornecer permissões extras ao usuário ’zabbix’ permitirá que este acesse os arquivos de configuração e execute operações
que podem comprometer a segurança geral da infraestrutura.
Quando implementando o princípio de mínimo privilégio para contas de usuário, os tipos de usuário do frontend do Zabbix devem
ser levados em conta. É importante entender que enquanto um usuário do tipo ”Admin” tem menos privilégios do um usuário do
tipo ”Super Admin”, ele tem permissões administrativas que o permitem gerenciar configurações e executar scripts customizados.
Note:
Algumas informações estão disponíveis até mesmo para usuários sem privilégio. Por exemplo, conquanto Administração
→ Scripts esteja disponível apenas para usuários Super Admins, os próprios scripts estão disponíveis para recuperação
através do uso da API do Zabbix. Limitação nas permissões dos scripts e a não adição de informações sensíveis (como
credenciais de acesso, etc) devem ser consideradas para evitar a exposição de informações sensíveis existentes nos scripts
globais.
Usuário seguro para Zabbix Agent
Na configuração padrão, os processos do Zabbix Server e Zabbix Agent compartilham um usuário ’zabbix’. Se você desejar
certificar-se de que o Agent não tenha acesso a detalhes sensíveis na configuração do Server (p.e. informações de login do banco
de dados), o Agent deve ser executado com um usuário diferente:
1. Crie um usuário seguro
2. Especifique este usuário no arquivo de configuração (parâmetro ’User’) do Agent
3. Reinicie o Agent com privilégios de administrador. Estes privilégios serão substituídos pelos privilégios do usuário especifi-
cado.
Codificação UTF-8
O UTF-8 é o único formato de codificação suportado pelo Zabbix. É conhecido por operar sem quaisquer falhas de segurança.
Usuários devem estar cientes de que há problemas de segurança conhecidos quando usando algum dos outros formatos.
Windows installer paths
When using Windows installers, it is recommended to use default paths provided by the installer as using custom paths without
proper permissions could compromise the security of the installation.
Zabbix Security Advisories and CVE database
62
See Zabbix Security Advisories and CVE database.
Configurando SSL para Zabbix Frontend
No RHEL/Centos, instale o pacote mod_ssl:
yum install mod_ssl
Crie diretório para as chaves SSL:
mkdir -p /etc/httpd/ssl/private
chmod 700 /etc/httpd/ssl/private
Crie o certificado SSL:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/httpd/ssl/private/[Link] -
Preencha cada informação com os dados apropriados. A linha mais importante é a que solicita o Nome Comum (Common Name).
Aqui você precisa informar o nome de domínio que deseja que seja associado ao seu servidor. Você pode informar o endereço de
IP público caso não tenha um nome de domínio. Neste artigo nós faremos uso do nome [Link].
Country Name (2 letter code) [XX]:
State or Province Name (full name) []:
Locality Name (eg, city) [Default City]:
Organization Name (eg, company) [Default Company Ltd]:
Organizational Unit Name (eg, section) []:
Common Name (eg, your name or your server's hostname) []:[Link]
Email Address []:
Edite as configurações de SSL do Apache:
/etc/httpd/conf.d/[Link]
DocumentRoot "/usr/share/zabbix"
ServerName [Link]
SSLCertificateFile /etc/httpd/ssl/[Link]
SSLCertificateKeyFile /etc/httpd/ssl/private/[Link]
Reinicie o serviço do Apache para aplicar as alterações:
systemctl restart [Link]
Web server hardening
Habilitando o Zabbix no diretório raíz da URL
Adicione um virtual host na configuração do Apache e configure um redirecionamento permanente do diretório raíz (DocumentRoot)
para a URL com SSL do Zabbix. Não esqueça de substituir [Link] pelo nome real do servidor.
/etc/httpd/conf/[Link]
#Linhas adicionais
<VirtualHost *:*>
ServerName [Link]
Redirect permanent / [Link]
</VirtualHost>
Reinicie o serviço do Apache para aplicar as alterações:
systemctl restart [Link] && systemctl status [Link]
Habilitando HTTP Strict Transport Security (HSTS) no servidor web
Para proteger o Zabbix Frontend contra ataques de rebaixamento de protocolo, nós recomendamos habilitar a política de HSTS no
servidor web.
Por exemplo, para habilitar a política HSTS para seu Zabbix Frontend na configuração do Apache:
/etc/httpd/conf/[Link]
adicione a seguinte diretiva à configuração do seu virtual host:
<VirtualHost *:443>
Header set Strict-Transport-Security "max-age=31536000"
63
</VirtualHost>
Reinicie o serviço do Apache para aplicar as alterações:
systemctl restart [Link]
Enabling Content Security Policy (CSP) on the web server
To protect Zabbix frontend against Cross Site Scripting (XSS), data injection, and similar attacks, we recommend enabling Content
Security Policy on the web server. To do so, configure the web server to return the HTTP header.
Attention:
The following CSP header configuration is only for the default Zabbix frontend installation and for cases when all content
originates from the site’s domain (excluding subdomains). A different CSP header configuration may be required if you
are, for example, configuring the URL widget to display content from the site’s subdomains or external domains, switching
from OpenStreetMap to another map engine, or adding external CSS or widgets.
To enable CSP for your Zabbix frontend in Apache configuration, follow these steps:
1. Locate your virtual host’s configuration file:
• /etc/httpd/conf/[Link] on RHEL-based systems
• /etc/apache2/sites-available/[Link] on Debian/Ubuntu
2. Add the following directive to your virtual host’s configuration file:
<VirtualHost *:*>
Header set Content-Security-Policy: "default-src 'self' *.[Link]; script-src 'self' 'unsafe
</VirtualHost>
3. Restart the Apache service to apply the changes:
#### On RHEL-based systems:
systemctl restart [Link]
#### On Debian/Ubuntu
systemctl restart [Link]
Desabilitando exposição de informação do servidor web
É recomendado desabilitar todas as assinaturas do web server como parte do processo de garantia da segurança. O Web Server
expõe sua assinatura de software por padrão:
A assinatura pode ser desabilitada através da adição de duas linhas no arquivo de configuração do Apache, por exemplo::
ServerSignature Off
ServerTokens Prod
A assinatura do PHP (X-Powered-By HTTP header) pode ser desabilitada pela alteração do arquivo de configuração [Link] (neste
caso a assinatura é desabilitada por padrão):
expose_php = Off
Um reinício do Web Server é necessário para que as alterações no arquivo de configuração sejam aplicadas.
Um nível adicional de segurança pode ser alcançado usando mod_security (pacote libapache2-mod-security2) com Apache. O
mod_security permite remover toda a assinatura do server em vez de apenas remover a versão. A assinatura pode ser alterada
para qualquer valor pela alteração de ”SecServerSignature” para um valor desejado após a instalação do mod_security.
64
Por favor, consulte a documentação do seu Web Server para encontrar auxílio em como remover/alterar as assinaturas de software.
Desabilitando as páginas de erro padrão do Web Server
É recomendado desabilitar as páginas de erro padrão para evitar exposição de informação. O Web Server usa as páginas de erro
embutidas por padrão:
Páginas de erro padrão devem ser substituídas/removidas como parte do processo de aprimoramento da segurança. A diretiva
”ErrorDocument” pode ser usada para definir uma página/texto de erro customizado para o Apache Web Server (usado como
exemplo).
Por favor, consulte a documentação do seu Web Server para encontrar auxílio em como substituir/remover as páginas de erro
padrão.
Removendo a página de teste do Web Server
É recomendado remover a página de teste do Web Server para evitar a exposição de informações. Por padrão, o diretório raíz do
Web Server contém uma página de teste chamada [Link] (usando Apache2 no Ubuntu como exemplo):
A página de teste deve ser removida ou tornada indisponível como parte do processo de aprimoramento da segurança do Web
Server.
Configurações do Zabbix
Por padrão, o Zabbix possui a opção X-Frame-Options HTTP response header configurada como SAMEORIGIN, significando que o
conteúdo só pode ser carregado em um frame que tenha a mesma origem da página em si.
Os elementos do Zabbix Frontend que buscam conteúdo de URLs externas (especificamente, o widget de URL para dashboard)
apresentam o conteúdo encontrado em uma área isolada (sandbox) com todas as restrições habilitadas.
Estas configurações aprimoram a segurança do Zabbix Frontend e proveem proteção contra ataques do tipo XSS e clickjacking.
Super Admins podem modificar os parâmetros iframe sandboxing e X-Frame-Options HTTP response header conforme necessário.
Por favor, pese cuidadosamente os riscos e benefícios antes de alterar as configurações padrão. Desativar completamente a
função de sandboxing ou X-Frame-Options não é recomendado.
Zabbix Windows Agent com OpenSSL
O Zabbix Windows Agent compilado com OpenSSL tentará encontrar o arquivo de configuração SSL em C:\openssl-64bit. O diretório
”openssl-64bit” na partição C: pode ser criado por usuários sem privilégio elevado.
Assim, para aprimoramento da segurança, é necessária a criação deste diretório manualmente e então a retirada do acesso de
escrita para os usuários que não sejam administradores.
65
Por favor, note que os nomes do diretório serão diferentes nas versões 32-bit e 64-bit do Windows.
Cryptography
Escondendo o arquivo com lista de senhas mais comuns
Para aumentar a complexidade de ataques de força bruta sobre senha, é sugerido limitar o acesso ao arquivo ui/data/top_passwords.txt
modificando a configuração do Web Server. Este arquivo contém uma lista das senhas mais comuns e com contexto específico, e
é usado para prevenir os usuários de criar senhas semelhantes se o parâmetro Avoid easy-to-guess passwords estiver habilitado
na política de senha.
Por exemplo, no NGINX o acesso ao arquivo pode ser limitado usando a diretiva location:
location = /data/top_passwords.txt {
deny all;
return 404;
}
No Apache, usando o arquivo .htacess:
<Files "top_passwords.txt">
Order Allow,Deny
Deny from all
</Files>
3 Instalação a partir do código-fonte
É possível acessar a versão mais recente do Zabbix compilando-a a partir do código-fonte.
A seguir, fornecemos um tutorial com os passos para instalação do Zabbix a partir do código-fonte.
1 Instalando daemons do Zabbix
1 Download do arquivo fonte
Vá até a página de download do Zabbix e baixe o arquivo fonte. Uma vez baixado, extraia os fontes, executando:
$ tar -zxvf [Link]
Note:
Informe a versão correta do Zabbix no comando. Ela deve corresponder ao nome do arquivo baixado.
2 Criar conta de usuário
Para todos os processos de daemon do Zabbix, um usuário sem privilégios é requirido. Se um daemon Zabbix é iniciado a partir
de uma conta de usuário sem privilégios, ele será executado como tal usuário.
No entando, se um daemon é iniciado a partir de uma conta ’root’, ele mudará para uma conta de usuário ’zabbix’, que deve
existir. Para criar esta conta de usuário (em seu próprio grupo, ”zabbix”),
em sistemas baseados em RedHat, execute:
groupadd --system zabbix
useradd --system -g zabbix -d /usr/lib/zabbix -s /sbin/nologin -c "Zabbix Monitoring System" zabbix
em sistemas baseados em Debian, execute:
addgroup --system --quiet zabbix
adduser --quiet --system --disabled-login --ingroup zabbix --home /var/lib/zabbix --no-create-home zabbix
66
Attention:
Os processos Zabbix não precisam de um diretório home, sendo este o motivo de não recomendarmos a sua criação. No
entanto, se você estiver usando alguma funcionalidade que demande tal diretório (p.e. armazenar credenciais MySQL em
$HOME/.[Link]), você está livre para criá-lo usando os seguintes comandos:
Em sistemas baseados em RedHat, execute:
mkdir -m u=rwx,g=rwx,o= -p /usr/lib/zabbix
chown zabbix:zabbix /usr/lib/zabbix
Em sistemas baseados em Debian, execute:
mkdir -m u=rwx,g=rwx,o= -p /var/lib/zabbix
chown zabbix:zabbix /var/lib/zabbix
Não é necessária uma conta de usuário separada para a instalação do Zabbix Frontend.
Se o Zabbix Server e Agent são executados na mesma máquina é recomendado usar um usuário diferente para executar o server
daquele usado para o agent. Caso contrário, se ambos são executados com o mesmo usuário, o agent pode acessar os arquivos de
configuração do server e assim qualquer usuário do Zabbix com perfil de Admin pode facilmente, por exemplo, descobrir a senha
do banco de dados.
Attention:
Executar o Zabbix como root, bin, ou qualquer outra conta com permissões especiais é um risco à segurança.
3 Criar banco de dados Zabbix
Para os daemons do Zabbix Server e Proxy, bem como para o Zabbix Frontend, um banco de dados é necessário. No entanto não
é necessário para executar o Zabbix Agent.
Scripts SQL são disponibilizados para criação do schema de banco de dados e carga do conjunto de dados iniciais. O banco de
dados do Zabbix Proxy necessita apenas do schema enquanto que o banco de dados do Zabbix Server requer também o conjunto
de dados junto ao schema.
Tendo criado um banco de dados para o Zabbix, prossiga para os próximos passos de compilação do Zabbix.
4 Configurar os fontes
Ao configurar os fontes para o Zabbix Server ou Proxy, você deve especificar o tipo de banco de dados a ser usado. Apenas um
tipo de banco de dados pode ser compilado com um processo Server ou Proxy por vez.
Para ver todas as opções de configuração suportadas, dentro do diretório de fonte do Zabbix extraído, execute:
./configure --help
Para configurar os fontes para o Zabbix Server e Agent, você pode executar algo como o seguinte:
./configure --enable-server --enable-agent --with-mysql --enable-ipv6 --with-net-snmp --with-libcurl --wit
Para configurar os fontes para o Zabbix Server (com PostgreSQL, etc.), você pode usar:
./configure --enable-server --with-postgresql --with-net-snmp
Para configurar os fontes para Zabbix Proxy (com SQLite, etc.), você pode executar:
./configure --prefix=/usr --enable-proxy --with-net-snmp --with-sqlite3 --with-ssh2
Para configurar os fontes para o Zabbix Agent, você pode utilizar:
./configure --enable-agent
ou, para Zabbix Agent 2:
./configure --enable-agent2
Note:
Um ambiente Go configurado com uma versão atualmente suportada é necessário para compilar o Zabbix Agent 2. Con-
sulte [Link] para instruções de instalação.
Notas sobre as opções de compilação:
• Os utilitários de linha de comando zabbix_get e zabbix_sender são compilados se a opção --enable-agent é usada.
67
• As opções de configuração --with-libcurl e --with-libxml2 são necessárias para monitoramento de máquinas virtuais; --with-
libcurl também é necessário para autenticação SMTP e itens [Link].* do Zabbix Agent. Note que o cURL na versão
7.20.0 ou maior é necessário com a opção de configuração --with-libcurl.
• O Zabbix sempre compila com a biblioteca PCRE (desde a versão 3.4.0); sua instalação não é opcional. --with-libpcre=[DIR]
apenas permite o direcionamento para um diretório de instalação específico, em vez de buscar entre um número de lugares
comuns pelos arquivos da biblioteca libpcre.
• Você pode usar o marcador --enable-static para vincular bibliotecas de forma estática. Se você planeja distribuir binários
compilados entre diferentes servidores, você deve usar este marcador para que tais binários funcionem sem as bibliotecas
exigidas. Note que --enable-static não funciona em Solaris.
• O uso da opção --enable-static não é recomendado quanto compilando o server. Para compilar o server estaticamente, você
deve ter uma versão estática de cada biblioteca externa necessária. Não há uma verificação rigorosa quanto a isso no script
de configuração.
• Adicione um caminho opcional para o arquivo de configuração do MySQL --with-mysql=/<path_to_the_file>/mysql_config
para selecionar a biblioteca de cliente MySQL desejada quando houver necessidade de utilizar uma que não esteja localizada
no local padrão. Isto é útil quando há várias versões de MySQL instaladas ou um MariaDB instalado junto ao MySQL no mesmo
sistema.
• Use o marcador --with-oracle para especificar a localização da API OCI.
Attention:
[Link] para
Se ./configure falhar devido bibliotecas ausentes ou alguma outra circunstância, por favor verifique o
libssl está ausente, a mensagem de erro imediata pode ser confusa:
mais detalhes quanto ao erro. Por exemplo, se
checking for main in -lmysqlclient... no
configure: error: Not found mysqlclient library
Enquanto que o [Link] possui uma descrição mais detalhada:
/usr/bin/ld: cannot find -lssl
/usr/bin/ld: cannot find -lcrypto
Veja também:
• Compilando Zabbix com suporte à criptografia
• Problemas conhecidos na compilação do Zabbix Agent em HP-UX
5 Make e install para tudo
Note:
Se instalando através do repositório Git do Zabbix, é necessário primeiro executar:
$ make dbschema
make install
Esta etapa deve ser executada usando um usuário com permissões suficientes (comumente ’root’, ou utilizando elevação de
usuário com sudo).
A execução do comando make install instalará, por padrão, os binários dos daemons (zabbix_server, zabbix_agentd, zab-
bix_proxy) em /usr/local/sbin e os binários de client (zabbix_get, zabbix_sender) em /usr/local/bin.
Note:
Para especificar um local diferente de /usr/local, use a chave --prefix na etapa anterior de configuração dos fontes, por
exemplo --prefix=/home/zabbix. Neste caso os binários dos daemons seriam instalados dentro de <prefix>/sbin, enquanto
que os utilitários em <prefix>/bin. As páginas de manual seriam instaladas em <prefix>/share.
6 Revise e edite os arquivos de configuração
• edite o arquivo de configuração do Zabbix Agent /usr/local/etc/zabbix_agentd.conf
Você precisa configurar este arquivo para cada máquina com zabbix_agentd instalado.
Você deve especificar o endereço IP do servidor Zabbix no arquivo. Conexões de outros endereços serão negadas.
• edite o arquivo de configuração do Zabbix Server /usr/local/etc/zabbix_server.conf
Você deve especificar o nome do banco de dados, usuário e senha (se usando alguma).
O restante dos parâmetros o atenderão com seus valores padrão se você tiver um ambiente pequeno (até 10 máquinas mon-
itoradas). Todavia, você deve alterar os parâmetros padrão se você pretende maximizar a performance do Zabbix Server (ou
Proxy). Consulte a seção ajustes de performance para mais detalhes.
• se você tem instalado um Zabbix Proxy, edite o arquivo de configuração /usr/local/etc/zabbix_proxy.conf
68
Você deve especificar o endereço IP e o nome do servidor do Zabbix Proxy (que deve ser conhecido pelo Zabbix Server), bem como
o nome do banco de dados, usuário e senha (se usando alguma).
Note:
Com SQLite deve ser especificado o caminho completo para o arquivo de banco de dados; Usuário e senha do banco de
dados não são exigidos.
7 Inicie os daemons
Execute o zabbix_server no lado do servidor:
shell> zabbix_server
Note:
Certifique-se de que seu sistema permita a alocação de 36MB (ou um pouco mais) de memória compartilhada, caso
contrário o Server pode não iniciar e você verá a mensagem ”Impossível alocar memória compartilhada para <tipo de
cache>.” (se log em inglês: ”Cannot allocate shared memory for <type of cache>.”) no arquivo de log. Isto pode ocorrer
com FreeBSD, Solaris 8.
Verifique a seção ”Veja também” ao final desta página para descobrir como configurar a memória compartilhada.
Execute zabbix_agentd em todas as máquinas monitoradas:
shell> zabbix_agentd
Note:
Certifique-se de que seu sistema permita a alocação de 2MB de memória compartilhada, caso contrário o Agente pode não
iniciar e você verá a mensagem ”Impossível alocar memória compartilhada para o coletor” ( se log em inglês: ”Cannot
allocate shared memory for collector.”) no arquivo de log. Isto pode ocorrer em Solaris 8.
Se você tem instalado o Zabbix Proxy, execute zabbix_proxy.
shell> zabbix_proxy
2 Instalação da interface web do Zabbix
Copiando arquivos PHP
O frontend do Zabbix é escrito em PHP, assim, para executá-lo, é necessário um webserver com suporte ao PHP. A instalação é
feita com a simples cópia dos arquivos PHP do diretório ui para o diretório de documentos HTML do webserver.
Locais comuns para o diretório de documentos HTML no Apache Web Server incluem:
• /usr/local/apache2/htdocs (diretório padrão quando instalando o Apache a partir do fonte)
• /srv/www/htdocs (OpenSUSE, SLES)
• /var/www/html (Debian, Ubuntu, Fedora, RHEL, CentOS)
Sugere-se usar um subdiretório em vez da raíz do diretório HTML. Para criar um subdiretório e copiar os arquivos do frontend
do Zabbix para dentro dele, execute os seguintes comandos, informando o diretório raíz junto ao nome do subdiretório que se
prentede criar:
mkdir <htdocs>/zabbix
cd ui
cp -a . <htdocs>/zabbix
Para mais instruções quando usando idioma diferente do Inglês, consulte Instalação de idiomas de frontend adicionais.
Instalação do frontend
Por favor, consulte a página Instalação da interface web para se informar sobre o assitente de instalação do Zabbix frontend.
3 Instalação do Java Gateway
A instalação do Java Gateway é exigida apenas se você pretende monitorar aplicações JMX. O Java Gateway é leve e não necessita
de um banco de dados.
Para instalar a partir dos fontes, primeiro faça o download e então extraia o arquivo fonte.
Para compilar o Java Gateway, execute o script ./configure com a opção --enable-java. É aconselhável que você especifique
--prefix para direcionar a instalação para outro local diferente do padrão /usr/local, porque a instalação criará uma árvore de
diretórios completa, e não apenas um simples executável.
69
$ ./configure --enable-java --prefix=$PREFIX
Para compilar e empacotar o Java Gateway em um arquivo JAR, execute make. Note que para este processo você necessitará dos
executáveis javac e jar no seu path.
$ make
Agora você tem um arquivo zabbix-java-gateway-$[Link] em src/zabbix_java/bin. Se você se sente confortável em executar
o Java Gateway a partir de src/zabbix_java no diretório da distribuição, então você pode prosseguir às instruções de configuração
e execução do Java Gateway. Caso contrário, certifique-se de possuir os privilégios necessários e execute make install.
$ make install
Prossiga até Configuração inicial para mais detalhes na configuração e execução do Java Gateway.
4 Instalando o serviço web Zabbix
A instalação do serviço web Zabbix só é necessária se você quiser usarrelatório agendado.
Para instalar a partir de fontes, primeiro download e extraia o arquivo com as fontes .
Para compilar o serviço web Zabbix, execute o script ./configure com opção --enable-webservice .
Note:
Uma versãoGo configurada com ambiente 1.13+é necessário para construir o serviço web Zabbix.
Execute zabbix_web_service na máquina onde o serviço web está instalado:
shell> zabbix_web_service
Prossiga para configuração para obter mais detalhes sobre como configurar a geração de relatórios agendados.
Construindo Agente Zabbix 2 no Windows
Visão geral
Esta seção demonstra como construir o Zabbix agent 2 (Windows) a partir de fontes.
Instalando o compilador MinGW
1. Download MinGW-w64 with SJLJ (set jump/long jump) Manipulação de exceção e tópicos do Windows (for example x86_64-8.1.0-
release-win32-sjlj-rt_v6-rev0.7z)
2. Extract and move to c:\mingw
3. Setup environmental variable
@echo off
set PATH=%PATH%;c:\mingw\bin
cmd
Ao compilar, use o prompt do Windows em vez do terminal MSYS fornecido por MinGW
Compilando bibliotecas de desenvolvimento PCRE
As instruções a seguir irão compilar e instalar o PCRE de 64 bits bibliotecas em c:\dev\pcre e bibliotecas de 32 bits em c:\dev\pcre32:
1. Baixe a biblioteca PCRE versão [Link] em [Link] ([Link] e extrair
2. Abra cmd e navegue até as fontes extraídas
Build 64bit PCRE
1. Delete old configuration/cache if exists:
del [Link]
rmdir /q /s CMakeFiles
2. Run cmake (CMake can be installed from [Link]
cmake -G "MinGW Makefiles" -DCMAKE_C_COMPILER=gcc -DCMAKE_C_FLAGS="-O2 -g" -DCMAKE_CXX_FLAGS="-O2 -g" -DCM
3. Next, run:
mingw32-make clean
mingw32-make install
70
Build 32bit PCRE
1. Run:
mingw32-make clean
2. Delete [Link]:
del [Link]
rmdir /q /s CMakeFiles
3. Run cmake:
cmake -G "MinGW Makefiles" -DCMAKE_C_COMPILER=gcc -DCMAKE_C_FLAGS="-m32 -O2 -g" -DCMAKE_CXX_FLAGS="-m32 -O
4. Next, run:
mingw32-make install
Instalando bibliotecas de desenvolvimento OpenSSL
1. Download versões 32 e 64 bit através de [Link]
2. Extraia os arquivos em c:\dev\openssl32 ec:\dev\openssl directories accordingly.
3. Depois disso, remova *.dll.a (bibliotecas de wrapper de chamadas dll) já que o MinGW os prioriza antes das bibliotecas estáticas.
Compilando agente Zabbix 2
32 bit
Abra o ambiente MinGW (prompt de comando do Windows) e navegue até build/mingw diretório de fonte Zabbix .
Execute:
mingw32-make clean
mingw32-make ARCH=x86 PCRE=c:\dev\pcre32 OPENSSL=c:\dev\openssl32
64 bit
Abra o ambiente MinGW (prompt de comando do Windows) e navegue até build/mingw diretório de fonte Zabbix .
Execute:
mingw32-make clean
mingw32-make PCRE=c:\dev\pcre OPENSSL=c:\dev\openssl
Note:
Ambas as versões de 32 e 64 bitspodem ser criadas em uma plataforma 64-bit, mas apenas a versão 32-bit pode criar em
uma plataforma 32-bit. Ao trabalhar na plataforma de 32 bits, siga as mesmas etapas para 64 bits pata plataforma versão
64 bits.
Criando agente Zabbix no Windows
Visão Geral
Esta seção demonstra como construir binários do agente Zabbix para Windows de fontes com ou sem TLS..
Compiling OpenSSL
The following steps will help you to compile OpenSSL from sources on MS Windows 10 (64-bit).
1. For compiling OpenSSL you will need on Windows machine:
1. C compiler (e.g. VS 2017 RC),
2. NASM ([Link]
3. Perl (e.g. Strawberry Perl from [Link]
4. Perl module Text::Template (cpan Text::Template).
2. Get OpenSSL sources from [Link] OpenSSL 1.1.1 is used here.
3. Unpack OpenSSL sources, for example, in E:\openssl-1.1.1.
4. Open a commandline window e.g. the x64 Native Tools Command Prompt for VS 2017 RC.
5. Go to the OpenSSL source directory, e.g. E:\openssl-1.1.1.
1. Verify that NASM can be found:e:\openssl-1.1.1> nasm --version NASM version 2.13.01 compiled
on May 1 2017
71
6. Configure OpenSSL, for example:e:\openssl-1.1.1>
perl E:\openssl-1.1.1\Configure VC-WIN64A no-shared
no-capieng no-srp no-gost no-dgram no-dtls1-method no-dtls1_2-method --api=1.1.0 --prefix=C:\OpenSSL
--openssldir=C:\OpenSSL-Win64-111-static
• Note the option ’no-shared’: if ’no-shared’ is used then the OpenSSL static libraries [Link] and [Link] will be
’self-sufficient’ and resulting Zabbix binaries will include OpenSSL in themselves, no need for external OpenSSL DLLs.
Advantage: Zabbix binaries can be copied to other Windows machines without OpenSSL libraries. Disadvantage: when
a new OpenSSL bugfix version is released, Zabbix agent needs to recompiled and reinstalled.
• If ’no-shared’ is not used, then the static libraries [Link] and [Link] will be using OpenSSL DLLs at runtime.
Advantage: when a new OpenSSL bugfix version is released, probably you can upgrade only OpenSSL DLLs, without
recompiling Zabbix agent. Disadvantage: copying Zabbix agent to another machine requires copying OpenSSL DLLs,
too.
7. Compile OpenSSL, run tests, install:e:\openssl-1.1.1>
nmake e:\openssl-1.1.1> nmake test ...
All tests successful. Files=152, Tests=1152, 501 wallclock secs ( 0.67 usr + 0.61 sys
= 1.28 CPU) Result: PASS e:\openssl-1.1.1> nmake install_sw’install_sw’ installs only software
components (i.e. libraries, header files, but no documentation). If you want everything, use ”nmake install”.
Compiling PCRE
1. Download PCRE library (mandatory library since Zabbix 4.0) from [Link], version [Link]; not pcre2 ([Link]
[Link])
2. Extract to directory E:\pcre-8.41
3. Install CMake from [Link] during install select: and ensure that cmake\bin is on your path (tested
version 3.9.4).
4. Create a new, empty build directory, preferably a subdirectory of the source dir. For example, E:\pcre-8.41\build.
5. Open a commandline window e.g. the x64 Native Tools Command Prompt for VS 2017 and from that shell environment run
cmake-gui. Do not try to start Cmake from the Windows Start menu, as this can lead to errors.
6. Enter E:\pcre-8.41 and E:\pcre-8.41\build for the source and build directories, respectively.
7. Hit the ”Configure” button.
8. When specifying the generator for this project select ”NMake Makefiles”.
9. Create a new, empty install directory. For example, E:\pcre-8.41-install.
10. The GUI will then list several configuration options. Make sure the following options are selected:
• PCRE_SUPPORT_UNICODE_PROPERTIES ON
• PCRE_SUPPORT_UTF ON
• CMAKE_INSTALL_PREFIX E:\pcre-8.41-install
11. Hit ”Configure” again. The adjacent ”Generate” button should now be active.
12. Hit ”Generate”.
13. In the event that errors occur, it is recommended that you delete the CMake cache before attempting to repeat the CMake
build process. In the CMake GUI, the cache can be deleted by selecting ”File > Delete Cache”.
14. The build directory should now contain a usable build system - Makefile.
15. Open a commandline window e.g. the x64 Native Tools Command Prompt for VS 2017 and navigate to the Makefile mentioned
above.
16. Run NMake command: E:\pcre-8.41\build> nmake install
Compiling Zabbix
The following steps will help you to compile Zabbix from sources on MS Windows 10 (64-bit). When compiling Zabbix with/without
TLS support the only significant difference is in step 4.
1. On a Linux machine check out the source from git:$ git clone [Link]
$ cd zabbix $ ./[Link] $ ./configure --enable-agent --enable-ipv6 --prefix=`pwd`
$ make dbschema $ make dist
2. Copy and unpack the archive, e.g. [Link], on a Windows machine.
3. Let’s assume that sources are in e:\zabbix-4.4.0. Open a commandline window e.g. the x64 Native Tools Command Prompt
for VS 2017 RC. Go to E:\zabbix-4.4.0\build\win32\project.
4. Compile zabbix_get, zabbix_sender and zabbix_agent.
• without TLS: E:\zabbix-4.4.0\build\win32\project> nmake /K PCREINCDIR=E:\pcre-8.41-install\include
PCRELIBDIR=E:\pcre-8.41-install\lib
• with TLS: E:\zabbix-4.4.0\build\win32\project> nmake /K -f Makefile_get TLS=openssl TLSINCDIR=C:\Ope
TLSLIBDIR=C:\OpenSSL-Win64-111-static\lib PCREINCDIR=E:\pcre-8.41-install\include PCRELIBDIR=E:\p
E:\zabbix-4.4.0\build\win32\project> nmake /K -f Makefile_sender TLS=openssl TLSINCDIR="C:\OpenSS
TLSLIBDIR="C:\OpenSSL-Win64-111-static\lib" PCREINCDIR=E:\pcre-8.41-install\include
PCRELIBDIR=E:\pcre-8.41-install\lib E:\zabbix-4.4.0\build\win32\project> nmake /K -f
Makefile_agent TLS=openssl TLSINCDIR=C:\OpenSSL-Win64-111-static\include TLSLIBDIR=C:\OpenSSL-Win
PCREINCDIR=E:\pcre-8.41-install\include PCRELIBDIR=E:\pcre-8.41-install\lib
5. New binaries are located in e:\zabbix-4.4.0\bin\win64. Since OpenSSL was compiled with ’no-shared’ option, Zabbix binaries
72
contain OpenSSL within themselves and can be copied to other machines that do not have OpenSSL.
Compiling Zabbix with LibreSSL
The process is similar to compiling with OpenSSL, but you need to make small changes in files located in the build\win32\project
directory:
* In ''Makefile_tls'' delete ''/DHAVE_OPENSSL_WITH_PSK''. i.e. find <code>
CFLAGS = $(CFLAGS) /DHAVE_OPENSSL /DHAVE_OPENSSL_WITH_PSK</code>and replace it with CFLAGS = $(CFLAGS)
/DHAVE_OPENSSL
* In ''Makefile_common.inc'' add ''/NODEFAULTLIB:LIBCMT'' i.e. find <code>
/MANIFESTUAC:”level=’asInvoker’ uiAccess=’false’” /DYNAMICBASE:NO /PDB:$(TARGETDIR)\$(TARGETNAME).pdb</code>and re-
place it with /MANIFESTUAC:"level='asInvoker' uiAccess='false'" /DYNAMICBASE:NO /PDB:$(TARGETDIR)\$(TARGETNAME)
/NODEFAULTLIB:LIBCMT
Criando o agente Zabbix no macOS
Visão geral
Esta seção demonstra como construir os binários do agente Zabbix para macOS a partir da fonte com ou sem TLS.
Pré-requisitos
Você precisará de ferramentas de desenvolvedor de linha de comando (Xcode não é necessário), Automake, pkg-config e PCRE
(v8.x) ou PCRE2 (v10.x). Se você deseja criar os binários do agente com TLS, você também precisará do OpenSSL ou GnuTLS.
Para instalar o Automake e o pkg-config, você precisará de um gerenciador de pacotes Homebrew de [Link] Para instalar,
abra o terminal e execute o seguinte comando:
$ /usr/bin/ruby -e "$(curl -fsSL [Link]
Em seguida, instale o Automake e o pkg-config:
$ brew install automake
$ brew install pkg-config
A prepração das bibliotecas do PCRE, OpenSSL e GnuTLS depende da maneira como eles serão vinculados ao agente.
Se você pretende executar os binários do agente em uma máquina macOS que possui estas bibliotecas, você pode utilizar bibliote-
cas pré-compiladas fornecidas pelo Homebrew. Normalmente, são máquinas macOS que usam o Homebrew para criar binários do
agente Zabbix ou para outros fins.
Se os binários do agente forem utilizados em máquinas macOS que não possuem a versão compartilhada das bibliotecas, você
deve compilar bibliotecas estáticas a partir da fonte e vincular o agente Zabbix com eles.
Construindo binários do agente com bibliotecas compartilhadas
Instalar o PCRE2 (substitua pcre2 por pcre nos comandos abaixo, caso necessário):
$ brew install pcre2
Ao construir com TLS, instale OpenSSL e/ou GnuTLS::
$ brew install openssl
$ brew install gnutls
Baixar o fonte do Zabbix:
$ git clone [Link]
Construir o agente sem TLS:
$ cd zabbix
$ ./[Link]
$ ./configure --sysconfdir=/usr/local/etc/zabbix --enable-agent --enable-ipv6
$ make
$ make install
Construir o agente com OpenSSL:
73
$ cd zabbix
$ ./[Link]
$ ./configure --sysconfdir=/usr/local/etc/zabbix --enable-agent --enable-ipv6 --with-openssl=/usr/local/op
$ make
$ make install
Construir o agente com GnuTLS:
$ cd zabbix-source/
$ ./[Link]
$ ./configure --sysconfdir=/usr/local/etc/zabbix --enable-agent --enable-ipv6 --with-gnutls=/usr/local/opt
$ make
$ make install
Construindo binários de agente com bibliotecas estáticas sem TLS
Vamos assumir que as bibliotecas estáticas do PCRE serão instaladas em $HOME/static-libs. Utilizaremos o PCRE2 10.39.
$ PCRE_PREFIX="$HOME/static-libs/pcre2-10.39"
Faça o download e construa o PCRE com suporte a propriedades Unicode:
$ mkdir static-libs-source
$ cd static-libs-source
$ curl --remote-name [Link]
$ tar xf [Link]
$ cd pcre2-10.39
$ ./configure --prefix="$PCRE_PREFIX" --disable-shared --enable-static --enable-unicode-properties
$ make
$ make check
$ make install
Faça o download do fonte do Zabbix e construa o agente:
$ git clone [Link]
$ cd zabbix
$ ./[Link]
$ ./configure --sysconfdir=/usr/local/etc/zabbix --enable-agent --enable-ipv6 --with-libpcre2="$PCRE_PREFI
$ make
$ make install
Construindo binários do agente com bibliotecas estáticas com o OpenSSL
Ao construir o OpenSSL, é recomendado executar make test após construção com sucesso. Mesmo que a construção tenha sido
bem-sucedida, os testes às vezes falham. Se este for o caso, os problemas devem ser pesquisados e resolvidos antes de continuar.
Vamos assumir que as bibliotecas estáticas PCRE e OpenSSL serão instaladas em $HOME/static-libs. Utilizaremos o PCRE2
10.39 e OpenSSL 1.1.1a.
$ PCRE_PREFIX="$HOME/static-libs/pcre2-10.39"
$ OPENSSL_PREFIX="$HOME/static-libs/openssl-1.1.1a"
Vamos construir as bibliotecas estáticas em static-libs-source:
$ mkdir static-libs-source
$ cd static-libs-source
Faça o download e construa o PCRE com suporte a propriedades Unicode:
$ curl --remote-name [Link]
$ tar xf [Link]
$ cd pcre2-10.39
$ ./configure --prefix="$PCRE_PREFIX" --disable-shared --enable-static --enable-unicode-properties
$ make
$ make check
$ make install
$ cd ..
Faça o download e construa o OpenSSL:
$ curl --remote-name [Link]
$ tar xf [Link]
74
$ cd openssl-1.1.1a
$ ./Configure --prefix="$OPENSSL_PREFIX" --openssldir="$OPENSSL_PREFIX" --api=1.1.0 no-shared no-capieng n
$ make
$ make test
$ make install_sw
$ cd ..
Faça o download do fonte do Zabbix e construa o agente:
$ git clone [Link]
$ cd zabbix
$ ./[Link]
$ ./configure --sysconfdir=/usr/local/etc/zabbix --enable-agent --enable-ipv6 --with-libpcre2="$PCRE_PREFI
$ make
$ make install
Construindo binários de agentes com bibliotecas estáticas com GnuTLS
O GnuTLS depende do back-end de criptografia Nettle e da biblioteca aritmética GMP. Em vez de usar a biblioteca GMP completa,
este guia usará o mini-gmp, que é incluído na Nettle.
Ao compilar GnuTLS e Nettle, é recomendado executar make check após a compilação bem-sucedida. Mesmo que a construção
tenha sido bem-sucedida, os testes às vezes falha. Se este for o caso, os problemas devem ser pesquisados e resolvido antes de
continuar.
Vamos assumir que as bibliotecas estáticas do PCRE, Nettle e GnuTLS serão instaladas em $HOME/static-libs. Utilizamores o
PCRE2 10.39, Nettle 3.4.1 e GnuTLS 3.6.5.
$ PCRE_PREFIX="$HOME/static-libs/pcre2-10.39"
$ NETTLE_PREFIX="$HOME/static-libs/nettle-3.4.1"
$ GNUTLS_PREFIX="$HOME/static-libs/gnutls-3.6.5"
Vamos construir bibliotecas estáticas em static-libs-source:
$ mkdir static-libs-source
$ cd static-libs-source
Faça o download e construa o Nettle:
$ curl --remote-name [Link]
$ tar xf [Link]
$ cd nettle-3.4.1
$ ./configure --prefix="$NETTLE_PREFIX" --enable-static --disable-shared --disable-documentation --disable
$ make
$ make check
$ make install
$ cd ..
Faça o download e construa o GnuTLS:
$ curl --remote-name [Link]
$ tar xf [Link]
$ cd gnutls-3.6.5
$ PKG_CONFIG_PATH="$NETTLE_PREFIX/lib/pkgconfig" ./configure --prefix="$GNUTLS_PREFIX" --enable-static --d
$ make
$ make check
$ make install
$ cd ..
Faça o download do fonte do Zabbix e construa o agente:
$ git clone [Link]
$ cd zabbix
$ ./[Link]
$ CFLAGS="-Wno-unused-command-line-argument -framework Foundation -framework Security" \
> LIBS="-lgnutls -lhogweed -lnettle" \
> LDFLAGS="-L$GNUTLS_PREFIX/lib -L$NETTLE_PREFIX/lib" \
> ./configure --sysconfdir=/usr/local/etc/zabbix --enable-agent --enable-ipv6 --with-libpcre2="$PCRE_PREFI
$ make
$ make install
75
4 Instalação via pacote
From Zabbix official repository
Zabbix SIA fornece pacotes oficiais para RPM and DEB:
• Red Hat Enterprise Linux/CentOS
• Debian/Ubuntu/Raspbian
• SUSE Linux Enterprise Server
Pacotes para yum/dnf, apt e zypper e outras várias distribuições de sistemas operacionais estão disponíveis em [Link].
Nota, embora algumas distribuições de sistema operacional (em particular distribuições baseadas em Debian) forneçam seus
próprios pacotes, esses pacotes não são suportados pela Zabbix. Pacotes fornecidos por terceiros podem ser disponibilizados com
atraso, não ter os recusos mais recentes e não conter correções de bugs. Então é recomendado o uso somente de pacotes oficiais
[Link]. Se você já utilizou pacotes não oficiais, veja essa nota upgrading Zabbix packages from OS repositories.
1 Sistema operacional Red Hat Enterprise Linux
Visão geral
Os pacotes oficiais Zabbix 6.0 LTS para Red Hat Enterprise Linux e Oracle Linux estão disponíveis em Zabbix website.
Pacotes estão disponíveis com suporte a banco de dados MySQL/PostgreSQL e servidor web Apache/Nginx.
Pacotes Zabbix agent e utilitários Zabbix get e Zabbix sender estão disponíveis no Repositório Oficial Zabbix para RHEL 9, RHEL
8, RHEL 7, RHEL 6, e RHEL 5.
O Repositório Oficial Zabbbix também fornece pacotes fping, iksemel e libssh2. Esses pacotes estão localizados no diretório
non-supported .
Attention:
O repositório EPEL para EL9 também fornece os pacotes Zabbix. Se ambos estiverem instalados (repositório oficial Zabbix
e EPEL repositórios), os pacotes do Zabbix no EPEL must be (devem ser) excluídos, adicionando a seguinte cláusula ao
arquivo de configuração do repositório EPEL /etc/[Link].d/:
[epel]
...
excludepkgs=zabbix*
Notas de instalação
Consulte as instruções de instalação installation instructions por plataforma na página de download para:
• instalar repositório
• instalar servidor/agente/frontend
• criar banco de dados inicial, importar dados inicial
• configurar bancos dados para servidor Zabbix
• configurar PHP para Zabbix frontend
• iniciar processos servidor/agente
• configurar Zabbix frontend
Se você desejar executar o agente Zabbix como raíz, consulte em Running agent as root.
O processo de serviço web do Zabbix, que é usado para scheduled reportgeneration, requer o navegador Google Chrome. O
navegador não está incluso nos pacotes e precisa ser instalado manualmente.
Importar dados com Timescale DB
Com o TimescaleDB, além do comando de importação para o PostgreSQL, também execute:
cat /usr/share/zabbix-sql-scripts/postgresql/[Link] | sudo -u zabbix psql zabbix
Warning:
O TimescaleDB somente é suportado com servidor Zabbix.
PHP 7.2
O Zabbix frontend requer a versão PHP 7.2 or newer.
76
Configuração SELinux
Zabbix utiliza a comunicação socket-based inter-process. Nos sistemas em que o SELinux está habilitado, pode ser necessário
adicionar regras de SELinux para permitir que o Zabbix crie e use soquetes de domínio UNIX no diretório SocketDir. Atualmente,
os arquivos de soquetes são usados pelo servidor (alerta, pré-processamento, IPMI) e proxy (IPMI). Os arquivos de soquete são
persistentes, isso significa que eles estão presentes enquanto o processo está sendo executado.
Tendo o status SELinux habilitado no modo de aplicação, você precisa executar os seguintes comandos para habilitar a comunicação
entre o Zabbix frontend e o servidor:
RHEL 7 and later:
setsebool -P httpd_can_connect_zabbix on
Se o banco de dados for acessível pela rede (incluir ’localhost’ em caso de PostgreSQL), você precisa autorizar a conexão do Zabbix
frontend com a bases de dados também:
setsebool -P httpd_can_network_connect_db on
RHEL prior to 7:
setsebool -P httpd_can_network_connect on
setsebool -P zabbix_can_network on
Uma vez que a configuração de frontend e SELinux estiver feita, reinicie o servidor Apache:
service httpd restart
Além disso, o Zabbix disponibiliza o pacote zabbix-selinux-policy como parte dos pacotes RPM de origem para RHEL 8 e RHEL 7.
Este pacote fornece uma política padrão básica para o SELinux e permite que os componentes do Zabbix funcionem out-of-the-box
(fora da caixa), permitindo que o Zabbix crie e use soquetes e habilite a conexão do https com o PostgreSQL (usado pelo frontend).
O arquivo de origem zabbix_policy.te contém as seguintes regras:
module zabbix_policy 1.2;
require {
type zabbix_t;
type zabbix_port_t;
type zabbix_var_run_t;
type postgresql_port_t;
type httpd_t;
class tcp_socket name_connect;
class sock_file { create unlink };
class unix_stream_socket connectto;
}
#============= zabbix_t ==============
allow zabbix_t self:unix_stream_socket connectto;
allow zabbix_t zabbix_port_t:tcp_socket name_connect;
allow zabbix_t zabbix_var_run_t:sock_file create;
allow zabbix_t zabbix_var_run_t:sock_file unlink;
allow httpd_t zabbix_port_t:tcp_socket name_connect;
#============= httpd_t ==============
allow httpd_t postgresql_port_t:tcp_socket name_connect;
Este pacote foi criado para evitar que os usuários desativem o SELinux por devido à complexidade da configuração. O pacote
contém a política padrão que é o suficiente para acelerar a implantação e configuração do Zabbix. Para o nível máximo de
segurança, é recomendável configurar as definições personalizadas do SELinux.
Instalação do proxy
Uma vez que o repositório requisitado é adicionado, você pode instalar o proxy do Zabbix executando:
dnf install zabbix-proxy-mysql zabbix-sql-scripts
Substitua ’mysql’ nos comandos com ’pgsql’ para usar PostgreSQL, ou com ’sqlite3’ para utilizar SQLite3 (somente proxy).
O pacote ’zabbix-sql-scripts’ contém esquemas de banco de dados para todos os sistemas de gerenciamento de bancos de dados
suportados, tanto para o servidor Zabbix quanto para o proxy Zabbix, e será utilizado para importação de dados.
Criando base de dados
77
[Criar] (/manual/appendix/install/db_scripts) uma base de dados separada para o Zabbix proxy. O servidor Zabbix e o proxy Zabbix
não podem usar a mesma base de dados. Se elas são instaladas no mesmo host, a base da dados do proxy deve ter um nome
diferente.
Importando dados
Importar esquema inicial:
cat /usr/share/zabbix-sql-scripts/mysql/[Link] | mysql -uzabbix -p zabbix
Para proxy com PostgreSQL (ou SQLite):
cat /usr/share/zabbix-sql-scripts/postgresql/[Link] | sudo -u zabbix psql zabbix
cat /usr/share/zabbix-sql-scripts/sqlite3/[Link] | sqlite3 [Link]
Configurar banco de dados para o proxy Zabbix
Editar zabbix_proxy.conf:
# vi /etc/zabbix/zabbix_proxy.conf
DBHost=localhost
DBName=__SOFIA_PII_2__
DBUser=zabbix
DB[SEGREDO_REMOVIDO]
No DBName para o proxy Zabbix, utilize um banco de dados separado do servidor Zabbix.
No DBPassword, utilize a senha do banco de dados Zabbix para o MySQL; a senha do usuário do PostgreSQL para PostgreSQL.
Utilize DBHost= com PostgreSQL. Você pode optar por manter a configuração padrão DBHost=localhost (ou um endereço de
IP), mas isso fará com que o PostgreSQL utilize um soquete de rede para se conectar com o Zabbix. Consulte SELinux configuration
para instruções.
Iniciando o processo do proxy Zabbix
Para iniciar um processo do proxy Zabbix e faze-lo iniciar automaticamente durante a inicialização do sistema:
service zabbix-proxy start
systemctl enable zabbix-proxy
Configuração Frontend
O proxy Zabbix não possui um frontend; ele se comunica somente com o servidor Zabbix.
Instalação do Java gateway
É necessário instalar o Java gateway somente se você seja monitorar as aplicações JMX. O gateway Java é leve e não requer um
banco de dados.
Uma vez que o repositório necessário é adicionado, você pode instalar o Zabbix Java gateway executando:
dnf install zabbix-java-gateway
Prossiga para setup para mais detalhes da configuração e execução do Java gateway.
Instalando pacotes debuginfo
Os pacotes Debuginfo atualmente estão disponíveis para as versões 7, 6 e 5 do RHE.
Para habilitar o repositório debuginfo, editar o arquivo /etc/[Link].d/[Link]. Altere enabled=0 para enabled=1 para o
repositório zabbix-debuginfo.
[zabbix-debuginfo]
name=__SOFIA_PII_3__
baseurl=[Link]
enabled=0
gpgkey=[Link]
gpgcheck=1
Isso permitirá que você instale o pacote zabbix-debuginfo.
dnf install zabbix-debuginfo
Esse pacote único contém informações debug para todos os componentes binários do Zabbix.
78
2 Debian/Ubuntu/Raspbian
Visão geral
Pacotes oficiais do Zabbix estão disponíveis para:
Debian 10 (Buster) Download
Debian 9 (Stretch) Download
Debian 8 (Jessie) Download
Ubuntu 20.04 (Focal Fossa) LTS Download
Ubuntu 18.04 (Bionic Beaver) LTS Download
Ubuntu 16.04 (Xenial Xerus) LTS Download
Ubuntu 14.04 (Trusty Tahr) LTS Download
Raspbian (Buster) Download
Raspbian (Stretch) Download
Os pacotes estão disponíveis com qualquer banco de dados MySQL/PostgreSQL e Suporte ao servidor da web Apache/Nginx.
Attention:
O Zabbix 6.0 ainda não foi lançado. Os links de download levar a pacotes pré-6.0.
Notas sobre a instalação
Veja o installation instructions por plataforma na página de download para:
• instalando o repositório
• instalando servidor / agente / frontend
• criação de banco de dados inicial, importação de dados iniciais
• configurar banco de dados para o servidor Zabbix
• configurar o PHP para o frontend Zabbix
• iniciar processos de servidor / agente
• configurando o frontend do Zabbix
Se você deseja executar o agente Zabbix como root, consulte running agent as root.
Processo de serviço da web Zabbix, que é usado para scheduled report generation, requer o navegador Google Chrome. O naveg-
ador não está incluído em pacotes e deve ser instalado manualmente.
Importando dados com Timescale DB
Com o TimescaleDB, além do comando de importação para PostgreSQL, também corre:
# zcat /usr/share/doc/zabbix-sql-scripts/postgresql/[Link] | sudo -u zabbix psql zabbix
Warning:
TimescaleDB é compatível com o servidor Zabbix só.
PHP 7.2
O frontend do Zabbix requer a versão PHP 7.2 ou mais recente começando com Zabbix 5.0.
See instructions por instalando o frontend do Zabbix em distribuições com versões do PHP abaixo de 7.2.
Configuração SELinux
Veja SELinux configuration para RHEL/CentOS.
Após a configuração do frontend e do SELinux, reinicie o Apache servidor web:
# service apache2 restart
Instalação Proxy
Assim que o repositório necessário for adicionado, você pode instalar o proxy Zabbix por Executando:
# apt install zabbix-proxy-mysql
Substitua ’mysql’ no comando por ’pgsql’ para usar PostgreSQL, ou com ’sqlite3’ para usar SQLite3.
Criando banco de dados
79
Create um banco de dados separado para Proxy Zabbix.
O servidor Zabbix e o proxy Zabbix não podem usar o mesmo banco de dados. Se eles são instalado no mesmo host, o banco de
dados proxy deve ter um diferente nome.
Importando dados
Importar esquema inicial:
# zcat /usr/share/doc/zabbix-sql-scripts/mysql/[Link] | mysql -uzabbix -p zabbix
Para proxy com PostgreSQL (ou SQLite):
# zcat /usr/share/doc/zabbix-sql-scripts/postgresql/[Link] | sudo -u zabbix psql zabbix
# zcat /usr/share/doc/zabbix-sql-scripts/sqlite3/[Link] | sqlite3 [Link]
Configurar banco de dados para Zabbix proxy
Edit zabbix_proxy.conf:
# vi /etc/zabbix/zabbix_proxy.conf
DBHost=localhost
DBName=__SOFIA_PII_2__
DBUser=zabbix
DB[SEGREDO_REMOVIDO]
Em DBName para Zabbix proxy, use um banco de dados separado do servidor Zabbix.
Em DBPassword, use a senha do banco de dados Zabbix para MySQL; Usuário PostgreSQL senha para PostgreSQL.
Use DBHost = com PostgreSQL. Você pode querer manter o padrão definir DBHost = localhost (ou um endereço IP), mas isso
faria O PostgreSQL usa um soquete de rede para se conectar ao Zabbix. Consulte o respective section para RHEL/CentOS para
obter instruções.
Iniciando o processo de Zabbix proxy
Para iniciar um processo de Zabbix proxy e fazê-lo iniciar na inicialização do sistema:
# systemctl restart zabbix-proxy
# systemctl enable zabbix-proxy
Configuração de front-end
Um Zabbix proxy não tem front-end; ele se comunica com o Zabbix servidor apenas.
Instalação do Java gateway
É necessário instalar Java gateway somente se você deseja monitorar aplicativos JMX. O gateway Java é leve e não requer um
banco de dados.
Assim que o repositório necessário for adicionado, você pode instalar o Zabbix Java gateway executando:
# apt install zabbix-java-gateway
Prossiga para setup para mais detalhes sobre como configurar e executar o Java gateway.
3 SUSE Linux Enterprise Server
Visão Geral
Pacotes oficiais Zabbix estão disponíveis para:
SUSE Linux Enterprise Server 15 Download
SUSE Linux Enterprise Server 12 Download
Attention:
O Zabbix 6.0 ainda não foi lançado. Os links de download são para pacotes anteriores à versão 6.0.
Note:
O modo de criptografia Verify CA não funciona em SLES 12 (todos os minor versions) com MySQL devido bibliotecas mais
antigas de MySQL.
80
Adicionando repositório Zabbix
Instale o pacote de configuração do repositório. Este pacote contém arquivos de configuração do YUM (gerenciador de pacotes).
SLES 15:
# rpm -Uvh --nosignature [Link]
# zypper --gpg-auto-import-keys refresh 'Zabbix Official Repository'
SLES 12:
# rpm -Uvh --nosignature [Link]
# zypper --gpg-auto-import-keys refresh 'Zabbix Official Repository'
Por favor, note que o processo de web service do Zabbix usado para a geração de relatório agendado requer o navegador Google
Chrome. O navegador não está incluso nos pacotes e deve ser instalado manualmente.
Instalação Server/Frontend/Agent
Para instalar o Zabbix Server/Frontend/Agent com suporte ao MySQL:
# zypper install zabbix-server-mysql zabbix-web-mysql zabbix-apache-conf zabbix-agent
Substitua ’apache’ no comando por ’nginx’ se estiver usando pacote para Nginx Web Server. Veja também: Configuração do Nginx
para Zabbix no SLES 12/15.
Substitua ’zabbix-agent’ por ’zabbix-agent2’ nestes comandos se estiver usando Zabbix Agent 2 (apenas SLES 15 SP1+).
Para instalar o Zabbix Proxy com suporte ao MySQL:
# zypper install zabbix-proxy-mysql
Substitua ’mysql’ nos comandos por ’pgsql’ para usar PostgreSQL.
Criando Banco de Dados
Para os processos do Zabbix Server e Proxy um banco de dados é exigido. Ele não é necessário para executar o Zabbix Agent.
Warning:
Bancos de dados isolados são necessários para o Zabbix Server e Zabbix Proxy; eles não podem utilizar o mesmo banco de
dados. Portanto, se eles estiverem instalados na mesma máquina, seus bancos de dados devem ser criados com nomes
diferentes!
Crie os bancos de dados usando as instruções disponíveis para MySQL ou PostgreSQL.
Importando dados
Agora importe o schema inicial e os dados para o server com MySQL:
# zcat /usr/share/doc/packages/zabbix-sql-scripts/mysql/[Link] | mysql -uzabbix -p zabbix
Será solicitado que você informe a senha para o banco de dados recém-criado.
Com PostgreSQL:
# zcat /usr/share/doc/packages/zabbix-sql-scripts/postgresql/[Link] | sudo -u zabbix psql zabbix
Com TimescaleDB, em adição ao comando anterior, também execute:
# zcat /usr/share/doc/packages/zabbix-sql-scripts/postgresql/[Link] | sudo -u <username> psql
Warning:
TimescaleDB é suportado apenas com Zabbix server.
Para o proxy, importe o schema inicial:
# zcat /usr/share/doc/packages/zabbix-sql-scripts/mysql/[Link] | mysql -uzabbix -p zabbix
Para proxy com PostgreSQL:
# zcat /usr/share/doc/packages/zabbix-sql-scripts/postgresql/[Link] | sudo -u zabbix psql zabbix
Configure o banco de dados para Zabbix Server/Proxy
Edite /etc/zabbix/zabbix_server.conf (e zabbix_proxy.conf) para usar seu respectivo banco de dados. Por exemplo:
81
# vi /etc/zabbix/zabbix_server.conf
DBHost=localhost
DBName=__SOFIA_PII_2__
DBUser=zabbix
DB[SEGREDO_REMOVIDO]
Em DBPassword use a senha do banco de dados do Zabbix no MySQL; senha do usuário PostgreSQL se estiver utilizando banco de
dados PostgreSQL.
Use DBHost= com PostgreSQL. Você poderia querer manter a configuração padrão DBHost=localhost (ou um endereço IP), mas
isto faria o PostgreSQL usar um socket de rede para se conectar ao Zabbix.
Configuração do Zabbix Frontend
Dependendo do Web Server utilizado (Apache/Nginx) edite o arquivo de configuração correspondente para o Zabbix Frontend:
• Para o Apache encontre o arquivo de configuração em /etc/apache2/conf.d/[Link]. Algumas definições de PHP
já estão configuradas. Mas é necessário descomentar a definição ”[Link]” e informar o timezone adequado para
você.
php_value max_execution_time 300
php_value memory_limit 128M
php_value post_max_size 16M
php_value upload_max_filesize 2M
php_value max_input_time 300
php_value max_input_vars 10000
php_value always_populate_raw_post_data -1
# php_value [Link] Europe/Riga
• O pacote zabbix-nginx-conf instala um servidor Nginx separado para o Zabbix Frontend. Seu arquivo de configuração está
localizado em /etc/nginx/conf.d/[Link]. Para o Zabbix Frontend funcionar, é necessário descomentar e config-
urar as diretivas listen e/ou server_name.
# listen 80;
# server_name [Link];
• O Zabbix usa seu próprio pool de conexão php-fpm dedicado com Nginx:
Ser aquivo de configuração está localizado em /etc/php7/fpm/php-fpm.d/[Link]. Algumas definições de PHP já estão
configuradas. Mas é necessário descomentar a definição ”[Link]” e informar o timezone adequado para você.
php_value[max_execution_time] = 300
php_value[memory_limit] = 128M
php_value[post_max_size] = 16M
php_value[upload_max_filesize] = 2M
php_value[max_input_time] = 300
php_value[max_input_vars] = 10000
; php_value[[Link]] = Europe/Riga
Agora você está pronto para prosseguir com os passos de instalação do Frontend que lhe permitirão o acesso ao seu Zabbix
recém-instalado.
Note que um Zabbix Proxy não tem um frontend; ele se comunica apenas com o Zabbix Server.
Iniciando o processo Zabbix Server/Agent
Inicie os processos do Zabbix Server e Agent e certifique-se de que iniciem com o boot do sistema.
Com Apache Web Server:
# systemctl restart zabbix-server zabbix-agent apache2 php-fpm
# systemctl enable zabbix-server zabbix-agent apache2 php-fpm
Substitua ’apache2’ por ’nginx’ para Nginx Web Server.
Instalando pacotes de debuginfo
Para habilitar o repositório de debuginfo edite o arquivo /etc/zypp/repos.d/[Link]. Altere enabled=0 para enabled=1 no
repositório zabbix-debuginfo.
[zabbix-debuginfo]
name=__SOFIA_PII_4__
type=rpm-md
82
baseurl=[Link]
gpgcheck=1
gpgkey=[Link]
enabled=0
update=1
Isto permitirá que você instale pacotes zabbix-<component>-debuginfo.
4 Instalação agente Windows por MSI
Visão Geral
O agente Zabbix Windows pode ser instalado a partir do instalador de pacote MSI do Windows (32 bits ou 64 bits) disponíveis em
download.
O pacote 32-bit não pode ser instalado em Windows 64-bits
Todos os pacotes vêm com suporte TLS, no entanto, configurar TLS é opcional.
Tanto a IU quanto a instalação baseada na linha de comando são suportadas.
Etapas de instalação
Para instalar, clique duas vezes no arquivo MSI baixado.
83
Aceite a licença para prosseguir para a próxima etapa.
Especifique
