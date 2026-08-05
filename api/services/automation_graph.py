from __future__ import annotations

from typing import Any
from uuid import uuid4
from collections import Counter
from datetime import datetime, timezone

from psycopg.types.json import Jsonb

from config.settings import settings
from ai.operational_query import format_related_problems, related_problems, unique_affected_hosts, wants_related_alarm_list
from connectors.zabbix import ZabbixConnector
from services.knowledge import search_knowledge
from services.postgres_store import postgres_store


CONNECTOR_CATALOG = [
    {"type":"trigger","label":"Alerta / pergunta","category":"Entrada","status":"active","description":"Inicia o fluxo a partir de uma pergunta, alerta ou evento recebido."},
    {"type":"zabbix","label":"Zabbix","category":"Observabilidade","status":"active","description":"Consulta hosts, grupos, triggers, problemas ativos e severidades."},
    {"type":"knowledge","label":"Base offline","category":"Conhecimento","status":"active","description":"Pesquisa documentos, runbooks e respostas aprendidas sem depender da internet."},
    {"type":"claude","label":"Claude curador","category":"Raciocínio","status":"active","description":"Explica e classifica contexto quando a base local ainda não possui resposta suficiente."},
    {"type":"correlate","label":"Correlacionar linha do tempo","category":"Raciocínio","status":"active","description":"Ordena métricas, logs, alertas e mudanças por horário para sugerir causa provável."},
    {"type":"report","label":"Gerar relatório","category":"Saída","status":"active","description":"Transforma evidências em resumo técnico, causa provável e próximos passos."},
    {"type":"grafana","label":"Grafana","category":"Observabilidade","status":"active","description":"Centraliza dashboards e permite explorar métricas e logs das fontes provisionadas."},
    {"type":"prometheus","label":"Prometheus","category":"Métricas","status":"active","description":"Coleta séries temporais de CPU, memória, disco, banco e saúde da API."},
    {"type":"loki","label":"Loki + Alloy","category":"Logs","status":"active","description":"Coleta logs dos containers e permite consultas e correlação por serviço e horário."},
    {"type":"postgres","label":"PostgreSQL","category":"Dados","status":"active","description":"Consulta, em modo somente leitura no Grafana, consumo, conexões e dados operacionais."},
    {"type":"jira","label":"Jira","category":"Chamados","status":"needs_configuration","description":"Relaciona incidentes a chamados; requer URL, e-mail e token de uma instância Jira."},
    {"type":"git","label":"Git local","category":"Mudanças","status":"active","description":"Consulta commits e alterações recentes do repositório local para correlacionar mudanças."},
]
CATALOG_BY_TYPE = {item["type"]: item for item in CONNECTOR_CATALOG}


