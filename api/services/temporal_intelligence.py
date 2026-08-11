from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from psycopg.types.json import Jsonb

from services.postgres_store import postgres_store


WINDOWS={15:15,30:30,60:60,120:120,240:240,360:360,720:720,1440:1440,10080:10080}


class TemporalIntelligence:
    def ensure_schema(self)->None:
        with postgres_store._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS domain_events (
                id BIGSERIAL PRIMARY KEY, domain_id TEXT NOT NULL, external_key TEXT NOT NULL,
                event_type TEXT NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '',
                occurred_at TIMESTAMPTZ NOT NULL, ended_at TIMESTAMPTZ, evidence_level TEXT NOT NULL
                CHECK(evidence_level IN ('observed','correlated','inferred','learned')),
                confidence DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK(confidence>=0 AND confidence<=1),
                source TEXT NOT NULL, entities JSONB NOT NULL DEFAULT '[]'::jsonb,
                evidence JSONB NOT NULL DEFAULT '{}'::jsonb, metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(domain_id,external_key))""")
            conn.execute("""CREATE TABLE IF NOT EXISTS domain_event_relations (
                id BIGSERIAL PRIMARY KEY, domain_id TEXT NOT NULL, from_event_id BIGINT NOT NULL REFERENCES domain_events(id) ON DELETE CASCADE,
                to_event_id BIGINT NOT NULL REFERENCES domain_events(id) ON DELETE CASCADE, relation_type TEXT NOT NULL,
                evidence_level TEXT NOT NULL CHECK(evidence_level IN ('correlated','inferred','learned')),
                confidence DOUBLE PRECISION NOT NULL CHECK(confidence>=0 AND confidence<=1), rationale TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE(from_event_id,to_event_id,relation_type))""")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain_events_window ON domain_events(domain_id,occurred_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_domain_relations_domain ON domain_event_relations(domain_id,created_at DESC)")
            conn.commit()

    @staticmethod
    def _problem_map(payload:dict[str,Any])->dict[str,dict[str,Any]]:
        problems=((payload or {}).get("zabbix") or {}).get("problems",[]) or []
        return {str(item.get("eventid")):item for item in problems if item.get("eventid")}

    def _save_event(self,conn:Any,*,domain_id:str,key:str,event_type:str,title:str,summary:str,at:datetime,level:str="observed",confidence:float=1,source:str="domain.snapshot",entities:list[dict[str,Any]]|None=None,evidence:dict[str,Any]|None=None)->int:
        row=conn.execute("""INSERT INTO domain_events(domain_id,external_key,event_type,title,summary,occurred_at,evidence_level,confidence,source,entities,evidence)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(domain_id,external_key) DO UPDATE SET title=EXCLUDED.title,summary=EXCLUDED.summary,evidence=EXCLUDED.evidence RETURNING id""",
            (domain_id,key,event_type,title,summary,at,level,confidence,source,Jsonb(entities or []),Jsonb(evidence or {}))).fetchone()
        return int(row[0])

    def ingest_snapshots(self,domain_id:str,minutes:int)->int:
        self.ensure_schema();since=datetime.now(timezone.utc)-timedelta(minutes=minutes)
        with postgres_store._connect() as conn:
            rows=conn.execute("SELECT id,generated_at,summary,payload FROM domain_snapshots WHERE domain_id=%s AND generated_at>=%s ORDER BY generated_at",(domain_id,since)).fetchall()
            previous:dict[str,dict[str,Any]]|None=None;count=0
            for snapshot_id,at,summary,payload in rows:
                current=self._problem_map(payload or {})
                if previous is not None:
                    for event_id in current.keys()-previous.keys():
                        item=current[event_id];hosts=item.get("hosts") or [];groups=item.get("groups") or []
                        entities=[{"type":"host","id":str(host),"label":str(host)} for host in hosts]+[{"type":"group","id":str(group),"label":str(group)} for group in groups]
                        self._save_event(conn,domain_id=domain_id,key=f"snapshot:{snapshot_id}:started:{event_id}",event_type="problem.started",title=str(item.get("name") or "Ocorrência iniciada"),summary=f"Ocorrência observada em {', '.join(map(str,hosts[:3])) or 'entidade não identificada'}.",at=at,entities=entities,evidence={"snapshot_id":snapshot_id,"event_id":event_id,"severity":item.get("severity_label") or item.get("severity")});count+=1
                    for event_id in previous.keys()-current.keys():
                        item=previous[event_id];hosts=item.get("hosts") or [];groups=item.get("groups") or []
                        entities=[{"type":"host","id":str(host),"label":str(host)} for host in hosts]+[{"type":"group","id":str(group),"label":str(group)} for group in groups]
                        self._save_event(conn,domain_id=domain_id,key=f"snapshot:{snapshot_id}:resolved:{event_id}",event_type="problem.resolved",title=str(item.get("name") or "Ocorrência resolvida"),summary=f"A fonte deixou de reportar a ocorrência em {', '.join(map(str,hosts[:3])) or 'entidade não identificada'}.",at=at,entities=entities,evidence={"snapshot_id":snapshot_id,"event_id":event_id});count+=1
                previous=current
            conn.commit()
        self.correlate(domain_id,minutes);return count

    def correlate(self,domain_id:str,minutes:int)->None:
        since=datetime.now(timezone.utc)-timedelta(minutes=minutes)
        with postgres_store._connect() as conn:
            rows=conn.execute("SELECT id,event_type,title,occurred_at,entities FROM domain_events WHERE domain_id=%s AND occurred_at>=%s ORDER BY occurred_at",(domain_id,since)).fetchall()
            for index,current in enumerate(rows):
                current_entities={f"{item.get('type')}:{item.get('id')}" for item in (current[4] or [])}
                for following in rows[index+1:index+15]:
                    delta=(following[3]-current[3]).total_seconds()
                    if delta>120:break
                    following_entities={f"{item.get('type')}:{item.get('id')}" for item in (following[4] or [])};shared=current_entities&following_entities
                    if shared:
                        conn.execute("""INSERT INTO domain_event_relations(domain_id,from_event_id,to_event_id,relation_type,evidence_level,confidence,rationale)
                            VALUES(%s,%s,%s,'same_entity_sequence','correlated',0.95,%s) ON CONFLICT DO NOTHING""",(domain_id,current[0],following[0],f"Eventos ocorreram em até {int(delta)} segundos e compartilham {len(shared)} entidade(s)."))
            conn.commit()

    def story(self,domain_id:str,window:int)->dict[str,Any]:
        minutes=WINDOWS.get(window,60);self.ingest_snapshots(domain_id,minutes);since=datetime.now(timezone.utc)-timedelta(minutes=minutes)
        with postgres_store._connect() as conn:
            rows=conn.execute("""SELECT id,event_type,title,summary,occurred_at,evidence_level,confidence,source,entities,evidence
                FROM domain_events WHERE domain_id=%s AND occurred_at>=%s ORDER BY occurred_at""",(domain_id,since)).fetchall()
            relation_rows=conn.execute("""SELECT from_event_id,to_event_id,relation_type,evidence_level,confidence,rationale FROM domain_event_relations
                WHERE domain_id=%s AND created_at>=%s ORDER BY created_at""",(domain_id,since)).fetchall()
        events=[{"id":row[0],"type":row[1],"title":row[2],"summary":row[3],"at":row[4].isoformat(),"level":row[5],"confidence":row[6],"source":row[7],"entities":row[8],"evidence":row[9]} for row in rows]
        episodes=[]
        for event in events:
            at=datetime.fromisoformat(event["at"])
            if not episodes or (at-datetime.fromisoformat(episodes[-1]["ended_at"])).total_seconds()>300:episodes.append({"started_at":event["at"],"ended_at":event["at"],"events":[event]})
            else:episodes[-1]["events"].append(event);episodes[-1]["ended_at"]=event["at"]
        for episode in episodes:
            affected={item.get("label") for event in episode["events"] for item in event.get("entities",[]) if item.get("label")};episode["affected_entities"]=sorted(affected);episode["title"]=f"{len(episode['events'])} mudança(s) relacionada(s)";episode["summary"]=f"{len(affected)} entidade(s) apareceram nesta sequência temporal."
        relations=[{"from":row[0],"to":row[1],"type":row[2],"level":row[3],"confidence":row[4],"rationale":row[5]} for row in relation_rows]
        return {"domain_id":domain_id,"window_minutes":minutes,"generated_at":datetime.now(timezone.utc).isoformat(),"events":events,"relations":relations,"episodes":episodes,"counts":{"events":len(events),"episodes":len(episodes),"relations":len(relations)},"legend":{"observed":"Confirmado pela fonte","correlated":"Relação calculada","inferred":"Hipótese não confirmada","learned":"Padrão recorrente confirmado"}}


temporal_intelligence=TemporalIntelligence()
