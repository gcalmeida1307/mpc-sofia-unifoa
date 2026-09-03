# Manual do usuário

Fonte: https://www.zabbix.com/documentation/current/pt/manual
Capturado em: 2026-09-01T15:38:10.594051+00:00
Páginas no domínio: 10

## Manual do usuário
URL: https://www.zabbix.com/documentation/current/pt/manual

Manual do usuário
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
Bem-vindo à documentação do Zabbix
Seu recurso principal para trabalhar com o monitoramento do Zabbix, desde configurações básicas até configurações avançadas. Este manual cobre tudo o que é necessário para instalar, configurar e operar o Zabbix.
Novidades no Zabbix 7.4
Primeiros passos com o Zabbix
Instalação
Instruções passo a passo para instalar o Zabbix na plataforma de sua preferência, abrangendo vários sistemas operacionais e configurações de banco de dados.
Requisitos
Uma lista de plataformas suportadas e pré-requisitos de software para ajudá-lo a preparar seu ambiente para uma implantação bem-sucedida do Zabbix.
Guias de início rápido
Guias concisos e orientados a tarefas que o conduzem pelos conceitos básicos — desde os primeiros passos de configuração até o recebimento do seu primeiro alerta de problema.
Zabbix Cloud
Comece a usar o Zabbix Cloud
Instruções guiadas para colocar sua instância do Zabbix Cloud em funcionamento rapidamente, incluindo a configuração inicial e a conexão dos seus dispositivos monitorados.
Zabbix Cloud vs. on-premises
Compare as diferenças de gerenciamento, escalabilidade e manutenção entre as duas implantações e descubra qual pode suportar seu fluxo de trabalho de forma mais eficiente.
Explore o Zabbix Cloud
Obtenha uma visão geral do Zabbix Cloud, incluindo seus principais recursos, vantagens e o que está incluído na assinatura. Para perguntas comuns sobre configuração e uso, consulte o FAQ.
Central do desenvolvedor
Módulos do frontend
Guias e referências para construir módulos personalizados que estendem ou modificam o frontend do Zabbix para atender a casos de uso específicos.
Widgets
Uma análise da estrutura e lógica dos widgets, com instruções para criar elementos personalizados do dashboard adaptados às suas necessidades.
Plugins
Uma visão geral sobre como desenvolver e gerenciar plugins do Zabbix para estender a funcionalidade ou integrar com sistemas externos.
Comunidade e outros recursos
Fóruns Zabbix
Um espaço para trocar ideias, encontrar soluções e compartilhar experiências em todos os níveis de conhecimento do Zabbix.
Blog do Zabbix
Notícias, tutoriais e estudos de caso selecionados pela equipe do Zabbix e colaboradores da comunidade.
Vídeos tutoriais
Uma biblioteca de vídeos com demonstrações, discussões e dicas para ajudá-lo a aproveitar ao máximo o Zabbix.
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 20 API
URL: https://www.zabbix.com/documentation/current/pt/manual/api

20 API
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
20 API
Nesta página
20 API
Visão geral
Estrutura
Realizando requisições
Autenticação
Métodos de autorização
Por cabeçalho "Authorization"
Por cookie do Zabbix
Fluxo de trabalho de exemplo
Recuperando hosts
Criando um novo item
Criando múltiplos triggers
Atualizando um item
Atualizando múltiplos triggers
Tratamento de erros
Versões da API
Leitura adicional
20 API
Visão geral
A API do Zabbix permite recuperar e modificar programaticamente a configuração do Zabbix e fornece acesso a dados históricos. Ela é amplamente usada para:
Criar novos aplicativos para trabalhar com o Zabbix.
Integrar o Zabbix a um software de terceiros.
Automatizar tarefas rotineiras.
A API do Zabbix é uma API baseada em HTTP e é fornecida como parte do web frontend. Ela usa o protocolo JSON-RPC 2.0, o que significa duas coisas:
A API consiste em um conjunto de métodos separados.
As solicitações e respostas entre os clientes e a API são codificadas usando o formato JSON.
Para mais informações sobre o protocolo e o JSON, consulte a
especificação JSON-RPC 2.0
e a
página inicial do formato JSON
.
Para mais informações sobre a integração da funcionalidade do Zabbix em seus aplicativos Python, consulte
Biblioteca Python para Zabbix
.
O acesso do usuário no Zabbix, incluindo tanto a configuração quanto os dados históricos, depende do
tipo de usuário
, da
função de usuário
atribuída e dos
grupos de usuários
.
Estrutura
A API consiste em vários métodos que, nominalmente, são agrupados em APIs separadas. Cada um dos métodos executa uma tarefa específica. Por exemplo, o método
host.create
pertence à
API de
host
e é usado para criar novos hosts. Historicamente, as APIs às vezes são chamadas de "classes".
A maioria das APIs contém pelo menos quatro métodos:
get
,
create
,
update
e
delete
para recuperar, criar, atualizar e excluir dados, respectivamente, mas algumas APIs podem fornecer um conjunto totalmente diferente de métodos.
Realizando requisições
Depois de configurar o frontend, você pode usar requisições HTTP remotas para chamar a API. Para isso, você precisa enviar requisições HTTP POST para o arquivo
api_jsonrpc.php
localizado no diretório do frontend.
Por exemplo, se o seu frontend do Zabbix estiver instalado em
https://example.com/zabbix
, uma requisição HTTP para chamar o método
apiinfo.version
pode ser assim:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'
A requisição deve ter o cabeçalho
Content-Type
definido como um destes valores:
application/json-rpc
,
application/json
ou
application/jsonrequest
.
O objeto da requisição deve conter as seguintes propriedades:
jsonrpc
- a versão do protocolo JSON-RPC usada pela API (a Zabbix API implementa a versão 2.0 do JSON-RPC);
method
- o método da API que está sendo chamado;
params
- os parâmetros que serão passados para o método da API;
id
- um identificador arbitrário da requisição (se omitido, a API trata a requisição como uma
notificação
).
Se a requisição estiver correta, a resposta retornada pela API deve ser semelhante a esta:
{
"jsonrpc"
:
"2.0"
,
"result"
:
"7.4.0"
,
"id"
:
1
}
O objeto de resposta, por sua vez, contém as seguintes propriedades:
jsonrpc
- a versão do protocolo JSON-RPC;
result
- os dados retornados pelo método;
id
- um identificador da requisição correspondente.
Autenticação
Para acessar quaisquer dados no Zabbix, você precisa:
Usar um token de API existente criado no frontend do Zabbix, na seção
Users
>
API tokens
, ou criado usando a
Token API
.
Usar um token de autenticação obtido com o método
user.login
.
Por exemplo, se você quisesse obter um novo token de autenticação ao fazer login como um usuário padrão
Admin
, uma solicitação JSON seria assim:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}'
Se você fornecer as credenciais corretamente, a resposta retornada pela API deverá conter o token de autenticação do usuário:
{
"jsonrpc"
:
"2.0"
,
"result"
:
"0424bd59b807674191e7d77572075f33"
,
"id"
:
1
}
Métodos de autorização
Por cabeçalho "Authorization"
Todas as solicitações da API exigem autenticação ou um token de API. Você pode fornecer as credenciais usando o cabeçalho Authorization na solicitação:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer 0424bd59b807674191e7d77572075f33'
Se você estiver enfrentando problemas de autenticação, consulte
Encaminhamento do cabeçalho Authorization
.
A API do Zabbix aceita cabeçalhos de forma case-insensitive (por exemplo,
authorization
,
Authorization
e
AUTHORIZATION
são tratados da mesma forma).
O cabeçalho Authorization é suportado em solicitações de origem cruzada (
CORS
).
Por cookie do Zabbix
Um cookie
"zbx_session"
é usado para autorizar uma solicitação de API da interface do Zabbix realizada usando JavaScript (de um módulo ou de um widget personalizado).
Fluxo de trabalho de exemplo
A seção a seguir orienta você por vários exemplos de uso com mais detalhes.
Recuperando hosts
Agora você tem um token de autenticação de usuário válido (representado como uma variável nos exemplos a seguir) que pode ser usado para acessar os dados no Zabbix. Por exemplo, você pode usar o método
host.get
para recuperar os IDs, nomes dos hosts e interfaces de todos os
hosts
configurados:
Solicitação:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data @data.json
data.json
é um arquivo que contém uma consulta JSON. Em vez de um arquivo, você pode passar a consulta no argumento
--data
.
data.json
{
"jsonrpc"
:
"2.0"
,
"method"
:
"host.get"
,
"params"
: {
"output"
: [
"hostid"
,
"host"
],
"selectInterfaces"
: [
"interfaceid"
,
"ip"
] },
"id"
:
2
}
O objeto de resposta conterá os dados solicitados sobre os hosts:
{
"jsonrpc"
:
"2.0"
,
"result"
: [ {
"hostid"
:
"10084"
,
"host"
:
"Zabbix server"
,
"interfaces"
: [ {
"interfaceid"
:
"1"
,
"ip"
:
"127.0.0.1"
} ] } ],
"id"
:
2
}
Por motivos de desempenho, é sempre recomendável listar as propriedades do objeto que você deseja recuperar. Assim, você evitará recuperar tudo.
Criando um novo item
Agora, crie um novo
item
no host "Zabbix server" usando os dados que você obteve da solicitação
host.get
anterior. Isso pode ser feito usando o método
item.create
:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"item.create","params":{"name":"Free disk space on /home/joe/","key_":"vfs.fs.size[/home/joe/,free]","hostid":"10084","type":0,"value_type":3,"interfaceid":"1","delay":30},"id":3}'
Uma resposta bem-sucedida conterá o ID do item recém-criado, que pode ser usado para referenciar o item nas solicitações a seguir:
{
"jsonrpc"
:
"2.0"
,
"result"
: {
"itemids"
: [
"24759"
] },
"id"
:
3
}
O método
item.create
, assim como outros
métodos de criação
, também pode aceitar arrays de objetos e criar vários items com uma única chamada da API.
Criando múltiplos triggers
Assim, se os
métodos de criação
aceitarem arrays, você pode adicionar vários
triggers
, por exemplo, este:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"trigger.create","params":[{"description":"Processor load is too high on {HOST.NAME}","expression":"last(/Linux server/system.cpu.load[percpu,avg1])>5"},{"description":"Too many processes on {HOST.NAME}","expression":"avg(/Linux server/proc.num[],5m)>300"}],"id":4}'
A resposta bem-sucedida conterá os IDs dos triggers recém-criados:
{
"jsonrpc"
:
"2.0"
,
"result"
: {
"triggerids"
: [
"17369"
,
"17370"
] },
"id"
:
4
}
Atualizando um item
Ative um item definindo seu status como
0
:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"item.update","params":{"itemid":"10092","status":0},"id":5}'
A resposta bem-sucedida conterá o ID do item atualizado:
{
"jsonrpc"
:
"2.0"
,
"result"
: {
"itemids"
: [
"10092"
] },
"id"
:
5
}
O método
item.update
, assim como outros
métodos de atualização
, também pode aceitar arrays de objetos e atualizar vários itens com uma única chamada da API.
Atualizando múltiplos triggers
Ative múltiplos triggers definindo seus status como
0
:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"trigger.update","params":[{"triggerid":"13938","status":0},{"triggerid":"13939","status":0}],"id":6}'
A resposta bem-sucedida conterá os IDs dos triggers atualizados:
{
"jsonrpc"
:
"2.0"
,
"result"
: {
"triggerids"
: [
"13938"
,
"13939"
] },
"id"
:
6
}
Este é o método preferencial de atualização. Alguns métodos da API, como o
host.massupdate
, permitem escrever um código mais simples. No entanto, não é recomendável usar esses métodos, pois eles serão removidos nas futuras versões.
Tratamento de erros
Até o momento, tudo o que você tentou funcionou corretamente. Mas o que aconteceria se você tentasse fazer uma chamada incorreta para a API? Tente criar outro host chamando
host.create
, mas omitindo o parâmetro obrigatório
groups
:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"host.create","params":{"host":"Linux server","interfaces":[{"type":1,"main":1,"useip":1,"ip":"192.168.3.1","dns":"","port":"10050"}]},"id":7}'
A resposta então conterá uma mensagem de erro:
{
"jsonrpc"
:
"2.0"
,
"error"
: {
"code"
:
-32602
,
"message"
:
"Invalid params."
,
"data"
:
"No groups for host \"Linux server\"."
},
"id"
:
7
}
Se ocorrer um erro, em vez da propriedade
result
, o objeto de resposta conterá a propriedade
error
com os seguintes dados:
code
- um código de erro;
message
- um breve resumo do erro;
data
- uma mensagem de erro mais detalhada.
Erros podem ocorrer em vários casos, como uso de valores de entrada incorretos, expiração de sessão ou tentativa de acessar objetos inexistentes. Sua aplicação deve ser capaz de lidar com esses tipos de erro de forma adequada.
Versões da API
Para simplificar o versionamento da API, desde o Zabbix 2.0.4, a versão da API corresponde à versão do próprio Zabbix. Você pode usar o método
apiinfo.version
para descobrir a versão da API com a qual você está trabalhando. Isso pode ser útil para ajustar sua aplicação para usar recursos específicos de uma determinada versão.
O Zabbix garante compatibilidade retroativa dos recursos dentro de uma versão principal. Ao fazer alterações incompatíveis com versões anteriores entre lançamentos principais, o Zabbix normalmente deixa os recursos antigos como obsoletos no próximo lançamento e só os remove no lançamento seguinte. Ocasionalmente, o Zabbix pode remover recursos entre versões principais sem fornecer qualquer compatibilidade retroativa. É importante que você nunca dependa de recursos obsoletos e migre para alternativas mais recentes o quanto antes.
Você pode acompanhar todas as alterações feitas na API no
changelog da API
.
Leitura adicional
Agora, você já tem conhecimento suficiente para começar a trabalhar com a Zabbix API; no entanto, não pare por aqui. Para leitura adicional, recomendamos que você consulte a
lista de APIs disponíveis
.
What’s next?
Apêndice 1. Comentário de referência
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 7 Configuração
URL: https://www.zabbix.com/documentation/current/pt/manual/config

