"""Generic module package for domains without a special retrieval policy."""

from __future__ import annotations

from .base import DomainRetrievalPackage


class GenericPackage(DomainRetrievalPackage):
    id = "generic"

    def manifest(self) -> dict[str, object]:
        return {"id": self.id, "features": ["hybrid-lexical-semantic"], "isolated": True}
