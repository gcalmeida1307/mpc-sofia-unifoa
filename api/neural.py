from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from .ingestion import files_for, ingest_module

ARCHITECTURE = [3, 4, 3]
SEMANTIC_STOPWORDS = {
    "para", "como", "sobre", "entre", "esta", "esse", "essa", "isso", "mais", "menos", "muito", "muita", "pelo", "pela", "pelos", "pelas", "quando", "onde", "qual", "quais", "uma", "umas", "uns", "dos", "das", "que", "com", "sem", "por", "nos", "nas", "aos", "aquelas", "aquele", "tambem", "sao", "ser", "tem", "sua", "seu", "suas", "seus", "the", "and", "for", "with", "from", "this", "that", "are",
}


def _model_path(root: Path, module_id: str) -> Path:
    return root.parent / "data" / "neural" / f"{module_id}.json"


def _dataset(root: Path, module_id: str) -> np.ndarray:
    chunks = ingest_module(root, module_id)
    if not chunks:
        raise ValueError(f"O módulo {module_id} não possui documentos para treinamento")
    raw: list[list[float]] = []
    for chunk in chunks:
        text = chunk.text
        words = re.findall(r"\w+", text, flags=re.UNICODE)
        chars = max(1, len(text))
        raw.append([float(len(text)), float(len(words)), sum(char.isdigit() for char in text) / chars])
    values = np.asarray(raw, dtype=float)
    minimum = values.min(axis=0)
    scale = values.max(axis=0) - minimum
    scale[scale == 0] = 1.0
    return np.clip((values - minimum) / scale, 0.0, 1.0)


def _seed(module_id: str) -> int:
    return int(hashlib.sha256(module_id.encode()).hexdigest()[:8], 16)


def _source_signature(root: Path, module_id: str) -> str:
    digest = hashlib.sha256()
    for path in files_for(root, module_id):
        try:
            stat = path.stat()
            digest.update(str(path.relative_to(root)).encode())
            digest.update(f":{stat.st_size}:{stat.st_mtime_ns}".encode())
        except OSError:
            continue
    return digest.hexdigest()


