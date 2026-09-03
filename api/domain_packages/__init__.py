"""Pluggable domain packages for SOFIA.

The CORE only calls this small retrieval contract.  A package may describe
source selection, query vocabulary, evidence filters and scoring hints without
adding domain rules to the generic retrieval engine.
"""

from .base import DomainRetrievalPackage, QueryProfile, SourceSelection
from .registry import package_for, package_ids, package_manifests

__all__ = [
    "DomainRetrievalPackage",
    "QueryProfile",
    "SourceSelection",
    "package_for",
    "package_ids",
    "package_manifests",
]
