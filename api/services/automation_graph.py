from __future__ import annotations

from typing import Any
from uuid import uuid4

from psycopg.types.json import Jsonb

from config.settings import settings


CONNECTOR_CATALOG = [
    {"type": "trigger", "label": "Alerta / pergunta", "category": "Entrada", "status": "active"},
    {"type": "zabbix", "label": "Zabbix", "category": "Observabilidade", "status": "active"},
    {"type": "knowledge", "label": "Base offline", "category": "Conhecimento", "status": "active"},
    {"type": "claude", "label": "Claude curador", "category": "Raciocínio", "status": "active"},
    {"type": "correlate", "label": "Correlacionar linha do tempo", "category": "Raciocínio", "status": "active"},
    {"type": "report", "label": "Gerar relatório", "category": "Saída", "status": "active"},
    {"type": "grafana", "label": "Grafana", "category": "Observabilidade", "status": "needs_configuration"},
    {"type": "prometheus", "label": "Prometheus", "category": "Métricas", "status": "needs_configuration"},
    {"type": "loki", "label": "Loki", "category": "Logs", "status": "needs_configuration"},
    {"type": "sql", "label": "SQL", "category": "Dados", "status": "needs_configuration"},
    {"type": "jira", "label": "Jira", "category": "Chamados", "status": "needs_configuration"},
    {"type": "git", "label": "Git", "category": "Mudanças", "status": "needs_configuration"},
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


automation_graph_store = AutomationGraphStore()
