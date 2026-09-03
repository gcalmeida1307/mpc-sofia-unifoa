from __future__ import annotations

import json
from pathlib import Path

from api.contracts import PIPELINE_STAGES
from api.domains import DOMAIN_CONTRACTS, domain_for
from api.mcp_contracts import TOOL_CONTRACTS


def test_all_current_domains_have_the_same_contract_shape() -> None:
    assert len(DOMAIN_CONTRACTS) >= 11
    required = {"id", "name", "keywords", "source_profile", "high_risk", "tools"}
    for module_id, contract in DOMAIN_CONTRACTS.items():
        assert required <= set(contract.manifest())
        assert contract.id == module_id
        assert contract.keywords


def test_unknown_domain_does_not_change_a_known_domain() -> None:
    known = domain_for("direito")
    unknown = domain_for("novo-modulo")
    assert known.high_risk is False
    assert unknown.id == "novo-modulo"
    assert unknown.name == "Domínio"


def test_tools_are_allowlisted_and_have_operational_contracts() -> None:
    assert TOOL_CONTRACTS
    for name, contract in TOOL_CONTRACTS.items():
        assert name == contract.name
        assert contract.timeout_seconds > 0
        assert contract.required_capability
        assert contract.audit_event


def test_eval_manifest_covers_every_domain_and_required_categories() -> None:
    manifest = json.loads((Path(__file__).parent / "evals" / "manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["modules"]) == set(DOMAIN_CONTRACTS)
    assert len(manifest["categories"]) == 14
    assert PIPELINE_STAGES[0] == "RECEIVED"
    assert PIPELINE_STAGES[-1] == "READY"
