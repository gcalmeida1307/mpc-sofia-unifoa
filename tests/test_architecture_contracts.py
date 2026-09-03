from __future__ import annotations

import json
import tempfile
from pathlib import Path

from api.contracts import PIPELINE_STAGES
from api.domain_packages import package_for
from api.domains import DOMAIN_CONTRACTS, domain_for
from api.evaluation import evaluation_coverage
from api.knowledge_graph import build_graph, graph_status
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


def test_domain_packages_are_isolated_and_legacy_files_enter_the_graph() -> None:
    assert package_for("direito").id == "legal"
    assert package_for("medicina").id == "medical"
    assert package_for("departamento-pessoal").id == "personnel"
    assert package_for("direito") is not package_for("medicina")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "knowledge"
        module = root / "direito"
        module.mkdir(parents=True)
        (module / "acordo.md").write_text(
            "Acordo coletivo: a compensação de jornada deve respeitar o prazo e a jornada máxima.",
            encoding="utf-8",
        )
        graph = build_graph(root, "direito")
        assert graph["document_count"] == 1
        assert graph["edge_count"] > 0
        assert graph_status(root, "direito")["status"] == "ready"


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


def test_eval_coverage_separates_reviewed_cases_from_drafts() -> None:
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory)
        root = project / "knowledge"
        (root / "direito").mkdir(parents=True)
        (root / "direito" / "lei.md").write_text("Uma regra documentada.", encoding="utf-8")
        (project / "tests" / "evals").mkdir(parents=True)
        (project / "tests" / "evals" / "manifest.json").write_text(
            json.dumps(
                {
                    "version": "1.1",
                    "modules": ["direito", "secretaria"],
                    "cases": [
                        {"module": "direito", "question": "qual regra?", "reviewed": True, "expected_sources": ["lei.md"]},
                        {"module": "direito", "question": "qual outra regra?", "reviewed": False, "expected_sources": ["lei.md"]},
                    ],
                }
            ),
            encoding="utf-8",
        )
        coverage = evaluation_coverage(root)
        assert coverage["reviewed_case_count"] == 1
        assert coverage["draft_case_count"] == 1
        assert coverage["modules_without_reviewed_cases"] == []
        assert coverage["modules_without_corpus"] == ["secretaria"]
