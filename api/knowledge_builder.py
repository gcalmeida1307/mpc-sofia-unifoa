"""Deterministic knowledge-building artifacts produced after extraction.

The builder does not pretend that heuristics are model training.  It creates
auditable metadata (summary, concepts, relations and likely questions) that
improves retrieval immediately and can later be replaced by a stronger local
model without changing the document contract.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from .domains import domain_for
from .query_analysis import normalize


def _sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    return [part.strip(" -•\t") for part in re.split(r"(?<=[.!?])\s+|\n+", normalized) if len(part.strip()) >= 45]


def _keywords(text: str, module_id: str, limit: int = 18) -> list[str]:
    words = re.findall(r"[\wÀ-ÿ][\wÀ-ÿ-]{2,}", normalize(text))
    stopwords = {
        "para", "como", "sobre", "entre", "esta", "este", "isso", "essa", "esse", "quando", "onde",
        "pode", "podem", "deve", "devem", "são", "ainda", "mais", "pelo", "pela", "pelos", "pelas",
        "uma", "umas", "uns", "dos", "das", "com", "sem", "que", "não", "nos", "nas", "por",
    }
    counts = Counter(word for word in words if word not in stopwords and not word.isdigit())
    domain_words = {normalize(word) for word in domain_for(module_id).keywords}
    ranked = sorted(counts, key=lambda word: (word not in domain_words, -counts[word], word))
    return ranked[:limit]


def _entities(text: str) -> list[str]:
    candidates = re.findall(
        r"\b(?:art\.?\s*\d+[º°]?|cláusula\s+\d+[ªº]?|CPC\s*[/.-]?\s*[A-Z0-9]+|CID[- ]?[A-Z0-9.]+|ICD[- ]?[A-Z0-9.]+|FHIR|Zabbix|SNMP|eSocial)\b",
        text,
        flags=re.IGNORECASE,
    )
    seen: set[str] = set()
    return [value.strip() for value in candidates if not (normalize(value) in seen or seen.add(normalize(value)))]


def _concepts(text: str, module_id: str, keywords: list[str]) -> list[str]:
    normalized = normalize(text)
    return list(dict.fromkeys([
        *[word for word in domain_for(module_id).keywords if normalize(word) in normalized],
        *keywords[:8],
    ]))[:16]


def _relations(text: str, concepts: list[str], source_name: str) -> list[dict[str, Any]]:
    normalized = normalize(text)
    relations: list[dict[str, Any]] = []
    for index, left in enumerate(concepts):
        for right in concepts[index + 1 :]:
            if normalize(left) in normalized and normalize(right) in normalized:
                relations.append({
                    "source": source_name,
                    "from": left,
                    "to": right,
                    "type": "co_occurrence",
                    "confidence": 0.62,
                    "status": "observed",
                })
            if len(relations) >= 24:
                return relations
    return relations


def build_artifacts(path: Path, text: str, module_id: str) -> dict[str, Any]:
    """Build privacy-neutral metadata from one extracted document."""
    clean = re.sub(r"\s+", " ", text).strip()
    sentences = _sentences(text)
    keywords = _keywords(text, module_id)
    entities = _entities(text)
    concepts = _concepts(text, module_id, keywords)
    # The first few informative sentences are a summary, never raw document
    # storage.  It is a derived artifact and can be regenerated at any time.
    summary = " ".join(sentences[:5])[:2400] if sentences else clean[:1600]
    question_templates = [
        f"Qual é o resumo de {path.name}?",
        f"Quais são os principais conceitos de {path.name}?",
        f"Com quais temas {path.name} se relaciona?",
    ]
    if concepts:
        question_templates.append(f"O que {path.name} informa sobre {concepts[0]}?")
    words = re.findall(r"\w+", clean, flags=re.UNICODE)
    quality = min(1.0, len(words) / 180) if words else 0.0
    quality += 0.20 if sentences else 0.0
    quality -= 0.15 if len(set(words)) < max(3, len(words) * 0.15) else 0.0
    return {
        "summary": summary,
        "keywords": keywords,
        "entities": entities,
        "concepts": concepts,
        "relations": _relations(text, concepts, path.name),
        "questions": question_templates,
        "quality": round(max(0.0, min(1.0, quality)), 4),
        "ocr_quality": None,
        "word_count": len(words),
        "text_chars": len(clean),
    }