7 Configuração
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
7 Configuração
Nesta página
7 Configuração
Visão geral
Principais tarefas de configuração
7 Configuração
Visão geral
A configuração no Zabbix envolve especificar quais hosts e sistemas monitorar, definir quais dados coletar e estabelecer como as notificações são entregues quando ocorrem problemas.
Use a barra lateral para navegar pelos aspectos de configuração relevantes.
Principais tarefas de configuração
Configurar um novo host ou grupo de hosts →
Hosts e grupos de hosts
Definir quais dados coletar dos hosts →
Items
Criar regras para detectar problemas →
Detecção de problemas com triggers
Configurar como as notificações são entregues →
Notificações em eventos
Exibir dados de monitoramento por meio de dashboards, gráficos e mapas →
Visualização
Reutilizar configurações em vários hosts →
Templates e grupos de templates
,
Templates prontos para uso
Controlar o acesso e as permissões dos usuários →
Usuários e grupos de usuários
What’s next?
1 Hosts e grupos de hosts
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 23 Guias de referência rápida
URL: https://www.zabbix.com/documentation/current/pt/manual/guides

23 Guias de referência rápida
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
23 Guias de referência rápida
Nesta página
23 Guias de referência rápida
Visão geral
23 Guias de referência rápida
Visão geral
Esta seção da documentação contém receitas rápidas para configurar o Zabbix para alguns objetivos de monitoramento comumente necessários.
Ela foi projetada pensando no novo usuário do Zabbix e pode ser usada como um guia de navegação por outras seções da documentação que contêm informações necessárias para resolver a tarefa.
Os seguintes guias de referência rápida estão disponíveis:
Monitorar Linux com o agent Zabbix
Monitorar Windows com o agent Zabbix
Monitorar Apache via HTTP
Monitorar MySQL com o agent 2 do Zabbix
Monitorar VMware com o Zabbix
Monitorar tráfego de rede com o Zabbix
Monitorar tráfego de rede com o Zabbix usando verificações ativas
Monitorar sites com itens Browser
Monitorar certificados de sites com o agent 2 do Zabbix (passivo)
Monitorar um switch ou roteador de rede com o Zabbix
Monitorar o log de eventos do Windows usando verificações ativas
What’s next?
1 Monitorar Linux com o agent do Zabbix
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 22 Apêndices
URL: https://www.zabbix.com/documentation/current/pt/manual/appendix

22 Apêndices
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
22 Apêndices
Nesta página
22 Apêndices
Visão geral
Referência essencial
22 Apêndices
Visão geral
Esta seção contém materiais de referência, parâmetros de configuração, especificações técnicas e guias de procedimentos que complementam o manual principal.
Referência essencial
Instalação e configuração
- criação do banco de dados, instalação e configuração do server e do agent.
Configuração de processos
- parâmetros de configuração para Zabbix server, proxy, agent e mais.
Items
- referência de chaves de item e tipos de dados suportados.
Macros
- sintaxe e uso de macros internas e de usuário.
What’s next?
1 Instalação e configuração
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 3 processos do Zabbix
URL: https://www.zabbix.com/documentation/current/pt/manual/concepts

3 processos do Zabbix
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
3 processos do Zabbix
Nesta página
3 processos do Zabbix
Visão geral
Processos principais
3 processos do Zabbix
Visão geral
O Zabbix consiste em vários processos que trabalham em conjunto para monitorar sistemas e enviar notificações. Cada processo tem uma função específica na infraestrutura de monitoramento.
Processos principais
Server
- o processo central que realiza polling e trapping de dados, calcula triggers e envia notificações aos usuários.
Agent
- coleta dados de hosts monitorados.
Agent 2
- uma nova geração de agent com arquitetura de plugins e recursos aprimorados.
Proxy
- coleta dados de monitoramento de dispositivos monitorados e envia as informações ao Zabbix server.
Java gateway
- permite o monitoramento de aplicações Java.
What’s next?
1 Server
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 6 Zabbix appliance
URL: https://www.zabbix.com/documentation/current/pt/manual/appliance

