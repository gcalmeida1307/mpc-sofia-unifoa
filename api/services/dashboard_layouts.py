from __future__ import annotations

from copy import deepcopy
from typing import Any

from psycopg.types.json import Jsonb

from services.postgres_store import postgres_store


WIDGET_CATALOG={
    "health":{"label":"Saúde geral","description":"Pontuação, tendência e comparação.","sizes":["small","medium"]},
    "changes":{"label":"Mudanças recentes","description":"Alertas novos, resolvidos e críticos.","sizes":["medium","large"]},
    "domains":{"label":"Saúde por área","description":"Comparação dos domínios monitorados.","sizes":["medium","large"]},
    "history":{"label":"Evolução da saúde","description":"Série das últimas doze horas.","sizes":["medium","large"]},
    "risks":{"label":"Principais riscos","description":"Ranking de riscos e confiança.","sizes":["medium","large"]},
    "patterns":{"label":"Padrões aprendidos","description":"Rotinas recorrentes comprovadas.","sizes":["medium","large"]},
    "devices":{"label":"Dispositivos monitorados","description":"Total e mudança na última leitura.","sizes":["small","medium"]},
}
DEFAULT_LAYOUT={"pages":[]}


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
                widgets.append({"id":widget_id,"type":widget_type,"size":size,"title":str(widget.get("title") or WIDGET_CATALOG[widget_type]["label"])[:80]})
            normalized.append({"id":page_id,"name":str(page.get("name") or f"Página {page_index+1}")[:60],"widgets":widgets})
        return {"pages":normalized}

    def get(self,user_id:int)->dict[str,Any]:
        self.ensure_schema()
        with postgres_store._connect() as conn:row=conn.execute("SELECT layout,updated_at FROM user_dashboard_layouts WHERE user_id=%s",(user_id,)).fetchone()
        return {"layout":deepcopy(row[0] if row else DEFAULT_LAYOUT),"updated_at":row[1].isoformat() if row else None,"catalog":WIDGET_CATALOG}

    def save(self,user_id:int,layout:dict[str,Any])->dict[str,Any]:
        self.ensure_schema();normalized=self.validate(layout)
        with postgres_store._connect() as conn:row=conn.execute("""INSERT INTO user_dashboard_layouts(user_id,layout) VALUES(%s,%s)
            ON CONFLICT(user_id) DO UPDATE SET layout=EXCLUDED.layout,updated_at=NOW() RETURNING updated_at""",(user_id,Jsonb(normalized))).fetchone();conn.commit()
        return {"layout":normalized,"updated_at":row[0].isoformat(),"catalog":WIDGET_CATALOG}


dashboard_layout_store=DashboardLayoutStore()
