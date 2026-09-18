# 2 Configuring a host

Fonte: https://www.zabbix.com/documentation/current/en/manual/config/hosts/host
Capturado em: 2026-09-16T13:20:39.167573+00:00
Páginas no domínio: 10

## 2 Configuring a host
URL: https://www.zabbix.com/documentation/current/en/manual/config/hosts/host

2 Configuring a host
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
1 Hosts and host groups
2 Configuring a host
On this page
2 Configuring a host
Overview
Configuration
Encryption
Value mapping
2 Configuring a host
Overview
To configure a host in Zabbix frontend, do the following:
Go to:
Data collection > Hosts
or
Monitoring > Hosts
Click
Create host
in the upper-right corner of the screen (or on the host name to edit an existing host)
Enter parameters of the host in the form
You can also use the
Clone
button in the configuration form of an existing host to create a new host. This host will have all of the properties of the existing host, including linked templates, entities (items, triggers, etc.) from those templates, as well as the entities directly attached to the existing host.
Note that when a host is cloned, it will retain all template entities as they are originally on the template. Any changes to those entities made on the existing host level (such as changed item interval, modified regular expression or added prototypes to the low-level discovery rule) will not be cloned to the new host; instead they will be as on the template.
Alternatively, you can use the
Host Wizard
to configure a host through a guided, step-by-step interface.
Configuration
The
Host
tab contains general host attributes:
All mandatory input fields are marked with a red asterisk.
Parameter
Description
Host name
Enter a unique host name. Alphanumerics, spaces, dots, dashes and underscores are allowed. However, leading and trailing spaces are disallowed.
Note:
With Zabbix agent running on the host you are configuring, the
agent configuration file
parameter
Hostname
must have the same value as the host name entered here. The name in the parameter is needed in the processing of
active checks
.
Visible name
Enter a unique visible name for the host. If you set this name, it will be the one visible in lists, maps, etc instead of the technical host name. This attribute has UTF-8 support.
Templates
Link templates
to the host. All entities (items, triggers, etc.) will be inherited from the template.
To link a new template, start typing the template name in the text input field. A list of matching templates will appear; scroll down to select. Alternatively, you may click
Select
next to the field and select templates from the list in a popup window. All selected templates will be linked to the host when the host configuration form is saved or updated.
To unlink a template, use one of the two options in the
Linked templates
block:
Unlink
- unlink the template, but preserve its entities (items, triggers, etc.);
Unlink and clear
- unlink the template and remove all its entities (items, triggers, etc.).
Listed template names are clickable links leading to the
template configuration form
.
Host groups
Select
host groups
the host belongs to. A host must belong to at least one host group. A new group can be created and linked to the host by adding a non-existing group name.
Interfaces
Several host interface types are supported for a host:
Agent
,
SNMP
,
JMX
and
IPMI
.
No interfaces are defined by default. To add a new interface, click
Add
in the
Interfaces
block, select the interface type and enter
IP/DNS
,
Connect to
and
Port
info.
Note:
Interfaces that are used in any items cannot be removed and link
Remove
is grayed out for them.
The "IP" or "DNS" from an SNMP interface is also used for
SNMP traps
.
During matching, only the selected "IP" or "DNS" in the host interface is used.
See
Configuring SNMP monitoring
for additional details on configuring an SNMP interface (v1, v2 and v3).
IP address
Host IP address (optional).
DNS name
Host DNS name (optional).
Connect to
Clicking the respective button will tell Zabbix server what to use to retrieve data from agents:
IP
- Connect to the host IP address (recommended)
DNS
- Connect to the host DNS name
Port
TCP/UDP port number. Default values are: 10050 for Zabbix agent, 161 for SNMP agent, 12345 for JMX and 623 for IPMI.
Default
Check the radio button to set the default interface.
Description
Enter the host description.
Monitored by
Select if the host is monitored by:
Server
- host is monitored by Zabbix server;
Proxy
- host is monitored by standalone proxy;
Proxy group
- host is monitored by proxy group.
Proxy
The assigned proxy name is displayed (only if Zabbix server has assigned one from the selected proxy group).
This field is displayed only if the host is monitored by a proxy group.
Enabled
When the checkbox is checked, the host is enabled - ready for monitoring.
When the checkbox is unchecked, the host is disabled - not monitored:
For passive data requests initiated by Zabbix server/proxy (for example,
Zabbix agent
,
SNMP agent
,
simple checks
), monitoring is disabled after configuration synchronization. Triggers and actions linked to the host are also disabled only after the configuration is reloaded.
For Zabbix agent
active checks
, monitoring stops within the time frame (approx. 5 seconds) that Zabbix agent receives information about the host having been disabled. During this brief interval, the host will continue to locally collect data for the active checks and try sending it to the server/proxy; however, since the host is marked as
Disabled
, the server/proxy will reject the data.
When you disable the host, its items are immediately removed from the history cache (except for their last values, which are kept for logs).
The
IPMI
tab contains IPMI management attributes.
Parameter
Description
Authentication algorithm
Select the authentication algorithm.
Privilege level
Select the privilege level.
Username
User name for authentication. User macros may be used.
Password
Password for authentication. User macros may be used.
The
Tags
tab allows you to define host-level
tags
. All problems of this host will be tagged with the values entered here.
User macros, {INVENTORY.*} macros, {HOST.HOST}, {HOST.NAME}, {HOST.CONN}, {HOST.DNS}, {HOST.IP}, {HOST.PORT} and {HOST.ID} macros are supported in tags.
The
Macros
tab allows you to define host-level
user macros
as a name-value pairs. Note that macro values can be kept as plain text, secret text or Vault secret. Adding a description is also supported.
You may also view here template-level and global user macros if you select the
Inherited and host macros
option. That is where all defined user macros for the host are displayed with the value they resolve to as well as their origin.
For convenience, links to respective templates and global macro configuration are provided. It is also possible to edit a template/global macro on the host level, effectively creating a copy of the macro on the host.
The
Inventory
tab allows you to manually enter
inventory
information for the host. You can also select to enable
Automatic
inventory population, or disable inventory population for this host.
If inventory is enabled (manual or automatic), a green dot is displayed with the tab name.
Encryption
The
Encryption
tab allows you to require
encrypted
connections with the host.
Parameter
Description
Connections to host
How Zabbix server or proxy connects to Zabbix agent on a host: no encryption (default), using PSK (pre-shared key) or certificate.
Connections from host
Select what type of connections are allowed from the host (i.e. from Zabbix agent and Zabbix sender). Several connection types can be selected at the same time (useful for testing and switching to other connection type). Default is "No encryption".
Issuer
Allowed issuer of certificate. Certificate is first validated with CA (certificate authority). If it is valid, signed by the CA, then the
Issuer
field can be used to further restrict allowed CA. This field is intended to be used if your Zabbix installation uses certificates from multiple CAs. If this field is empty then any CA is accepted.
Subject
Allowed subject of certificate. Certificate is first validated with CA. If it is valid, signed by the CA, then the
Subject
field can be used to allow only one value of
Subject
string. If this field is empty then any valid certificate signed by the configured CA is accepted.
PSK identity
Pre-shared key identity string.
Do not put sensitive information in the PSK identity, it is transmitted unencrypted over the network to inform a receiver which PSK to use.
PSK
Pre-shared key (hex-string). Maximum length: 512 hex-digits (256-byte PSK) if Zabbix uses GnuTLS or OpenSSL library, 64 hex-digits (32-byte PSK) if Zabbix uses mbed TLS (PolarSSL) library. Example: 1f87b595725ac58dd977beef14b97461a7c1045b9a1c963065002c5473194952
Value mapping
The
Value mapping
tab allows to configure human-friendly representation of item data in
value mappings
.
What’s next?
3 Configuring a host group
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

