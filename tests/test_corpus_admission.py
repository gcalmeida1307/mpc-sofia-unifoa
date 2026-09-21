from __future__ import annotations

import sqlite3
from pathlib import Path

from api.expansion import _source_score, expansion_settings
from api.ingestion import ready_files_for
from api.module_admission import assess_module_document


def test_infrastructure_rejects_clear_cross_domain_contamination() -> None:
    decision = assess_module_document(
        "infraestrutura",
        Path("www-gov-br.md"),
        "Notas técnicas sobre influenza e gripe. Cadastro CPF e orientações do Ministério da Saúde.",
    )
    assert decision.accepted is False
    assert "influenza" in decision.negative_markers
    assert "cpf" in decision.negative_markers


def test_infrastructure_rejects_generic_government_management_page() -> None:
    decision = assess_module_document(
        "infraestrutura",
        Path("www-gov-br-e50191f1ee29.md"),
        "Gestão Documental — Ministério da Gestão e da Inovação em Serviços Públicos. "
        "Informações e acesso a documentos públicos.",
    )
    assert decision.accepted is False


def test_infrastructure_accepts_zabbix_source() -> None:
    decision = assess_module_document(
        "infraestrutura",
        Path("zabbix-trigger.md"),
        "Configure o trigger do Zabbix para monitorar o host e a disponibilidade do servidor.",
    )
    assert decision.accepted is True


def test_ready_files_for_excludes_unapproved_physical_files(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "infraestrutura"
    module.mkdir(parents=True)
    ready = module / "ready.md"
    pending = module / "pending.md"
    unknown = module / "unknown.md"
    for path in (ready, pending, unknown):
        path.write_text(path.stem, encoding="utf-8")

    database = tmp_path / "data" / "knowledge_expansion.sqlite3"
    database.parent.mkdir()
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE documents (module_id TEXT, path TEXT, status TEXT, validation_status TEXT)")
    connection.executemany(
        "INSERT INTO documents VALUES (?, ?, ?, ?)",
        [
            ("infraestrutura", str(ready.resolve()), "READY", "READY"),
            ("infraestrutura", str(pending.resolve()), "VALIDATING", "PENDING"),
        ],
    )
    connection.commit()
    connection.close()

    assert ready_files_for(root, "infraestrutura") == [ready]


def test_public_expansion_is_paused_by_default(monkeypatch) -> None:
    monkeypatch.delenv("SOFIA_AUTO_EXPANSION", raising=False)
    assert expansion_settings()["enabled"] is False


def test_official_hosting_is_not_an_automatic_relevance_bonus() -> None:
    assert _source_score("infraestrutura", "https://www.gov.br/pagina", "Página institucional", ["zabbix"]) == 0.0
