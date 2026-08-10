from __future__ import annotations

from typing import Any


def validate_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], valid_types: set[str]) -> None:
    if len(nodes) > 80 or len(edges) > 160:
        raise ValueError("O grafo excede o limite seguro")
    ids = [str(node.get("id", "")) for node in nodes]
    if "" in ids or len(set(ids)) != len(ids):
        raise ValueError("Nós precisam de identificadores únicos")
    invalid = sorted({str(node.get("type")) for node in nodes} - valid_types)
    if invalid:
        raise ValueError(f"Tipos de bloco inválidos: {', '.join(invalid)}")
    known = set(ids)
    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        source, target = str(edge.get("source", "")), str(edge.get("target", ""))
        if source not in known or target not in known:
            raise ValueError("Conector aponta para um bloco inexistente")
        if source == target:
            raise ValueError("Um bloco não pode conectar a si mesmo")
        if (source, target) in seen_edges:
            raise ValueError("Conector duplicado")
        seen_edges.add((source, target))
    compile_graph(nodes, edges, reject_cycles=True)


def compile_graph(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], reject_cycles: bool = False) -> list[dict[str, Any]]:
    by_id = {str(node["id"]): node for node in nodes}
    indegree = {node_id: 0 for node_id in by_id}
    outgoing: dict[str, list[str]] = {node_id: [] for node_id in by_id}
    for edge in edges:
        source, target = str(edge["source"]), str(edge["target"])
        outgoing[source].append(target)
        indegree[target] += 1
    frontier = [node_id for node_id in by_id if indegree[node_id] == 0]
    ordered: list[dict[str, Any]] = []
    while frontier:
        node_id = frontier.pop(0)
        ordered.append(by_id[node_id])
        for target in outgoing[node_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                frontier.append(target)
    if len(ordered) != len(nodes):
        if reject_cycles:
            raise ValueError("O fluxo contém um ciclo e não pode ser executado")
        ordered.extend(by_id[node_id] for node_id, degree in indegree.items() if degree > 0)
    return ordered
