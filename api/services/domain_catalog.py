from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from psycopg.types.json import Jsonb

from services.knowledge import register_knowledge_source, search_knowledge
from services.postgres_store import postgres_store


DOMAIN_ID = re.compile(r"^[a-z][a-z0-9-]{2,39}$")
RESERVED = {"core", "auth", "api", "infrastructure", "zabbix", "admin", "ui"}
THEMES={
    "ocean":{"label":"Tecnologia","accent":"#2dd4bf","secondary":"#60a5fa","icon":"◈"},
    "clinical":{"label":"Saúde","accent":"#22c55e","secondary":"#38bdf8","icon":"✚"},
    "amber":{"label":"Almoxarifado","accent":"#f59e0b","secondary":"#fb7185","icon":"▣"},
    "violet":{"label":"Pessoas e RH","accent":"#a78bfa","secondary":"#f472b6","icon":"◎"},
    "emerald":{"label":"Financeiro","accent":"#10b981","secondary":"#84cc16","icon":"◆"},
    "indigo":{"label":"Educação","accent":"#6366f1","secondary":"#22d3ee","icon":"▤"},
}


def _experience(domain_id:str,display_name:str,purpose:str,entities:list[str],metrics:list[str],theme_key:str)->dict[str,Any]:
    theme=THEMES.get(theme_key,THEMES["ocean"])
    entity_label=entities[0].title() if entities else "Registros"
    metric_label=metrics[0].title() if metrics else "Indicadores"
    return {"domain_id":domain_id,"title":display_name,"purpose":purpose,"branding":{"preset":theme_key,**theme},
        "navigation":[
            {"label":"Visão geral","page":"overview","template":"executive_overview"},
            {"label":entity_label,"page":"records","template":"entity_list"},
            {"label":metric_label,"page":"analytics","template":"analytics"},
            {"label":"Conhecimento","page":"knowledge","template":"knowledge"},
        ],
        "pages":{
            "overview":{"title":f"Visão geral de {display_name}","template":"executive_overview","widgets":["metric","status","ranking","assistant_insight"]},
            "records":{"title":entity_label,"template":"entity_list","entity":entities[0] if entities else "registro","widgets":["table","entity_card"]},
            "analytics":{"title":metric_label,"template":"analytics","widgets":["trend","bar_chart","line_chart"]},
            "knowledge":{"title":"Conhecimento","template":"knowledge","widgets":["assistant_insight","table"]},
        },"vocabulary":{"entities":entities,"metrics":metrics},
        "suggested_questions":[f"Qual é o resumo atual de {display_name}?",f"Quais riscos exigem atenção em {display_name}?",f"O que mudou recentemente em {display_name}?"],
        "capabilities":[f"{domain_id}.read"],"version":"1.0.0"}


