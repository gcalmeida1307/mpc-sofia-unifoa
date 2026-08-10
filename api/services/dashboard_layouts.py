from __future__ import annotations

from copy import deepcopy
from typing import Any

from psycopg.types.json import Jsonb

from services.postgres_store import postgres_store


WIDGET_CATALOG={
    "metric":{"label":"Indicador","description":"Um número principal com contexto.","sizes":["small","medium"]},
    "bar":{"label":"Gráfico de barras","description":"Compara categorias ou áreas.","sizes":["medium","large"]},
    "line":{"label":"Gráfico de linha","description":"Mostra evolução ao longo do tempo.","sizes":["medium","large"]},
    "donut":{"label":"Gráfico de rosca","description":"Mostra distribuição e proporções.","sizes":["small","medium"]},
    "table":{"label":"Tabela","description":"Detalhes organizados em linhas e colunas.","sizes":["medium","large"]},
    "list":{"label":"Lista priorizada","description":"Itens, riscos ou recomendações.","sizes":["medium","large"]},
    "text":{"label":"Texto e orientação","description":"Título, contexto ou instruções da página.","sizes":["small","medium","large"]},
}
DATA_SOURCES={
    "overview":{"label":"Resumo da plataforma"},
    "domains":{"label":"Áreas e módulos"},
    "changes":{"label":"Mudanças recentes"},
    "history":{"label":"Histórico"},
    "risks":{"label":"Riscos e prioridades"},
    "patterns":{"label":"Padrões aprendidos"},
}
DEFAULT_LAYOUT={"pages":[{"id":"dashboard","name":"Dashboard","widgets":[
    {"id":"welcome","type":"text","source":"overview","size":"large","title":"Meu espaço de análise"},
    {"id":"overview","type":"metric","source":"overview","size":"small","title":"Visão geral"},
    {"id":"domains","type":"bar","source":"domains","size":"medium","title":"Áreas acompanhadas"},
    {"id":"changes","type":"table","source":"changes","size":"medium","title":"Últimas mudanças"},
]}]}


class DashboardLayoutStore:
    def ensure_schema(self)->None:
        with postgres_store._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS user_dashboard_layouts (
                user_id BIGINT PRIMARY KEY REFERENCES auth_users(id) ON DELETE CASCADE,
                layout JSONB NOT NULL DEFAULT '{\"pages\":[]}'::jsonb,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())""");conn.commit()

    @staticmethod
    def validate(layout:dict[str,Any])->dict[str,Any]:
        pages=layout.get("pages") if isinstance(layout,dict) else None
        if not isinstance(pages,list) or len(pages)>10:raise ValueError("O painel deve possuir no máximo 10 páginas.")
        normalized=[];page_ids=set()
        for page_index,page in enumerate(pages):
            if not isinstance(page,dict):raise ValueError("Página inválida.")
            page_id=str(page.get("id") or f"page-{page_index+1}")[:50]
            if page_id in page_ids:raise ValueError("Identificador de página duplicado.")
            page_ids.add(page_id);widgets=[];widget_ids=set()
            source_widgets=page.get("widgets") or []
            if not isinstance(source_widgets,list) or len(source_widgets)>30:raise ValueError("Cada página aceita no máximo 30 widgets.")
            for index,widget in enumerate(source_widgets):
                widget_type=str(widget.get("type") or "")
                if widget_type not in WIDGET_CATALOG:raise ValueError(f"Widget não autorizado: {widget_type}")
                widget_id=str(widget.get("id") or f"{page_id}-{index+1}")[:70]
                if widget_id in widget_ids:raise ValueError("Identificador de widget duplicado.")
                widget_ids.add(widget_id);allowed=WIDGET_CATALOG[widget_type]["sizes"];size=str(widget.get("size") or allowed[0])
                if size not in allowed:size=allowed[0]
                source=str(widget.get("source") or "overview")
                if source not in DATA_SOURCES:raise ValueError(f"Fonte não autorizada: {source}")
                widgets.append({"id":widget_id,"type":widget_type,"source":source,"size":size,"title":str(widget.get("title") or WIDGET_CATALOG[widget_type]["label"])[:80]})
            normalized.append({"id":page_id,"name":str(page.get("name") or f"Página {page_index+1}")[:60],"widgets":widgets})
        return {"pages":normalized}

    def get(self,user_id:int)->dict[str,Any]:
        self.ensure_schema()
        with postgres_store._connect() as conn:row=conn.execute("SELECT layout,updated_at FROM user_dashboard_layouts WHERE user_id=%s",(user_id,)).fetchone()
        raw=deepcopy(row[0] if row else DEFAULT_LAYOUT)
        legacy={"health":("metric","overview"),"devices":("metric","overview"),"changes":("table","changes"),"domains":("bar","domains"),"history":("line","history"),"risks":("list","risks"),"patterns":("list","patterns")}
        for page in raw.get("pages",[]):
            for widget in page.get("widgets",[]):
                if widget.get("type") in legacy:widget["type"],widget["source"]=legacy[widget["type"]]
                widget.setdefault("source","overview")
        return {"layout":raw,"updated_at":row[1].isoformat() if row else None,"catalog":WIDGET_CATALOG,"sources":DATA_SOURCES}

    def save(self,user_id:int,layout:dict[str,Any])->dict[str,Any]:
        self.ensure_schema();normalized=self.validate(layout)
        with postgres_store._connect() as conn:row=conn.execute("""INSERT INTO user_dashboard_layouts(user_id,layout) VALUES(%s,%s)
            ON CONFLICT(user_id) DO UPDATE SET layout=EXCLUDED.layout,updated_at=NOW() RETURNING updated_at""",(user_id,Jsonb(normalized))).fetchone();conn.commit()
        return {"layout":normalized,"updated_at":row[0].isoformat(),"catalog":WIDGET_CATALOG,"sources":DATA_SOURCES}


dashboard_layout_store=DashboardLayoutStore()
