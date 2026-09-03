from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .privacy import ExternalRedaction


def store_offline_candidate(
    root: Path,
    module_id: str,
    answer: str,
    sources: list[str],
    provider: str,
    retry_of: int | None = None,
) -> dict[str, Any]:
    """Persist an accepted, anonymized provider synthesis for later RAG use.

    This is intentionally a candidate, not a new source of truth. It is
    created only after the local evidence gate and critic approve the answer.
    The content is anonymized again with a fresh request scope, so the
    redaction map used by the provider call can never be persisted by mistake.
    """
    if not answer.strip() or provider not in {"openai", "gemini", "claude"}:
        return {"stored": False, "file_name": None, "reason": "provider_local_or_empty"}

    safe_answer = ExternalRedaction().clean(answer).strip()
    source_text = ", ".join(str(source) for source in sources[:20]) or "fontes locais recuperadas"
    identity = "|".join((module_id, str(retry_of or ""), provider, source_text, safe_answer))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    relative_name = f"offline/sofia-candidato-{digest}.md"
    destination = root / module_id / relative_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        destination.write_text(
            "\n".join(
                (
                    "# Síntese anonimizada — candidato offline",
                    "",
                    "Status: candidato; depende de revisão e feedback contínuos.",
                    f"Gerado em: {datetime.now(UTC).isoformat()}",
                    f"Motor auxiliar: {provider}",
                    f"Fontes locais relacionadas: {source_text}",
                    "",
                    safe_answer,
                    "",
                )
            ),
            encoding="utf-8",
        )
    return {
        "stored": True,
        "file_name": relative_name,
        "source_count": len(sources),
        "note": "Síntese anonimizada candidata; as fontes locais continuam sendo a autoridade principal.",
    }
