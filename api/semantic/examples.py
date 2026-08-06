SEMANTIC_EXAMPLES = [
    {
        "question": "Quantos switches tiveram triggers nos últimos 7 dias?",
        "query": {"intent":"historical_trigger_summary","domain":"network","source":"zabbix","entity_type":"switch","entity_name":"Switches","time_range":{"days":7},"metric":"trigger_count","state":"historical","group_by":"host","ambiguities":[],"confidence":0.99,"requires_clarification":False,"interpretation_source":"unknown"},
    },
    {
        "question": "Quais servidores estão com problemas ativos?",
        "query": {"intent":"active_trigger_summary","domain":"infrastructure","source":"zabbix","entity_type":"server","entity_name":"Servidores","time_range":None,"metric":"active_problems","state":"active","group_by":"host","ambiguities":[],"confidence":0.99,"requires_clarification":False,"interpretation_source":"unknown"},
    },
    {
        "question": "O que é um switch?",
        "query": {"intent":"general_chat","domain":"network","source":"none","entity_type":"switch","entity_name":None,"time_range":None,"metric":"none","state":"conceptual","group_by":"none","ambiguities":[],"confidence":0.98,"requires_clarification":False,"interpretation_source":"unknown"},
    },
]