class DeclarativeDomainCatalog:
    def ensure_schema(self) -> None:
        with postgres_store._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS domain_installations (
                domain_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, description TEXT NOT NULL,
                purpose TEXT NOT NULL, manifest JSONB NOT NULL, status TEXT NOT NULL DEFAULT 'ready',
                enabled BOOLEAN NOT NULL DEFAULT TRUE, created_by BIGINT REFERENCES auth_users(id),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            conn.commit()

    @staticmethod
    def _manifest(payload: dict[str, Any]) -> dict[str, Any]:
        domain_id=str(payload.get("domain_id") or "").strip().lower()
        if not DOMAIN_ID.fullmatch(domain_id) or domain_id in RESERVED:raise ValueError("Identificador inválido ou reservado; use letras minúsculas, números e hífen.")
        entities=sorted({str(item).strip() for item in payload.get("entities",[]) if str(item).strip()})
        metrics=sorted({str(item).strip() for item in payload.get("metrics",[]) if str(item).strip()})
        source_url=str(payload.get("source_url") or "").strip();source=None
        if source_url:
            parsed=urlparse(source_url)
            if parsed.scheme not in {"http","https"} or not parsed.hostname:raise ValueError("A fonte deve usar uma URL HTTP ou HTTPS válida.")
            source={"name":f"{domain_id}-primary","label":f"{payload.get('display_name')} · fonte principal","url":source_url,"allowed_domains":[parsed.hostname],"refresh_seconds":max(3600,int(payload.get("refresh_seconds") or 86400)),"enabled":True,"metadata":{"domain_id":domain_id,"collection":f"{domain_id}.knowledge"}}
        display_name=str(payload.get("display_name") or "").strip();purpose=str(payload.get("purpose") or "").strip();theme_key=str(payload.get("theme") or "ocean")
        if theme_key not in THEMES:raise ValueError("Tema visual inválido.")
        return {"domain_id":domain_id,"version":"1.0.0","display_name":display_name,"description":str(payload.get("description") or "").strip(),"purpose":purpose,"entities":entities,"metrics":metrics,"source":source,"experience":_experience(domain_id,display_name,purpose,entities,metrics,theme_key),"permissions":[f"{domain_id}.read",f"{domain_id}.manage"],"role_grants":{"user":[f"{domain_id}.read"],"analyst":[f"{domain_id}.read"],"operator":[f"{domain_id}.read"],"admin":[f"{domain_id}.read",f"{domain_id}.manage"]},"knowledge_collection":{"id":f"{domain_id}.knowledge","types":["documentation","runbook","policy","dataset"]},"routes":{"status":f"/domains/{domain_id}/status","search":f"/domains/{domain_id}/search","manifest":f"/domains/{domain_id}"},"health_checks":["manifest","knowledge_source"]}

    def install(self,payload:dict[str,Any],user_id:int)->dict[str,Any]:
        self.ensure_schema();manifest=self._manifest(payload)
        if not manifest["display_name"] or not manifest["purpose"]:raise ValueError("Nome e objetivo do domínio são obrigatórios.")
        source_status="waiting_for_documents"
        if manifest["source"]:register_knowledge_source(manifest["source"]);source_status="source_registered"
        manifest["provisioning"]={"manifest":"ready","routes":"ready","permissions":"ready","knowledge":source_status,"health":"ready"}
        with postgres_store._connect() as conn:
            exists=conn.execute("SELECT 1 FROM domain_installations WHERE domain_id=%s",(manifest["domain_id"],)).fetchone()
            if exists:raise ValueError("Já existe um domínio com esse identificador.")
            conn.execute("INSERT INTO domain_installations(domain_id,display_name,description,purpose,manifest,created_by) VALUES(%s,%s,%s,%s,%s,%s)",(manifest["domain_id"],manifest["display_name"],manifest["description"],manifest["purpose"],Jsonb(manifest),user_id));conn.commit()
        return {"status":"ready","domain":manifest}

    def list(self)->list[dict[str,Any]]:
        self.ensure_schema()
        with postgres_store._connect() as conn:rows=conn.execute("SELECT manifest,status,enabled,created_at FROM domain_installations ORDER BY display_name").fetchall()
        return [{**manifest,"status":status,"enabled":enabled,"created_at":created_at.isoformat()} for manifest,status,enabled,created_at in rows]

    def get(self,domain_id:str)->dict[str,Any]|None:
        self.ensure_schema()
        with postgres_store._connect() as conn:row=conn.execute("SELECT manifest,status,enabled,created_at FROM domain_installations WHERE domain_id=%s",(domain_id,)).fetchone()
        return {**row[0],"status":row[1],"enabled":row[2],"created_at":row[3].isoformat()} if row else None

    def set_enabled(self,domain_id:str,enabled:bool)->bool:
        self.ensure_schema()
        with postgres_store._connect() as conn:row=conn.execute("UPDATE domain_installations SET enabled=%s,updated_at=NOW() WHERE domain_id=%s RETURNING domain_id",(enabled,domain_id)).fetchone();conn.commit()
        return bool(row)

    def search(self,domain_id:str,query:str)->dict[str,Any]:
        manifest=self.get(domain_id)
        if not manifest or not manifest.get("enabled"):raise KeyError(domain_id)
        result=search_knowledge(f"{manifest['display_name']} {query}")
        source_name=(manifest.get("source") or {}).get("name")
        matches=[item for item in result.get("results",[]) if not source_name or source_name in str(item.get("source",''))]
        return {"domain_id":domain_id,"query":query,"results":matches,"status":"ready" if matches else "no_domain_evidence"}

    def experiences(self)->list[dict[str,Any]]:
        infrastructure=_experience("infrastructure","Infraestrutura","Monitorar disponibilidade, capacidade e riscos operacionais.",["host","incidente","interface"],["saúde","disponibilidade","severidade"],"ocean")
        infrastructure["capabilities"]=["infrastructure.summary.read"]
        installed=[item.get("experience") or _experience(item["domain_id"],item["display_name"],item["purpose"],item.get("entities",[]),item.get("metrics",[]),"ocean") for item in self.list() if item.get("enabled")]
        return [infrastructure,*installed]


declarative_domain_catalog=DeclarativeDomainCatalog()
