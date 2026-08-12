from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from psycopg.types.json import Jsonb

from core.domain_intelligence import DomainEvent, domain_provider_registry
from domains.infrastructure.intelligence import infrastructure_intelligence_provider
from services.postgres_store import postgres_store


WINDOWS = {value: value for value in (15, 30, 60, 120, 240, 360, 720, 1440, 10080)}
domain_provider_registry.register(infrastructure_intelligence_provider)


class TemporalIntelligence:
    def ensure_schema(self) -> None:
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

    def _save_event(self, conn: Any, *, domain_id: str, key: str, event_type: str, title: str,
                    summary: str, at: datetime, level: str = "observed", confidence: float = 1,
                    source: str = "domain.snapshot", entities: list[dict[str, Any]] | None = None,
                    evidence: dict[str, Any] | None = None) -> int:
        row = conn.execute("""INSERT INTO domain_events(domain_id,external_key,event_type,title,summary,occurred_at,evidence_level,confidence,source,entities,evidence)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(domain_id,external_key) DO UPDATE
            SET title=EXCLUDED.title,summary=EXCLUDED.summary,evidence=EXCLUDED.evidence RETURNING id""",
            (domain_id, key, event_type, title, summary, at, level, confidence, source, Jsonb(entities or []), Jsonb(evidence or {}))).fetchone()
        return int(row[0])

    @staticmethod
    def _entities(event: DomainEvent) -> list[dict[str, Any]]:
        return [{"type": item.type, "id": item.id, "label": item.label, "parent_id": item.parent_id,
                 "topology": list(item.topology), "attributes": item.attributes} for item in event.entities]

    def ingest_snapshots(self, domain_id: str, minutes: int) -> int:
        self.ensure_schema()
        provider = domain_provider_registry.get(domain_id)
        if provider is None:
            return 0
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        with postgres_store._connect() as conn:
            rows = conn.execute("SELECT id,generated_at,summary,payload FROM domain_snapshots WHERE domain_id=%s AND generated_at>=%s ORDER BY generated_at", (domain_id, since)).fetchall()
            previous: dict[str, DomainEvent] | None = None
            count = 0
            for snapshot_id, at, _summary, payload in rows:
                current = {item.external_key: item for item in provider.events_from_snapshot(snapshot_id, at, payload or {})}
                if previous is not None:
                    for key in current.keys() - previous.keys():
                        item = current[key]
                        self._save_event(conn, domain_id=domain_id, key=key, event_type=item.event_type,
                                         title=item.title, summary=item.summary, at=item.occurred_at,
                                         confidence=item.confidence, source=item.source,
                                         entities=self._entities(item), evidence=item.evidence)
                        count += 1
                    for key in previous.keys() - current.keys():
                        item = previous[key]
                        self._save_event(conn, domain_id=domain_id, key=f"snapshot:{snapshot_id}:resolved:{key}",
                                         event_type=f"{item.event_type}.resolved", title=f"Resolvido: {item.title}",
                                         summary="A fonte deixou de reportar o evento.", at=at, source=item.source,
                                         entities=self._entities(item), evidence={"snapshot_id": snapshot_id, "previous_event": key})
                        count += 1
                previous = current
            conn.commit()
        self.correlate(domain_id, minutes)
        return count

    def correlate(self, domain_id: str, minutes: int) -> None:
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        with postgres_store._connect() as conn:
            rows = conn.execute("SELECT id,event_type,title,occurred_at,entities FROM domain_events WHERE domain_id=%s AND occurred_at>=%s ORDER BY occurred_at", (domain_id, since)).fetchall()
            for index, current in enumerate(rows):
                current_items = current[4] or []
                current_entities = {f"{item.get('type')}:{item.get('id')}" for item in current_items}
                for following in rows[index + 1:index + 15]:
                    delta = (following[3] - current[3]).total_seconds()
                    if delta > 300:
                        break
                    following_items = following[4] or []
                    following_entities = {f"{item.get('type')}:{item.get('id')}" for item in following_items}
                    layers = [("temporal", max(.45, .9 - delta / 600), f"Eventos separados por {int(delta)} segundos.")]
                    shared = current_entities & following_entities
                    if shared:
                        layers.append(("same_entity", .95, f"Compartilham {len(shared)} entidade(s)."))
                    topology_a = {v for item in current_items for v in item.get("topology", [])}
                    topology_b = {v for item in following_items for v in item.get("topology", [])}
                    if topology_a & topology_b:
                        layers.append(("topological", .85, "Compartilham vínculo topológico observado."))
                    parents_a = {item.get("parent_id") for item in current_items if item.get("parent_id")}
                    parents_b = {item.get("parent_id") for item in following_items if item.get("parent_id")}
                    if parents_a & parents_b:
                        layers.append(("hierarchical", .82, "Pertencem ao mesmo agrupamento hierárquico."))
                    if current[1] == following[1]:
                        layers.append(("behavioral", .70, "O comportamento se repetiu na janela analisada."))
                    for relation_type, confidence, rationale in layers:
                        conn.execute("""INSERT INTO domain_event_relations(domain_id,from_event_id,to_event_id,relation_type,evidence_level,confidence,rationale)
                            VALUES(%s,%s,%s,%s,'correlated',%s,%s) ON CONFLICT DO NOTHING""",
                            (domain_id, current[0], following[0], relation_type, confidence, rationale))
            conn.commit()

    def story(self, domain_id: str, window: int) -> dict[str, Any]:
        minutes = WINDOWS.get(window, 60)
        self.ingest_snapshots(domain_id, minutes)
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        with postgres_store._connect() as conn:
            rows = conn.execute("SELECT id,event_type,title,summary,occurred_at,evidence_level,confidence,source,entities,evidence FROM domain_events WHERE domain_id=%s AND occurred_at>=%s ORDER BY occurred_at", (domain_id, since)).fetchall()
            relation_rows = conn.execute("SELECT from_event_id,to_event_id,relation_type,evidence_level,confidence,rationale FROM domain_event_relations WHERE domain_id=%s AND created_at>=%s ORDER BY created_at", (domain_id, since)).fetchall()
        events = [{"id": r[0], "type": r[1], "title": r[2], "summary": r[3], "at": r[4].isoformat(), "level": r[5], "confidence": r[6], "source": r[7], "entities": r[8], "evidence": r[9]} for r in rows]
        episodes: list[dict[str, Any]] = []
        for event in events:
            at = datetime.fromisoformat(event["at"])
            if not episodes or (at - datetime.fromisoformat(episodes[-1]["ended_at"])).total_seconds() > 300:
                episodes.append({"started_at": event["at"], "ended_at": event["at"], "events": [event]})
            else:
                episodes[-1]["events"].append(event); episodes[-1]["ended_at"] = event["at"]
        for episode in episodes:
            affected = {item.get("label") for event in episode["events"] for item in event.get("entities", []) if item.get("label")}
            episode.update({"affected_entities": sorted(affected), "title": f"{len(episode['events'])} mudança(s) relacionada(s)", "summary": f"{len(affected)} entidade(s) nesta sequência."})
        relations = [{"from": r[0], "to": r[1], "type": r[2], "level": r[3], "confidence": r[4], "rationale": r[5]} for r in relation_rows]
        return {"domain_id": domain_id, "window_minutes": minutes, "generated_at": datetime.now(timezone.utc).isoformat(), "events": events, "relations": relations, "episodes": episodes, "counts": {"events": len(events), "episodes": len(episodes), "relations": len(relations)}, "legend": {"observed": "Confirmado pela fonte", "correlated": "Relação calculada", "inferred": "Hipótese não confirmada", "learned": "Padrão recorrente confirmado"}}


temporal_intelligence = TemporalIntelligence()