class AutomationGraphStore:
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or settings.POSTGRES_DSN

    def connect(self):
        import psycopg
        return psycopg.connect(self.dsn)

    def ensure_schema(self) -> bool:
        try:
            with self.connect() as conn:
                conn.execute("""CREATE TABLE IF NOT EXISTS automation_graphs (
                    id UUID PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
                    nodes JSONB NOT NULL DEFAULT '[]'::jsonb, edges JSONB NOT NULL DEFAULT '[]'::jsonb,
                    enabled BOOLEAN NOT NULL DEFAULT FALSE, created_by BIGINT REFERENCES auth_users(id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
                conn.execute("""CREATE TABLE IF NOT EXISTS automation_runs (
                    id UUID PRIMARY KEY, graph_id UUID REFERENCES automation_graphs(id), status TEXT NOT NULL,
                    timeline JSONB NOT NULL DEFAULT '[]'::jsonb, created_by BIGINT REFERENCES auth_users(id),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
                conn.execute("ALTER TABLE automation_runs ADD COLUMN IF NOT EXISTS outputs JSONB NOT NULL DEFAULT '[]'::jsonb")
                conn.execute("ALTER TABLE automation_runs ADD COLUMN IF NOT EXISTS report TEXT NOT NULL DEFAULT ''")
                conn.commit()
            return True
        except Exception:
            return False

    @staticmethod
    def validate(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> None:
        if len(nodes) > 80 or len(edges) > 160:
            raise ValueError("O grafo excede o limite seguro")
        ids = {str(node.get("id", "")) for node in nodes}
        if "" in ids or len(ids) != len(nodes):
            raise ValueError("Nós precisam de identificadores únicos")
        invalid_types = sorted({str(node.get("type")) for node in nodes} - set(CATALOG_BY_TYPE))
        if invalid_types:
            raise ValueError(f"Tipos de bloco inválidos: {', '.join(invalid_types)}")
        for edge in edges:
            if str(edge.get("source")) not in ids or str(edge.get("target")) not in ids:
                raise ValueError("Conector aponta para um bloco inexistente")
            if edge.get("source") == edge.get("target"):
                raise ValueError("Um bloco não pode conectar a si mesmo")

    def list(self) -> list[dict[str, Any]]:
        self.ensure_schema()
        with self.connect() as conn:
            rows = conn.execute("SELECT id,name,description,nodes,edges,enabled,updated_at FROM automation_graphs ORDER BY updated_at DESC").fetchall()
        return [{"id":str(r[0]),"name":r[1],"description":r[2],"nodes":r[3],"edges":r[4],"enabled":r[5],"updated_at":r[6].isoformat()} for r in rows]

    def save(self, name: str, description: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], user_id: int, graph_id: str | None = None) -> dict[str, Any]:
        self.ensure_schema(); self.validate(nodes, edges); graph_id = graph_id or str(uuid4())
        with self.connect() as conn:
            row = conn.execute("""INSERT INTO automation_graphs(id,name,description,nodes,edges,created_by)
                VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(id) DO UPDATE SET name=EXCLUDED.name,
                description=EXCLUDED.description,nodes=EXCLUDED.nodes,edges=EXCLUDED.edges,updated_at=NOW()
                RETURNING id,updated_at""", (graph_id,name.strip(),description.strip(),Jsonb(nodes),Jsonb(edges),user_id)).fetchone(); conn.commit()
        return {"id":str(row[0]),"updated_at":row[1].isoformat()}

    def simulate(self, graph_id: str, user_id: int) -> dict[str, Any]:
        self.ensure_schema()
        with self.connect() as conn:
            row=conn.execute("SELECT nodes,edges FROM automation_graphs WHERE id=%s",(graph_id,)).fetchone()
            if not row: raise KeyError(graph_id)
            nodes,edges=row; incoming={str(e['target']) for e in edges}; ordered=[]; pending={str(n['id']):n for n in nodes}
            frontier=[key for key in pending if key not in incoming]
            while frontier:
                node_id=frontier.pop(0)
                if node_id not in pending: continue
                node=pending.pop(node_id); connector=CATALOG_BY_TYPE[node['type']]
                status='ready' if connector['status']=='active' else 'needs_configuration'
                ordered.append({"node_id":node_id,"label":node.get('label') or connector['label'],"connector":node['type'],"status":status})
                frontier.extend(str(e['target']) for e in edges if str(e['source'])==node_id)
            for node in pending.values():
                ordered.append({"node_id":str(node['id']),"label":node.get('label',node['type']),"connector":node['type'],"status":"blocked_or_cyclic"})
            run_id=str(uuid4()); status='ready' if all(x['status']=='ready' for x in ordered) else 'configuration_required'
            conn.execute("INSERT INTO automation_runs(id,graph_id,status,timeline,created_by) VALUES(%s,%s,%s,%s,%s)",(run_id,graph_id,status,Jsonb(ordered),user_id)); conn.commit()
        return {"run_id":run_id,"status":status,"timeline":ordered,"executed":False}

    @staticmethod
    def _ordered_nodes(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        incoming={str(e['target']) for e in edges};ordered=[];pending={str(n['id']):n for n in nodes}
        frontier=[key for key in pending if key not in incoming]
        while frontier:
            node_id=frontier.pop(0)
            if node_id not in pending:continue
            node=pending.pop(node_id);ordered.append(node)
            frontier.extend(str(e['target']) for e in edges if str(e['source'])==node_id)
        ordered.extend(pending.values())
        return ordered

    @staticmethod
    def _zabbix_analysis(problems: list[dict[str, Any]]) -> dict[str, Any]:
        severity = Counter(str(item.get('severity_label') or 'Não classificado') for item in problems)
        groups = Counter(group for item in problems for group in (item.get('groups') or []))
        timeline = []
        now = datetime.now(timezone.utc)
        for item in problems:
            try:
                started = datetime.fromtimestamp(int(item.get('clock')), tz=timezone.utc)
                age_seconds = max(0, int((now - started).total_seconds()))
                started_at = started.isoformat()
            except (TypeError, ValueError, OSError):
                age_seconds, started_at = None, None
            timeline.append({'eventid':item.get('eventid'),'started_at':started_at,'age_seconds':age_seconds,
                'status':'active','name':item.get('name'),'hosts':item.get('hosts') or [],
                'severity':item.get('severity_label') or 'Não classificado'})
        timeline.sort(key=lambda event: event.get('started_at') or '')
        snapshots = postgres_store.get_recent_snapshots(limit=30)
        insights = postgres_store.get_recent_insights(limit=10)
        series = [{'generated_at':snap.get('generated_at'),'problems':int((snap.get('summary') or {}).get('problems',0) or 0)} for snap in reversed(snapshots)]
        return {
            'severity_distribution':[{'label':key,'value':value} for key,value in severity.most_common()],
            'group_distribution':[{'label':key,'value':value} for key,value in groups.most_common(8)],
            'event_timeline':timeline,
            'behavior':{'status':'collecting' if len(snapshots)<10 else 'baseline_ready','snapshot_count':len(snapshots),
                'insight_count':len(insights),'interval_seconds':settings.SNAPSHOT_INTERVAL_SECONDS,
                'first_sample_at':snapshots[-1].get('generated_at') if snapshots else None,
                'last_sample_at':snapshots[0].get('generated_at') if snapshots else None,
                'problem_series':series,'method':'baseline estatístico e detecção de recorrência'},
        }

    @staticmethod
    def _execute_connector(node: dict[str, Any], input_text: str, previous: list[dict[str, Any]]) -> dict[str, Any]:
        connector_type=str(node.get('type',''))
        if connector_type=='trigger':
            return {'summary':f'Entrada recebida: {input_text}','data':{'input':input_text}}
        if connector_type=='zabbix':
            active=ZabbixConnector().list_active_problems(limit=2000)
            matches=related_problems(input_text,active) if wants_related_alarm_list(input_text) else active[:20]
            affected_hosts=unique_affected_hosts(matches)
            analysis=AutomationGraphStore._zabbix_analysis(matches)
            return {
                'summary':format_related_problems(matches,len(active),input_text),
                'data':{'active_problem_count':len(active),'related_problem_count':len(matches),'unique_host_count':len(affected_hosts),'hosts':affected_hosts,'problems':matches,**analysis},
            }
        if connector_type=='knowledge':
            result=search_knowledge(input_text);hits=result.get('results',[]) if isinstance(result,dict) else []
            summary='\n'.join(str(hit.get('snippet','')) for hit in hits[:5]) or 'A base offline não encontrou conteúdo relacionado.'
            return {'summary':summary,'data':{'results':hits[:5]}}
        if connector_type=='correlate':
            evidence=[item.get('summary','') for item in previous if item.get('summary')]
            return {'summary':f'Foram correlacionadas {len(evidence)} evidência(s) na ordem do fluxo.','data':{'evidence_count':len(evidence)}}
        if connector_type=='report':
            evidence=[item.get('summary','') for item in previous if item.get('connector') not in {'trigger','report'} and item.get('summary')]
            report='Relatório da automação\n\nPergunta/evento: '+input_text+'\n\n'+'\n\n'.join(evidence)
            return {'summary':report,'data':{'evidence_count':len(evidence)},'is_report':True}
        connector=CATALOG_BY_TYPE.get(connector_type,{})
        return {'summary':f"{connector.get('label',connector_type)} está disponível, mas este bloco ainda não possui executor automático.",'data':{}}

    def execute(self, graph_id: str, user_id: int, input_text: str) -> dict[str, Any]:
        self.ensure_schema()
        with self.connect() as conn:
            row=conn.execute("SELECT nodes,edges FROM automation_graphs WHERE id=%s",(graph_id,)).fetchone()
            if not row:raise KeyError(graph_id)
            nodes,edges=row;self.validate(nodes,edges);ordered=self._ordered_nodes(nodes,edges)
            outputs=[];timeline=[];report=''
            for node in ordered:
                connector=CATALOG_BY_TYPE[node['type']]
                if connector['status']!='active':
                    result={'summary':f"{connector['label']} requer configuração.",'data':{}}
                    step_status='needs_configuration'
                else:
                    try:
                        result=self._execute_connector(node,input_text,outputs);step_status='completed'
                    except Exception as exc:
                        result={'summary':f"Falha ao executar {connector['label']}: {exc}",'data':{}}
                        step_status='failed'
                output={'node_id':str(node['id']),'label':node.get('label') or connector['label'],'connector':node['type'],'status':step_status,**result}
                outputs.append(output);timeline.append({key:output[key] for key in ('node_id','label','connector','status')})
                if result.get('is_report'):report=result['summary']
            status='completed' if all(item['status']=='completed' for item in outputs) else 'partial'
            if not report:report='\n\n'.join(item['summary'] for item in outputs if item['connector']!='trigger')
            run_id=str(uuid4())
            conn.execute("INSERT INTO automation_runs(id,graph_id,status,timeline,outputs,report,created_by) VALUES(%s,%s,%s,%s,%s,%s,%s)",(run_id,graph_id,status,Jsonb(timeline),Jsonb(outputs),report,user_id));conn.commit()
        return {'run_id':run_id,'status':status,'timeline':timeline,'outputs':outputs,'report':report,'executed':True}


automation_graph_store = AutomationGraphStore()