## Zabbix guidelines
URL: https://www.zabbix.com/documentation/guidelines/en

Zabbix guidelines
Docs
Version:
guidelines
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
Coding
C coding guidelines
Go coding guidelines
Code style guidelines
Development process guidelines
HTML/CSS coding guidelines
JavaScript coding guidelines
PHP coding guidelines
Perl coding guidelines
SQL coding guidelines
Shell coding guidelines
Creating plugins
Loadable plugins
Built-in plugins
Template guidelines
Creating webhooks
Development process
Localizing Zabbix
Getting started
Translating UI
Translating documentation
Naming guidelines
Error message style
On this page
Zabbix guidelines
Zabbix guidelines
These pages contain official Zabbix guidelines with regard to:
Coding
C coding guidelines
Go coding guidelines
HTML/CSS coding guidelines
JavaScript coding guidelines
Perl coding guidelines
PHP coding guidelines
Shell coding guidelines
SQL coding guidelines
Building plugins
Loadable plugins
Built-in plugins
Template guidelines
Creating webhooks
Development process
Localizing Zabbix UI and Documentation
Getting started
Translating UI
Translating documentation
Naming guidelines
Error message style
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

## Zabbix Documentation License
URL: https://www.zabbix.com/documentation/info/en/license

Zabbix Documentation License
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
Zabbix Documentation License
Zabbix documentation is NOT distributed under the AGPL-3.0 license. Use of Zabbix documentation is subject to the following terms:
You may create a printed copy of this documentation solely for your own personal use. Conversion to other formats is allowed as long as the actual content is not altered or edited in any way. You shall not publish or distribute this documentation in any form or on any media, except if you distribute the documentation in a manner similar to how Zabbix disseminates it (that is, electronically for download on a Zabbix web site) or on a USB or similar medium, provided however that the documentation is disseminated together with the software on the same medium. Any other use, such as any dissemination of printed copies or use of this documentation, in whole or in part, in another publication, requires the prior written consent from an authorized representative of Zabbix. Zabbix reserves any and all rights to this documentation not expressly granted above.
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

