# 1 Configuring a trigger

Fonte: https://www.zabbix.com/documentation/current/en/manual/config/triggers/trigger
Capturado em: 2026-09-08T13:30:29.820128+00:00
Páginas no domínio: 10

## 1 Configuring a trigger
URL: https://www.zabbix.com/documentation/current/en/manual/config/triggers/trigger

1 Configuring a trigger
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
English
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
User manual
1 Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 7.4.0
6 What's new in Zabbix 7.4.x
2 Definitions
3 Zabbix processes
1 Server
1 High availability
2 Agent
3 Agent 2
4 Proxy
5 Java gateway
1 Setup from RHEL packages
2 Setup from Debian/Ubuntu packages
3 Setup from sources
6 Sender
7 Get
8 JS
9 Web service
4 Installation and first steps
1 Getting Zabbix
2 Requirements
3 Installation from sources
1 Building Zabbix agent on Windows
2 Building Zabbix agent 2 on Windows
3 Building Zabbix agent on macOS
4 Installation from packages
1 Windows agent installation from MSI
2 macOS agent installation from PKG
3 Unstable releases
5 Installation from containers
6 Installation on public cloud platforms
1 AWS deployment guide for Zabbix server
2 AWS deployment guide for Zabbix proxy
3 Azure deployment guide for Zabbix server
4 Azure deployment guide for Zabbix proxy
5 Google Cloud deployment guide
7 Web interface installation
8 Upgrade procedure
1 Upgrade from sources
2 Upgrade from packages
1 Red Hat Enterprise Linux
2 Debian/Ubuntu
3 Upgrade from containers
9 Known issues
1 Compilation issues
2 Escaping-related upgrade issues
10 Template changes
11 Upgrade notes for 7.4.0
12 Upgrade notes for 7.4.x
5 Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
6 Zabbix appliance
7 Configuration
1 Hosts and host groups
1 Host Wizard
2 Configuring a host
3 Configuring a host group
4 Inventory
5 Mass update
2 Items
1 Creating an item
1 Item key format
2 Custom intervals
2 Item value preprocessing
1 Preprocessing testing
2 Preprocessing details
3 Preprocessing examples
4 JSONPath functionality
1 Escaping special characters from LLD macro values in JSONPath
5 JavaScript preprocessing
1 Additional JavaScript objects
2 Browser item JavaScript objects
6 CSV to JSON preprocessing
3 Item types
1 Zabbix agent
1 Zabbix agent 2
2 Windows Zabbix agent
3 Log file monitoring
2 Simple check
1 VMware monitoring item keys
3 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 MIB files
4 SNMP trap
5 Zabbix internal
6 Zabbix trapper
7 External check
8 Database monitor
9 HTTP agent
1 Prometheus check
10 IPMI agent
11 SSH agent
12 Telnet agent
13 JMX agent
14 Calculated item
1 Aggregate calculations
15 Dependent item
16 Script item
17 Browser item
4 History and trends
5 User parameters
1 Extending Zabbix agents
6 Windows performance counters
7 Mass update
8 Value mapping
9 Queue
10 Value cache
11 Execute now
12 Restricting agent checks
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customizing trigger severities
6 Mass update
7 Predictive trigger functions
4 Events
1 Trigger event generation
2 Other event sources
3 Manual closing of problems
5 Event correlation
1 Trigger-based event correlation
2 Global event correlation
6 Tagging
7 Visualization
1 Graphs
1 Simple graphs
2 Custom graphs
3 Ad-hoc graphs
2 Network maps
1 Configuring a network map
2 Host group elements
3 Link indicators
3 Dashboards
8 Templates and template groups
1 Configuring a template
2 Configuring a template group
3 Linking/unlinking
4 Nesting
5 Mass update
9 Templates out of the box
1 Zabbix agent template operation
2 Zabbix agent 2 template operation
3 HTTP template operation
4 IPMI template operation
5 JMX template operation
6 ODBC template operation
7 Standardized templates for network devices
8 VMware template operation
10 Notifications upon events
1 Media types
1 Email
1 Automated Gmail/Office365 media types
2 SMS
3 Custom alert scripts
4 Webhook
1 Webhook script examples
2 Actions
1 Conditions
2 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
3 Recovery operations
4 Update operations
5 Escalations
3 Receiving notification on unsupported items
11 Macros
1 Macro functions
2 User macros
3 User macros with context
4 Secret user macros
5 Low-level discovery macros
6 Expression macros
12 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
13 Storage of secrets
1 CyberArk configuration
2 HashiCorp configuration
14 Scheduled reports
15 Data export
1 Export to files
2 Streaming to external systems
3 SNMP gateway
8 Service monitoring
1 Service tree
2 SLA
3 Setup example
9 Web monitoring
1 Web monitoring items
2 Real-life scenario
10 Virtual machine monitoring
1 VMware monitoring item keys
2 Virtual machine discovery key fields
3 JSON examples for VMware items
4 VMware monitoring setup example
11 Maintenance
12 Regular expressions
13 Problem acknowledgment
1 Problem suppression
14 Configuration export/import
1 Template groups
2 Host groups
3 Templates
4 Hosts
5 Network maps
6 Media types
15 Discovery
1 Network discovery
1 Configuring a network discovery rule
2 Active agent autoregistration
3 Low-level discovery
1 Item prototypes
2 Trigger prototypes
3 Graph prototypes
4 Host prototypes
5 Discovery prototypes
6 Notes on low-level discovery
7 Discovery rules
1 Discovery of mounted filesystems
2 Discovery of network interfaces
3 Discovery of CPUs and CPU cores
4 Discovery of SNMP OIDs
5 Discovery of SNMP OIDs (legacy)
6 Discovery of JMX objects
7 Discovery of IPMI sensors
8 Discovery of systemd services
9 Discovery of Windows services
10 Discovery of Windows performance counter instances
11 Discovery using WMI queries
12 Discovery using ODBC SQL queries
13 Discovery using Prometheus data
14 Discovery of block devices
15 Discovery of host interfaces in Zabbix
8 Custom LLD rules
16 Distributed monitoring
1 Proxies
1 Synchronization of monitoring configuration
2 Proxy load balancing and high availability
17 Encryption
1 Using certificates
2 Using pre-shared keys
3 Troubleshooting
1 Connection type or permission problems
2 Certificate problems
3 PSK problems
18 Web interface
1 Menu
1 Event menu
2 Host menu
3 Item menu
2 Frontend sections
1 Dashboards
1 Dashboard widgets
1 Action log
2 Clock
3 Discovery status
4 Favorite graphs
5 Favorite maps
6 Gauge
7 Geomap
8 Graph
9 Graph (classic)
10 Graph prototype
11 Honeycomb
12 Host availability
13 Host card
14 Host navigator
15 Item card
16 Item history
17 Item navigator
18 Item value
19 Map
20 Map navigation tree
21 Pie chart
22 Problem hosts
23 Problems
24 Problems by severity
25 SLA report
26 System information
27 Top hosts
28 Top items
29 Top triggers
30 Trigger overview
31 URL
32 Web monitoring
2 Monitoring
1 Problems
1 Cause and symptom problems
2 Hosts
1 Graphs
2 Host dashboards
3 Web scenarios
3 Latest data
4 Maps
5 Discovery
3 Services
1 Services
2 SLA
3 SLA report
4 Inventory
1 Overview
2 Hosts
5 Reports
1 System information
2 Scheduled reports
3 Availability report
4 Top 100 triggers
5 Audit log
6 Action log
7 Notifications
6 Data collection
1 Template groups
2 Host groups
3 Templates
1 Items
2 Triggers
3 Graphs
4 Discovery rules
1 Item prototypes
2 Trigger prototypes
3 Graph prototypes
4 Host prototypes
5 Discovery prototypes
5 Web scenarios
4 Hosts
1 Items
2 Triggers
3 Graphs
4 Discovery rules
1 Item prototypes
2 Trigger prototypes
3 Graph prototypes
4 Host prototypes
5 Discovery prototypes
5 Web scenarios
5 Maintenance
6 Event correlation
7 Discovery
7 Alerts
1 Actions
2 Media types
3 Scripts
8 Users
1 User groups
2 User roles
3 Users
4 API tokens
5 Authentication
1 HTTP
2 LDAP
3 SAML
4 MFA
9 Administration
1 General
2 Audit log
3 Housekeeping
4 Proxies
5 Proxy groups
6 Macros
7 Queue
3 User settings
1 Global notifications
2 Sound in browsers
4 Global search
5 Frontend maintenance mode
6 Page parameters
7 Definitions
8 Creating your own theme
9 Debug mode
10 Cookies used by Zabbix
11 Time zones
12 Resetting password
13 Time period selector
19 Best practices
1 Security best practices
1 Access control
1 Securing MySQL/MariaDB
2 Securing PostgreSQL/TimescaleDB
2 Cryptography
3 Web server
2 Configuration best practices
20 API
Appendix 1. Reference commentary
Appendix 2. Changes from 7.2 to 7.4
Appendix 3. Changes in 7.4
Method reference
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.get
action.update
Alert
Alert object
alert.get
Audit log
Audit log object
auditlog.get
Authentication
Authentication object
authentication.get
authentication.update
Autoregistration
Autoregistration object
autoregistration.get
autoregistration.update
Configuration
configuration.export
configuration.import
configuration.importcompare
Connector
Connector object
connector.create
connector.delete
connector.get
connector.update
Correlation
Correlation object
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Dashboard object
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Dashboard widget fields
1 Action log
2 Clock
3 Discovery status
4 Favorite graphs
5 Favorite maps
6 Gauge
7 Geomap
8 Graph
9 Graph (classic)
10 Graph prototype
11 Honeycomb
12 Host availability
13 Host card
14 Host navigator
15 Item card
16 Item history
17 Item navigator
18 Item value
19 Map
20 Map navigation tree
21 Pie chart
22 Problem hosts
23 Problems
24 Problems by severity
25 SLA report
26 System information
27 Top hosts
28 Top items
29 Top triggers
30 Trigger overview
31 URL
32 Web monitoring
Discovered host
Discovered host object
dhost.get
Discovered service
Discovered service object
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.get
drule.update
Event
Event object
event.acknowledge
event.get
Graph
Graph object
graph.create
graph.delete
graph.get
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
High availability node
High availability node object
hanode.get
History
History object
history.clear
history.get
history.push
Host
Host object
host.create
host.delete
host.get
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.propagate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Host prototype
Host prototype object
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Housekeeping
Housekeeping object
housekeeping.get
housekeeping.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Image
Image object
image.create
image.delete
image.get
image.update
Item
Item object
item.create
item.delete
item.get
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
LLD rule
LLD rule object
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
LLD rule prototype
LLD rule prototype object
discoveryruleprototype.create
discoveryruleprototype.delete
discoveryruleprototype.get
discoveryruleprototype.update
MFA
MFA object
mfa.create
mfa.delete
mfa.get
mfa.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.get
map.update
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Module
Module object
module.create
module.delete
module.get
module.update
Problem
Problem object
problem.get
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.update
Proxy group
Proxy group object
proxygroup.create
proxygroup.delete
proxygroup.get
proxygroup.update
Regular expression
Regular expression object
regexp.create
regexp.delete
regexp.get
regexp.update
Report
Report object
report.create
report.delete
report.get
report.update
Role
Role object
role.create
role.delete
role.get
role.update
SLA
SLA object
sla.create
sla.delete
sla.get
sla.getsli
sla.update
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyevents
script.getscriptsbyhosts
script.update
Service
Service object
service.create
service.delete
service.get
service.update
Settings
Settings object
settings.get
settings.update
Task
Task object
task.create
task.get
Template
Template object
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template dashboard
Template dashboard object
templatedashboard.create
templatedashboard.delete
templatedashboard.get
templatedashboard.update
Template group
Template group object
templategroup.create
templategroup.delete
templategroup.get
templategroup.massadd
templategroup.massremove
templategroup.massupdate
templategroup.propagate
templategroup.update
Token
Token object
token.create
token.delete
token.generate
token.get
token.update
Trend
Trend object
trend.get
Trigger
Trigger object
trigger.create
trigger.delete
trigger.get
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
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
User directory
User directory object
userdirectory.create
userdirectory.delete
userdirectory.get
userdirectory.test
userdirectory.update
User group
User group object
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Value map
Value map object
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Web scenario
Web scenario object
httptest.create
httptest.delete
httptest.get
httptest.update
21 Extensions
1 Loadable modules
2 Plugins
3 Frontend modules
22 Appendixes
1 Installation and setup
1 Database creation
2 Repairing Zabbix database character set and collation
3 Database upgrade to primary keys
4 Preparing auditlog table for partitioning
5 Secure connection to the database
1 MySQL encryption configuration
2 PostgreSQL encryption configuration
6 Secure connection to the frontend
7 TimescaleDB setup
8 Elasticsearch setup
9 Distribution-specific notes on setting up Nginx for Zabbix
10 Running agent as root
11 Zabbix agent on Microsoft Windows
12 SAML setup with Microsoft Entra ID
13 SAML setup with Okta
14 SAML setup with OneLogin
15 Setting up scheduled reports
16 Additional frontend languages
17 Google Chrome TLS certificate trust
2 Process configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent 2 (UNIX)
5 Zabbix agent (Windows)
6 Zabbix agent 2 (Windows)
7 Zabbix agent 2 plugins
1 Ceph plugin
2 Docker plugin
3 Ember+ plugin
4 Memcached plugin
5 Modbus plugin
6 MongoDB plugin
7 MQTT plugin
8 MSSQL plugin
9 MySQL plugin
10 NVIDIA GPU plugin
11 Oracle plugin
12 PostgreSQL plugin
13 Redis plugin
14 SMART plugin
8 Zabbix Java gateway
9 Zabbix web service
10 Environment variables
3 Protocols
1 Server-proxy data exchange protocol
2 Zabbix agent/agent2 protocol
4 Zabbix agent 2 plugin protocol
5 Zabbix sender protocol
6 Header
7 Newline-delimited JSON export protocol
4 Items
1 vm.memory.size parameters
2 Passive and active agent checks
3 Minimum permission level for Windows agent items
4 Encoding of returned values
5 Large file support
6 Sensor
7 Notes on memtype parameter in proc.mem items
8 Notes on selecting processes in proc.mem and proc.num items
9 Implementation details of net.tcp.service and net.udp.service checks
10 proc.get parameters
11 Unreachable/unavailable host interface settings
12 Remote monitoring of Zabbix stats
13 Configuring Kerberos with Zabbix
14 modbus.get parameters
15 Creating custom performance counter names for VMware
16 Return values for system.sw.packages.get
17 Return values for net.dns.get
18 Notes on system.cpu.util items on Windows
5 Supported functions
1 Aggregate functions
1 Foreach functions
2 Bitwise functions
3 Date and time functions
4 History functions
5 Trend functions
6 Mathematical functions
7 Operator functions
8 Predictive functions
9 String functions
6 Macros
1 Macros supported by location
2 User macros supported by location
7 Unit symbols
8 Time period syntax
9 Command execution
10 Version compatibility
11 Zabbix sender dynamic link library for Windows
12 Service monitoring upgrade
13 Other issues
14 Agent vs agent 2 comparison
15 Escaping examples
23 Quick reference guides
1 Monitor Linux with Zabbix agent
2 Monitor Windows with Zabbix agent
3 Monitor Apache via HTTP
4 Monitor MySQL with Zabbix agent 2
5 Monitor VMware with Zabbix
6 Monitor network traffic with Zabbix
7 Monitor network traffic using active checks
8 Monitor websites with Browser items
9 Monitor website certificates with Zabbix agent 2 (passive)
10 Monitor a network switch or router with Zabbix
11 Monitor Windows event log using active checks
Zabbix Cloud
Deploy Zabbix in the cloud
Node configuration
Adding users
Key differences of Zabbix Cloud
Audit log
Developer center
Modules
Module file structure
manifest.json
Actions
Views
Assets
Register a new module
Widgets
Configuration
Presentation
Tutorials
Create a module (tutorial)
Create a widget (tutorial)
Examples
Plugins
Examples
Create a plugin (tutorial)
Plugin interfaces
Python library for Zabbix
Installation
Quickstart guide
Use Zabbix API
Collect data from Zabbix agent
Send data to Zabbix server or proxy
Debug logging
Changes to extension development
Zabbix manpages
zabbix_agent2
zabbix_agentd
zabbix_get
zabbix_js
zabbix_proxy
zabbix_sender
zabbix_server
zabbix_web_service
Copyright notice
User manual
7 Configuration
3 Triggers
1 Configuring a trigger
On this page
1 Configuring a trigger
Overview
Configuration
Testing expressions
1 Configuring a trigger
Overview
To configure a trigger, do the following:
Go to:
Data collection
>
Hosts
Click
Triggers
in the row of the host
Click
Create trigger
to the right (or on the trigger name to edit an existing trigger)
Enter parameters of the trigger in the form
See also
general information
on triggers and their calculation times.
Configuration
The
Trigger
tab contains all the essential trigger attributes.
All mandatory input fields are marked with a red asterisk.
Parameter
Description
Name
Trigger name.
Supported
macros
are: {HOST.HOST}, {HOST.NAME}, {HOST.PORT}, {HOST.CONN}, {HOST.DNS}, {HOST.IP}, {ITEM.VALUE}, {ITEM.VALUE.AGE}, {ITEM.VALUE.DATE}, {ITEM.VALUE.TIME}, {ITEM.VALUE.TIMESTAMP}, {ITEM.LASTVALUE}, {ITEM.LASTVALUE.AGE}, {ITEM.LASTVALUE.DATE}, {ITEM.LASTVALUE.TIME}, {ITEM.LASTVALUE.TIMESTAMP}, {ITEM.LOG.*}, and {$MACRO} user macros.
$1, $2...$9
macros can be used to refer to the first, second...ninth constant of the expression.
Note
: $1-$9 macros will resolve correctly if referring to constants in relatively simple, straightforward expressions. For example, the name "Processor load above $1 on {HOST.NAME}" will automatically change to "Processor load above 5 on New host" if the expression is last(/New host/system.cpu.load[percpu,avg1])>5.
Event name
When defined, this name will be used to create the problem event name. By default, the event name is the same as the trigger name.
The event name may be used to build meaningful alerts containing problem data (see
example
).
The same set of macros is supported as in the trigger name, plus {TIME}, {TIMESTAMP}, and {?EXPRESSION} expression macros.
Operational data
Enter some string with macros to display dynamic, real-time data in
Monitoring
>
Problems
. Alternatively, leave this field empty to display the latest values of all items from the trigger expression.
The same set of macros is supported as in the trigger name, with the ability to resolve dynamically. For example:
{ITEM.VALUE<1-9>} resolves to the item values at the moment the trigger state is changed (problem created, resolved, closed manually, or closed by correlation).
{ITEM.LASTVALUE<1-9>} resolves to the latest item values.
Note that closing a problem manually does not produce a new value, so both macros will still show the value from the problem time. Also note that both macros resolve to
UNKNOWN
if the latest value is older than
Max history display period
(see
Administration > General
).
Severity
Set the required trigger
severity
by clicking the buttons.
Expression
Logical
expression
used to define the conditions of a problem.
Time suffixes
and
memory size suffixes
are supported.
A problem is created after all the conditions included in the expression are met, i.e. the expression evaluates to TRUE. The problem will be resolved as soon as the expression evaluates to FALSE, unless additional recovery conditions are specified in
Recovery expression
.
OK event generation
OK event generation options:
Expression
- OK events are generated based on the same expression as problem events;
Recovery expression
- OK events are generated if the problem expression evaluates to FALSE and the recovery expression evaluates to TRUE;
None
- in this case the trigger will never return to an OK state on its own.
Recovery expression
Logical
expression
(optional) defining additional conditions that have to be met before the problem is resolved, after the original problem expression has already been evaluated as FALSE.
Recovery expression is useful for trigger
hysteresis
. It is
not
possible to resolve a problem by recovery expression alone if the problem expression is still TRUE.
This field is only available if 'Recovery expression' is selected for
OK event generation
.
PROBLEM event generation mode
Mode for generating problem events:
Single
- a single event is generated when a trigger goes into the 'Problem' state for the first time;
Multiple
- an event is generated upon
every
'Problem' evaluation of the trigger.
OK event closes
Select if OK event closes:
All problems
- all problems of this trigger;
All problems if tag values match
- only those trigger problems with matching event tag values.
Tag for matching
Enter event tag name to use for event correlation.
This field is displayed if 'All problems if tag values match' is selected for the
OK event closes
property and is mandatory in this case.
Allow manual close
Check to allow
manual closing
of problem events generated by this trigger. Manual closing is possible when acknowledging problem events.
Menu entry name
If not empty, the name entered here (up to 64 characters) is used in several frontend locations as a label for the trigger URL specified in the
Menu entry URL
parameter. If empty, the default name
Trigger URL
is used.
The same set of macros is supported as in the trigger name, plus {EVENT.ID}, {HOST.ID}, and {TRIGGER.ID}.
Menu entry URL
If not empty, the URL entered here (up to 2048 characters) is available as a link in the
event menu
in several frontend locations, for example, when clicking the problem name in
Monitoring >
Problems
or
Problems
dashboard widget.
The same set of macros is supported as in the trigger name, plus {EVENT.ID}, {HOST.ID}, and {TRIGGER.ID}. Note: user macros with secret values will not be resolved in the URL.
Description
Text field used to provide more information about this trigger. May contain instructions for fixing specific problem, contact detail of responsible staff, etc.
The same set of macros is supported as in the trigger name.
Enabled
Unchecking this box will disable the trigger if required.
Problems of a disabled trigger are no longer displayed in the frontend, but are not deleted.
The
Tags
tab allows you to define trigger-level
tags
. All problems of this trigger will be tagged with the values entered here.
In addition, the
Inherited and trigger tags
option allows you to view tags defined on the template level if the trigger comes from that template. If there are multiple templates with the same tag, these tags are displayed once and template names are separated by commas. A trigger does not "inherit" and display host-level tags.
Parameter
Description
Name/Value
Set custom tags to mark trigger events.
Tags are a pair of tag name and value. You can use only the name or pair it with a value. A trigger may have several tags with the same name, but different values.
User macros, user macros with context, low-level discovery macros, and macro
functions
with
{{ITEM.VALUE}}
,
{{ITEM.LASTVALUE}}
are supported in event tags. Low-level discovery macros can be used inside macro context.
{TRIGGER.ID} macro is supported in trigger tag values. It may be useful for identifying triggers created from trigger prototypes and, for example, suppressing problems from these triggers during maintenance.
If the total length of expanded value exceeds 255, it will be cut to 255 characters.
See all
macros
supported for event tags.
Event tags
can be used for event correlation, in action conditions and will also be seen in
Monitoring
>
Problems
or the
Problems
widget.
The
Dependencies
tab contains all the
dependencies
of the trigger.
Click
Add
to add a new dependency.
You can also configure a trigger by opening an existing one, clicking the
Clone
button and then saving under a different name.
Testing expressions
It is possible to test the configured trigger expression as to what the expression result would be depending on the received value.
The following expression from an official template is taken as an example:
avg(/Cisco IOS SNMPv2/sensor.temp.value[ciscoEnvMonTemperatureValue.{#SNMPINDEX}],5m)>{$TEMP_WARN} or last(/Cisco IOS SNMPv2/sensor.temp.status[ciscoEnvMonTemperatureState.{#SNMPINDEX}])={$TEMP_WARN_STATUS}
To test the expression, click
Expression constructor
under the expression field.
In the Expression constructor, all individual expressions are listed. To open the testing window, click
Test
below the expression list.
In the testing window you can enter sample values ('80', '70', '0', '1' in this example) and then see the expression result, by clicking the
Test
button.
The result of the individual expressions as well as the whole expression can be seen.
"TRUE" means that the specified expression is correct. In this particular case A, "80" is greater than the {$TEMP_WARN} specified value, "70" in this example. As expected, a "TRUE" result appears.
"FALSE" means that the specified expression is incorrect. In this particular case B, {$TEMP_WARN_STATUS} "1" needs to be equal with specified value, "0" in this example. As expected, a "FALSE" result appears.
The chosen expression type is "OR". If at least one of the specified conditions (A or B in this case) is TRUE, the overall result will be TRUE as well. Meaning that the current value exceeds the warning value and a problem has occurred.
What’s next?
2 Trigger expression
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

## General Information
URL: https://www.zabbix.com/documentation/info/en

General Information
Docs
Version:
info
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
English
English
Theme:
Light
Dark
System
Zabbix Documentation License
General Information
These pages contain official general information:
Zabbix Documentation License
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/1.8/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
1.8
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
English
English
日本語
Русский
Português
Français
Polski
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1 About
1 Overview of Zabbix
2 Goals and Principles
3 Installation and Upgrade Notes
4. What's new in Zabbix 1.8
5 What's new in Zabbix 1.8.1
6 What's new in Zabbix 1.8.2
7 What's new in Zabbix 1.8.3
8 What's new in Zabbix 1.8.4
9 What's new in Zabbix 1.8.5
10 What's new in Zabbix 1.8.6
11 What's new in Zabbix 1.8.7
11 What's new in Zabbix 1.8.8
11 What's new in Zabbix 1.8.9
12 What's new in Zabbix 1.8.10
13 What's new in Zabbix 1.8.11
14 What's new in Zabbix 1.8.12
15 What's new in Zabbix 1.8.13
15 What's new in Zabbix 1.8.14
16 What's new in Zabbix 1.8.15
17 What's new in Zabbix 1.8.16
18 What's new in Zabbix 1.8.17
19 What's new in Zabbix 1.8.18
20 What's new in Zabbix 1.8.20
21 What's new in Zabbix 1.8.21
22 What's new in Zabbix 1.8.22
2 Installation
1 How to Get Zabbix
2 Requirements
3 Components
4 Installation from Source
5 Upgrading
6 Using Zabbix appliance
3 Zabbix Processes
1 Zabbix Server
2 Zabbix Proxy
3 Zabbix Agent (UNIX, Standalone daemon)
4 Zabbix Agent (UNIX, Inetd version)
5 Zabbix Agent (Windows)
6 Zabbix Sender (UNIX)
7 Zabbix Get (UNIX)
8 Special notes on "Include" configuration parameter
4 Configuration
1 Actions
2 Macros
3 Applications
4 Graphs
5 Media
6 Host templates
7 Host groups
8 Host and trigger dependencies
10 User Parameters
11 Windows performance counters
12 Triggers
13 Screens and Slide Shows
14 IT Services
15 User permissions
16 The Queue
17 Utilities
18 Regular expressions
19 Items
20 Frontend definitions
21 Suffixes
22 Time period specification
5 Quick Start Guide
1 Login
2 Add user
3 Email settings
4 Monitoring an agent-enabled host
5 Set up notifications
6 XML Import and Export
1 Goals
2 Overview
3 Host export
4 Host import
5 Map export and import
6 Screen export and import
7 Tutorials
1 Extending Zabbix Agents
2 Monitoring of log files
3 Remote commands
4 Monitoring of Windows Services
9 WEB Monitoring
1 Goals
2 Overview
3 WEB Scenario
4 WEB Step
5 Real life scenario
10 Log File Monitoring
2 How it works
Overview
11 Discovery
1 Goals
2 Overview
3 How it works
4 Network discovery rule
5 Real life scenario
12 Advanced SNMP Monitoring
1 Special OIDs
2 Use of dynamic indexes
13 Monitoring of IPMI devices
1 Goals
2 IPMI parameters
3 IPMI actions
14 Use of Proxies
1 Why use Proxy?
2 Proxy v.s. Node
3 Configuration
15 Distributed Monitoring
1 Goals
2 Overview
3 Configuration
4 Platform independence
5 Configuration of a single Node
6 Switching between nodes
7 Data flow
8 Performance considerations
16 Maintenance mode for Zabbix GUI
1 Goals
2 Configuration
3 How it looks like
17 WEB Interface
1 Creating your own theme
2 Configuration
3 Administration
4 Page parameters
18 Performance Tuning
2 Performance tuning
Real world configuration
19 Cookbook
2 Monitoring of Specific Applications
3 Integration
General Recipes
20 Troubleshooting
1 Error and warning messages
2 Sound in browsers
21 Escalations and repeated notifications
1 Overview
2 Simple messages
3 Remote commands
4 Repeated notifications
5 Delayed notifications
6 Escalate to Boss
7 Complex scenario
Zabbix API
APIInfo
version()
Action
create()
delete()
exists()
get()
update()
Alert
get()
Application
create()
delete()
exists()
get()
massAdd()
update()
DCheck
get()
DHost
delete()
get()
DRule
create()
delete()
exists()
get()
update()
DService
create()
delete()
exists()
get()
update()
Event
acknowledge()
delete()
get()
Example API session
Getting started with Zabbix API
Graph
create()
delete()
exists()
get()
update()
Graphitem
get()
History
delete()
get()
Host
create()
delete()
exists()
get()
massAdd()
massRemove()
massUpdate()
update()
Hostgroup
create()
delete()
exists()
get()
massAdd()
massRemove()
massUpdate()
update()
Image
create()
delete()
exists()
get()
update()
Item
create()
delete()
exists()
get()
update()
Maintenance
create()
delete()
exists()
get()
update()
Map
create()
delete()
exists()
get()
update()
Mediatype
create()
delete()
get()
update()
Proxy
get()
Screen
create()
delete()
exists()
get()
update()
Script
create()
delete()
execute()
get()
update()
Template
create()
delete()
exists()
get()
massAdd()
massRemove()
massUpdate()
update()
Trigger
addDependencies()
create()
delete()
deleteDependencies()
exists()
get()
update()
User
addMedia()
authenticate()
create()
delete()
deleteMedia()
get()
login()
logout()
update()
updateMedia()
updateProfile()
Usergroup
create()
delete()
exists()
get()
massAdd()
massRemove()
massUpdate()
update()
Usermacro
createGlobal()
deleteGlobal()
deleteHostMacro()
get()
massAdd()
massRemove()
massUpdate()
updateGlobal()
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
Zabbix Protocols
1 Zabbix Agent
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Log in with your
Zabbix forums
username and password to be able to watch pages.
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/2.0/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
2.0
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
English
English
日本語
Русский
Français
Polski
Português
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1. Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 2.0.0
6 What's new in Zabbix 2.0.1
7 What's new in Zabbix 2.0.2
8 What's new in Zabbix 2.0.3
9 What's new in Zabbix 2.0.4
10 What's new in Zabbix 2.0.5
11 What's new in Zabbix 2.0.6
12 What's new in Zabbix 2.0.7
13 What's new in Zabbix 2.0.8
14 What's new in Zabbix 2.0.9
15 What's new in Zabbix 2.0.10
16 What's new in Zabbix 2.0.11
17 What's new in Zabbix 2.0.12
18 What's new in Zabbix 2.0.13
19 What's new in Zabbix 2.0.14
20 What's new in Zabbix 2.0.15
21 What's new in Zabbix 2.0.16
22 What's new in Zabbix 2.0.17
Frontend improvements
2. Zabbix concepts
1 Zabbix definitions
2 Server
3 Agent
4 Proxy
5 Java gateway
6 Sender
7 Get
3. Installation
1 Getting Zabbix
2 Requirements
3 Installation from packages
4 Installation from sources
5 Known issues
6 Upgrade procedure
7 Upgrade notes for 2.0.0
8 Upgrade notes for 2.0.1
9 Upgrade notes for 2.0.2
10 Upgrade notes for 2.0.3
11 Upgrade notes for 2.0.4
12 Upgrade notes for 2.0.5
13 Upgrade notes for 2.0.6
14 Upgrade notes for 2.0.7
15 Upgrade notes for 2.0.8
16 Upgrade notes for 2.0.9
17 Upgrade notes for 2.0.10
18 Upgrade notes for 2.0.11
19 Upgrade notes for 2.0.12
20 Upgrade notes for 2.0.13
21 Upgrade notes for 2.0.14
22 Upgrade notes for 2.0.15
23 Upgrade notes for 2.0.16
24 Upgrade notes for 2.0.17
4. Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
5. Zabbix appliance
6. Configuration
1 Hosts and host groups
1 Configuring a host
2 Inventory
3 Mass update
2 Items
1 Creating an item
1 Item key
2 Item types
1 Zabbix agent
Windows-specific item keys
2 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 SNMP traps
4 IPMI checks
5 Simple checks
6 Log file monitoring
7 Calculated items
8 Internal checks
9 SSH checks
10 Telnet checks
11 External checks
12 Aggregate checks
13 Trapper items
14 JMX monitoring
15 ODBC monitoring
3 History and trends
4 User parameters
1 Extending Zabbix agents
5 Windows performance counters
6 Mass update
7 Value mapping
8 Applications
9 Queue
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customising trigger severities
6 Unit symbols
7 Mass update
4 Events
1 Event sources
5 Visualisation
1 Graphs
1 Simple graphs
2 Custom graphs
2 Network maps
1 Configuring a network map
2 Link indicators
3 Screens
4 Slide shows
6 Templates
1 Configuring a template
2 Linking/unlinking
3 Nesting
7 Notifications upon events
1 Media types
1 E-mail
2 SMS
3 Jabber
4 Ez Texting
5 Custom alertscripts
2 Actions
1 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
2 Conditions
3 Escalations
8 Macros
User macros
9 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
7. IT services
8. Web monitoring
1 Web monitoring items
2 Real life scenario
9. Maintenance
10. Regular expressions
11. Event acknowledgment
12. Configuration export/import
Groups
Hosts
13. Discovery
1 Network discovery
Configuring a network discovery rule
2 Active agent auto-registration
3 Low-level discovery
14. Distributed monitoring
1 Proxies
2 Nodes
15. Web interface
1 Frontend sections
1 Monitoring
1 Dashboard
2 Overview
3 Web
4 Latest data
5 Triggers
6 Events
7 Graphs
8 Screens
9 Maps
10 Discovery
11 IT services
2 Inventory
1 Overview
2 Hosts
3 Reports
1 Status of Zabbix
2 Availability report
3 Triggers top 100
4 Bar reports
4 Configuration
1 Host groups
2 Templates
3 Hosts
1 Applications
2 Items
3 Triggers
4 Graphs
5 Discovery rules
4 Maintenance
5 Web
6 Actions
7 Screens
8 Slide shows
9 Maps
10 Discovery
11 IT services
5 Administration
1 General
2 DM
3 Authentication
4 Users
5 Media types
6 Scripts
7 Audit
8 Queue
9 Notifications
10 Installation
2 User profile
1 Global notifications
2 Sound in browsers
3 Global search
4 Frontend maintenance mode
5 Definitions
6 Creating your own theme
7 Debug mode
16. Appendixes
1 Frequently asked questions / Troubleshooting
2 Installation
1 Database creation scripts
2 Zabbix agent on Microsoft Windows
3 Troubleshooting installation issues
3 Daemon configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent (Windows)
5 Zabbix Java gateway
6 Archive: Zabbix agent (UNIX, Inetd version)
7 Special notes on "Include" parameter
4 Items
1 Items supported by platform
2 vm.memory.size parameters
3 Passive and active agent checks
4 Encoding of returned values
5 Large file support
6 Unreachable/unavailable host settings
7 Implementation details of net.tcp.service checks
5 Triggers
1 Supported trigger functions
6 Macros
1 Macros supported by location
7 Setting time periods
8 Command execution
9 Recipes for monitoring
10 Performance tuning
11 Version compatibility
Zabbix API
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.exists
action.get
action.update
Alert
Alert object
alert.get
Application
Application object
application.create
application.delete
application.exists
application.get
application.massadd
application.update
Configuration
configuration.export
configuration.import
Discovered host
Discovered host object
dhost.exists
dhost.get
Discovered service
Discovered service object
dservice.exists
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.exists
drule.get
drule.isreadable
drule.iswritable
drule.update
Event
Event object
event.acknowledge
event.get
Generic Zabbix API information
Graph
Graph object
graph.create
graph.delete
graph.exists
graph.get
graph.getobjects
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.exists
graphprototype.get
graphprototype.getobjects
graphprototype.update
History
History object
history.get
Host
Host object
host.create
host.delete
host.exists
host.get
host.getobjects
host.isreadable
host.iswritable
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.exists
hostgroup.get
hostgroup.getobjects
hostgroup.isreadable
hostgroup.iswritable
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.exists
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
IT service
IT Service object
service.adddependencies
service.addtimes
service.create
service.delete
service.deletedependencies
service.deletetimes
service.get
service.getsla
service.isreadable
service.iswritable
service.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.isreadable
iconmap.iswritable
iconmap.update
Image
Image object
image.create
image.delete
image.exists
image.get
image.getobjects
image.update
Item
Item object
item.create
item.delete
item.exists
item.get
item.getobjects
item.isreadable
item.iswritable
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.exists
itemprototype.get
itemprototype.isreadable
itemprototype.iswritable
itemprototype.update
LLD rule
LLD rule object
discoveryrule.copy
discoveryrule.create
discoveryrule.delete
discoveryrule.exists
discoveryrule.get
discoveryrule.isreadable
discoveryrule.iswritable
discoveryrule.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.exists
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.exists
map.get
map.getobjects
map.isreadable
map.iswritable
map.update
Media
Media object
usermedia.get
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.isreadable
proxy.iswritable
proxy.update
Screen
Screen object
screen.create
screen.delete
screen.exists
screen.get
screen.update
Screen item
Screen item object
screenitem.create
screenitem.delete
screenitem.get
screenitem.isreadable
screenitem.iswritable
screenitem.update
screenitem.updatebyposition
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyhosts
script.update
Template
Template object
template.create
template.delete
template.exists
template.get
template.getobjects
template.isreadable
template.iswritable
template.massadd
template.massremove
template.massupdate
template.update
Template screen
Template screen object
templatescreen.copy
templatescreen.create
templatescreen.delete
templatescreen.exists
templatescreen.get
templatescreen.isreadable
templatescreen.iswritable
templatescreen.update
Template screen item
Template screen item object
templatescreenitem.get
Trigger
Trigger object
trigger.adddependencies
trigger.create
trigger.delete
trigger.deletedependencies
trigger.exists
trigger.get
trigger.getobjects
trigger.isreadable
trigger.iswritable
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
user.addmedia
user.authenticate
user.create
user.delete
user.deletemedia
user.get
user.isreadable
user.iswritable
user.login
user.logout
user.update
user.updatemedia
user.updateprofile
User group
User group object
usergroup.create
usergroup.delete
usergroup.exists
usergroup.get
usergroup.getobjects
usergroup.isreadable
usergroup.iswritable
usergroup.massadd
usergroup.massupdate
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Web scenario
Web scenario object
webcheck.create
webcheck.delete
webcheck.get
webcheck.isreadable
webcheck.iswritable
webcheck.update
Zabbix API changes from 1.8 to 2.0
Zabbix API changes in 2.0
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
Zabbix API
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Use the sidebar navigation to browse documentation pages.
To be able to watch pages, log in with your
Zabbix forums
username and password.
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/2.2/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
2.2
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
English
English
日本語
Русский
Polski
Português
Русский
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1. Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 2.2.0
6 What's new in Zabbix 2.2.1
7 What's new in Zabbix 2.2.2
8 What's new in Zabbix 2.2.3
9 What's new in Zabbix 2.2.4
10 What's new in Zabbix 2.2.5
11 What's new in Zabbix 2.2.6
12 What's new in Zabbix 2.2.7
13 What's new in Zabbix 2.2.8
14 What's new in Zabbix 2.2.9
15 What's new in Zabbix 2.2.10
16 What's new in Zabbix 2.2.11
17 What's new in Zabbix 2.2.12
18 What's new in Zabbix 2.2.13
19 What's new in Zabbix 2.2.15
20 What's new in Zabbix 2.2.16
21 What's new in Zabbix 2.2.17
22 What's new in Zabbix 2.2.18
23 What's new in Zabbix 2.2.19
24 What's new in Zabbix 2.2.20
25 What's new in Zabbix 2.2.21
26 What's new in Zabbix 2.2.22
27 What's new in Zabbix 2.2.23
28 What's new in Zabbix 2.2.24
2. Zabbix concepts
1 Zabbix definitions
2 Server
3 Agent
4 Proxy
5 Java gateway
6 Sender
7 Get
3. Installation
1 Getting Zabbix
2 Requirements
Best practices for secure Zabbix setup
3 Installation from packages
4 Installation from sources
5 Upgrade procedure
6 Known issues
7 Template changes
8 Upgrade notes for 2.2.0
9 Upgrade notes for 2.2.1
10 Upgrade notes for 2.2.2
11 Upgrade notes for 2.2.3
12 Upgrade notes for 2.2.4
13 Upgrade notes for 2.2.5
14 Upgrade notes for 2.2.6
15 Upgrade notes for 2.2.7
16 Upgrade notes for 2.2.8
17 Upgrade notes for 2.2.9
18 Upgrade notes for 2.2.10
19 Upgrade notes for 2.2.11
20 Upgrade notes for 2.2.12
21 Upgrade notes for 2.2.13
22 Upgrade notes for 2.2.14
23 Upgrade notes for 2.2.15
24 Upgrade notes for 2.2.16
25 Upgrade notes for 2.2.17
26 Upgrade notes for 2.2.18
27 Upgrade notes for 2.2.19
28 Upgrade notes for 2.2.20
29 Upgrade notes for 2.2.21
30 Upgrade notes for 2.2.22
31 Upgrade notes for 2.2.23
4. Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
5. Zabbix appliance
6. Configuration
1 Hosts and host groups
1 Configuring a host
2 Inventory
3 Mass update
2 Items
1 Creating an item
1 Item key format
2 Item types
1 Zabbix agent
Windows-specific item keys
2 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 SNMP traps
4 IPMI checks
5 Simple checks
1 VMware monitoring item keys
6 Log file monitoring
7 Calculated items
8 Internal checks
9 SSH checks
10 Telnet checks
11 External checks
12 Aggregate checks
13 Trapper items
14 JMX monitoring
15 ODBC monitoring
3 History and trends
4 User parameters
1 Extending Zabbix agents
5 Loadable modules
6 Windows performance counters
7 Mass update
8 Value mapping
9 Applications
10 Queue
11 Value cache
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customising trigger severities
6 Unit symbols
7 Mass update
4 Events
1 Event sources
5 Visualisation
1 Graphs
1 Simple graphs
2 Custom graphs
2 Network maps
1 Configuring a network map
2 Host group elements
3 Link indicators
3 Screens
4 Slide shows
6 Templates
1 Configuring a template
2 Linking/unlinking
3 Nesting
7 Notifications upon events
1 Media types
1 E-mail
2 SMS
3 Jabber
4 Ez Texting
5 Custom alertscripts
2 Actions
1 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
2 Conditions
3 Escalations
3 Receiving notification on unsupported items
8 Macros
User macros
9 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
7. IT services
8. Web monitoring
1 Web monitoring items
2 Real life scenario
9. Virtual machine monitoring
Virtual machine discovery key fields
10. Maintenance
11. Regular expressions
12. Event acknowledgement
13. Configuration export/import
Groups
Hosts
14. Discovery
1 Network discovery
Configuring a network discovery rule
2 Active agent auto-registration
3 Low-level discovery
15. Distributed monitoring
1 Proxies
2 Nodes
16. Web interface
1 Frontend sections
1 Monitoring
1 Dashboard
2 Overview
3 Web
4 Latest data
5 Triggers
6 Events
7 Graphs
8 Screens
9 Maps
10 Discovery
11 IT services
2 Inventory
1 Overview
2 Hosts
3 Reports
1 Status of Zabbix
2 Availability report
3 Triggers top 100
4 Bar reports
4 Configuration
1 Host groups
2 Templates
3 Hosts
1 Applications
2 Items
3 Triggers
4 Graphs
5 Discovery rules
6 Web scenarios
4 Maintenance
5 Actions
6 Screens
7 Slide shows
8 Maps
9 Discovery
10 IT services
5 Administration
1 General
2 DM
3 Authentication
4 Users
5 Media types
6 Scripts
7 Audit
8 Queue
9 Notifications
10 Installation
2 User profile
1 Global notifications
2 Sound in browsers
3 Global search
4 Frontend maintenance mode
5 Page parameters
6 Definitions
7 Creating your own theme
8 Debug mode
17. API
Appendix 1. Reference commentary
Appendix 2. Changes from 2.0 to 2.2
Method reference
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.exists
action.get
action.update
Alert
Alert object
alert.get
Application
Application object
application.create
application.delete
application.exists
application.get
application.massadd
application.update
Configuration
configuration.export
configuration.import
Discovered host
Discovered host object
dhost.exists
dhost.get
Discovered service
Discovered service object
dservice.exists
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.exists
drule.get
drule.isreadable
drule.iswritable
drule.update
Event
Event object
event.acknowledge
event.get
Graph
Graph object
graph.create
graph.delete
graph.exists
graph.get
graph.getobjects
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.exists
graphprototype.get
graphprototype.getobjects
graphprototype.update
History
History object
history.get
Host
Host object
host.create
host.delete
host.exists
host.get
host.getobjects
host.isreadable
host.iswritable
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.exists
hostgroup.get
hostgroup.getobjects
hostgroup.isreadable
hostgroup.iswritable
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.exists
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Host prototype
Host prototype object
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.isreadable
hostprototype.iswritable
hostprototype.update
IT service
IT Service object
service.adddependencies
service.addtimes
service.create
service.delete
service.deletedependencies
service.deletetimes
service.get
service.getsla
service.isreadable
service.iswritable
service.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.isreadable
iconmap.iswritable
iconmap.update
Image
Image object
image.create
image.delete
image.exists
image.get
image.getobjects
image.update
Item
Item object
item.create
item.delete
item.exists
item.get
item.getobjects
item.isreadable
item.iswritable
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.exists
itemprototype.get
itemprototype.isreadable
itemprototype.iswritable
itemprototype.update
LLD rule
LLD rule object
discoveryrule.copy
discoveryrule.create
discoveryrule.delete
discoveryrule.exists
discoveryrule.get
discoveryrule.isreadable
discoveryrule.iswritable
discoveryrule.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.exists
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.exists
map.get
map.getobjects
map.isreadable
map.iswritable
map.update
Media
Media object
usermedia.get
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.isreadable
proxy.iswritable
proxy.update
Screen
Screen object
screen.create
screen.delete
screen.exists
screen.get
screen.update
Screen item
Screen item object
screenitem.create
screenitem.delete
screenitem.get
screenitem.isreadable
screenitem.iswritable
screenitem.update
screenitem.updatebyposition
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyhosts
script.update
Template
Template object
template.create
template.delete
template.exists
template.get
template.getobjects
template.isreadable
template.iswritable
template.massadd
template.massremove
template.massupdate
template.update
Template screen
Template screen object
templatescreen.copy
templatescreen.create
templatescreen.delete
templatescreen.exists
templatescreen.get
templatescreen.isreadable
templatescreen.iswritable
templatescreen.update
Template screen item
Template screen item object
templatescreenitem.get
Trigger
Trigger object
trigger.adddependencies
trigger.create
trigger.delete
trigger.deletedependencies
trigger.exists
trigger.get
trigger.getobjects
trigger.isreadable
trigger.iswritable
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
user.addmedia
user.authenticate
user.checkAuthentication
user.create
user.delete
user.deletemedia
user.get
user.isreadable
user.iswritable
user.login
user.logout
user.update
user.updatemedia
user.updateprofile
User group
User group object
usergroup.create
usergroup.delete
usergroup.exists
usergroup.get
usergroup.getobjects
usergroup.isreadable
usergroup.iswritable
usergroup.massadd
usergroup.massupdate
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Web scenario
Web scenario object
httptest.create
httptest.delete
httptest.get
httptest.isreadable
httptest.iswritable
httptest.update
webcheck.create
webcheck.delete
webcheck.get
webcheck.isreadable
webcheck.iswritable
webcheck.update
Zabbix API changes in 2.2
18. Appendixes
1 Frequently asked questions / Troubleshooting
2 Installation
1 Database creation scripts
2 Zabbix agent on Microsoft Windows
3 Troubleshooting installation issues
3 Daemon configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent (Windows)
5 Zabbix Java gateway
6 Archive: Zabbix agent (UNIX, Inetd version)
7 Special notes on "Include" parameter
4 Protocols
1 Zabbix sender protocol
2 Zabbix agent protocol
3 Header and data length
5 Items
1 Items supported by platform
2 vm.memory.size parameters
3 Passive and active agent checks
4 Trapper items
5 Encoding of returned values
6 Large file support
7 Sensor
8 Implementation details of net.tcp.service checks
9 Unreachable/unavailable host settings
6 Triggers
1 Supported trigger functions
7 Macros
1 Macros supported by location
8 Setting time periods
9 Command execution
10 Recipes for monitoring
11 Performance tuning
12 Version compatibility
13 Database error handling
14 Zabbix sender dynamic link library for Windows
15 Other issues
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Use the sidebar navigation to browse documentation pages.
To be able to watch pages, log in with your
Zabbix forums
username and password.
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/2.4/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
2.4
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
English
English
Русский
Português
Русский
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1. Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 2.4.0
6 What's new in Zabbix 2.4.1
7 What's new in Zabbix 2.4.2
8 What's new in Zabbix 2.4.3
9 What's new in Zabbix 2.4.4
10 What's new in Zabbix 2.4.5
11 What's new in Zabbix 2.4.6
12 What's new in Zabbix 2.4.7
13 What's new in Zabbix 2.4.8
2. Zabbix concepts
1 Zabbix definitions
2 Server
3 Agent
4 Proxy
5 Java gateway
6 Sender
7 Get
3. Installation
1 Getting Zabbix
2 Requirements
3 Installation from packages
4 Installation from sources
5 Upgrade procedure
6 Known issues
7 Template changes
8 Upgrade notes for 2.4.0
9 Upgrade notes for 2.4.1
10 Upgrade notes for 2.4.2
11 Upgrade notes for 2.4.3
12 Upgrade notes for 2.4.4
13 Upgrade notes for 2.4.5
14 Upgrade notes for 2.4.6
15 Upgrade notes for 2.4.7
16 Upgrade notes for 2.4.8
4. Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
5. Zabbix appliance
6. Configuration
1 Hosts and host groups
1 Configuring a host
2 Inventory
3 Mass update
2 Items
1 Creating an item
1 Item key
2 Item types
1 Zabbix agent
Windows-specific item keys
2 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 SNMP traps
4 IPMI checks
5 Simple checks
1 VMware monitoring item keys
6 Log file monitoring
7 Calculated items
8 Internal checks
9 SSH checks
10 Telnet checks
11 External checks
12 Aggregate checks
13 Trapper items
14 JMX monitoring
15 ODBC monitoring
3 History and trends
4 User parameters
1 Extending Zabbix agents
5 Loadable modules
6 Windows performance counters
7 Mass update
8 Value mapping
9 Applications
10 Queue
11 Value cache
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customising trigger severities
6 Unit symbols
7 Mass update
4 Events
1 Event sources
5 Visualisation
1 Graphs
1 Simple graphs
2 Custom graphs
3 Ad-hoc graphs
2 Network maps
1 Configuring a network map
2 Link indicators
3 Screens
1 Screen elements
4 Slide shows
6 Templates
1 Configuring a template
2 Linking/unlinking
3 Nesting
7 Notifications upon events
1 Media types
1 E-mail
2 SMS
3 Jabber
4 Ez Texting
5 Custom alertscripts
2 Actions
1 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
2 Conditions
3 Escalations
3 Receiving notification on unsupported items
8 Macros
1 User macros
9 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
7. IT services
8. Web monitoring
1 Web monitoring items
2 Real life scenario
9. Virtual machine monitoring
1 Virtual machine discovery key fields
10. Maintenance
11. Regular expressions
12. Event acknowledgment
13. Configuration export/import
Groups
Hosts
14. Discovery
1 Network discovery
Configuring a network discovery rule
2 Active agent auto-registration
3 Low-level discovery
15. Distributed monitoring
1 Proxies
16. Web interface
1 Frontend sections
1 Monitoring
1 Dashboard
2 Overview
3 Web
4 Latest data
5 Triggers
6 Events
7 Graphs
8 Screens
9 Maps
10 Discovery
11 IT services
2 Inventory
1 Overview
2 Hosts
3 Reports
1 Status of Zabbix
2 Availability report
3 Triggers top 100
4 Bar reports
4 Configuration
1 Host groups
2 Templates
3 Hosts
1 Applications
2 Items
3 Triggers
4 Graphs
5 Discovery rules
6 Web scenarios
4 Maintenance
5 Actions
6 Screens
7 Slide shows
8 Maps
9 Discovery
10 IT services
5 Administration
1 General
2 Proxies
3 Authentication
4 Users
5 Media types
6 Scripts
7 Audit
8 Queue
9 Notifications
10 Installation
2 User profile
1 Global notifications
2 Sound in browsers
3 Global search
4 Frontend maintenance mode
5 Page parameters
6 Definitions
7 Creating your own theme
8 Debug mode
17. API
Appendix 1. Reference commentary
Appendix 2. Changes from 2.2 to 2.4
Method reference
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.exists
action.get
action.update
Alert
Alert object
alert.get
Application
Application object
application.create
application.delete
application.exists
application.get
application.massadd
application.update
Configuration
configuration.export
configuration.import
Discovered host
Discovered host object
dhost.exists
dhost.get
Discovered service
Discovered service object
dservice.exists
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.exists
drule.get
drule.isreadable
drule.iswritable
drule.update
Event
Event object
event.acknowledge
event.get
Graph
Graph object
graph.create
graph.delete
graph.exists
graph.get
graph.getobjects
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.exists
graphprototype.get
graphprototype.getobjects
graphprototype.update
History
History object
history.get
Host
Host object
host.create
host.delete
host.exists
host.get
host.getobjects
host.isreadable
host.iswritable
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.exists
hostgroup.get
hostgroup.getobjects
hostgroup.isreadable
hostgroup.iswritable
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.exists
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Host prototype
Host prototype object
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.isreadable
hostprototype.iswritable
hostprototype.update
IT service
IT Service object
service.adddependencies
service.addtimes
service.create
service.delete
service.deletedependencies
service.deletetimes
service.get
service.getsla
service.isreadable
service.iswritable
service.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.isreadable
iconmap.iswritable
iconmap.update
Image
Image object
image.create
image.delete
image.exists
image.get
image.getobjects
image.update
Item
Item object
item.create
item.delete
item.exists
item.get
item.getobjects
item.isreadable
item.iswritable
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.exists
itemprototype.get
itemprototype.isreadable
itemprototype.iswritable
itemprototype.update
LLD rule
LLD rule object
discoveryrule.copy
discoveryrule.create
discoveryrule.delete
discoveryrule.exists
discoveryrule.get
discoveryrule.isreadable
discoveryrule.iswritable
discoveryrule.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.exists
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.exists
map.get
map.getobjects
map.isreadable
map.iswritable
map.update
Media
Media object
usermedia.get
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.isreadable
proxy.iswritable
proxy.update
Screen
Screen object
screen.create
screen.delete
screen.exists
screen.get
screen.update
Screen item
Screen item object
screenitem.create
screenitem.delete
screenitem.get
screenitem.isreadable
screenitem.iswritable
screenitem.update
screenitem.updatebyposition
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyhosts
script.update
Template
Template object
template.create
template.delete
template.exists
template.get
template.getobjects
template.isreadable
template.iswritable
template.massadd
template.massremove
template.massupdate
template.update
Template screen
Template screen object
templatescreen.copy
templatescreen.create
templatescreen.delete
templatescreen.exists
templatescreen.get
templatescreen.isreadable
templatescreen.iswritable
templatescreen.update
Template screen item
Template screen item object
templatescreenitem.get
Trigger
Trigger object
trigger.adddependencies
trigger.create
trigger.delete
trigger.deletedependencies
trigger.exists
trigger.get
trigger.getobjects
trigger.isreadable
trigger.iswritable
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
user.addmedia
user.create
user.delete
user.deletemedia
user.get
user.isreadable
user.iswritable
user.login
user.logout
user.update
user.updatemedia
user.updateprofile
User group
User group object
usergroup.create
usergroup.delete
usergroup.exists
usergroup.get
usergroup.getobjects
usergroup.isreadable
usergroup.iswritable
usergroup.massadd
usergroup.massupdate
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Web scenario
Web scenario object
httptest.create
httptest.delete
httptest.get
httptest.isreadable
httptest.iswritable
httptest.update
Zabbix API changes in 2.4
18. Appendixes
1 Frequently asked questions / Troubleshooting
2 Installation
1 Database creation scripts
2 Zabbix agent on Microsoft Windows
3 Troubleshooting installation issues
3 Daemon configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent (Windows)
5 Zabbix Java gateway
6 Archive: Zabbix agent (UNIX, Inetd version)
7 Special notes on "Include" parameter
4 Items
1 Items supported by platform
2 vm.memory.size parameters
3 Passive and active agent checks
4 Encoding of returned values
5 Large file support
6 Unreachable/unavailable host settings
7 Sensor
8 Implementation details of net.tcp.service checks
5 Triggers
1 Supported trigger functions
6 Macros
1 Macros supported by location
7 Setting time periods
8 Command execution
9 Recipes for monitoring
10 Performance tuning
11 Version compatibility
12 Database error handling
13 Zabbix sender dynamic link library for Windows
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
Zabbix 2.4 API
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Use the sidebar navigation to browse documentation pages.
To be able to watch pages, log in with your
Zabbix forums
username and password.
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/3.0/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
3.0
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
English
English
Русский
Português
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1. Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 3.0.0
6 What's new in Zabbix 3.0.1
7 What's new in Zabbix 3.0.2
8 What's new in Zabbix 3.0.3
9 What's new in Zabbix 3.0.4
10 What's new in Zabbix 3.0.5
11 What's new in Zabbix 3.0.6
12 What's new in Zabbix 3.0.7
13 What's new in Zabbix 3.0.8
14 What's new in Zabbix 3.0.9
15 What's new in Zabbix 3.0.10
16 What's new in Zabbix 3.0.11
17 What's new in Zabbix 3.0.12
18 What's new in Zabbix 3.0.13
19 What's new in Zabbix 3.0.14
20 What's new in Zabbix 3.0.15
21 What's new in Zabbix 3.0.16
22 What's new in Zabbix 3.0.17
23 What's new in Zabbix 3.0.18
24 What's new in Zabbix 3.0.19
25 What's new in Zabbix 3.0.20
26 What's new in Zabbix 3.0.21
27 What's new in Zabbix 3.0.22
28 What's new in Zabbix 3.0.23
29 What's new in Zabbix 3.0.24
30 What's new in Zabbix 3.0.25
31 What's new in Zabbix 3.0.26
32 What's new in Zabbix 3.0.27
33 What's new in Zabbix 3.0.28
34 What's new in Zabbix 3.0.29
35 What's new in Zabbix 3.0.30
36 What's new in Zabbix 3.0.31
37 What's new in Zabbix 3.0.32
2. Zabbix concepts
1 Zabbix definitions
2 Server
3 Agent
4 Proxy
5 Java gateway
6 Sender
7 Get
3. Installation
3 Installation from sources
Building Windows agent binaries with/without TLS
4 Installation from packages
5 Proxy installation
1 Red Hat Enterprise Linux/CentOS
2 Debian/Ubuntu
4 Agent installation
agent_installation.md
1 Repository installation
repository_installation.md
2 Server installation with MySQL database
server_installation_with_mysql.md
3 Server installation with PostgreSQL database
server_installation_with_postgresql.md
5 Installation from containers
6 Upgrade procedure using sources
7 Upgrade procedure using packages
1 Red Hat Enterprise Linux/CentOS
2 Debian/Ubuntu
8 Known issues
9 Template changes
10 Upgrade notes for 3.0.0
11 Upgrade notes for 3.0.1
12 Upgrade notes for 3.0.2
13 Upgrade notes for 3.0.3
14 Upgrade notes for 3.0.4
15 Upgrade notes for 3.0.5
16 Upgrade notes for 3.0.6
17 Upgrade notes for 3.0.7
18 Upgrade notes for 3.0.8
19 Upgrade notes for 3.0.9
20 Upgrade notes for 3.0.10
21 Upgrade notes for 3.0.11
22 Upgrade notes for 3.0.12
23 Upgrade notes for 3.0.13
24 Upgrade notes for 3.0.14
25 Upgrade notes for 3.0.15
26 Upgrade notes for 3.0.16
27 Upgrade notes for 3.0.17
28 Upgrade notes for 3.0.18
29 Upgrade notes for 3.0.19
30 Upgrade notes for 3.0.20
31 Upgrade notes for 3.0.21
32 Upgrade notes for 3.0.22
33 Upgrade notes for 3.0.23
34 Upgrade notes for 3.0.24
35 Upgrade notes for 3.0.25
36 Upgrade notes for 3.0.26
37 Upgrade notes for 3.0.27
38 Upgrade notes for 3.0.28
40 Upgrade notes for 3.0.30
41 Upgrade notes for 3.0.31
42 Upgrade notes for 3.0.32
1 Getting Zabbix
getting_zabbix.md
2 Requirements
requirements.md
Best practices for secure Zabbix setup
4. Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
5. Zabbix appliance
6. Configuration
1 Hosts and host groups
1 Configuring a host
2 Inventory
3 Mass update
2 Items
1 Creating an item
1 Item key format
2 Custom intervals
2 Item types
1 Zabbix agent
Windows-specific item keys
2 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 SNMP traps
4 IPMI checks
5 Simple checks
1 VMware monitoring item keys
6 Log file monitoring
7 Calculated items
8 Internal checks
9 SSH checks
10 Telnet checks
11 External checks
12 Aggregate checks
13 Trapper items
14 JMX monitoring
15 ODBC monitoring
3 History and trends
4 User parameters
1 Extending Zabbix agents
5 Loadable modules
6 Windows performance counters
7 Mass update
8 Value mapping
9 Applications
10 Queue
11 Value cache
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customising trigger severities
6 Unit symbols
7 Mass update
8 Predictive trigger functions
4 Events
1 Event sources
5 Visualisation
1 Graphs
1 Simple graphs
2 Custom graphs
3 Ad-hoc graphs
2 Network maps
1 Configuring a network map
2 Host group elements
3 Link indicators
3 Screens
1 Screen elements
4 Slide shows
6 Templates
1 Configuring a template
2 Linking/unlinking
3 Nesting
7 Notifications upon events
1 Media types
1 E-mail
2 SMS
3 Jabber
4 Ez Texting
5 Custom alertscripts
2 Actions
1 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
2 Conditions
3 Escalations
3 Receiving notification on unsupported items
8 Macros
User macros
9 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
7. IT services
8. Web monitoring
1 Web monitoring items
2 Real life scenario
9. Virtual machine monitoring
Virtual machine discovery key fields
10. Maintenance
11. Regular expressions
12. Event acknowledgement
13. Configuration export/import
Groups
Hosts
14. Discovery
1 Network discovery
Configuring a network discovery rule
2 Active agent auto-registration
3 Low-level discovery
Notes on low-level discovery
15. Distributed monitoring
1 Proxies
16. Encryption
1 Using certificates
2 Using pre-shared keys
3 Troubleshooting
1 Connection type or permission problems
2 Certificate problems
3 PSK problems
17. Web interface
1 Frontend sections
1 Monitoring
1 Dashboard
2 Overview
3 Web
4 Latest data
5 Triggers
6 Events
7 Graphs
8 Screens
9 Maps
10 Discovery
11 IT services
2 Inventory
1 Overview
2 Hosts
3 Reports
1 Status of Zabbix
2 Availability report
3 Triggers top 100
4 Audit
5 Action log
6 Notifications
4 Configuration
1 Host groups
2 Templates
3 Hosts
1 Applications
2 Items
3 Triggers
4 Graphs
5 Discovery rules
6 Web scenarios
4 Maintenance
5 Actions
6 Discovery
7 IT services
5 Administration
1 General
2 Proxies
3 Authentication
4 User groups
5 Users
6 Media types
7 Scripts
8 Queue
2 User profile
1 Global notifications
2 Sound in browsers
3 Global search
4 Frontend maintenance mode
5 Page parameters
6 Definitions
7 Creating your own theme
8 Debug mode
18. API
Appendix 1. Reference commentary
Appendix 2. Changes from 2.4 to 3.0
Method reference
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.get
action.update
Alert
Alert object
alert.get
Application
Application object
application.create
application.delete
application.get
application.massadd
application.update
Configuration
configuration.export
configuration.import
Discovered host
Discovered host object
dhost.get
Discovered service
Discovered service object
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.get
drule.isreadable
drule.iswritable
drule.update
Event
Event object
event.acknowledge
event.get
Graph
Graph object
graph.create
graph.delete
graph.get
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
History
History object
history.get
Host
Host object
host.create
host.delete
host.get
host.isreadable
host.iswritable
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.isreadable
hostgroup.iswritable
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Host prototype
Host prototype object
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.isreadable
hostprototype.iswritable
hostprototype.update
IT service
IT Service object
service.adddependencies
service.addtimes
service.create
service.delete
service.deletedependencies
service.deletetimes
service.get
service.getsla
service.isreadable
service.iswritable
service.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.isreadable
iconmap.iswritable
iconmap.update
Image
Image object
image.create
image.delete
image.get
image.update
Item
Item object
item.create
item.delete
item.get
item.isreadable
item.iswritable
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.isreadable
itemprototype.iswritable
itemprototype.update
LLD rule
LLD rule object
discoveryrule.copy
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.isreadable
discoveryrule.iswritable
discoveryrule.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.get
map.isreadable
map.iswritable
map.update
Media
Media object
usermedia.get
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.isreadable
proxy.iswritable
proxy.update
Screen
Screen object
screen.create
screen.delete
screen.get
screen.update
Screen item
Screen item object
screenitem.create
screenitem.delete
screenitem.get
screenitem.isreadable
screenitem.iswritable
screenitem.update
screenitem.updatebyposition
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyhosts
script.update
Template
Template object
template.create
template.delete
template.get
template.isreadable
template.iswritable
template.massadd
template.massremove
template.massupdate
template.update
Template screen
Template screen object
templatescreen.copy
templatescreen.create
templatescreen.delete
templatescreen.get
templatescreen.isreadable
templatescreen.iswritable
templatescreen.update
Template screen item
Template screen item object
templatescreenitem.get
Trend
Trend object
trend.get
Trigger
Trigger object
trigger.adddependencies
trigger.create
trigger.delete
trigger.deletedependencies
trigger.get
trigger.isreadable
trigger.iswritable
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
user.addmedia
user.checkAuthentication
user.create
user.delete
user.deletemedia
user.get
user.isreadable
user.iswritable
user.login
user.logout
user.update
user.updatemedia
user.updateprofile
User group
User group object
usergroup.create
usergroup.delete
usergroup.get
usergroup.isreadable
usergroup.iswritable
usergroup.massadd
usergroup.massupdate
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Value map
Value map object
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Web scenario
Web scenario object
httptest.create
httptest.delete
httptest.get
httptest.isreadable
httptest.iswritable
httptest.update
Zabbix API changes in 3.0
19. Appendixes
1 Frequently asked questions / Troubleshooting
2 Installation
1 Database creation scripts
2 Zabbix agent on Microsoft Windows
3 Daemon configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent (Windows)
5 Zabbix Java gateway
6 Special notes on "Include" parameter
4 Protocols
1 Zabbix sender protocol
2 Zabbix agent protocol
3 Header and data length
5 Items
1 Items supported by platform
2 vm.memory.size parameters
3 Passive and active agent checks
4 Trapper items
5 Minimum permission level for Windows agent items
6 Encoding of returned values
7 Large file support
8 Sensor
9 Notes on memtype parameter in proc.mem items
10 Notes on selecting processes in proc.mem and proc.num items
11 Implementation details of net.tcp.service and net.udp.service checks
12 Unreachable/unavailable host settings
6 Triggers
1 Supported trigger functions
7 Macros
1 Supported macros
8 Setting time periods
9 Command execution
10 Recipes for monitoring
11 Performance tuning
12 Version compatibility
13 Database error handling
14 Zabbix sender dynamic link library for Windows
15 Other issues
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Use the sidebar navigation to browse documentation pages.
To be able to watch pages, log in with your
Zabbix forums
username and password.
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/3.2/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
3.2
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
English
English
Русский
Português
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1. Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 3.2.0
6 What's new in Zabbix 3.2.1
7 What's new in Zabbix 3.2.2
8 What's new in Zabbix 3.2.3
9 What's new in Zabbix 3.2.4
10 What's new in Zabbix 3.2.5
11 What's new in Zabbix 3.2.6
12 What's new in Zabbix 3.2.7
13 What's new in Zabbix 3.2.8
14 What's new in Zabbix 3.2.9
15 What's new in Zabbix 3.2.10
16 What's new in Zabbix 3.2.11
2. Zabbix concepts
2 Server
2. Definitions
3 Agent
4 Proxy
5 Java gateway
6 Sender
7 Get
3. Installation
3 Installation from sources
4 Installation from packages
1 Repository installation
2 Server installation with MySQL database
3 Server installation with PostgreSQL database
4 Agent installation
5 Proxy installation
5 Installation from containers
6 Upgrade procedure using sources
7 Upgrade procedure using packages
1 Red Hat Enterprise Linux/CentOS
2 Debian/Ubuntu
8 Known issues
9 Template changes
10 Upgrade notes for 3.2.0
11 Upgrade notes for 3.2.1
12 Upgrade notes for 3.2.2
13 Upgrade notes for 3.2.3
14 Upgrade notes for 3.2.4
15 Upgrade notes for 3.2.5
16 Upgrade notes for 3.2.6
17 Upgrade notes for 3.2.7
18 Upgrade notes for 3.2.8
19 Upgrade notes for 3.2.9
20 Upgrade notes for 3.2.10
21 Upgrade notes for 3.2.11
1 Getting Zabbix
getting_zabbix.md
2 Requirements
requirements.md
Best practices for secure Zabbix setup
4. Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
5. Zabbix appliance
6. Configuration
1 Hosts and host groups
1 Configuring a host
2 Inventory
3 Mass update
2 Items
1 Creating an item
1 Item key
2 Custom intervals
2 Item types
1 Zabbix agent
Windows-specific item keys
2 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 SNMP traps
4 IPMI checks
5 Simple checks
1 VMware monitoring item keys
6 Log file monitoring
7 Calculated items
8 Internal checks
9 SSH checks
10 Telnet checks
11 External checks
12 Aggregate checks
13 Trapper items
14 JMX monitoring
15 ODBC monitoring
3 History and trends
4 User parameters
1 Extending Zabbix agents
5 Loadable modules
6 Windows performance counters
7 Mass update
8 Value mapping
9 Applications
10 Queue
11 Value cache
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customising trigger severities
6 Unit symbols
7 Mass update
8 Predictive trigger functions
9 Event tags
4 Events
1 Event sources
2 Manual closing of problems
5 Event correlation
1 Trigger-based event correlation
2 Global event correlation
6 Visualisation
1 Graphs
1 Simple graphs
2 Custom graphs
3 Ad-hoc graphs
2 Network maps
1 Configuring a network map
2 Host group elements
3 Link indicators
3 Screens
1 Screen elements
4 Slide shows
7 Templates
1 Configuring a template
2 Linking/unlinking
3 Nesting
8 Notifications upon events
1 Media types
1 E-mail
2 SMS
3 Jabber
4 Ez Texting
5 Custom alertscripts
2 Actions
2 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
3 Recovery operations
4 Escalations
1 Conditions
conditions.md
3 Receiving notification on unsupported items
9 Macros
1 Macro functions
2 User macros
3 Low-level discovery macros
10 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
7. IT services
8. Web monitoring
1 Web monitoring items
2 Real life scenario
9. Virtual machine monitoring
Virtual machine discovery key fields
10. Maintenance
11. Regular expressions
12. Event acknowledgment
13. Configuration export/import
Groups
Hosts
14. Discovery
1 Network discovery
Configuring a network discovery rule
2 Active agent auto-registration
3 Low-level discovery
Notes on low-level discovery
15. Distributed monitoring
1 Proxies
16. Encryption
1 Using certificates
2 Using pre-shared keys
3 Troubleshooting
1 Connection type or permission problems
2 Certificate problems
3 PSK problems
17. Web interface
1 Frontend sections
1 Monitoring
1 Dashboard
2 Problems
3 Overview
4 Web
5 Latest data
6 Triggers
7 Graphs
8 Screens
9 Maps
10 Discovery
11 IT services
2 Inventory
1 Overview
2 Hosts
3 Reports
1 Status of Zabbix
2 Availability report
3 Triggers top 100
4 Audit
5 Action log
6 Notifications
4 Configuration
1 Host groups
2 Templates
3 Hosts
1 Applications
2 Items
3 Triggers
4 Graphs
5 Discovery rules
6 Web scenarios
4 Maintenance
5 Actions
6 Event correlation
7 Discovery
8 IT services
5 Administration
1 General
2 Proxies
3 Authentication
4 User groups
5 Users
6 Media types
7 Scripts
8 Queue
2 User profile
1 Global notifications
2 Sound in browsers
3 Global search
4 Frontend maintenance mode
5 Page parameters
6 Definitions
7 Creating your own theme
8 Debug mode
18. API
Appendix 1. Reference commentary
Appendix 2. Changes from 3.0 to 3.2
Method reference
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.get
action.update
Alert
Alert object
alert.get
Application
Application object
application.create
application.delete
application.get
application.massadd
application.update
Configuration
configuration.export
configuration.import
Correlation
Correlation object
correlation.create
correlation.delete
correlation.get
correlation.update
Discovered host
Discovered host object
dhost.get
Discovered service
Discovered service object
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.get
drule.isreadable
drule.iswritable
drule.update
Event
Event object
event.acknowledge
event.get
Graph
Graph object
graph.create
graph.delete
graph.get
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
History
History object
history.get
Host
Host object
host.create
host.delete
host.get
host.isreadable
host.iswritable
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.isreadable
hostgroup.iswritable
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Host prototype
Host prototype object
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.isreadable
hostprototype.iswritable
hostprototype.update
IT service
IT Service object
service.adddependencies
service.addtimes
service.create
service.delete
service.deletedependencies
service.deletetimes
service.get
service.getsla
service.isreadable
service.iswritable
service.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.isreadable
iconmap.iswritable
iconmap.update
Image
Image object
image.create
image.delete
image.get
image.update
Item
Item object
item.create
item.delete
item.get
item.isreadable
item.iswritable
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.isreadable
itemprototype.iswritable
itemprototype.update
LLD rule
LLD rule object
discoveryrule.copy
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.isreadable
discoveryrule.iswritable
discoveryrule.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.get
map.isreadable
map.iswritable
map.update
Media
Media object
usermedia.get
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Problem
Problem object
problem.get
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.isreadable
proxy.iswritable
proxy.update
Screen
Screen object
screen.create
screen.delete
screen.get
screen.update
Screen item
Screen item object
screenitem.create
screenitem.delete
screenitem.get
screenitem.isreadable
screenitem.iswritable
screenitem.update
screenitem.updatebyposition
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyhosts
script.update
Template
Template object
template.create
template.delete
template.get
template.isreadable
template.iswritable
template.massadd
template.massremove
template.massupdate
template.update
Template screen
Template screen object
templatescreen.copy
templatescreen.create
templatescreen.delete
templatescreen.get
templatescreen.isreadable
templatescreen.iswritable
templatescreen.update
Template screen item
Template screen item object
templatescreenitem.get
Trend
Trend object
trend.get
Trigger
Trigger object
trigger.adddependencies
trigger.create
trigger.delete
trigger.deletedependencies
trigger.get
trigger.isreadable
trigger.iswritable
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
user.addmedia
user.create
user.delete
user.deletemedia
user.get
user.isreadable
user.iswritable
user.login
user.logout
user.update
user.updatemedia
user.updateprofile
User group
User group object
usergroup.create
usergroup.delete
usergroup.get
usergroup.isreadable
usergroup.iswritable
usergroup.massadd
usergroup.massupdate
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Value map
Value map object
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Web scenario
Web scenario object
httptest.create
httptest.delete
httptest.get
httptest.isreadable
httptest.iswritable
httptest.update
Zabbix API changes in 3.2
19. Appendixes
1 Frequently asked questions / Troubleshooting
2 Installation
1 Database creation scripts
2 Zabbix agent on Microsoft Windows
3 Daemon configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent (Windows)
5 Zabbix Java gateway
6 Special notes on "Include" parameter
4 Protocols
Server-proxy data exchange protocol
5 Items
1 Items supported by platform
2 vm.memory.size parameters
3 Passive and active agent checks
4 Encoding of returned values
5 Large file support
6 Unreachable/unavailable host settings
7 Sensor
8 Notes on memtype parameter in proc.mem items
9 Notes on selecting processes in proc.mem and proc.num items
10 Implementation details of net.tcp.service and net.udp.service checks
6 Triggers
1 Supported trigger functions
7 Macros
1 Supported macros
8 Setting time periods
9 Command execution
10 Recipes for monitoring
11 Performance tuning
12 Version compatibility
13 Database error handling
14 Zabbix sender dynamic link library for Windows
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Use the sidebar navigation to browse documentation pages.
To be able to watch pages, log in with your
Zabbix forums
username and password.
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/3.4/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
3.4
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
English
English
Русский
中文
Português
Türkçe
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1. Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 3.4.0
6 What's new in Zabbix 3.4.1
7 What's new in Zabbix 3.4.2
8 What's new in Zabbix 3.4.3
9 What's new in Zabbix 3.4.4
10 What's new in Zabbix 3.4.5
11 What's new in Zabbix 3.4.6
12 What's new in Zabbix 3.4.7
13 What's new in Zabbix 3.4.8
14 What's new in Zabbix 3.4.9
15 What's new in Zabbix 3.4.10
16 What's new in Zabbix 3.4.11
17 What's new in Zabbix 3.4.12
18 What's new in Zabbix 3.4.13
19 What's new in Zabbix 3.4.14
20 What's new in Zabbix 3.4.15
2. Definitions
3. Zabbix processes
1 Server
2 Agent
3 Proxy
4 Java gateway
5 Sender
6 Get
4. Installation
1 Getting Zabbix
2 Requirements
Best practices for secure Zabbix setup
3 Installation from sources
4 Installation from packages
2 Debian/Ubuntu
debian_ubuntu.md
1 Red Hat Enterprise Linux/CentOS
rhel_centos.md
5 Installation from containers
6 Upgrade procedure using sources
7 Upgrade procedure using packages
1 Red Hat Enterprise Linux/CentOS
2 Debian/Ubuntu
8 Known issues
9 Template changes
10 Upgrade notes for 3.4.0
11 Upgrade notes for 3.4.1
12 Upgrade notes for 3.4.2
13 Upgrade notes for 3.4.3
14 Upgrade notes for 3.4.4
15 Upgrade notes for 3.4.5
16 Upgrade notes for 3.4.6
17 Upgrade notes for 3.4.7
18 Upgrade notes for 3.4.8
19 Upgrade notes for 3.4.9
20 Upgrade notes for 3.4.10
21 Upgrade notes for 3.4.11
22 Upgrade notes for 3.4.12
23 Upgrade notes for 3.4.13
24 Upgrade notes for 3.4.14
25 Upgrade notes for 3.4.15
5. Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
6. Zabbix appliance
7. Configuration
1 Hosts and host groups
1 Configuring a host
2 Inventory
3 Mass update
2 Items
1 Creating an item
1 Item key format
2 Custom intervals
2 Item types
1 Zabbix agent
Windows-specific item keys
2 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 SNMP traps
4 IPMI checks
5 Simple checks
1 VMware monitoring item keys
6 Log file monitoring
7 Calculated items
8 Internal checks
9 SSH checks
10 Telnet checks
11 External checks
12 Aggregate checks
13 Trapper items
14 JMX monitoring
15 ODBC monitoring
1 Recommended UnixODBC settings for MySQL
2 Recommended UnixODBC settings for PostgreSQL
3 Recommended UnixODBC settings for Oracle
4 Recommended UnixODBC settings for MSSQL
16 Dependent items
3 History and trends
4 User parameters
1 Extending Zabbix agents
5 Loadable modules
6 Windows performance counters
7 Mass update
8 Value mapping
9 Applications
10 Queue
11 Value cache
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customising trigger severities
6 Event tags
7 Mass update
8 Predictive trigger functions
4 Events
1 Trigger event generation
2 Manual closing of problems
3 Other event sources
5 Event correlation
1 Trigger-based event correlation
2 Global event correlation
6 Visualisation
1 Graphs
1 Simple graphs
2 Custom graphs
3 Ad-hoc graphs
2 Network maps
1 Configuring a network map
2 Host group elements
3 Link indicators
3 Screens
1 Screen elements
4 Slide shows
5 Host screens
7 Templates
1 Configuring a template
2 Linking/unlinking
3 Nesting
8 Templates out of the box
1 Standardized templates for network devices
9 Notifications upon events
1 Media types
1 E-mail
2 SMS
3 Jabber
4 Ez Texting
5 Custom alertscripts
2 Actions
2 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
3 Recovery operations
4 Acknowledgement operations
5 Escalations
1 Conditions
conditions.md
3 Receiving notification on unsupported items
10 Macros
1 Macro functions
2 User macros
3 Low-level discovery macros
11 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
8. Service monitoring
9. Web monitoring
1 Web monitoring items
2 Real life scenario
10. Virtual machine monitoring
1 Virtual machine discovery key fields
11. Maintenance
12. Regular expressions
13. Event acknowledgement
14. Configuration export/import
1 Host groups
2 Templates
3 Hosts
4 Network maps
5 Screens
15. Discovery
1 Network discovery
1 Configuring a network discovery rule
2 Active agent auto-registration
3 Low-level discovery
1 Discovery of network interfaces
2 Discovery of CPUs and CPU cores
3 Discovery of SNMP OIDs
4 Discovery of JMX objects
5 Discovery using ODBC SQL queries
6 Discovery of Windows services
7 Discovery of host interfaces in Zabbix
Notes on low-level discovery
16. Distributed monitoring
1 Proxies
17. Encryption
1 Using certificates
2 Using pre-shared keys
3 Troubleshooting
1 Connection type or permission problems
2 Certificate problems
3 PSK problems
18. Web interface
1 Frontend sections
1 Monitoring
1 Dashboard
1 Dashboard widgets
2 Problems
3 Overview
4 Web
5 Latest data
6 Triggers
7 Graphs
8 Screens
9 Maps
10 Discovery
11 Services
2 Inventory
1 Overview
2 Hosts
3 Reports
1 Status of Zabbix
2 Availability report
3 Triggers top 100
4 Audit
5 Action log
6 Notifications
4 Configuration
1 Host groups
2 Templates
3 Hosts
1 Applications
2 Items
3 Triggers
4 Graphs
5 Discovery rules
6 Web scenarios
4 Maintenance
5 Actions
6 Event correlation
7 Discovery
8 Services
5 Administration
1 General
2 Proxies
3 Authentication
4 User groups
5 Users
6 Media types
7 Scripts
8 Queue
2 User profile
1 Global notifications
2 Sound in browsers
3 Global search
4 Frontend maintenance mode
5 Page parameters
6 Definitions
7 Creating your own theme
8 Debug mode
19. API
Appendix 1. Reference commentary
Appendix 2. Changes from 3.2 to 3.4
Method reference
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.get
action.update
Alert
Alert object
alert.get
Application
Application object
application.create
application.delete
application.get
application.massadd
application.update
Configuration
configuration.export
configuration.import
Correlation
Correlation object
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Dashboard object
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Discovered host
Discovered host object
dhost.get
Discovered service
Discovered service object
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.get
drule.update
Event
Event object
event.acknowledge
event.get
Graph
Graph object
graph.create
graph.delete
graph.get
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
History
History object
history.get
Host
Host object
host.create
host.delete
host.get
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Host prototype
Host prototype object
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Image
Image object
image.create
image.delete
image.get
image.update
Item
Item object
item.create
item.delete
item.get
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
LLD rule
LLD rule object
discoveryrule.copy
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.get
map.update
Media
Media object
usermedia.get
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Problem
Problem object
problem.get
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.update
Screen
Screen object
screen.create
screen.delete
screen.get
screen.update
Screen item
Screen item object
screenitem.create
screenitem.delete
screenitem.get
screenitem.update
screenitem.updatebyposition
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyhosts
script.update
Service
Service object
service.adddependencies
service.addtimes
service.create
service.delete
service.deletedependencies
service.deletetimes
service.get
service.getsla
service.update
Template
Template object
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template screen
Template screen object
templatescreen.copy
templatescreen.create
templatescreen.delete
templatescreen.get
templatescreen.update
Template screen item
Template screen item object
templatescreenitem.get
Trend
Trend object
trend.get
Trigger
Trigger object
trigger.adddependencies
trigger.create
trigger.delete
trigger.deletedependencies
trigger.get
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
user.addmedia
user.checkAuthentication
user.create
user.delete
user.deletemedia
user.get
user.login
user.logout
user.update
user.updatemedia
user.updateprofile
User group
User group object
usergroup.create
usergroup.delete
usergroup.get
usergroup.massadd
usergroup.massupdate
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Value map
Value map object
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Web scenario
Web scenario object
httptest.create
httptest.delete
httptest.get
httptest.update
Zabbix API changes in 3.4
20. Appendixes
1 Frequently asked questions / Troubleshooting
2 Installation
1 Database creation
2 Zabbix agent on Microsoft Windows
3 Elasticsearch setup
3 Daemon configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent (Windows)
5 Zabbix Java gateway
6 Special notes on "Include" parameter
4 Protocols
1 Server-proxy data exchange protocol
2 Zabbix agent protocol
3 Zabbix sender protocol
4 Header and data length
5 Items
1 Items supported by platform
2 vm.memory.size parameters
3 Passive and active agent checks
4 Trapper items
5 Encoding of returned values
6 Large file support
7 Sensor
8 Notes on memtype parameter in proc.mem items
9 Notes on selecting processes in proc.mem and proc.num items
10 Implementation details of net.tcp.service and net.udp.service checks
11 Item value preprocessing details
12 Unreachable/unavailable host settings
6 Triggers
1 Supported trigger functions
7 Macros
1 Supported macros
2 User macros supported by location
8 Unit symbols
9 Setting time periods
10 Command execution
11 Recipes for monitoring
12 Performance tuning
13 Version compatibility
14 Database error handling
15 Zabbix sender dynamic link library for Windows
16 Issues with SELinux
17 Other issues
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Use the sidebar navigation to browse documentation pages.
To be able to watch pages, log in with your
Zabbix forums
username and password.
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

## Zabbix documentation
URL: https://www.zabbix.com/documentation/4.0/en

Zabbix documentation
This is the documentation page for an unsupported version of Zabbix.
Is this not what you were looking for? Switch to the
current version
or choose one from the drop-down menu.
Docs
Version:
4.0
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
English
English
Français
Русский
中文
Español
Português
Türkçe
Download Zabbix Manual in PDF
Theme:
Light
Dark
System
Zabbix Manual
1. Introduction
1 Manual structure
2 What is Zabbix
3 Zabbix features
4 Zabbix overview
5 What's new in Zabbix 4.0.0
6 What's new in Zabbix 4.0.1
7 What's new in Zabbix 4.0.2
8 What's new in Zabbix 4.0.3
9 What's new in Zabbix 4.0.4
10 What's new in Zabbix 4.0.5
11 What's new in Zabbix 4.0.6
12 What's new in Zabbix 4.0.7
13 What's new in Zabbix 4.0.8
14 What's new in Zabbix 4.0.9
15 What's new in Zabbix 4.0.10
16 What's new in Zabbix 4.0.11
17 What's new in Zabbix 4.0.12
18 What's new in Zabbix 4.0.13
19 What's new in Zabbix 4.0.14
20 What's new in Zabbix 4.0.15
21 What's new in Zabbix 4.0.16
22 What's new in Zabbix 4.0.17
23 What's new in Zabbix 4.0.18
24 What's new in Zabbix 4.0.19
25 What's new in Zabbix 4.0.20
26 What's new in Zabbix 4.0.21
27 What's new in Zabbix 4.0.22
28 What's new in Zabbix 4.0.23
29 What's new in Zabbix 4.0.24
30 What's new in Zabbix 4.0.25
31 What's new in Zabbix 4.0.26
32 What's new in Zabbix 4.0.27
33 What's new in Zabbix 4.0.28
34 What's new in Zabbix 4.0.29
35 What's new in Zabbix 4.0.30
36 What's new in Zabbix 4.0.31
37 What's new in Zabbix 4.0.32
38 What's new in Zabbix 4.0.33
39 What's new in Zabbix 4.0.34
40 What's new in Zabbix 4.0.35
41 What's new in Zabbix 4.0.36
42 What's new in Zabbix 4.0.37
43 What's new in Zabbix 4.0.38
44 What's new in Zabbix 4.0.39
2. Definitions
3. Zabbix processes
4 Java gateway
2 Setup from RHEL/CentOS packages
3 Setup from Debian/Ubuntu packages
Setup from sources
5 Sender
6 Get
2 Agent
agent.md
3 Proxy
proxy.md
1 Server
server.md
4. Installation
1 Getting Zabbix
2 Requirements
Best practices for secure Zabbix setup
3 Installation from sources
Building Windows agent binaries with/without TLS
4 Installation from packages
1 Red Hat Enterprise Linux/CentOS
2 Debian/Ubuntu/Raspbian
3 Windows agent installation from MSI
4 Mac OS agent installation from PKG
5 Installation from containers
6 Upgrade procedure
Upgrade from packages
1 Red Hat Enterprise Linux/CentOS
2 Debian/Ubuntu
Upgrade from sources
7 Known issues
8 Template changes
9 Upgrade notes for 4.0.0
10 Upgrade notes for 4.0.1
11 Upgrade notes for 4.0.2
12 Upgrade notes for 4.0.3
14 Upgrade notes for 4.0.5
15 Upgrade notes for 4.0.6
16 Upgrade notes for 4.0.7
17 Upgrade notes for 4.0.8
18 Upgrade notes for 4.0.9
19 Upgrade notes for 4.0.10
20 Upgrade notes for 4.0.11
21 Upgrade notes for 4.0.12
22 Upgrade notes for 4.0.13
23 Upgrade notes for 4.0.14
24 Upgrade notes for 4.0.15
25 Upgrade notes for 4.0.16
26 Upgrade notes for 4.0.17
27 Upgrade notes for 4.0.18
28 Upgrade notes for 4.0.19
29 Upgrade notes for 4.0.20
30 Upgrade notes for 4.0.21
31 Upgrade notes for 4.0.22
32 Upgrade notes for 4.0.23
33 Upgrade notes for 4.0.24
34 Upgrade notes for 4.0.25
35 Upgrade notes for 4.0.26
36 Upgrade notes for 4.0.27
37 Upgrade notes for 4.0.28
38 Upgrade notes for 4.0.29
39 Upgrade notes for 4.0.30
40 Upgrade notes for 4.0.31
41 Upgrade notes for 4.0.32
42 Upgrade notes for 4.0.33
43 Upgrade notes for 4.0.34
44 Upgrade notes for 4.0.35
45 Upgrade notes for 4.0.36
46 Upgrade notes for 4.0.37
47 Upgrade notes for 4.0.38
48 Upgrade notes for 4.0.39
5. Quickstart
1 Login and configuring user
2 New host
3 New item
4 New trigger
5 Receiving problem notification
6 New template
6. Zabbix appliance
7. Configuration
1 Hosts and host groups
1 Configuring a host
2 Inventory
3 Mass update
2 Items
1 Creating an item
1 Item key format
2 Custom intervals
2 Item types
1 Zabbix agent
Windows-specific item keys
2 SNMP agent
1 Dynamic indexes
2 Special OIDs
3 MIB files
3 SNMP traps
4 IPMI checks
5 Simple checks
1 VMware monitoring item keys
6 Log file monitoring
7 Calculated items
8 Internal checks
9 SSH checks
10 Telnet checks
11 External checks
12 Aggregate checks
13 Trapper items
14 JMX monitoring
15 ODBC monitoring
1 Recommended UnixODBC settings for MySQL
2 Recommended UnixODBC settings for PostgreSQL
3 Recommended UnixODBC settings for Oracle
4 Recommended UnixODBC settings for MSSQL
16 Dependent items
17 HTTP agent
3 History and trends
4 User parameters
1 Extending Zabbix agents
5 Loadable modules
6 Windows performance counters
7 Mass update
8 Value mapping
9 Applications
10 Queue
11 Value cache
12 Check now
3 Triggers
1 Configuring a trigger
2 Trigger expression
3 Trigger dependencies
4 Trigger severity
5 Customizing trigger severities
6 Mass update
7 Predictive trigger functions
4 Events
1 Trigger event generation
2 Other event sources
3 Manual closing of problems
5 Event correlation
1 Trigger-based event correlation
Event tags
2 Global event correlation
6 Visualization
1 Graphs
1 Simple graphs
2 Custom graphs
3 Ad-hoc graphs
2 Network maps
1 Configuring a network map
2 Host group elements
3 Link indicators
3 Screens
1 Screen elements
4 Slide shows
5 Host screens
7 Templates
1 Configuring a template
2 Linking/unlinking
3 Nesting
8 Templates out of the box
1 Standardized templates for network devices
9 Notifications upon events
1 Media types
1 E-mail
2 SMS
3 Jabber
4 Ez Texting
5 Custom alertscripts
2 Actions
2 Operations
1 Sending message
2 Remote commands
3 Additional operations
4 Using macros in messages
3 Recovery operations
4 Update operations
5 Escalations
1 Conditions
conditions.md
3 Receiving notification on unsupported items
10 Macros
1 Macro functions
2 User macros
3 Low-level discovery macros
11 Users and user groups
1 Configuring a user
2 Permissions
3 User groups
8. Service monitoring
9. Web monitoring
1 Web monitoring items
2 Real life scenario
10. Virtual machine monitoring
1 Virtual machine discovery key fields
11. Maintenance
12. Regular expressions
13. Problem acknowledgment
14. Configuration export/import
1 Host groups
2 Templates
3 Hosts
4 Network maps
5 Screens
15. Discovery
1 Network discovery
1 Configuring a network discovery rule
2 Active agent auto-registration
3 Low-level discovery
1 Discovery of mounted filesystems
1 Discovery of network interfaces
2 Discovery of CPUs and CPU cores
3 Discovery of SNMP OIDs
4 Discovery of JMX objects
5 Discovery using ODBC SQL queries
6 Discovery of Windows services
7 Discovery of host interfaces in Zabbix
Notes on low-level discovery
16. Distributed monitoring
1 Proxies
17. Encryption
1 Using certificates
2 Using pre-shared keys
3 Troubleshooting
1 Connection type or permission problems
2 Certificate problems
3 PSK problems
18. Web interface
1 Frontend sections
1 Monitoring
1 Dashboard
1 Dashboard widgets
2 Problems
3 Overview
4 Web
5 Latest data
6 Graphs
7 Screens
8 Maps
9 Discovery
10 Services
2 Inventory
1 Overview
2 Hosts
3 Reports
1 System information
2 Availability report
3 Triggers top 100
4 Audit
5 Action log
6 Notifications
4 Configuration
1 Host groups
2 Templates
3 Hosts
1 Applications
2 Items
3 Triggers
4 Graphs
5 Discovery rules
6 Web scenarios
4 Maintenance
5 Actions
6 Event correlation
7 Discovery
8 Services
5 Administration
1 General
2 Proxies
3 Authentication
4 User groups
5 Users
6 Media types
7 Scripts
8 Queue
2 User profile
1 Global notifications
2 Sound in browsers
3 Global search
4 Frontend maintenance mode
5 Page parameters
6 Definitions
7 Creating your own theme
8 Debug mode
9 Cookies used by Zabbix
19. API
Appendix 1. Reference commentary
Appendix 2. Changes from 3.4 to 4.0
Method reference
API info
apiinfo.version
Action
Action object
action.create
action.delete
action.get
action.update
Alert
Alert object
alert.get
Application
Application object
application.create
application.delete
application.get
application.massadd
application.update
Configuration
configuration.export
configuration.import
Correlation
Correlation object
correlation.create
correlation.delete
correlation.get
correlation.update
Dashboard
Dashboard object
dashboard.create
dashboard.delete
dashboard.get
dashboard.update
Discovered host
Discovered host object
dhost.get
Discovered service
Discovered service object
dservice.get
Discovery check
Discovery check object
dcheck.get
Discovery rule
Discovery rule object
drule.create
drule.delete
drule.get
drule.update
Event
Event object
event.acknowledge
event.get
Graph
Graph object
graph.create
graph.delete
graph.get
graph.update
Graph item
Graph item object
graphitem.get
Graph prototype
Graph prototype object
graphprototype.create
graphprototype.delete
graphprototype.get
graphprototype.update
History
History object
history.get
Host
Host object
host.create
host.delete
host.get
host.massadd
host.massremove
host.massupdate
host.update
Host group
Host group object
hostgroup.create
hostgroup.delete
hostgroup.get
hostgroup.massadd
hostgroup.massremove
hostgroup.massupdate
hostgroup.update
Host interface
Host interface object
hostinterface.create
hostinterface.delete
hostinterface.get
hostinterface.massadd
hostinterface.massremove
hostinterface.replacehostinterfaces
hostinterface.update
Host prototype
Host prototype object
hostprototype.create
hostprototype.delete
hostprototype.get
hostprototype.update
Icon map
Icon map object
iconmap.create
iconmap.delete
iconmap.get
iconmap.update
Image
Image object
image.create
image.delete
image.get
image.update
Item
Item object
item.create
item.delete
item.get
item.update
Item prototype
Item prototype object
itemprototype.create
itemprototype.delete
itemprototype.get
itemprototype.update
LLD rule
LLD rule object
discoveryrule.copy
discoveryrule.create
discoveryrule.delete
discoveryrule.get
discoveryrule.update
Maintenance
Maintenance object
maintenance.create
maintenance.delete
maintenance.get
maintenance.update
Map
Map object
map.create
map.delete
map.get
map.update
Media type
Media type object
mediatype.create
mediatype.delete
mediatype.get
mediatype.update
Problem
Problem object
problem.get
Proxy
Proxy object
proxy.create
proxy.delete
proxy.get
proxy.update
Screen
Screen object
screen.create
screen.delete
screen.get
screen.update
Screen item
Screen item object
screenitem.create
screenitem.delete
screenitem.get
screenitem.update
screenitem.updatebyposition
Script
Script object
script.create
script.delete
script.execute
script.get
script.getscriptsbyhosts
script.update
Service
Service object
service.adddependencies
service.addtimes
service.create
service.delete
service.deletedependencies
service.deletetimes
service.get
service.getsla
service.update
Task
task.create
Template
Template object
template.create
template.delete
template.get
template.massadd
template.massremove
template.massupdate
template.update
Template screen
Template screen object
templatescreen.copy
templatescreen.create
templatescreen.delete
templatescreen.get
templatescreen.update
Template screen item
Template screen item object
templatescreenitem.get
Trend
Trend object
trend.get
Trigger
Trigger object
trigger.adddependencies
trigger.create
trigger.delete
trigger.deletedependencies
trigger.get
trigger.update
Trigger prototype
Trigger prototype object
triggerprototype.create
triggerprototype.delete
triggerprototype.get
triggerprototype.update
User
User object
user.checkAuthentication
user.create
user.delete
user.get
user.login
user.logout
user.update
User group
User group object
usergroup.create
usergroup.delete
usergroup.get
usergroup.update
User macro
User macro object
usermacro.create
usermacro.createglobal
usermacro.delete
usermacro.deleteglobal
usermacro.get
usermacro.update
usermacro.updateglobal
Value map
Value map object
valuemap.create
valuemap.delete
valuemap.get
valuemap.update
Web scenario
Web scenario object
httptest.create
httptest.delete
httptest.get
httptest.update
Zabbix API changes in 4.0
20. Appendixes
1 Frequently asked questions / Troubleshooting
2 Installation
1 Database creation
2 Repairing Zabbix database character set and collation
3 Elasticsearch setup
4 Real-time export of events, item values, trends
5 Running Agent as root
6 Zabbix agent on Microsoft Windows
7 Additional frontend languages
3 Daemon configuration
1 Zabbix server
2 Zabbix proxy
3 Zabbix agent (UNIX)
4 Zabbix agent (Windows)
5 Zabbix Java gateway
6 Special notes on "Include" parameter
4 Protocols
1 Server-proxy data exchange protocol
2 Zabbix agent protocol
3 Zabbix sender protocol
4 Header
5 Real-time export protocol
5 Items
1 Items supported by platform
2 vm.memory.size parameters
3 Passive and active agent checks
4 Trapper items
5 Minimum permission level for Windows agent items
6 Encoding of returned values
7 Large file support
8 Sensor
9 Notes on memtype parameter in proc.mem items
10 Notes on selecting processes in proc.mem and proc.num items
11 Implementation details of net.tcp.service and net.udp.service checks
12 Item value preprocessing details
13 Supported JSONPath functionality
14 Unreachable/unavailable host settings
15 Remote monitoring of Zabbix stats
6 Triggers
1 Supported trigger functions
7 Macros
1 Supported macros
2 User macros supported by location
8 Unit symbols
9 Setting time periods
10 Command execution
11 Version compatibility
12 Database error handling
13 Zabbix sender dynamic link library for Windows
14 Issues with SELinux
15 Other issues
Zabbix manpages
zabbix_agentd
zabbix_get
zabbix_proxy
zabbix_sender
zabbix_server
On this page
Zabbix documentation
Zabbix documentation
These pages contain official Zabbix documentation.
Use the sidebar navigation to browse documentation pages.
To be able to watch pages, log in with your
Zabbix forums
username and password.
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
