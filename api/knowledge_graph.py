"""Evidence graph derived from document artifacts.

The graph stores concepts, entities and cross-document relations with source
provenance. It is an evidence graph, not a causal or predictive model.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .expansion import ExpansionStore
from .ingestion import extract_text, files_for
from .knowledge_builder import build_artifacts


def _json(value: Any, fallback: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    try:
        decoded = json.loads(str(value))
        return decoded if isinstance(decoded, type(fallback)) else fallback
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


def _graph_path(root: Path, module_id: str) -> Path:
    return root.parent / "data" / "knowledge-graph" / f"{module_id}.json"


def build_graph(root: Path, module_id: str, max_nodes: int = 5000) -> dict[str, Any]:
    documents = ExpansionStore(root).pipeline_documents(module_id, limit=5000)
    # Older knowledge already present before the observable pipeline was
    # introduced must still be represented. Build metadata in memory for
    # those files; the canonical document record remains created by ingestion.
    known_files = {str(item.get("file_name", "")) for item in documents}
    for path in files_for(root, module_id):
        if path.name in known_files:
            continue
        try:
            text = extract_text(path)
            if len(text.strip()) < 20:
                continue
            artifacts = build_artifacts(path, text, module_id)
            documents.append(
                {
                    "file_name": path.name,
                    "artifacts": {
                        f"{key}_json": json.dumps(artifacts.get(key, []), ensure_ascii=False)
                        for key in ("concepts", "entities", "topics", "relations")
                    },
                }
            )
        except (OSError, RuntimeError, ValueError, TypeError):
            continue
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str], dict[str, Any]] = {}
    concept_documents: defaultdict[str, set[str]] = defaultdict(set)
    concept_frequency: Counter[str] = Counter()

    def node(node_id: str, label: str, kind: str, source: str | None = None) -> None:
        if len(nodes) >= max_nodes and node_id not in nodes:
            return
        item = nodes.setdefault(node_id, {"id": node_id, "label": label[:160], "kind": kind, "sources": []})
        if source and source not in item["sources"]:
            item["sources"].append(source)

    def edge(source: str, target: str, relation: str, confidence: float = 0.6, provenance: str | None = None) -> None:
        key = (source, target, relation)
        item = edges.setdefault(key, {"source": source, "target": target, "relation": relation, "confidence": confidence, "provenance": []})
        if provenance and provenance not in item["provenance"]:
            item["provenance"].append(provenance)
        item["confidence"] = max(float(item["confidence"]), confidence)

    for document in documents:
        source = str(document.get("file_name", "documento"))
        document_node = f"document:{source}"
        node(document_node, source, "document", source)
        artifacts = document.get("artifacts") or {}
        concepts = [str(value) for value in _json(artifacts.get("concepts_json"), []) if str(value).strip()]
        entities = [str(value) for value in _json(artifacts.get("entities_json"), []) if str(value).strip()]
        topics = [str(value) for value in _json(artifacts.get("topics_json"), concepts) if str(value).strip()]
        for concept in dict.fromkeys([*concepts, *topics]):
            key = re.sub(r"[^a-z0-9_-]+", "-", concept.casefold()).strip("-") or "concept"
            concept_node = f"concept:{key}"
            node(concept_node, concept, "concept", source)
            edge(document_node, concept_node, "supported_by", 0.8, source)
            concept_documents[key].add(source)
            concept_frequency[key] += 1
        for entity in dict.fromkeys(entities):
            key = re.sub(r"[^a-z0-9_-]+", "-", entity.casefold()).strip("-") or "entity"
            entity_node = f"entity:{key}"
            node(entity_node, entity, "entity", source)
            edge(document_node, entity_node, "mentions", 0.7, source)
        for relation in _json(artifacts.get("relations_json"), []):
            if not isinstance(relation, dict):
                continue
            left = str(relation.get("from", "")).strip()
            right = str(relation.get("to", "")).strip()
            if not left or not right:
                continue
            left_key = re.sub(r"[^a-z0-9_-]+", "-", left.casefold()).strip("-")
            right_key = re.sub(r"[^a-z0-9_-]+", "-", right.casefold()).strip("-")
            edge(f"concept:{left_key}", f"concept:{right_key}", str(relation.get("type", "related_to")), float(relation.get("confidence", 0.6) or 0.6), source)

    # A cross-document edge is stronger than mere co-occurrence inside one
    # chunk, but it remains an observed relation and is never presented as
    # causality.
    keys = sorted(concept_documents)
    for index, left in enumerate(keys):
        for right in keys[index + 1 :]:
            overlap = len(concept_documents[left] & concept_documents[right])
            if overlap:
                edge(f"concept:{left}", f"concept:{right}", "cross_document_relation", min(0.95, 0.55 + overlap * 0.08), f"{overlap} documento(s) compartilhado(s)")

    payload = {
        "module_id": module_id,
        "generated_at": datetime.now(UTC).isoformat(),
        "document_count": len(documents),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
        "concept_frequency": dict(concept_frequency.most_common(100)),
        "meaning": "Relações observadas em artefatos documentais; não representam causalidade nem recomendação automática.",
    }
    destination = _graph_path(root, module_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(destination)
    return payload


def graph_status(root: Path, module_id: str) -> dict[str, Any]:
    path = _graph_path(root, module_id)
    if not path.exists():
        return {"module_id": module_id, "status": "pending", "node_count": 0, "edge_count": 0, "path": str(path)}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {"module_id": module_id, "status": "ready", "node_count": payload.get("node_count", 0), "edge_count": payload.get("edge_count", 0), "generated_at": payload.get("generated_at"), "path": str(path)}
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"module_id": module_id, "status": "failed", "node_count": 0, "edge_count": 0, "error": str(exc)[:240], "path": str(path)}


def read_graph(root: Path, module_id: str) -> dict[str, Any]:
    path = _graph_path(root, module_id)
    if not path.exists():
        return build_graph(root, module_id)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return build_graph(root, module_id)