def _save(path: Path, weights: dict[str, np.ndarray], metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**metadata, "weights": {key: value.tolist() for key, value in weights.items()}}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _load(path: Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    weights = {key: np.asarray(value, dtype=float) for key, value in payload["weights"].items()}
    return weights, payload


def train(
    root: Path,
    module_id: str,
    epochs: int = 120,
    learning_rate: float = 0.08,
    trigger: str = "manual",
) -> dict[str, Any]:
    if not 1 <= epochs <= 2_000:
        raise ValueError("epochs deve estar entre 1 e 2.000")
    if not 0.0001 <= learning_rate <= 1:
        raise ValueError("learning_rate deve estar entre 0.0001 e 1")
    dataset = _dataset(root, module_id)
    path = _model_path(root, module_id)
    previous_round = 0
    weights: dict[str, np.ndarray]
    if path.exists():
        try:
            stored_weights, stored_metadata = _load(path)
            expected_shapes = {"w1": (3, 4), "b1": (4,), "w2": (4, 3), "b2": (3,)}
            if all(stored_weights.get(key, np.empty(0)).shape == shape for key, shape in expected_shapes.items()):
                # Continue from the existing model instead of resetting it on
                # every upload or negative-feedback event.
                weights = stored_weights
                previous_round = int(stored_metadata.get("training_round", 0) or 0)
            else:
                raise ValueError("arquitetura armazenada incompatível")
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            rng = np.random.default_rng(_seed(module_id))
            weights = {
                "w1": rng.normal(0, 0.35, (3, 4)),
                "b1": np.zeros(4),
                "w2": rng.normal(0, 0.35, (4, 3)),
                "b2": np.zeros(3),
            }
    else:
        rng = np.random.default_rng(_seed(module_id))
        weights = {
            "w1": rng.normal(0, 0.35, (3, 4)),
            "b1": np.zeros(4),
            "w2": rng.normal(0, 0.35, (4, 3)),
            "b2": np.zeros(3),
        }
    loss = 0.0
    for _ in range(epochs):
        hidden = np.tanh(dataset @ weights["w1"] + weights["b1"])
        prediction = hidden @ weights["w2"] + weights["b2"]
        error = prediction - dataset
        loss = float(np.mean(error * error))
        gradient_prediction = 2 * error / len(dataset)
        gradient_w2 = hidden.T @ gradient_prediction
        gradient_b2 = gradient_prediction.sum(axis=0)
        gradient_hidden = (gradient_prediction @ weights["w2"].T) * (1 - hidden * hidden)
        gradient_w1 = dataset.T @ gradient_hidden
        gradient_b1 = gradient_hidden.sum(axis=0)
        weights["w2"] -= learning_rate * gradient_w2
        weights["b2"] -= learning_rate * gradient_b2
        weights["w1"] -= learning_rate * gradient_w1
        weights["b1"] -= learning_rate * gradient_b1
    metadata = {
        "module_id": module_id,
        "architecture": ARCHITECTURE,
        "samples": len(dataset),
        "epochs": epochs,
        "learning_rate": learning_rate,
        "mse": round(loss, 8),
        "trained_at": datetime.now(UTC).isoformat(),
        "source_signature": _source_signature(root, module_id),
        "training": "autoencoder_reconstruction_from_knowledge_chunks",
        "training_round": previous_round + 1,
        "training_trigger": trigger,
    }
    _save(_model_path(root, module_id), weights, metadata)
    return {"trained": True, **metadata}


def status(root: Path, module_id: str) -> dict[str, Any]:
    path = _model_path(root, module_id)
    if not path.exists():
        return {"trained": False, "module_id": module_id, "architecture": ARCHITECTURE, "samples": 0}
    _, metadata = _load(path)
    current_signature = _source_signature(root, module_id)
    return metadata | {"trained": True, "stale": metadata.get("source_signature") != current_signature}


def infer(root: Path, module_id: str, values: list[float]) -> dict[str, Any]:
    if len(values) != 3:
        raise ValueError("A rede neural recebe exatamente 3 valores de entrada")
    path = _model_path(root, module_id)
    if not path.exists():
        raise ValueError(f"A rede do módulo {module_id} ainda não foi treinada")
    weights, metadata = _load(path)
    values_array = np.asarray(values, dtype=float)
    hidden = np.tanh(values_array @ weights["w1"] + weights["b1"])
    reconstruction = hidden @ weights["w2"] + weights["b2"]
    error = float(np.mean((reconstruction - values_array) ** 2))
    return {
        "module_id": module_id,
        "input": values_array.round(6).tolist(),
        "hidden": hidden.round(6).tolist(),
        "reconstruction": reconstruction.round(6).tolist(),
        "reconstruction_error": round(error, 8),
        "architecture": metadata.get("architecture", ARCHITECTURE),
        "trained_at": metadata.get("trained_at"),
        "trained": True,
    }


def _semantic_tokens(text: str) -> list[str]:
    normalized = "".join(char for char in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(char))
    return [token for token in re.findall(r"[a-zA-ZÀ-ÿ][\w-]+", normalized) if len(token) >= 4 and token not in SEMANTIC_STOPWORDS and not token.isnumeric()]


def graph(root: Path, module_id: str, max_concepts: int = 18, max_documents: int = 8) -> dict[str, Any]:
    """Return the learned network state plus a graph of concepts found in real chunks."""
    chunks = ingest_module(root, module_id)
    document_terms: dict[str, list[str]] = defaultdict(list)
    term_frequency: Counter[str] = Counter()
    term_documents: defaultdict[str, set[str]] = defaultdict(set)
    for chunk in chunks:
        document_id = chunk.path.name
        terms = _semantic_tokens(chunk.text)
        document_terms[document_id].extend(terms)
        term_frequency.update(terms)
        for term in set(terms):
            term_documents[term].add(document_id)

    concepts = [term for term, count in term_frequency.most_common() if count >= 2][:max_concepts]
    if not concepts:
        concepts = [term for term, _ in term_frequency.most_common(max_concepts)]
    documents = sorted(document_terms, key=lambda name: sum(term_frequency[term] for term in document_terms[name]), reverse=True)[:max_documents]
    nodes: list[dict[str, Any]] = []
    for index, document in enumerate(documents):
        y = 12 + (76 * index / max(1, len(documents) - 1))
        nodes.append({"id": f"document:{document}", "label": document[:26], "kind": "document", "x": 12, "y": round(y, 3), "frequency": len(document_terms[document])})
    for index, term in enumerate(concepts):
        y = 8 + (84 * index / max(1, len(concepts) - 1))
        nodes.append({"id": f"concept:{term}", "label": term, "kind": "concept", "x": 58, "y": round(y, 3), "frequency": term_frequency[term], "documents": len(term_documents[term])})

    edges: list[dict[str, Any]] = []
    for document in documents:
        counts = Counter(document_terms[document])
        for term in concepts:
            if counts[term]:
                edges.append({"source": f"document:{document}", "target": f"concept:{term}", "weight": round(min(1.0, counts[term] / 6), 4), "kind": "evidence"})
    cooccurrence: Counter[tuple[str, str]] = Counter()
    for terms in document_terms.values():
        present = sorted({term for term in terms if term in concepts})
        for left_index, left in enumerate(present):
            for right in present[left_index + 1:]:
                cooccurrence[(left, right)] += 1
    for (left, right), count in cooccurrence.most_common(40):
        if count >= 1:
            edges.append({"source": f"concept:{left}", "target": f"concept:{right}", "weight": round(min(1.0, count / 4), 4), "kind": "semantic"})

    model_path = _model_path(root, module_id)
    trained = False
    metadata: dict[str, Any] = {"architecture": ARCHITECTURE, "samples": 0, "epochs": 0, "mse": None, "trained_at": None, "stale": False}
    weights: dict[str, list[list[float]]] = {}
    if model_path.exists():
        learned_weights, loaded_metadata = _load(model_path)
        trained = True
        metadata.update({key: loaded_metadata.get(key) for key in ("architecture", "samples", "epochs", "mse", "trained_at")})
        metadata["stale"] = loaded_metadata.get("source_signature") != _source_signature(root, module_id)
        weights = {key: value.round(6).tolist() for key, value in learned_weights.items() if key in {"w1", "w2"}}
    try:
        from .knowledge_graph import read_graph

        evidence_graph = read_graph(root, module_id)
    except (OSError, RuntimeError, TypeError, ValueError, json.JSONDecodeError):
        evidence_graph = {"status": "pending", "nodes": [], "edges": []}
    return {
        "module_id": module_id,
        "trained": trained,
        "architecture": metadata["architecture"],
        "training": metadata,
        "features": ["tamanho do chunk", "quantidade de palavras", "densidade numérica"],
        "nodes": nodes,
        "edges": edges,
        "concept_count": len(concepts),
        "document_count": len(documents),
        "weights": weights,
        "evidence_graph": evidence_graph,
        "meaning": "As conexões semânticas representam coocorrência de conceitos nos mesmos chunks; as arestas de evidência ligam cada conceito aos documentos que o sustentam.",
    }
