"""Conservative relations with explicit premises, never causal invention.

This is a bounded rule engine for documented taxonomies, rules and differences.
Unsupported language stays as quoted evidence; it does not become a graph fact.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from .query_analysis import normalize


@dataclass(frozen=True)
class Unit:
    id: str
    source: str
    ordinal: int
    page: int | None
    text: str


def sentences(text: str) -> list[str]:
    # Do not split decimal numbers or article abbreviations at their dots.
    text = re.sub(r"\b(Art|art|Dr|Dra)\.", r"\1§DOT§", text)
    values = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\d])|\n+", text)
    return [v.replace("§DOT§", ".").strip(" -•\t") for v in values if len(v.strip()) >= 18]


def evidence_units(result) -> list[Unit]:
    units, seen = [], set()
    for item in result.evidence:
        for sentence in sentences(item.chunk.text):
            key = (item.chunk.path.name, normalize(sentence))
            if key in seen:
                continue
            seen.add(key)
            units.append(Unit(f"E{len(units)+1}", item.chunk.path.name, item.chunk.ordinal, item.chunk.page, sentence))
    return units


def canonical(text: str) -> str:
    return re.sub(r"^(?:o|a|os|as|um|uma|todo|toda|todos|todas)\s+", "", normalize(text).strip(" .:;"))


def extract_relations(units: list[Unit]) -> list[dict]:
    relations = []
    for unit in units:
        text = unit.text.strip(" .")
        patterns = [
            (r"^(.+?)\s+é\s+(?:um tipo de|uma subclasse de|uma espécie de)\s+(.+)$", "subclass", "fact"),
            (r"^(.+?)\s+é\s+(?:um|uma)\s+(.+)$", "instance", "fact"),
            (r"^(?:Todo|Toda)\s+(.+?)\s+(?:exige|requer|deve ter)\s+(.+)$", "requires", "fact"),
            (r"^(.+?)\s+(?:está correlacionad[oa] com|está associad[oa] a|correlaciona-se com)\s+(.+)$", "association", "correlation"),
            (r"^(.+?)\s+(?:pode causar|poderia causar|pode provocar)\s+(.+)$", "possible_cause", "hypothesis"),
            (r"^(.+?)\s+(?:causa|provoca)\s+(.+)$", "reported_cause", "causal_claim"),
        ]
        for pattern, relation_type, kind in patterns:
            match = re.match(pattern, text, re.I)
            if match:
                relations.append({"from": match[1], "to": match[2], "type": relation_type, "kind": kind, "premises": [unit.id], "inferred": False, "source": unit.source, "quote": unit.text})
                break
    # Two bounded passes support instance -> subclass -> required property.
    for _ in range(2):
        for left in list(relations):
            if left["type"] not in {"instance", "subclass"}:
                continue
            for right in list(relations):
                if canonical(left["to"]) != canonical(right["from"]) or right["type"] not in {"requires", "subclass"}:
                    continue
                inferred = {"from": left["from"], "to": right["to"], "type": right["type"] if right["type"] == "requires" else left["type"], "kind": "inference", "premises": list(dict.fromkeys(left["premises"] + right["premises"])), "inferred": True}
                if not any((r["from"], r["to"], r["type"]) == (inferred["from"], inferred["to"], inferred["type"]) for r in relations):
                    relations.append(inferred)
                if len(relations) >= 100:
                    return relations
    return relations


def compare_units(units: list[Unit]) -> list[dict]:
    differences = []
    for i, left in enumerate(units):
        for right in units[i+1:]:
            if left.source == right.source:
                continue
            a, b = normalize(left.text), normalize(right.text)
            na, nb = re.findall(r"\b\d+(?:[.,]\d+)?\b", a), re.findall(r"\b\d+(?:[.,]\d+)?\b", b)
            skeleton_a = re.sub(r"\b\d+(?:[.,]\d+)?\b", "#", a)
            skeleton_b = re.sub(r"\b\d+(?:[.,]\d+)?\b", "#", b)
            neg_a, neg_b = bool(re.search(r"\bnao\b", a)), bool(re.search(r"\bnao\b", b))
            if na and nb and skeleton_a == skeleton_b and na != nb:
                differences.append({"kind": "conflict", "type": "numeric_difference", "premises": [left.id, right.id], "status": "requires_scope_review"})
            elif neg_a != neg_b and re.sub(r"\bnao\s+", "", a) == re.sub(r"\bnao\s+", "", b):
                differences.append({"kind": "conflict", "type": "negation", "premises": [left.id, right.id], "status": "requires_scope_review"})
            elif a == b:
                differences.append({"kind": "pattern", "type": "agreement", "premises": [left.id, right.id]})
    return differences


def analyze(result) -> dict:
    units = evidence_units(result)
    return {"units": [asdict(u) for u in units], "relations": extract_relations(units), "comparisons": compare_units(units), "method": "bounded_rules_with_source_premises"}


def requested(question: str) -> bool:
    query = normalize(question)
    return any(m in query for m in ("resuma", "resumo", "compare", "comparacao", "relac", "infer", "subclasse", "conflito", "padrao", "padroes", "correl", "causal"))


def render(question: str, result, analysis: dict | None = None) -> str | None:
    if not result.has_quality_evidence or not requested(question):
        return None
    analysis = analysis or analyze(result)
    units = analysis["units"]
    if not units:
        return None
    query = normalize(question)
    parts = []
    summary = any(m in query for m in ("resuma", "resumo"))
    if summary:
        parts.append("Os documentos apresentam os seguintes pontos:")
    else:
        conflicts = [d for d in analysis["comparisons"] if d["kind"] == "conflict"]
        if conflicts:
            parts.append("Há uma divergência textual que precisa ser conferida quanto à versão, vigência e abrangência:")
            for conflict in conflicts[:4]:
                selected = [u for u in units if u["id"] in conflict["premises"]]
                parts.append("\n".join(f"- {u['text']} [{u['id']}]" for u in selected))
        inferences = [r for r in analysis["relations"] if r["inferred"]]
        for relation in inferences[:5]:
            verb = "exige" if relation["type"] == "requires" else "pertence a"
            parts.append(f"Inferência: {relation['from']} {verb} {relation['to']}, pela aplicação das regras documentadas. " + " ".join(f"[{p}]" for p in relation["premises"]))
        for relation in [r for r in analysis["relations"] if r["kind"] in {"correlation", "hypothesis", "causal_claim"}][:4]:
            label = {"correlation": "Correlação documentada", "hypothesis": "Hipótese documentada", "causal_claim": "Alegação causal da fonte; não validada independentemente"}[relation["kind"]]
            parts.append(f"{label}: {relation['quote']} [{relation['premises'][0]}]")
        if not parts:
            parts.append("Os trechos permitem esta leitura conjunta. Não foi identificada uma relação ou contradição comprovada pelas regras de comparação disponíveis:")
    # Guarantee source coverage and retain full, complete sentences. Excerpts
    # are attached to the claim, never dumped as an unlabeled global context.
    used = set(re.findall(r"\[(E\d+)\]", "\n".join(parts)))
    for source in result.sources:
        selected = [u for u in units if u["source"] == source]
        limit = 5 if summary else 2
        available = [u for u in selected if u["id"] not in used][:limit]
        if available:
            parts.append("\n".join(f"{u['text']} [{u['id']}]" for u in available))
    if any(r["kind"] in {"correlation", "hypothesis", "causal_claim"} for r in analysis["relations"]):
        parts.append("Associação ou simultaneidade não demonstra causalidade; hipóteses exigem verificação adicional.")
    parts.append("A análise cobre os trechos recuperados; ausência de conflito nesta consulta não prova compatibilidade integral dos documentos.")
    used = set(re.findall(r"\[(E\d+)\]", "\n".join(parts)))
    parts.append("Fontes e trechos:\n" + "\n".join(f"- [{u['id']}] {u['source']} — " + (f"página {u['page']}" if u['page'] else f"trecho {u['ordinal']}") for u in units if u["id"] in used))
    return "\n\n".join(parts)