6 Zabbix appliance
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
6 Zabbix appliance
Nesta página
6 Zabbix appliance
Visão geral
Início rápido
Pré-requisitos
Instalação
Configuração
Credenciais
Sistema
Frontend do Zabbix
Banco de dados
Acesso ao frontend
Endereço IP estático
Configuração do firewall
Repositórios
Fuso horário
Localização dos arquivos
Serviços do sistema
Observações específicas do formato de imagem
VMware
Imagem HDD/flash (raw)
Hyper-V
Solução de problemas
6 Zabbix appliance
Visão geral
O appliance do Zabbix oferece uma maneira de implantar instantaneamente o server e o frontend do Zabbix, em vez de configurá-los manualmente ou reutilizar um server existente para o Zabbix.
O appliance para o Zabbix 7.4 é baseado em derivados do Red Hat Enterprise Linux 8, como AlmaLinux ou Rocky Linux, e contém um server do Zabbix pré-configurado executando em MySQL e o frontend executando em um web server Nginx.
Este appliance foi projetado para avaliação do Zabbix. Seu uso em ambientes de produção críticos é desencorajado.
As imagens do appliance estão disponíveis para
download
nos seguintes formatos:
CD/DVD de instalação (.iso)
VMware (.vmx) - veja
notas
Formato de virtualização aberto (.ovf)
Microsoft Hyper-V (.vhd/.vhdx) - veja
notas
KVM, Parallels, QEMU, pendrive USB, VirtualBox, Xen (.raw) - veja
notas
KVM, QEMU (.qcow2)
Menu de inicialização do CD/DVD de instalação do Zabbix:
Início rápido
Pré-requisitos
Certifique-se de que a máquina host possui recursos suficientes para atender aos requisitos de sistema da máquina virtual:
RAM
: 4 GB
Espaço em disco
: pelo menos 8 GB devem ser alocados para a máquina virtual
CPU
: mínimo de 2 núcleos
Caso ainda não tenha sido instalado, instale o software de virtualização para inicializar a imagem do appliance (por exemplo,
VirtualBox
).
Baixe
o appliance no formato suportado pelo seu software de virtualização.
Verifique as configurações de rede para garantir que o DHCP esteja habilitado na máquina host.
Instalação
Inicialize a máquina virtual do appliance a partir da imagem baixada. Para instruções, consulte a documentação do seu software de virtualização, por exemplo,
documentação do VirtualBox
.
Configure as definições de rede da máquina virtual para permitir acesso a partir de um navegador na máquina host. Isso pode ser feito habilitando o
modo Bridge
.
Faça login na máquina virtual usando as
credenciais
padrão do sistema.
Para recuperar o endereço IP, execute o seguinte comando na máquina virtual:
ip addr show
Abra um navegador na máquina host e aponte-o para o endereço IP que o appliance recebeu via DHCP.
Faça login no Zabbix usando as
credenciais
padrão e comece a monitorar.
Configuração
Esta seção descreve as configurações padrão frequentemente necessárias, juntamente com as opções de personalização disponíveis.
Credenciais
Sistema
Nome de usuário: root
Senha: zabbix
Frontend do Zabbix
Nome de usuário: Admin
Senha: zabbix
Após o login, você pode alterar a senha padrão nas
configurações do perfil do usuário
ou
criar novos usuários
e excluir o usuário padrão.
Banco de dados
As senhas para todos os usuários do banco de dados são geradas aleatoriamente durante o processo de instalação. Os seguintes usuários são definidos para o banco de dados:
Root:
Nome de usuário: root
Senha: a senha é armazenada no arquivo
/root/.my.cnf
. Não é necessário informar uma senha na conta root.
Servidor Zabbix:
Nome de usuário: zabbix_srv
Senha: a senha é armazenada no arquivo
/etc/zabbix/zabbix\_server.conf
Frontend do Zabbix:
Nome de usuário: zabbix_web
Senha: a senha é armazenada no arquivo
/etc/zabbix/web/zabbix.conf.php
Para alterar a senha de um usuário do banco de dados, modifique-a no MySQL e no arquivo de configuração correspondente.
Acesso ao frontend
O frontend do Zabbix pode ser acessado em
http://<IP da máquina virtual>
.
Por padrão, o acesso é permitido de qualquer lugar. Para limitar o acesso, modifique
/etc/nginx/conf.d/zabbix.conf
. Após salvar o arquivo editado, reinicie o Nginx conectando-se via SSH como
usuário root
e executando:
systemctl restart nginx
Endereço IP estático
Por padrão, o appliance usa DHCP para obter o endereço IP. Para definir um endereço IP estático:
Faça login como
usuário root
.
Execute os seguintes comandos para instalar o NetworkManager, habilitá-lo na inicialização e iniciá-lo:
dnf install NetworkManager systemctl
enable
NetworkManager systemctl start NetworkManager
Modifique o arquivo
/etc/sysconfig/network-scripts/ifcfg-eth0
definindo:
NM_CONTROLLED="yes"
Para aplicar a configuração, recarregue o arquivo de conexão atualizado:
nmcli connection reload
Execute os seguintes comandos, substituindo os valores pelo seu endereço IP personalizado:
nmcli con mod eth0 ipv4.addresses 192.168.1.10/24
# Endereço IP/CIDR do appliance
nmcli con mod eth0 ipv4.gateway 192.168.1.1
# Endereço IP do gateway
nmcli con mod eth0 ipv4.dns 8.8.8.8
# Endereço IP do servidor DNS
nmcli con mod eth0 ipv4.method manual systemctl restart network
Para verificar se as alterações na configuração de rede foram aplicadas, execute o seguinte comando:
nmcli dev show eth0
Configuração do firewall
Para gerenciar as configurações do firewall, o appliance utiliza o iptables com regras predefinidas:
Abrir a porta SSH (22 TCP)
Abrir as portas do agent Zabbix (10050 TCP) e do trapper Zabbix (10051 TCP)
Abrir as portas HTTP (80 TCP) e HTTPS (443 TCP)
Abrir a porta SNMP trap (162 UDP)
Abrir conexões de saída para a porta NTP (123 UDP)
Limitar pacotes ICMP a 5 pacotes por segundo
Bloquear todas as outras conexões de entrada
Para abrir portas adicionais, modifique o arquivo
/etc/sysconfig/iptables
e recarregue as regras do firewall:
systemctl reload iptables
Repositórios
O appliance Zabbix usa o pacote
zabbix-release
do
repositório
do Zabbix. Os repositórios são configurados no diretório
/etc/yum.repos.d/*
.
Fuso horário
Por padrão, o appliance usa UTC para o relógio do sistema. Para alterar o fuso horário, copie o arquivo apropriado de
/usr/share/zoneinfo
para
/etc/localtime
, por exemplo:
cp /usr/share/zoneinfo/Europe/Riga /etc/localtime
O
fuso horário do frontend
do Zabbix é definido separadamente e pode ser alterado nas configurações do frontend. O fuso horário padrão para o frontend do Zabbix é Europe/Riga.
Localização dos arquivos
Os arquivos de configuração estão localizados em
/etc/zabbix
Os arquivos de log do Zabbix server, proxy e agent estão localizados em
/var/log/zabbix
O frontend do Zabbix está localizado em
/usr/share/zabbix
O diretório home do usuário
zabbix
é
/var/lib/zabbix
Serviços do sistema
Os serviços do Systemd estão disponíveis. Para ver a lista de serviços do Zabbix, execute o seguinte comando na máquina virtual:
systemctl list-units zabbix*
Observações específicas do formato de imagem
VMware
As imagens no formato
vmdk
podem ser usadas diretamente nos produtos VMware Player, Server e Workstation. Para uso no ESX, ESXi e vSphere, elas devem ser convertidas usando o
VMware vCenter Converter
(autenticação necessária para download). Se você usar o VMware vCenter Converter, pode encontrar problemas com o adaptador de rede híbrido. Nesse caso, você pode tentar especificar o adaptador E1000 durante o processo de conversão. Como alternativa, após a conclusão da conversão, você pode excluir o adaptador existente e adicionar um adaptador E1000.
Imagem HDD/flash (raw)
Para inicializar a imagem, execute:
dd if=./zabbix_appliance_7.4.0.raw of=/dev/sdc bs=4k conv=fdatasync
Substitua
/dev/sdc
pelo caminho do dispositivo de disco Flash/HDD.
Hyper-V
Se o appliance não iniciar no Hyper-V, tente pressionar
Ctrl+Alt+F2
para alternar para uma sessão TTY.
Solução de problemas
Se você encontrar a mensagem de erro
Access denied for user 'replace_user'@'localhost' (using password: YES)
ao tentar fazer login no frontend, isso pode indicar que a instalação ainda está em andamento.
Se o erro persistir após alguns minutos, ou se você observar qualquer outro comportamento inesperado, provavelmente significa que o processo de instalação não foi concluído com sucesso. Nesse caso, recomendamos excluir o appliance atual e implantá-lo novamente seguindo as mesmas instruções de instalação. Essa etapa geralmente resolve o problema.
Observe que tentar corrigir manualmente uma instalação corrompida não é recomendado, pois pode levar a complicações adicionais.
What’s next?
7 Configuração
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 15 Descoberta
URL: https://www.zabbix.com/documentation/current/pt/manual/discovery

15 Descoberta
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
15 Descoberta
Nesta página
15 Descoberta
Visão geral
Métodos de descoberta
15 Descoberta
Visão geral
A descoberta fornece maneiras automáticas de adicionar hosts e configurar o monitoramento sem configuração manual. O Zabbix oferece suporte a vários métodos de descoberta para se adaptar a diferentes cenários.
Métodos de descoberta
Descoberta de rede
- detecta automaticamente hosts e serviços disponíveis na sua rede.
Autorregistro de agent ativo
- permite que agents ativos se registrem automaticamente no server.
Descoberta de baixo nível
- cria automaticamente itens, triggers, gráficos e hosts para entidades descobertas, como sistemas de arquivos ou interfaces de rede, usando protótipos e regras de descoberta aninhadas.
What’s next?
1 Descoberta de rede
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 17 Criptografia
URL: https://www.zabbix.com/documentation/current/pt/manual/encryption

17 Criptografia
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funções preditivas de trigger
4 Eventos
1 Geração de evento de trigger
2 Outras fontes de eventos
3 Fechamento manual de problemas
5 Correlação de eventos
1 Correlação de eventos baseada em trigger
2 Correlação global de eventos
6 Tagging
7 Visualização
1 Gráficos
1 Gráficos simples
2 Gráficos personalizados
3 Gráficos ad-hoc
2 Mapas de rede
1 Configurando um mapa de rede
2 Elementos de grupo de hosts
3 Indicadores de link
3 Dashboards
8 Templates e grupos de templates
1 Configurando um template
2 Configurando um grupo de templates
3 Vinculando/desvinculando
4 Aninhamento
5 Atualização em massa
9 Templates prontos para uso
1 Operação de template do Zabbix agent
2 Operação do template do Zabbix agent 2
3 Operação de template HTTP
4 Operação de template IPMI
5 Operação de template JMX
6 Operação de template ODBC
7 Templates padronizados para dispositivos de rede
8 Operação de template VMware
10 Notificações em eventos
1 Tipos de mídia
1 E-mail
1 Tipos de mídia automatizados do Gmail/Office365
2 SMS
3 Scripts de alerta personalizados
4 Webhook
1 Exemplos de scripts de webhook
2 Ações
1 Condições
2 Operações
1 Enviando mensagem
2 Comandos remotos
3 Operações adicionais
4 Usando macros em mensagens
3 Operações de recuperação
4 Atualizar operações
5 Escalonamentos
3 Recebendo notificação sobre items não suportados
11 Macros
1 Funções de macro
2 Macros de usuário
3 Macros de usuário com contexto
4 Macros de usuário secretas
5 Macros de descoberta de baixo nível
6 Macros de expressão
12 Usuários e grupos de usuários
1 Configurando um usuário
2 Permissões
3 Grupos de usuários
13 Armazenamento de segredos
1 Configuração do CyberArk
2 Configuração do HashiCorp
14 Relatórios agendados
15 Exportação de dados
1 Exportar para arquivos
2 Transmitindo para sistemas externos
3 SNMP gateway
8 Monitoramento de serviços
1 Árvore de serviços
2 SLA
3 Exemplo de configuração
9 Monitoramento web
1 Itens de monitoramento web
2 Cenário da vida real
10 Monitoramento de máquina virtual
1 Chaves de item de monitoramento do VMware
2 Campos de chave de descoberta de máquina virtual
3 exemplos de JSON para items VMware
4 Exemplo de configuração de monitoramento VMware
11 Manutenção
12 Expressões regulares
13 Reconhecimento de problema
1 Supressão de problema
14 Exportação/importação de configuração
1 Grupos de templates
2 Grupos de hosts
3 Templates
4 Hosts
5 Mapas de rede
6 Tipos de mídia
15 Descoberta
1 Descoberta de rede
1 Configurando uma regra de descoberta de rede
2 Autoregistro de agent ativo
3 Descoberta de baixo nível
1 Prototypes de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
6 Notas sobre descoberta de baixo nível
7 Regras de descoberta
1 Descoberta de sistemas de arquivos montados
2 Descoberta de interfaces de rede
3 Descoberta de CPUs e núcleos de CPU
4 Descoberta de OIDs SNMP
5 Descoberta de OIDs SNMP (legado)
6 Descoberta de objetos JMX
7 Descoberta de sensores IPMI
8 Descoberta de serviços systemd
9 Descoberta de serviços do Windows
10 Descoberta de instâncias de contadores de desempenho do Windows
11 Descoberta usando consultas WMI
12 Descoberta usando consultas SQL ODBC
13 Descoberta usando dados do Prometheus
14 Descoberta de dispositivos de bloco
15 Descoberta de interfaces de host no Zabbix
8 Regras LLD personalizadas
16 Monitoramento distribuído
1 Proxies
1 Sincronização da configuração de monitoramento
2 Balanceamento de carga e alta disponibilidade do proxy
17 Criptografia
1 Usando certificados
2 Usando chaves pré-compartilhadas
3 Solução de problemas
1 Problemas de tipo de conexão ou permissão
2 Problemas de certificado
3 Problemas com PSK
18 Interface web
1 Menu
1 Menu de evento
2 Menu de host
3 Menu de item
2 Seções do frontend
1 Dashboards
1 Widgets do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
2 Monitoramento
1 Problemas
1 Problemas de causa e sintoma
2 Hosts
1 Gráficos
2 Dashboards de host
3 Cenários web
3 Últimos dados
4 Mapas
5 Descoberta
3 Serviços
1 Serviços
2 SLA
3 Relatório de SLA
4 Inventário
1 Visão geral
2 Hosts
5 Relatórios
1 Informações do sistema
2 Relatórios agendados
3 Relatório de disponibilidade
4 Top 100 triggers
5 Log de auditoria
6 Log de ações
7 Notificações
6 Coleta de dados
1 Grupos de templates
2 Grupos de hosts
3 Templates
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Prototipagem de items
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
4 Hosts
1 Items
2 Triggers
3 Gráficos
4 Regras de descoberta
1 Protótipos de item
2 Protótipos de trigger
3 Protótipos de gráficos
4 Protótipos de host
5 Protótipos de descoberta
5 Cenários web
5 Manutenção
6 Correlação de eventos
7 Descoberta
7 Alertas
1 Ações
2 Tipos de mídia
3 Scripts
8 Usuários
1 Grupos de usuários
2 Funções de usuário
3 Usuários
4 Tokens de API
5 Autenticação
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administração
1 Geral
2 Log de auditoria
3 Limpeza
4 Proxies
5 Grupos de proxy
6 Macros
7 Fila
3 Configurações do usuário
1 Notificações globais
2 Som nos navegadores
4 Pesquisa global
5 Modo de manutenção do frontend
6 Parâmetros de página
7 Definições
8 Criando seu próprio tema
9 Modo de depuração
10 Cookies usados pelo Zabbix
11 Fusos horários
12 Redefinindo a senha
13 Seletor de período de tempo
19 Melhores práticas
1 Melhores práticas de segurança
1 Controle de acesso
1 Protegendo o MySQL/MariaDB
2 Protegendo PostgreSQL/TimescaleDB
2 Criptografia
3 Servidor web
2 Melhores práticas de configuração
20 API
Apêndice 1. Comentário de referência
Apêndice 2. Alterações da versão 7.2 para a 7.4
Apêndice 3. Alterações na 7.4
Referência de métodos
Action
Objeto action
action.create
action.delete
action.get
action.update
Alert
Objeto alert
alert.get
Autenticação
Objeto de autenticação
authentication.get
authentication.update
Autoregistration
Objeto de autorregistro
autoregistration.get
autoregistration.update
Cenário web
Objeto de cenário web
httptest.create
httptest.delete
httptest.get
httptest.update
Configuração
configuration.export
configuration.import
configuration.importcompare
Configurações
Objeto settings
settings.get
settings.update
Connector
Objeto connector
connector.create
connector.delete
connector.get
connector.update
Correlation
Objeto correlation
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Objeto dashboard
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Campos do widget do dashboard
1 Log de ações
2 Relógio
3 Status da descoberta
4 Gráficos favoritos
5 Mapas favoritos
6 Gauge
7 Geomapa
8 Gráfico
9 Gráfico (clássico)
10 Protótipo de gráfico
11 Honeycomb
12 Disponibilidade do host
13 Cartão de host
14 Navegador de hosts
15 Cartão de item
16 Histórico de item
17 Navegador de item
18 Valor do item
19 Mapa
20 Árvore de navegação do mapa
21 Gráfico de pizza
22 Hosts com problemas
23 Problemas
24 Problemas por gravidade
26 Informações do sistema
27 Principais hosts
28 Principais items
29 Principais triggers
30 Visão geral de trigger
31 URL
32 Monitoramento web
Relatório de SLA 25
Diretório de usuários
Objeto de diretório de usuário
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
Event
Objeto event
event.acknowledge
event.get
Expressão regular
Objeto de expressão regular
regexp.create
regexp.delete
regexp.get
regexp.update
Graph
Objeto graph
graph.create
graph.delete
graph.get
graph.update
Grupo de hosts
Objeto de grupo de hosts
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Grupo de proxy
Objeto de grupo de proxy
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Grupo de template
Objeto de grupo de template
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Grupo de usuários
Objeto de grupo de usuários
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
History
Objeto de histórico
history.clear
history.get
history.push
Host
Objeto host
host.create
host.delete
host.get
host.massadd
host.massremove
host.update
massupdate.md
Host descoberto
Objeto de host descoberto
dhost.get
Housekeeping
Objeto de limpeza
housekeeping.get
housekeeping.update
Icon map
Objeto de mapa de ícones
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Imagem
Objeto de imagem
image.create
image.delete
image.get
image.update
Informações da API
apiinfo.version
Interface do host
Objeto de interface de host
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Item
Objeto item
item.create
item.delete
item.get
item.update
Item de gráfico
Objeto de item de gráfico
graphitem.get
Log de auditoria
Objeto de log de auditoria
auditlog.get
MFA
Objeto MFA
mfa.create
mfa.delete
mfa.get
mfa.update
Macro de usuário
Objeto macro de usuário
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Manutenção
Objeto de manutenção
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Objeto de mapa
map.create
map.delete
map.get
map.update
Mapa de valores
Objeto de mapa de valor
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Módulo
Objeto module
module.create
module.delete
module.get
module.update
Nó de alta disponibilidade
Objeto de nó de alta disponibilidade
hanode.get
Problem
Objeto problem
problem.get
Protótipo de gráfico
Objeto de protótipo de gráfico
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
Protótipo de host
Objeto de protótipo de host
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Protótipo de item
Objeto de protótipo de item
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
Protótipo de regra de LLD
Objeto de protótipo de regra de LLD
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
Proxy
Objeto proxy
proxy.create
proxy.delete
proxy.get
proxy.update
Regra de LLD
Objeto de regra de LLD
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Regra de descoberta
Objeto de regra de descoberta
drule.create
drule.delete
drule.get
drule.update
Report
Objeto report
report.create
report.delete
report.get
report.update
Role
Objeto role
role.create
role.delete
role.get
role.update
SLA
Objeto SLA
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Objeto script
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Objeto de serviço
service.create
service.delete
service.get
service.update
Serviço descoberto
Objeto de serviço descoberto
dservice.get
Task
Objeto task
task.create
task.get
Template
Objeto template
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Objeto de dashboard de template
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Tipo de mídia
Objeto media type
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Token
Objeto token
token.create
token.delete
token.generate
token.get
token.update
Trend
Objeto de tendência
trend.get
Trigger
Objeto trigger
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Objeto de protótipo de trigger
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
Usuário
Objeto de usuário
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.provision
user.resettotp
user.unblock
user.update
Verificação de descoberta
Objeto de verificação de descoberta
dcheck.get
21 Extensões
1 Módulos carregáveis
2 Plugins
3 módulos do frontend
22 Apêndices
1 Instalação e configuração
1 Criação do banco de dados
2 Reparando o conjunto de caracteres e a collation do banco de dados do Zabbix
3 Atualização do banco de dados para chaves primárias
4 Preparando a tabela auditlog para particionamento
5 Conexão segura com o banco de dados
1 Configuração de criptografia do MySQL
2 Configuração de criptografia do PostgreSQL
6 Conexão segura com o frontend
7 Configuração do TimescaleDB
8 Configuração do Elasticsearch
9 Notas específicas da distribuição sobre a configuração do Nginx para o Zabbix
10 Executando o agent como root
11 Agent Zabbix no Microsoft Windows
12 Configuração do SAML com o Microsoft Entra ID
13 Configuração do SAML com Okta
14 Configuração do SAML com OneLogin
15 Configurando relatórios agendados
16 Idiomas adicionais do frontend
17 Confiança no certificado TLS do Google Chrome
2 Configuração de processos
1 servidor Zabbix
2 Zabbix proxy
3 Agente Zabbix (UNIX)
4 Agente Zabbix 2 (UNIX)
5 Zabbix agent (Windows)
6 Agente Zabbix 2 (Windows)
7 Plugins do Zabbix Agent 2
1 Plugin Ceph
2 Plugin Docker
3 Plugin Ember+
4 Plugin Memcached
5 Plugin Modbus
6 Plugin do MongoDB
7 Plugin MQTT
8 Plugin MSSQL
9 Plugin MySQL
10 Plugin NVIDIA GPU
11 Plugin do Oracle
12 Plugin do PostgreSQL
13 Plugin Redis
14 Plugin SMART
8 Zabbix Java gateway
9 Serviço web do Zabbix
10 Variáveis de ambiente
3 Protocolos
1 Protocolo de troca de dados server-proxy
2 Protocolo do agent/agent2 do Zabbix
4 Protocolo de plugin do Zabbix agent 2
5 Protocolo do Zabbix sender
6 Cabeçalho
7 Protocolo de exportação JSON delimitado por nova linha
4 Items
1 parâmetros vm.memory.size
2 Verificações passivas e ativas do agent
3 Nível mínimo de permissão para itens do agent do Windows
4 Codificação dos valores retornados
5 Suporte a arquivos grandes
6 Sensor
7 Notas sobre o parâmetro memtype em itens proc.mem
8 Notas sobre a seleção de processos em itens proc.mem e proc.num
9 Detalhes de implementação das verificações net.tcp.service e net.udp.service
10 parâmetros proc.get
11 Configurações de interface de host inacessível/indisponível
12 Monitoramento remoto das estatísticas do Zabbix
13 Configurando o Kerberos com o Zabbix
14 parâmetros modbus.get
15 Criando nomes personalizados de contadores de desempenho para VMware
16 Valores de retorno para system.sw.packages.get
17 Valores de retorno para net.dns.get
18 Notas sobre itens system.cpu.util no Windows
5 Funções suportadas
1 Funções agregadas
1 Funções Foreach
2 Funções bitwise
3 Funções de data e hora
4 Funções de histórico
5 Funções de tendência
6 Funções matemáticas
7 Funções de operador
8 Funções preditivas
9 Funções de string
6 Macros
1 Macros suportadas por local
2 Macros de usuário suportadas por local
7 Símbolos de unidade
8 Sintaxe do período de tempo
9 Execução de comandos
10 Compatibilidade de versões
11 Biblioteca de vínculo dinâmico do Zabbix sender para Windows
12 Atualização do monitoramento de serviços
13 Outros problemas
14 Comparação entre Agent e agent 2
15 Exemplos de escape
23 Guias de referência rápida
1 Monitorar Linux com o agent do Zabbix
2 Monitorar Windows com o Zabbix agent
3 Monitorar o Apache via HTTP
4 Monitorar o MySQL com o Zabbix agent 2
5 Monitorar VMware com o Zabbix
6 Monitorar o tráfego de rede com o Zabbix
7 Monitorar o tráfego de rede usando verificações ativas
8 Monitorar sites com itens do Browser
9 Monitorar certificados de sites com o Zabbix agent 2 (passivo)
10 Monitore um switch ou roteador de rede com o Zabbix
11 Monitorar o log de eventos do Windows usando verificações ativas
Zabbix Cloud
Implante o Zabbix na nuvem
Configuração do nó
Adicionando usuários
Principais diferenças do Zabbix Cloud
Log de auditoria
Centro do desenvolvedor
Módulos
Estrutura de arquivos do módulo
manifest.json
Ações
Views
Assets
Registrar um novo módulo
Widgets
Configuração
Apresentação
Tutoriais
Criar um módulo (tutorial)
Criar um widget (tutorial)
Exemplos
Biblioteca Python para Zabbix
Instalação
Guia de início rápido
Usar a API do Zabbix
Coletar dados do agent Zabbix
Enviar dados para o Zabbix server ou proxy
Log de depuração
Plugins
Exemplos
Criar um plugin (tutorial)
Interfaces de plugin
Alterações no desenvolvimento de extensões
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Aviso de direitos autorais
Manual do usuário
17 Criptografia
Nesta página
17 Criptografia
Visão geral
Limitações
Compilando o Zabbix com suporte a criptografia
Gerenciamento da criptografia de conexões
zabbix_get e zabbix_sender com criptografia
Suítes de cifras
Ciphersuites configuradas pelo usuário
Conexões de saída
Conexões de entrada
Testando strings de cifra e permitindo apenas ciphersuites PFS
Mudando de AES128 para AES256
17 Criptografia
Visão geral
O Zabbix suporta comunicações criptografadas entre os componentes do Zabbix usando o protocolo Transport Layer Security (TLS) v.1.2 e 1.3 (dependendo da biblioteca de criptografia). A criptografia baseada em certificado e baseada em chave pré-compartilhada é suportada.
A criptografia pode ser configurada para conexões:
Entre o Zabbix server, Zabbix proxy, Zabbix agent, Zabbix web service, utilitários zabbix_sender e zabbix_get
Para o banco de dados Zabbix
a partir do Zabbix frontend e server/proxy
Entre o Zabbix frontend e o Zabbix server
A criptografia é opcional e configurável para componentes individuais:
Alguns proxies e agents podem ser configurados para usar criptografia baseada em certificado com o server, enquanto outros podem usar criptografia baseada em chave pré-compartilhada, e ainda outros continuam com comunicações não criptografadas (como antes).
O server (proxy) pode usar diferentes configurações de criptografia para diferentes hosts.
Os programas daemon do Zabbix usam uma porta de escuta para conexões recebidas criptografadas e não criptografadas. Adicionar uma criptografia não requer a abertura de novas portas em firewalls.
Limitações
As chaves privadas são armazenadas em texto simples em arquivos legíveis pelos componentes do Zabbix durante a inicialização.
As chaves pré-compartilhadas são inseridas no frontend do Zabbix e armazenadas no banco de dados do Zabbix em texto simples.
A criptografia interna não protege as comunicações entre o servidor web que executa o frontend do Zabbix e o navegador web do usuário.
Atualmente, cada conexão criptografada é aberta com um handshake TLS completo, sem cache de sessão e tickets implementados.
Adicionar criptografia aumenta o tempo para verificações de item e ações, dependendo da latência da rede:
Por exemplo, se o atraso do pacote for de 100ms, abrir uma conexão TCP e enviar uma solicitação não criptografada leva cerca de 200ms. Com criptografia, cerca de 1000 ms são adicionados para estabelecer a conexão TLS.
Os timeouts podem precisar ser aumentados, caso contrário, alguns itens e ações que executam scripts remotos em agents podem funcionar com conexões não criptografadas, mas falhar com timeout quando criptografadas.
A criptografia não é suportada pela
descoberta de rede
. As verificações do agent Zabbix realizadas pela descoberta de rede serão não criptografadas e, se o agent Zabbix estiver configurado para rejeitar conexões não criptografadas, essas verificações não terão sucesso.
Compilando o Zabbix com suporte a criptografia
Para oferecer suporte à criptografia, o Zabbix deve ser compilado e vinculado com uma das bibliotecas criptográficas suportadas:
GnuTLS - a partir da versão 3.1.18
OpenSSL - versões 1.0.1, 1.0.2, 1.1.0, 1.1.1, 3.0.x - 3.5.x
LibreSSL - testado com as versões 2.7.4, 2.8.2:
LibreSSL 2.6.x não é suportado
LibreSSL é suportado como uma substituição compatível do OpenSSL; as novas funções de API específicas do LibreSSL
tls_*()
não são usadas. Componentes do Zabbix compilados com LibreSSL não poderão usar PSK; apenas certificados podem ser usados.
Você pode encontrar mais informações sobre a configuração de SSL para o frontend do Zabbix consultando estas
boas práticas
.
A biblioteca é selecionada especificando a respectiva opção no script "configure":
--with-gnutls[=DIR]
--with-openssl[=DIR]
(também usado para LibreSSL)
Por exemplo, para configurar os fontes do server e do agent com
OpenSSL
, você pode usar algo como:
./configure --enable-server --enable-agent --with-mysql --enable-ipv6 --with-net-snmp --with-libcurl --with-libxml2 --with-openssl
Diferentes componentes do Zabbix podem ser compilados com diferentes bibliotecas criptográficas (por exemplo, um server com
OpenSSL
, um agent com
GnuTLS
).
Se você planeja usar chaves pré-compartilhadas (PSK), considere usar bibliotecas
GnuTLS
ou
OpenSSL 1.1.0
(ou mais recentes) nos componentes do Zabbix que utilizam PSKs. As bibliotecas
GnuTLS
e
OpenSSL 1.1.0
suportam conjuntos de cifras PSK com
Perfect Forward Secrecy
. Versões mais antigas da biblioteca
OpenSSL
(1.0.1, 1.0.2c) também suportam PSKs, mas os conjuntos de cifras PSK disponíveis não fornecem Perfect Forward Secrecy.
Gerenciamento da criptografia de conexões
As conexões no Zabbix podem usar:
sem criptografia (padrão)
criptografia baseada em certificado RSA
criptografia baseada em PSK
Há dois parâmetros importantes usados para especificar a criptografia entre os componentes do Zabbix:
TLSConnect - especifica qual criptografia usar para conexões de saída (sem criptografia, PSK ou certificado)
TLSAccept - especifica quais tipos de conexões são permitidos para conexões de entrada (sem criptografia, PSK ou certificado). Um ou mais valores podem ser especificados.
TLSConnect
é usado nos arquivos de configuração do Zabbix proxy (no modo ativo, especifica apenas conexões com o server) e do Zabbix agent (para verificações ativas). No frontend do Zabbix, o equivalente de TLSConnect é o campo
Connections to host
na aba
Data collection → Hosts → <some host> → Encryption
e o campo
Connections to proxy
na aba
Administration → Proxies → <some proxy> → Encryption
. Se o tipo de criptografia configurado para a conexão falhar, nenhum outro tipo de criptografia será tentado.
TLSAccept
é usado nos arquivos de configuração do Zabbix proxy (no modo passivo, especifica apenas conexões do server) e do Zabbix agent (para verificações passivas). No frontend do Zabbix, o equivalente de TLSAccept é o campo
Connections from host
na aba
Data collection → Hosts → <some host> → Encryption
e o campo
Connections from proxy
na aba
Administration → Proxies → <some proxy> → Encryption
.
Normalmente, você configura apenas um tipo de criptografia para conexões de entrada. Mas talvez você queira alterar o tipo de criptografia, por exemplo, de sem criptografia para baseada em certificado, com o mínimo de indisponibilidade e possibilidade de reversão. Para isso:
Defina
TLSAccept=unencrypted,cert
no arquivo de configuração do agent e reinicie o Zabbix agent
Teste a conexão com zabbix_get para o agent usando certificado. Se funcionar, você pode reconfigurar a criptografia para esse agent no frontend do Zabbix, na aba
Data collection → Hosts → <some host> → Encryption
, definindo
Connections to host
como "Certificate".
Quando o cache de configuração do server for atualizado (e a configuração do proxy for atualizada, se o host for monitorado por proxy), as conexões com esse agent serão criptografadas
Se tudo funcionar como esperado, você pode definir
TLSAccept=cert
no arquivo de configuração do agent e reiniciar o Zabbix agent. Agora o agent aceitará apenas conexões criptografadas baseadas em certificado. Conexões sem criptografia e baseadas em PSK serão rejeitadas.
De forma semelhante, isso funciona no server e no proxy. Se, no frontend do Zabbix, na configuração do host,
Connections from host
estiver definido como "Certificate", então apenas conexões criptografadas baseadas em certificado serão aceitas do agent (verificações ativas) e do zabbix_sender (itens trapper).
Muito provavelmente, você configurará as conexões de entrada e saída para usar o mesmo tipo de criptografia ou nenhuma criptografia. Mas, tecnicamente, é possível configurá-las de forma assimétrica, por exemplo, criptografia baseada em certificado para conexões de entrada e baseada em PSK para conexões de saída.
A configuração de criptografia de cada host é exibida no frontend do Zabbix, em
Data collection
>
Hosts
, na coluna
Agent encryption
. Por exemplo:
Example
Connections to host
Allowed connections from host
Rejected connections from host
Sem criptografia
Sem criptografia
Criptografadas, criptografadas baseadas em certificado e baseadas em PSK
Criptografadas, baseadas em certificado
Criptografadas, baseadas em certificado
Sem criptografia e criptografadas baseadas em PSK
Criptografadas, baseadas em PSK
Criptografadas, baseadas em PSK
Sem criptografia e criptografadas baseadas em certificado
Criptografadas, baseadas em PSK
Sem criptografia e criptografadas baseadas em PSK
Criptografadas baseadas em certificado
Criptografadas, baseadas em certificado
Sem criptografia, PSK ou criptografadas baseadas em certificado
-
As conexões são sem criptografia por padrão. A criptografia deve ser configurada individualmente para cada host e proxy.
zabbix_get e zabbix_sender com criptografia
Consulte as páginas de manual do
zabbix_get
e
zabbix_sender
para usá-los com criptografia.
Suítes de cifras
Por padrão, as suítes de cifras são configuradas internamente durante a inicialização do Zabbix.
Também há suporte para suítes de cifras configuradas pelo usuário para GnuTLS e OpenSSL. Os usuários podem
configurar
as suítes de cifras de acordo com suas políticas de segurança. O uso desse recurso é opcional (as suítes de cifras padrão integradas continuam funcionando).
Para bibliotecas criptográficas compiladas com configurações padrão, as regras integradas do Zabbix normalmente resultam nas seguintes suítes de cifras (em ordem da maior para a menor prioridade):
Biblioteca
Suítes de cifras de certificado
Suítes de cifras PSK
GnuTLS 3.1.18
TLS_ECDHE_RSA_AES_128_GCM_SHA256
TLS_ECDHE_RSA_AES_128_CBC_SHA256
TLS_ECDHE_RSA_AES_128_CBC_SHA1
TLS_RSA_AES_128_GCM_SHA256
TLS_RSA_AES_128_CBC_SHA256
TLS_RSA_AES_128_CBC_SHA1
TLS_ECDHE_PSK_AES_128_CBC_SHA256
TLS_ECDHE_PSK_AES_128_CBC_SHA1
TLS_PSK_AES_128_GCM_SHA256
TLS_PSK_AES_128_CBC_SHA256
TLS_PSK_AES_128_CBC_SHA1
OpenSSL 1.0.2c
ECDHE-RSA-AES128-GCM-SHA256
ECDHE-RSA-AES128-SHA256
ECDHE-RSA-AES128-SHA
AES128-GCM-SHA256
AES128-SHA256
AES128-SHA
PSK-AES128-CBC-SHA
OpenSSL 1.1.0
ECDHE-RSA-AES128-GCM-SHA256
ECDHE-RSA-AES128-SHA256
ECDHE-RSA-AES128-SHA
AES128-GCM-SHA256
AES128-CCM8
AES128-CCM
AES128-SHA256
AES128-SHA
ECDHE-PSK-AES128-CBC-SHA256
ECDHE-PSK-AES128-CBC-SHA
PSK-AES128-GCM-SHA256
PSK-AES128-CCM8
PSK-AES128-CCM
PSK-AES128-CBC-SHA256
PSK-AES128-CBC-SHA
OpenSSL 1.1.1d
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
ECDHE-RSA-AES128-GCM-SHA256
ECDHE-RSA-AES128-SHA256
ECDHE-RSA-AES128-SHA
AES128-GCM-SHA256
AES128-CCM8
AES128-CCM
AES128-SHA256
AES128-SHA
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
ECDHE-PSK-AES128-CBC-SHA256
ECDHE-PSK-AES128-CBC-SHA
PSK-AES128-GCM-SHA256
PSK-AES128-CCM8
PSK-AES128-CCM
PSK-AES128-CBC-SHA256
PSK-AES128-CBC-SHA
Ciphersuites configuradas pelo usuário
Os critérios internos de seleção de ciphersuites podem ser substituídos por ciphersuites configuradas pelo usuário.
Ciphersuites configuradas pelo usuário são um recurso destinado a usuários avançados que compreendem ciphersuites TLS, sua segurança e as consequências de erros, e que estejam confortáveis com a solução de problemas de TLS.
Os critérios internos de seleção de ciphersuites podem ser substituídos usando os seguintes parâmetros:
Escopo de substituição
Parâmetro
Valor
Descrição
Seleção de ciphersuite para certificados
TLSCipherCert13
Cipher strings
válidas do OpenSSL 1.1.1 para o protocolo TLS 1.3 (seus valores são passados para a função OpenSSL
SSL_CTX_set_ciphersuites()
).
Critérios de seleção de ciphersuite baseados em certificado para TLS 1.3
Apenas OpenSSL 1.1.1 ou mais recente.
TLSCipherCert
Cipher strings
válidas do OpenSSL para TLS 1.2 ou
priority strings
válidas do GnuTLS. Seus valores são passados para as funções
SSL_CTX_set_cipher_list()
ou
gnutls_priority_init()
, respectivamente.
Critérios de seleção de ciphersuite baseados em certificado para TLS 1.2/1.3 (GnuTLS), TLS 1.2 (OpenSSL)
Seleção de ciphersuite para PSK
TLSCipherPSK13
Cipher strings
válidas do OpenSSL 1.1.1 para o protocolo TLS 1.3 (seus valores são passados para a função OpenSSL
SSL_CTX_set_ciphersuites()
).
Critérios de seleção de ciphersuite baseados em PSK para TLS 1.3
Apenas OpenSSL 1.1.1 ou mais recente.
TLSCipherPSK
Cipher strings
válidas do OpenSSL para TLS 1.2 ou
priority strings
válidas do GnuTLS. Seus valores são passados para as funções
SSL_CTX_set_cipher_list()
ou
gnutls_priority_init()
, respectivamente.
Critérios de seleção de ciphersuite baseados em PSK para TLS 1.2/1.3 (GnuTLS), TLS 1.2 (OpenSSL)
Lista combinada de ciphersuites para certificado e PSK
TLSCipherAll13
Cipher strings
válidas do OpenSSL 1.1.1 para o protocolo TLS 1.3 (seus valores são passados para a função OpenSSL
SSL_CTX_set_ciphersuites()
).
Critérios de seleção de ciphersuite para TLS 1.3
Apenas OpenSSL 1.1.1 ou mais recente.
TLSCipherAll
Cipher strings
válidas do OpenSSL para TLS 1.2 ou
priority strings
válidas do GnuTLS. Seus valores são passados para as funções
SSL_CTX_set_cipher_list()
ou
gnutls_priority_init()
, respectivamente.
Critérios de seleção de ciphersuite para TLS 1.2/1.3 (GnuTLS), TLS 1.2 (OpenSSL)
Para substituir a seleção de ciphersuite nas utilitários
zabbix_get
e
zabbix_sender
- use os parâmetros de linha de comando:
--tls-cipher13
--tls-cipher
Os novos parâmetros são opcionais. Se um parâmetro não for especificado, o valor padrão interno será usado. Se um parâmetro for definido, ele não pode estar vazio.
Se a configuração de um valor TLSCipher* na biblioteca de criptografia falhar, o server, proxy ou agent não será iniciado e um erro será registrado.
É importante entender quando cada parâmetro é aplicável.
Conexões de saída
O caso mais simples são as conexões de saída:
Para conexões de saída com certificado - use TLSCipherCert13 ou TLSCipherCert
Para conexões de saída com PSK - use TLSCipherPSK13 ou TLSCipherPSK
No caso das utilitários zabbix_get e zabbix_sender, os parâmetros de linha de comando
--tls-cipher13
ou
--tls-cipher
podem ser usados (a criptografia é especificada de forma inequívoca com o parâmetro
--tls-connect
)
Conexões de entrada
É um pouco mais complicado com conexões de entrada porque as regras são específicas para componentes e configuração.
Para o Zabbix
agent
:
Configuração de conexão do agent
Configuração de cifras
TLSConnect=cert
TLSCipherCert, TLSCipherCert13
TLSConnect=psk
TLSCipherPSK, TLSCipherPSK13
TLSAccept=cert
TLSCipherCert, TLSCipherCert13
TLSAccept=psk
TLSCipherPSK, TLSCipherPSK13
TLSAccept=cert,psk
TLSCipherAll, TLSCipherAll13
Para o Zabbix
server
e
proxy
:
Configuração de conexão
Configuração de cifras
Conexões de saída usando PSK
TLSCipherPSK, TLSCipherPSK13
Conexões de entrada usando certificados
TLSCipherAll, TLSCipherAll13
Conexões de entrada usando PSK se o server não tiver certificado
TLSCipherPSK, TLSCipherPSK13
Conexões de entrada usando PSK se o server tiver certificado
TLSCipherAll, TLSCipherAll13
É possível observar um padrão nas duas tabelas acima:
TLSCipherAll e TLSCipherAll13 podem ser especificados somente se uma lista combinada de conjuntos de cifras baseados em certificado
e
PSK for usada. Há dois casos em que isso ocorre: server (proxy) com um certificado configurado (os conjuntos de cifras PSK são sempre configurados no server, proxy se a biblioteca criptográfica oferecer suporte a PSK), agent configurado para aceitar conexões de entrada baseadas tanto em certificado quanto em PSK
em outros casos, TLSCipherCert* e/ou TLSCipherPSK* são suficientes
As tabelas a seguir mostram os valores padrão internos de
TLSCipher*
. Eles podem ser um bom ponto de partida para seus próprios valores personalizados.
Parameter
GnuTLS 3.6.12
TLSCipherCert
NONE:+VERS-TLS1.2:+ECDHE-RSA:+RSA:+AES-128-GCM:+AES-128-CBC:+AEAD:+SHA256:+SHA1:+CURVE-ALL:+COMP-NULL:+SIGN-ALL:+CTYPE-X.509
TLSCipherPSK
NONE:+VERS-TLS1.2:+ECDHE-PSK:+PSK:+AES-128-GCM:+AES-128-CBC:+AEAD:+SHA256:+SHA1:+CURVE-ALL:+COMP-NULL:+SIGN-ALL
TLSCipherAll
NONE:+VERS-TLS1.2:+ECDHE-RSA:+RSA:+ECDHE-PSK:+PSK:+AES-128-GCM:+AES-128-CBC:+AEAD:+SHA256:+SHA1:+CURVE-ALL:+COMP-NULL:+SIGN-ALL:+CTYPE-X.509
Parameter
OpenSSL 1.1.1d
1
TLSCipherCert13
TLSCipherCert
EECDH+aRSA+AES128:RSA+aRSA+AES128
TLSCipherPSK13
TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256
TLSCipherPSK
kECDHEPSK+AES128:kPSK+AES128
TLSCipherAll13
TLSCipherAll
EECDH+aRSA+AES128:RSA+aRSA+AES128:kECDHEPSK+AES128:kPSK+AES128
1
Os valores padrão são diferentes para versões mais antigas do OpenSSL (1.0.1, 1.0.2, 1.1.0), para o LibreSSL e se o OpenSSL for compilado sem suporte a PSK.
Exemplos de conjuntos de cifras configurados pelo usuário
Veja abaixo os seguintes exemplos de conjuntos de cifras configurados pelo usuário:
Testando strings de cifras e permitindo apenas conjuntos de cifras PFS
Mudando de AES128 para AES256
Testando strings de cifra e permitindo apenas ciphersuites PFS
Para ver quais ciphersuites foram selecionadas, você precisa definir 'DebugLevel=4' no arquivo de configuração ou usar a opção
-vv
para o zabbix_sender.
Pode ser necessário experimentar com os parâmetros
TLSCipher*
antes de obter as ciphersuites desejadas. É inconveniente reiniciar o Zabbix server, proxy ou agent várias vezes apenas para ajustar os parâmetros
TLSCipher*
. Opções mais convenientes são usar o zabbix_sender ou o comando
openssl
. Vamos mostrar ambos.
1.
Usando o zabbix_sender.
Vamos criar um arquivo de configuração de teste, por exemplo
/home/zabbix/test.conf
, com a sintaxe de um arquivo
zabbix_agentd.conf
:
Hostname=nonexisting ServerActive=nonexisting TLSConnect=cert TLSCAFile=/home/zabbix/ca.crt TLSCertFile=/home/zabbix/agent.crt TLSKeyFile=/home/zabbix/agent.key TLSPSKIdentity=nonexisting TLSPSKFile=/home/zabbix/agent.psk
Você precisa de certificados CA e agent válidos e PSK para este exemplo. Ajuste os caminhos e nomes dos arquivos de certificado e PSK para o seu ambiente.
Se você não estiver usando certificados, mas apenas PSK, pode criar um arquivo de teste mais simples:
Hostname=nonexisting ServerActive=nonexisting TLSConnect=psk TLSPSKIdentity=nonexisting TLSPSKFile=/home/zabbix/agentd.psk
As ciphersuites selecionadas podem ser vistas executando o zabbix_sender (exemplo compilado com OpenSSL 1.1.d):
$ zabbix_sender -vv -c /home/zabbix/test.conf -k nonexisting_item -o 1 2>&1 | grep ciphersuites zabbix_sender [41271]: DEBUG: zbx_tls_init_child() certificate ciphersuites: TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-RSA-AES128-SHA256 ECDHE-RSA-AES128-SHA AES128-GCM-SHA256 AES128-CCM8 AES128-CCM AES128-SHA256 AES128-SHA zabbix_sender [41271]: DEBUG: zbx_tls_init_child() PSK ciphersuites: TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-PSK-AES128-CBC-SHA256 ECDHE-PSK-AES128-CBC-SHA PSK-AES128-GCM-SHA256 PSK-AES128-CCM8 PSK-AES128-CCM PSK-AES128-CBC-SHA256 PSK-AES128-CBC-SHA zabbix_sender [41271]: DEBUG: zbx_tls_init_child() certificate and PSK ciphersuites: TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-RSA-AES128-SHA256 ECDHE-RSA-AES128-SHA AES128-GCM-SHA256 AES128-CCM8 AES128-CCM AES128-SHA256 AES128-SHA ECDHE-PSK-AES128-CBC-SHA256 ECDHE-PSK-AES128-CBC-SHA PSK-AES128-GCM-SHA256 PSK-AES128-CCM8 PSK-AES128-CCM PSK-AES128-CBC-SHA256 PSK-AES128-CBC-SHA
Aqui você vê as ciphersuites selecionadas por padrão. Esses valores padrão são escolhidos para garantir a interoperabilidade com agents Zabbix executando em sistemas com versões mais antigas do OpenSSL (a partir de 1.0.1).
Com sistemas mais recentes, você pode optar por reforçar a segurança permitindo apenas algumas ciphersuites, por exemplo, apenas ciphersuites com PFS (Perfect Forward Secrecy). Vamos tentar permitir apenas ciphersuites com PFS usando os parâmetros
TLSCipher*
.
O resultado não será interoperável com sistemas usando OpenSSL 1.0.1 e 1.0.2, se PSK for usado. A criptografia baseada em certificado deve funcionar.
Adicione duas linhas ao arquivo de configuração
test.conf
:
TLSCipherCert=EECDH+aRSA+AES128 TLSCipherPSK=kECDHEPSK+AES128
e teste novamente:
$ zabbix_sender -vv -c /home/zabbix/test.conf -k nonexisting_item -o 1 2>&1 | grep ciphersuites zabbix_sender [42892]: DEBUG: zbx_tls_init_child() certificate ciphersuites: TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-RSA-AES128-SHA256 ECDHE-RSA-AES128-SHA zabbix_sender [42892]: DEBUG: zbx_tls_init_child() PSK ciphersuites: TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-PSK-AES128-CBC-SHA256 ECDHE-PSK-AES128-CBC-SHA zabbix_sender [42892]: DEBUG: zbx_tls_init_child() certificate and PSK ciphersuites: TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-RSA-AES128-SHA256 ECDHE-RSA-AES128-SHA AES128-GCM-SHA256 AES128-CCM8 AES128-CCM AES128-SHA256 AES128-SHA ECDHE-PSK-AES128-CBC-SHA256 ECDHE-PSK-AES128-CBC-SHA PSK-AES128-GCM-SHA256 PSK-AES128-CCM8 PSK-AES128-CCM PSK-AES128-CBC-SHA256 PSK-AES128-CBC-SHA
As listas "certificate ciphersuites" e "PSK ciphersuites" mudaram
elas estão mais curtas do que antes, contendo apenas ciphersuites TLS 1.3 e ciphersuites TLS 1.2 ECDHE-*, como esperado.
2.
TLSCipherAll e TLSCipherAll13 não podem ser testados com zabbix_sender; eles não afetam o valor "certificate and PSK ciphersuites" mostrado no exemplo acima. Para ajustar TLSCipherAll e TLSCipherAll13, você precisa experimentar com o agent, proxy ou server.
Portanto, para permitir apenas ciphersuites PFS, pode ser necessário adicionar até três parâmetros
TLSCipherCert=EECDH+aRSA+AES128 TLSCipherPSK=kECDHEPSK+AES128 TLSCipherAll=EECDH+aRSA+AES128:kECDHEPSK+AES128
ao zabbix_agentd.conf, zabbix_proxy.conf e zabbix_server_conf se cada um deles tiver um certificado configurado e o agent também tiver PSK.
Se o seu ambiente Zabbix usar apenas criptografia baseada em PSK e não certificados, então apenas um:
TLSCipherPSK=kECDHEPSK+AES128
Agora que você entende como funciona, pode testar a seleção de ciphersuite mesmo fora do Zabbix, com o comando
openssl
. Vamos testar todos os três valores de parâmetro
TLSCipher*
:
$ openssl ciphers EECDH+aRSA+AES128 | sed 's/:/ /g' TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-RSA-AES128-SHA256 ECDHE-RSA-AES128-SHA $ openssl ciphers kECDHEPSK+AES128 | sed 's/:/ /g' TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-PSK-AES128-CBC-SHA256 ECDHE-PSK-AES128-CBC-SHA $ openssl ciphers EECDH+aRSA+AES128:kECDHEPSK+AES128 | sed 's/:/ /g' TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 TLS_AES_128_GCM_SHA256 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-RSA-AES128-SHA256 ECDHE-RSA-AES128-SHA ECDHE-PSK-AES128-CBC-SHA256 ECDHE-PSK-AES128-CBC-SHA
Você pode preferir
openssl ciphers
com a opção
-V
para uma saída mais detalhada:
$ openssl ciphers -V EECDH+aRSA+AES128:kECDHEPSK+AES128 0x13,0x02 - TLS_AES_256_GCM_SHA384 TLSv1.3 Kx=any Au=any Enc=AESGCM(256) Mac=AEAD 0x13,0x03 - TLS_CHACHA20_POLY1305_SHA256 TLSv1.3 Kx=any Au=any Enc=CHACHA20/POLY1305(256) Mac=AEAD 0x13,0x01 - TLS_AES_128_GCM_SHA256 TLSv1.3 Kx=any Au=any Enc=AESGCM(128) Mac=AEAD 0xC0,0x2F - ECDHE-RSA-AES128-GCM-SHA256 TLSv1.2 Kx=ECDH Au=RSA Enc=AESGCM(128) Mac=AEAD 0xC0,0x27 - ECDHE-RSA-AES128-SHA256 TLSv1.2 Kx=ECDH Au=RSA Enc=AES(128) Mac=SHA256 0xC0,0x13 - ECDHE-RSA-AES128-SHA TLSv1 Kx=ECDH Au=RSA Enc=AES(128) Mac=SHA1 0xC0,0x37 - ECDHE-PSK-AES128-CBC-SHA256 TLSv1 Kx=ECDHEPSK Au=PSK Enc=AES(128) Mac=SHA256 0xC0,0x35 - ECDHE-PSK-AES128-CBC-SHA TLSv1 Kx=ECDHEPSK Au=PSK Enc=AES(128) Mac=SHA1
Da mesma forma, você pode testar as strings de prioridade para GnuTLS:
$ gnutls-cli -l --priority=NONE:+VERS-TLS1.2:+ECDHE-RSA:+AES-128-GCM:+AES-128-CBC:+AEAD:+SHA256:+CURVE-ALL:+COMP-NULL:+SIGN-ALL:+CTYPE-X.509 Cipher suites for NONE:+VERS-TLS1.2:+ECDHE-RSA:+AES-128-GCM:+AES-128-CBC:+AEAD:+SHA256:+CURVE-ALL:+COMP-NULL:+SIGN-ALL:+CTYPE-X.509 TLS_ECDHE_RSA_AES_128_GCM_SHA256 0xc0, 0x2f TLS1.2 TLS_ECDHE_RSA_AES_128_CBC_SHA256 0xc0, 0x27 TLS1.2 Protocols: VERS-TLS1.2 Ciphers: AES-128-GCM, AES-128-CBC MACs: AEAD, SHA256 Key Exchange Algorithms: ECDHE-RSA Groups: GROUP-SECP256R1, GROUP-SECP384R1, GROUP-SECP521R1, GROUP-X25519, GROUP-X448, GROUP-FFDHE2048, GROUP-FFDHE3072, GROUP-FFDHE4096, GROUP-FFDHE6144, GROUP-FFDHE8192 PK-signatures: SIGN-RSA-SHA256, SIGN-RSA-PSS-SHA256, SIGN-RSA-PSS-RSAE-SHA256, SIGN-ECDSA-SHA256, SIGN-ECDSA-SECP256R1-SHA256, SIGN-EdDSA-Ed25519, SIGN-RSA-SHA384, SIGN-RSA-PSS-SHA384, SIGN-RSA-PSS-RSAE-SHA384, SIGN-ECDSA-SHA384, SIGN-ECDSA-SECP384R1-SHA384, SIGN-EdDSA-Ed448, SIGN-RSA-SHA512, SIGN-RSA-PSS-SHA512, SIGN-RSA-PSS-RSAE-SHA512, SIGN-ECDSA-SHA512, SIGN-ECDSA-SECP521R1-SHA512, SIGN-RSA-SHA1, SIGN-ECDSA-SHA1
Mudando de AES128 para AES256
O Zabbix usa AES128 como padrão interno para dados. Vamos supor que você esteja usando certificados e queira mudar para AES256, no OpenSSL 1.1.1.
Isso pode ser feito adicionando os respectivos parâmetros em
zabbix_server.conf
:
TLSCAFile=/home/zabbix/ca.crt TLSCertFile=/home/zabbix/server.crt TLSKeyFile=/home/zabbix/server.key TLSCipherCert13=TLS_AES_256_GCM_SHA384 TLSCipherCert=EECDH+aRSA+AES256:-SHA1:-SHA384 TLSCipherPSK13=TLS_CHACHA20_POLY1305_SHA256 TLSCipherPSK=kECDHEPSK+AES256:-SHA1 TLSCipherAll13=TLS_AES_256_GCM_SHA384 TLSCipherAll=EECDH+aRSA+AES256:-SHA1:-SHA384
Embora apenas os ciphersuites relacionados a certificados sejam usados, os parâmetros
TLSCipherPSK*
também são definidos para evitar seus valores padrão, que incluem cifras menos seguras para maior interoperabilidade. Os ciphersuites PSK não podem ser completamente desabilitados no server/proxy.
E em
zabbix_agentd.conf
:
TLSConnect=cert TLSAccept=cert TLSCAFile=/home/zabbix/ca.crt TLSCertFile=/home/zabbix/agent.crt TLSKeyFile=/home/zabbix/agent.key TLSCipherCert13=TLS_AES_256_GCM_SHA384 TLSCipherCert=EECDH+aRSA+AES256:-SHA1:-SHA384
What’s next?
1 Usando certificados
Did you find what you needed?
0
1
2
3
4
5
6
7
8
9
10
Not at all
Completely
Can you tell us more about your rating?
Your input is anonymous and helps us improve the documentation.
Send feedback
Help us improve this page
Select the text you'd like to improve and press
Ctrl + Enter
Command + Enter
to send feedback to our editors.
Search tip
Press
Ctrl + Alt + H
Command + Option + H
to toggle search highlight
Need help?
Technical Support
All services
Professional Training
Zabbix Forum
© 2001-2026 by Zabbix SIA. All rights reserved.
License
Copy
Copied
Suggest edit
Suggest edit
Cancel
Report
Suggest an example
Cancel
Report
Thank you!
Your feedback has been sent. We appreciate you taking the time to help improve Zabbix documentation.
Your suggestion has been sent to the editors. We appreciate you taking the time to help improve Zabbix documentation.
Something happened wrong. Please try again next time.
Ok

## 21 Extensões
URL: https://www.zabbix.com/documentation/current/pt/manual/extensions

21 Extensões
Esta página inclui conteúdo traduzido automaticamente. Se você notar um erro, selecione-o e pressione
Ctrl+Enter
Cmd+Enter
para reportá-lo aos editores.
Docs
Version:
7.4
(current)
Supported
7.4
(current)
7.0
6.0
In development
8.0
(devel)
Unsupported
7.2
6.4
6.2
5.4
5.2
5.0
4.4
4.2
4.0
3.4
3.2
3.0
2.4
2.2
2.0
1.8
General
info
guidelines
Language:
Português
English
日本語
Português
Español
Français
Latviešu
中文
Polski
Italiano
Deutsch
Русский
Català
Srpski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Manual do usuário
1 Introdução
1 Estrutura do manual
2 O que é o Zabbix
3 Funcionalidades do Zabbix
4 Visão geral do Zabbix
5 O que há de novo no Zabbix 7.4.0
6 O que há de novo no Zabbix 7.4.x
2. Definições
3 processos do Zabbix
1 Server
1 Alta disponibilidade
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Configuração a partir dos pacotes RHEL
2 Configuração a partir de pacotes Debian/Ubuntu
3 Configuração a partir do código-fonte
6 Sender
7 Obter
8 JS
9 Serviço web
4 Instalação e primeiros passos
1 Obtendo o Zabbix
2 Requisitos
3 Instalação a partir do código-fonte
1 Compilando o Zabbix agent no Windows
2 Compilando o Zabbix agent 2 no Windows
3 Compilando o Zabbix agent no macOS
4 Instalação a partir de pacotes
1 Instalação do agent do Windows a partir do MSI
2 Instalação do agent no macOS a partir do PKG
3 Lançamentos instáveis
5 Instalação a partir de containers
6 Instalação da interface web
7 Procedimento de atualização
1 Atualização a partir do código-fonte
2 Atualização a partir de pacotes
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Atualização a partir de containers
8 Problemas conhecidos
1 Problemas de compilação
2 Problemas de atualização relacionados a escaping
9 Alterações de template
10 Notas de atualização para 7.4.0
11 Notas de atualização para 7.4.x
5 Início rápido
1 Login e configuração do usuário
2 Novo host
3 Novo item
4 Novo trigger
5 Recebendo notificações de problemas
6 Novo modelo (template)
6 Zabbix appliance
7 Configuração
1 Hosts e grupos de hosts
1 Assistente de host
2 Configurando um host
3 Configurando um grupo de hosts
4 Inventário
5 Atualização em massa
2 Items
1 Criando um item
1 Formato da chave do item
2 Intervalos personalizados
2 Pré-processamento de valor de item
1 Teste de pré-processamento
2 Detalhes do pré-processamento
3 Exemplos de pré-processamento
4 Funcionalidade JSONPath
1 Escape de caracteres especiais de valores de macros LLD em JSONPath
5 Pré-processamento JavaScript
1 Objetos JavaScript adicionais
2 Objetos JavaScript de item de navegador
6 Pré-processamento de CSV para JSON
3 Tipos de item
1 Agent Zabbix
1 Zabbix agent 2
2 Agent Zabbix para Windows
3 Monitoramento de arquivos de log
2 Verificação simples
1 Chaves de item de monitoramento do VMware
3 agent SNMP
1 Índices dinâmicos
2 OIDs especiais
3 Arquivos MIB
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 Verificação externa
8 Monitor de banco de dados
9 agent HTTP
1 Verificação do Prometheus
10 agent IPMI
11 SSH agent
12 Telnet agent
13 agent JMX
14 item calculado
1 Cálculos agregados
15 item dependente
16 Item de script
17 item do navegador
4 Histórico e tendências
5 Parâmetros de usuário
1 Estendendo os agents do Zabbix
6 Contadores de desempenho do Windows
7 Atualização em massa
8 Mapeamento de valores
9 Fila
10 Cache de valores
11 Executar agora
12 Restringindo verificações do agent
3 triggers
1 Configurando um trigger
2 Expressão de trigger
3 Dependências de trigger
4 Severidade do trigger
5 Personalizando as severidades dos triggers
6 Atualização em massa
7 Funçõ
