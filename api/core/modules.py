from __future__ import annotations

from typing import Any

from core.base_module import BaseModule


class KnowledgeModule(BaseModule):
    name = "knowledge"
    version = "1.0.0"
    capabilities = ["ingest", "search", "reindex"]


class WorkflowModule(BaseModule):
    name = "workflow"
    version = "1.0.0"
    capabilities = ["run", "orchestrate"]


class MarketplaceModule(BaseModule):
    name = "marketplace"
    version = "1.0.0"
    capabilities = ["install", "catalog"]