## Zabbix Cloud
URL: https://www.zabbix.com/documentation/current/en/cloud

Zabbix Cloud
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
Zabbix Cloud
Zabbix Cloud
Discover the available configuration options and access controls for organizations and nodes in Zabbix Cloud.
Please note that Zabbix Cloud nodes currently run
Zabbix 7.0
.
For in-depth information on Zabbix 7.0, see
official documentation
.
Set up and manage Zabbix Cloud
Start using Zabbix Cloud
Guided instructions to get your Zabbix Cloud instance up and running quickly, including initial configuration and connecting your monitored devices.
Node configuration
Learn how to set up your Zabbix Cloud node, focusing on access, data handling, and resource settings.
Adding users
Find out how to add and assign roles to users within a Zabbix Cloud organization and its nodes.
Learn about Zabbix Cloud
Zabbix Cloud vs. on-premises
Compare the differences in management, scalability, and maintenance between the two deployments, and learn which can support your workflow most seamlessly.
Explore Zabbix Cloud
Get an overview of Zabbix Cloud, including its key features, perks, and what comes with a subscription. For common questions on setup and usage, see the FAQ.
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

## Developer center
URL: https://www.zabbix.com/documentation/current/en/devel

Developer center
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
Developer center
Developer center
Start developing custom extensions for Zabbix with guidance on plugins, modules, and widgets.
Build on Zabbix
Plugins
An overview on how to develop and manage Zabbix plugins to extend functionality or integrate with external systems.
Python library for Zabbix
Resources for using the official
zabbix_utils
library to interact with the Zabbix API and build integrations.
Frontend modules
Guides and references for building custom modules that extend or modify the Zabbix frontend to suit specific use cases.
Widgets
A breakdown of widget structure and logic, with instructions for creating custom dashboard elements tailored to your needs.
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

## User manual
URL: https://www.zabbix.com/documentation/current/en/manual

User manual
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
Welcome to Zabbix Documentation
Your go-to resource for working with Zabbix monitoring, from basic setups to advanced configurations. This manual covers everything needed to install, configure, and operate Zabbix.
What's new in Zabbix 7.4
Get started with Zabbix
Installation
Step-by-step instructions to install Zabbix on your preferred platform, covering various operating systems and database configurations.
Requirements
A list of supported platforms and software prerequisites to help you prepare your environment for a successful Zabbix deployment.
Quickstart guides
Concise, task-oriented how-tos that walk you through the basics—from your first configuration steps to receiving your first problem alert.
Zabbix Cloud
Start using Zabbix Cloud
Guided instructions to get your Zabbix Cloud instance up and running quickly, including initial configuration and connecting your monitored devices.
Zabbix Cloud vs. on-premises
Compare the differences in management, scalability, and maintenance between the two deployments, and learn which can support your workflow most seamlessly.
Explore Zabbix Cloud
Get an overview of Zabbix Cloud, including its key features, perks, and what comes with a subscription. For common questions on setup and usage, see the FAQ.
Developer center
Frontend modules
Guides and references for building custom modules that extend or modify the Zabbix frontend to suit specific use cases.
Widgets
A breakdown of widget structure and logic, with instructions for creating custom dashboard elements tailored to your needs.
Plugins
An overview on how to develop and manage Zabbix plugins to extend functionality or integrate with external systems.
Community & other resources
Zabbix Forums
A space to exchange ideas, find solutions, and share experiences across all levels of Zabbix expertise.
Zabbix Blog
News, tutorials, and case studies curated by the Zabbix team and community contributors.
How-to videos
A video library featuring demonstrations, discussions, and tips to help you make the most of Zabbix.
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

