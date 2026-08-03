# Zabbix knowledge

## Severity and host groups

When investigating operational issues in Zabbix, the usual workflow is:

1. Identify the affected host group.
2. Review the severity average for the group.
3. Correlate alerts with runbooks and historical incidents.
4. Check the relevant documentation before applying mitigation.

The SOFIA platform should use the Zabbix module to query hosts, problems and triggers, then combine that with Knowledge to explain the operational impact of a severity average trend.
