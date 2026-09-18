import asyncio
from pathlib import Path

from api.domain_packages.base import named_source_paths
from api.orchestration import answer
from api.policies import policy_for
from api.retrieval import retrieve
from api.runtime_cache import clear, stats


def _legal_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "knowledge"
    module = root / "direito"
    module.mkdir(parents=True)
    (module / "Saae_2026_2027.md").write_text(
        "Cláusula 27: assegura repouso remunerado ao empregado que chegar atrasado, "
        "se o ingresso for permitido e o atraso for compensado no fim da jornada.\n"
        "Cláusula 1: salários.",
        encoding="utf-8",
    )
    (module / "Vade_mecum_Senado_Federal_3ed.md").write_text(
        "Art. 58. §1º Variações no registro de ponto não excedentes de cinco minutos "
        "não são descontadas, observado o limite de dez minutos diários. §2º O tempo "
        "da residência ao posto por qualquer transporte não é computado na jornada.",
        encoding="utf-8",
    )
    (module / "processo-stj.md").write_text(
        "Atraso injustificado de audiência e tutela de urgência em processo judicial.",
        encoding="utf-8",
    )
    (module / "RiskyUsers.csv").write_text(
        "ID,Usuário,Nível de risco\n1,Pessoa,Alto\n",
        encoding="utf-8",
    )
    return root


def test_named_delay_comparison_rejects_unrelated_pages_and_personnel_csv(tmp_path: Path) -> None:
    root = _legal_fixture(tmp_path)
    question = (
        "Atraso superior a 15 minutos devido a questão de tempo ou trânsito é tratada "
        "como? O SAAE prevê algo? VADE MENCUM prevê algo?"
    )
    selected = named_source_paths(list((root / "direito").iterdir()), question)
    assert {path.name for path in selected} == {"Saae_2026_2027.md", "Vade_mecum_Senado_Federal_3ed.md"}
    result = retrieve(root, "direito", question, policy_for("direito"), limit=8)
    assert result.has_quality_evidence
    assert set(result.sources) == {"Saae_2026_2027.md", "Vade_mecum_Senado_Federal_3ed.md"}
    assert len(result.evidence) == 2
    joined = result.context.casefold()
    assert "cláusula 27" in joined
    assert "art. 58" in joined
    assert "tutela de urgência" not in joined
    assert "riskyusers" not in joined


def test_delay_answer_is_human_separate_and_traceable(tmp_path: Path) -> None:
    root = _legal_fixture(tmp_path)
    question = (
        "Atraso superior a 15 minutos devido a questão de tempo ou trânsito é tratada "
        "como? O SAAE prevê algo? VADE MENCUM prevê algo?"
    )
    result = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            external_allowed=False,
            history=[],
            question=question,
        )
    )
    assert result.provider == "local-rag"
    assert "cláusula 27" in result.answer.casefold()
    assert "art. 58" in result.answer.casefold()
    assert "não fica automaticamente abonado" in result.answer.casefold()
    assert "processo-stj" not in result.answer
    assert "riskyusers" not in result.answer.casefold()


def test_retrieval_cache_hits_and_invalidates_when_a_source_changes(tmp_path: Path) -> None:
    clear("retrieval")
    root = tmp_path / "knowledge"
    module = root / "financeiro"
    module.mkdir(parents=True)
    source = module / "manual.txt"
    source.write_text("O fluxo de caixa registra entradas e saídas diariamente.", encoding="utf-8")
    question = "O que o manual informa sobre fluxo de caixa?"
    first = retrieve(root, "financeiro", question, policy_for("financeiro"), limit=4)
    after_first = stats()
    second = retrieve(root, "financeiro", question, policy_for("financeiro"), limit=4)
    after_second = stats()
    assert first.context == second.context
    assert after_second["hits"] > after_first["hits"]

    source.write_text("O fluxo de caixa registra apenas pagamentos mensais.", encoding="utf-8")
    third = retrieve(root, "financeiro", question, policy_for("financeiro"), limit=4)
    assert "apenas pagamentos mensais" in third.context
    assert stats()["misses"] > after_second["misses"]