## Zabbix manpages
URL: https://www.zabbix.com/documentation/current/en/manpages

Zabbix manpages
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
Zabbix manpages
Reference documentation for Zabbix command‑line tools and services, listing available commands, options, and usage examples.
What’s next?
zabbix_agent2
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

## Copyright notice
URL: https://www.zabbix.com/documentation/current/en/copyright

Copyright notice
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
Copyright notice
Zabbix documentation is NOT distributed under the AGPL-3.0 license. Use of Zabbix documentation is subject to the following terms:
You may create a printed copy of this documentation solely for your own personal use. Conversion to other formats is allowed as long as the actual content is not altered or edited in any way. You shall not publish or distribute this documentation in any form or on any media, except if you distribute the documentation in a manner similar to how Zabbix disseminates it (that is, electronically for download on a Zabbix web site) or on a USB or similar medium, provided however that the documentation is disseminated together with the software on the same medium. Any other use, such as any dissemination of printed copies or use of this documentation, in whole or in part, in another publication, requires the prior written consent from an authorized representative of Zabbix. Zabbix reserves any and all rights to this documentation not expressly granted above.
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
URL: https://www.zabbix.com/documentation/current/en/manual/api

20 API
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
20 API
On this page
20 API
Overview
Structure
Performing requests
Authentication
Authorization methods
By "Authorization" header
By Zabbix cookie
Example workflow
Retrieving hosts
Creating a new item
Creating multiple triggers
Updating an item
Updating multiple triggers
Error handling
API versions
Further reading
20 API
Overview
The Zabbix API allows you to programmatically retrieve and modify configuration of Zabbix and provides access to historical data. It is widely used to:
Create new applications to work with Zabbix.
Integrate Zabbix into a third-party software.
Automate routine tasks.
The Zabbix API is an HTTP-based API, and it is shipped as a part of the web frontend. It uses the JSON-RPC 2.0 protocol, which means two things:
The API consists of a set of separate methods.
Requests and responses between the clients and the API are encoded using the JSON format.
For more information about the protocol and JSON, see the
JSON-RPC 2.0 specification
and the
JSON format homepage
.
For more information about integrating Zabbix functionality into your Python applications, see
Python library for Zabbix
.
User access in Zabbix, including both configuration and historical data, depends on the
user type
, the assigned
user role
, and
user groups
.
Structure
The API consists of a number of methods that are nominally grouped into separate APIs. Each of the methods performs one specific task. For example, the
host.create
method belongs to the
host
API
and is used to create new hosts. Historically, APIs are sometimes referred to as "classes".
Most APIs contain at least four methods:
get
,
create
,
update
and
delete
for retrieving, creating, updating and deleting data respectively, but some APIs may provide a totally different set of methods.
Performing requests
Once you have set up the frontend, you can use remote HTTP requests to call the API. To do that, you need to send HTTP POST requests to the
api_jsonrpc.php
file located in the frontend directory.
For example, if your Zabbix frontend is installed under
https://example.com/zabbix
, an HTTP request to call the
apiinfo.version
method may look like this:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}'
The request must have the
Content-Type
header set to one of these values:
application/json-rpc
,
application/json
or
application/jsonrequest
.
The request object must contain the following properties:
jsonrpc
- the version of the JSON-RPC protocol used by the API (Zabbix API implements JSON-RPC version 2.0);
method
- the API method being called;
params
- the parameters that will be passed to the API method;
id
- an arbitrary identifier of the request (if omitted, the API treats the request as a
notification
).
If the request is correct, the response returned by the API should look like this:
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
The response object, in turn, contains the following properties:
jsonrpc
- the version of the JSON-RPC protocol;
result
- the data returned by the method;
id
- an identifier of the corresponding request.
Authentication
To access any data in Zabbix, you need to either:
Use an existing API token created in the Zabbix frontend,
Users
>
API tokens
section, or created using the
Token API
.
Use an authentication token obtained with the
user.login
method.
For example, if you wanted to obtain a new authentication token by logging in as a standard
Admin
user, then a JSON request would look like this:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}'
If you provided the credentials correctly, the response returned by the API should contain the user authentication token:
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
Authorization methods
By "Authorization" header
All API requests require an authentication or an API token. You can provide the credentials by using the Authorization header in the request:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer 0424bd59b807674191e7d77572075f33'
If you are experiencing authentication issues, see
Authorization header forwarding
.
Zabbix API accepts headers in a case-insensitive way (e.g.,
authorization
,
Authorization
, and
AUTHORIZATION
are treated the same).
The Authorization header is supported in cross-origin requests (
CORS
).
By Zabbix cookie
A
"zbx_session"
cookie is used to authorize an API request from Zabbix UI performed using JavaScript (from a module or a custom widget).
Example workflow
The following section walks you through several usage examples in greater detail.
Retrieving hosts
Now you have a valid user authentication token (represented as a variable in the following examples) that can be used to access the data in Zabbix. For example, you can use the
host.get
method to retrieve the IDs, host names and interfaces of all the configured
hosts
:
Request:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data @data.json
data.json
is a file that contains a JSON query. Instead of a file, you can pass the query in the
--data
argument.
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
The response object will contain the requested data about the hosts:
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
For performance reasons it is always recommended to list the object properties you want to retrieve. Thus, you will avoid retrieving everything.
Creating a new item
Now, create a new
item
on the host "Zabbix server" using the data you have obtained from the previous
host.get
request. This can be done using the
item.create
method:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"item.create","params":{"name":"Free disk space on /home/joe/","key_":"vfs.fs.size[/home/joe/,free]","hostid":"10084","type":0,"value_type":3,"interfaceid":"1","delay":30},"id":3}'
A successful response will contain the ID of the newly created item, which can be used to reference the item in the following requests:
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
The
item.create
method as well as other
create methods
can also accept arrays of objects and create multiple items with one API call.
Creating multiple triggers
Thus, if
create methods
accept arrays, you can add multiple
triggers
, for example, this one:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"trigger.create","params":[{"description":"Processor load is too high on {HOST.NAME}","expression":"last(/Linux server/system.cpu.load[percpu,avg1])>5"},{"description":"Too many processes on {HOST.NAME}","expression":"avg(/Linux server/proc.num[],5m)>300"}],"id":4}'
The successful response will contain the IDs of the newly created triggers:
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
Updating an item
Enable an item by setting its status to
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
The successful response will contain the ID of the updated item:
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
The
item.update
method as well as other
update methods
can also accept arrays of objects and update multiple items with one API call.
Updating multiple triggers
Enable multiple triggers by setting their status to
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
The successful response will contain the IDs of the updated triggers:
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
This is the preferred method of updating. Some API methods, such as the
host.massupdate
allow to write a simpler code. However, it is not recommended to use these methods as they will be removed in the future releases.
Error handling
Up to the present moment, everything you have tried has worked fine. But what would happen if you tried making an incorrect call to the API? Try to create another host by calling
host.create
but omitting the mandatory
groups
parameter:
curl --request POST \ --url
'https://example.com/zabbix/api_jsonrpc.php'
\ --header
'Authorization: Bearer ${AUTHORIZATION_TOKEN}'
\ --header
'Content-Type: application/json-rpc'
\ --data
'{"jsonrpc":"2.0","method":"host.create","params":{"host":"Linux server","interfaces":[{"type":1,"main":1,"useip":1,"ip":"192.168.3.1","dns":"","port":"10050"}]},"id":7}'
The response will then contain an error message:
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
If an error has occurred, instead of the
result
property, the response object will contain the
error
property with the following data:
code
- an error code;
message
- a short error summary;
data
- a more detailed error message.
Errors can occur in various cases, such as, using incorrect input values, a session timeout or trying to access non-existing objects. Your application should be able to gracefully handle these kinds of errors.
API versions
To simplify API versioning, since Zabbix 2.0.4, the version of the API matches the version of Zabbix itself. You can use the
apiinfo.version
method to find out the version of the API you are working with. This can be useful for adjusting your application to use version-specific features.
Zabbix guarantees feature backward compatibility inside a major version. When making backward incompatible changes between major releases, Zabbix usually leaves the old features as deprecated in the next release, and only removes them in the release after that. Occasionally, Zabbix may remove features between major releases without providing any backward compatibility. It is important that you never rely on any deprecated features and migrate to newer alternatives as soon as possible.
You can follow all the changes made to the API in the
API changelog
.
Further reading
Now, you have enough knowledge to start working with the Zabbix API, however, do not stop here. For further reading you are advised to have a look at the
list of available APIs
.
What’s next?
Appendix 1. Reference commentary
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
