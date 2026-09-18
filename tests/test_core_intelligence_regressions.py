import asyncio
from pathlib import Path

from api.orchestration import _retrieval_question, answer
from api.policies import policy_for
from api.rca import is_rca_request
from api.retrieval import retrieve


def test_short_medical_follow_up_keeps_the_active_symptom() -> None:
    history = [
        {"role": "user", "content": "Tosse persistente por dias, seca e raras vezes existe muco, o que pode ser?"},
        {"role": "assistant", "content": "A tosse aparece em quadros respiratórios. Fontes e trechos: guia.md."},
    ]
    resolved = _retrieval_question("Então, oq pode ser?", history)
    assert "Tosse persistente" in resolved
    assert "Então, oq pode ser?" in resolved


def test_document_source_handoff_keeps_the_prior_rule_question() -> None:
    history = [
        {
            "role": "user",
            "content": "Se eu chego atrasado às 07:20 para uma entrada prevista às 07:00 e saio às 16:20 ao invés de sair 16:00, isso não me dá problema nenhum segundo o SAAE?",
        },
        {
            "role": "assistant",
            "content": "Não encontrei evidência suficiente nesta primeira busca.",
        },
    ]
    resolved = _retrieval_question("E quando vai pro VADE Mecum?", history)
    assert "SAAE" in resolved
    assert "VADE Mecum" in resolved
    assert "07:20" in resolved


def test_padded_document_source_handoff_keeps_the_prior_rule_question() -> None:
    history = [
        {
            "role": "user",
            "content": "Se eu chegar 20 minutos depois do horário mas sair 20 minutos depois, isso é permitido segundo o SAAE?",
        },
        {"role": "assistant", "content": "O SAAE prevê uma regra específica para o atraso."},
    ]
    resolved = _retrieval_question(
        "Entendi, e quando falamos do VADE Mecum, o que ele diz sobre?",
        history,
    )
    assert resolved.startswith("Se eu chegar 20 minutos depois")
    assert "SAAE" in resolved
    assert "VADE Mecum" in resolved


def test_source_handoff_skips_intermediate_source_questions() -> None:
    history = [
        {"role": "user", "content": "Qual regra de atraso está prevista no SAAE?"},
        {"role": "assistant", "content": "O SAAE prevê uma regra específica."},
        {"role": "user", "content": "Entendi, e quando falamos do VADE Mecum, o que ele diz sobre?"},
        {"role": "assistant", "content": "O Vade Mecum é uma coletânea de normas."},
    ]
    resolved = _retrieval_question(
        "Entendo, mas o que ele diz sobre atraso na jornada superior a 20 minutos?",
        history,
    )
    assert resolved.startswith("Qual regra de atraso")
    assert "VADE Mecum" in resolved
    assert "atraso na jornada superior a 20 minutos" in resolved


def test_source_handoff_is_not_tied_to_a_legal_source_vocabulary() -> None:
    history = [
        {"role": "user", "content": "Como vejo os desvios do indicador mensal?"},
        {"role": "assistant", "content": "Vou consultar os registros do módulo."},
    ]
    resolved = _retrieval_question(
        "Entendi, e no manual de operações, o que ele diz sobre?",
        history,
    )
    assert resolved.startswith("Como vejo os desvios")
    assert "manual de operações" in resolved


def test_document_source_handoff_recovers_saae_and_vade_rules(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito"
    module.mkdir(parents=True)
    (module / "Saae_2026_2027.md").write_text(
        "Cláusula 27: assegura o repouso remunerado ao empregado que chegar atrasado, quando permitido o ingresso e o atraso for compensado no final da jornada.",
        encoding="utf-8",
    )
    (module / "Vade_mecum_Senado_Federal_3ed.md").write_text(
        "Art. 58 trata da jornada e do registro de ponto. Art. 59 trata das horas extras.",
        encoding="utf-8",
    )
    history = [
        {
            "role": "user",
            "content": "Se eu chego atrasado às 07:20 para uma entrada prevista às 07:00 e saio às 16:20 ao invés de sair 16:00, isso não me dá problema nenhum segundo o SAAE?",
        },
        {
            "role": "assistant",
            "content": "Não encontrei evidência suficiente nesta primeira busca.",
        },
    ]
    response = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            question="E quando vai pro VADE Mecum?",
            history=history,
            external_allowed=False,
        )
    )
    assert response.model in {"local-rag", "local-source-evidence"}
    assert set(response.sources) == {"Saae_2026_2027.md", "Vade_mecum_Senado_Federal_3ed.md"}
    assert "cláusula 27" in response.answer.casefold()
    assert "art. 58" in response.answer.casefold()


def test_padded_source_handoff_recovers_both_named_rules(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito"
    module.mkdir(parents=True)
    (module / "Saae_2026_2027.md").write_text(
        "Cláusula 27: assegura o repouso remunerado ao empregado que chegar atrasado, quando permitido o ingresso e o atraso for compensado no final da jornada.",
        encoding="utf-8",
    )
    (module / "Vade_mecum_Senado_Federal_3ed.md").write_text(
        "Art. 58, § 1º, trata das variações no registro de ponto de até cinco minutos, observado o limite diário de dez minutos.",
        encoding="utf-8",
    )
    first_question = "Se eu chegar 20 minutos depois do horário mas sair 20 minutos depois, isso é permitido segundo o SAAE?"
    handoff_question = "Entendi, e quando falamos do VADE Mecum, o que ele diz sobre?"
    history = [
        {"role": "user", "content": first_question},
        {"role": "assistant", "content": "O SAAE prevê uma regra específica para o atraso."},
        {"role": "user", "content": handoff_question},
        {"role": "assistant", "content": "O Vade Mecum é uma coletânea de normas."},
    ]
    response = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            question="Entendo, mas o que ele diz sobre atraso na jornada superior a 20 minutos?",
            history=history,
            external_allowed=False,
        )
    )
    assert set(response.sources) == {"Saae_2026_2027.md", "Vade_mecum_Senado_Federal_3ed.md"}
    assert "cláusula 27" in response.answer.casefold()
    assert "art. 58" in response.answer.casefold()


def test_saae_delay_question_uses_clause_27_on_the_first_query(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito"
    module.mkdir(parents=True)
    (module / "Saae_2026_2027.md").write_text(
        "Cláusula 5: o excesso de horas pode ser compensado por diminuição correspondente em outro dia, dentro dos limites do acordo.\n\n"
        "Cláusula 27: assegura o repouso remunerado ao empregado que chegar atrasado, quando permitido o ingresso e o atraso for compensado no final da jornada do dia ou da semana.",
        encoding="utf-8",
    )
    question = (
        "Se eu chego atrasado às 07:20 para uma entrada prevista às 07:00 e saindo às 16:20 "
        "ao invés de sair 16:00, isso não me dá problema nenhum segundo o SAAE?"
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            question=question,
            history=[],
            external_allowed=False,
        )
    )
    assert response.model in {"local-rag", "local-source-evidence"}
    assert "cláusula 27" in response.answer.casefold()
    assert "chegar atrasado" in response.answer.casefold()
    assert "20 minutos" in response.answer.casefold()
    assert "cláusula 5" not in response.answer.casefold()
    assert "Saae_2026_2027.md" in response.answer


def test_medical_symptom_gate_rejects_icd_cancer_noise(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "medicina" / "links"
    module.mkdir(parents=True)
    (module / "guia-respiratorio.md").write_text(
        "Gripe é uma infecção respiratória. Entre os principais sintomas estão tosse, febre e dor de garganta.",
        encoding="utf-8",
    )
    (module / "ICD-11-Reference-Guide-2024-01-pt.pdf").write_text(
        "Metástases hepáticas podem ser devidas a câncer de estômago.",
        encoding="utf-8",
    )
    result = retrieve(root, "medicina", "Tosse persistente, então o que pode ser?", policy_for("medicina"), limit=6)
    assert result.has_quality_evidence
    assert result.sources == ("guia-respiratorio.md",)
    assert "cancer de estomago" not in result.context.casefold()
    response = asyncio.run(
        answer(
            root=root,
            module_id="medicina",
            provider="auto",
            question="Tosse persistente, então o que pode ser?",
            history=[],
            external_allowed=False,
        )
    )
    assert response.model == "local-source-evidence"
    assert "câncer" not in response.answer.casefold()
    assert "tosse" in response.answer.casefold()


def test_named_law_query_rejects_personnel_csv_from_same_module(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "infraestrutura" / "links"
    module.mkdir(parents=True)
    (module / "www-gov-br-e50191f1ee29.md").write_text(
        "Lei nº 12.527, de 18 de novembro de 2011. A Lei de Acesso à Informação trata do acesso e da divulgação de informações públicas.",
        encoding="utf-8",
    )
    (root / "infraestrutura" / "RiskyUsers.csv").write_text(
        "Nome,Nível de risco\nPessoa,Alto\n",
        encoding="utf-8",
    )
    result = retrieve(root, "infraestrutura", "O que diz a Lei nº 12.527, de 18 de novembro de 2011?", policy_for("infraestrutura"), limit=6)
    assert result.has_quality_evidence
    assert result.sources == ("www-gov-br-e50191f1ee29.md",)
    assert "RiskyUsers.csv" not in result.context
    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question="O que diz a Lei nº 12.527, de 18 de novembro de 2011?",
            history=[],
            external_allowed=False,
        )
    )
    assert response.model == "local-source-evidence"
    assert "Lei de Acesso à Informação" in response.answer
    assert "RiskyUsers" not in response.answer


def test_direct_extra_hours_question_uses_complete_art_59_rule(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito" / "textos"
    module.mkdir(parents=True)
    (module / "Vade_mecum.md").write_text(
        "Art. 59. A duracao diaria pode ser acrescida de horas extras, em numero nao excedente de duas. A remuneracao da hora extra sera de 50%.",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            question="Se eu fizer 3 horas a mais no dia? O que acontece?",
            history=[],
            external_allowed=False,
        )
    )
    assert response.model == "local-source-evidence"
    assert "art. 59" in response.answer.casefold()
    assert "duas horas" in response.answer.casefold()
    assert "três horas" in response.answer.casefold()
    assert "penalidade específica" in response.answer.casefold()


def test_generic_overtime_query_prefers_normative_source_over_legal_blogs(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito" / "textos"
    module.mkdir(parents=True)
    (module / "Vade_mecum.md").write_text(
        "Art. 59. A duração diária pode ser acrescida de horas extras, em número não excedente de duas. A remuneração da hora extra será de 50%.",
        encoding="utf-8",
    )
    (module / "blog-trabalhista.md").write_text(
        "Artigo informativo sobre trabalho e horas em diferentes situações.",
        encoding="utf-8",
    )
    result = retrieve(
        root,
        "direito",
        "Se eu fizer 3 horas a mais no dia? O que acontece?",
        policy_for("direito"),
        limit=6,
    )
    assert result.sources == ("Vade_mecum.md",)


def test_habeas_corpus_types_are_synthesized_from_classification_articles(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito" / "textos"
    module.mkdir(parents=True)
    (module / "Vade_mecum.md").write_text(
        "CAPÍTULO X — Do Habeas Corpus e Seu Processo. "
        "Art. 647. Dar-se-á habeas corpus sempre que alguém sofrer ou se achar na iminência de sofrer violência ou coação ilegal na sua liberdade de ir e vir. "
        "Art. 647-A. A autoridade judicial poderá expedir ordem de habeas corpus individual ou coletivo. "
        "Art. 660, § 4º. Se a ordem for concedida para evitar ameaça, dar-se-á ao paciente salvo-conduto.",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            question="Quais são os tipos possíveis de habeas corpus?",
            history=[],
            external_allowed=False,
        )
    )
    assert response.model == "local-source-evidence"
    assert "liberdade de locomoção" in response.answer
    assert "repressivo ou liberatório" in response.answer
    assert "preventivo" in response.answer
    assert "individual ou coletiva" in response.answer
    assert "salvo-conduto" in response.answer
    assert "não aparecem nos trechos recuperados" in response.answer
    assert "página" in response.answer or "trecho" in response.answer


def test_mandado_de_injuncao_uses_cabimento_rule_not_competence_fragments(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito" / "textos"
    module.mkdir(parents=True)
    (module / "Vade_mecum.md").write_text(
        "Constituição Federal. Art. 5º, LXXI — conceder-se-á mandado de injunção "
        "sempre que a falta de norma regulamentadora torne inviável o exercício "
        "dos direitos e liberdades constitucionais e das prerrogativas inerentes "
        "à nacionalidade, à soberania e à cidadania. "
        "Art. 102, I, q — compete ao STF julgar mandado de injunção em hipóteses "
        "determinadas. Art. 105, I, h — compete ao STJ julgar outras hipóteses.",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            question="Cabe mandado de injunção contra lei ou norma infraconstitucional?",
            history=[],
            external_allowed=False,
        )
    )
    assert response.model == "local-source-evidence"
    assert "não é usado para atacar uma lei ou norma infraconstitucional" in response.answer
    assert "falta de norma regulamentadora" in response.answer
    assert "direitos e liberdades constitucionais" in response.answer
    assert "competência do STF e do STJ" in response.answer
    assert "não substituem a regra de cabimento" in response.answer


def test_cross_domain_symptom_is_blocked_before_infrastructure_provider(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    (root / "infraestrutura" / "textos").mkdir(parents=True)
    (root / "infraestrutura" / "textos" / "zabbix.txt").write_text(
        "O Zabbix monitora disponibilidade, serviços e reinicializações.",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question="O que acontece se eu começar a tossir, algo do tipo tosse seca?",
            history=[],
            external_allowed=True,
        )
    )
    assert response.model == "module-scope-gate"
    assert response.sources == []
    assert "Medicina" in response.answer
    assert "orientação clínica" not in response.answer.casefold()


def test_concrete_unrelated_conversation_is_blocked_before_provider(tmp_path: Path) -> None:
    """An active domain must not become a general-purpose recipe assistant."""

    response = asyncio.run(
        answer(
            root=tmp_path / "knowledge",
            module_id="direito",
            provider="auto",
            question="Quero fazer pão, me ajuda?",
            history=[],
            external_allowed=True,
        )
    )
    assert response.model == "module-scope-gate"
    assert response.sources == []
    assert "Direito" in response.answer
    assert "culinária" in response.answer
    assert "receita" not in response.answer.casefold()


def test_cross_domain_symptom_is_blocked_after_infrastructure_turn(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    (root / "infraestrutura" / "textos").mkdir(parents=True)
    (root / "infraestrutura" / "textos" / "zabbix.txt").write_text(
        "O Zabbix monitora disponibilidade, serviços e reinicializações.",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question="E o que acontece se eu começar a tossir, algo do tipo tosse seca?",
            history=[
                {"role": "user", "content": "O que normalmente tela azul significa? O Zabbix conseguiria pegar esse defeito?"},
                {"role": "assistant", "content": "A tela azul indica uma falha crítica do Windows; o Zabbix pode observar os sinais operacionais."},
            ],
            external_allowed=True,
        )
    )
    assert response.model == "module-scope-gate"
    assert response.sources == []
    assert "Medicina" in response.answer


def test_cross_domain_symptom_gate_is_shared_by_all_nonmedical_modules(tmp_path: Path) -> None:
    question = "Estou com tosse seca; o que pode ser?"
    for module_id in (
        "almoxarifado",
        "contabilidade",
        "departamento-pessoal",
        "direito",
        "financeiro",
        "gestao-empresarial",
        "infraestrutura",
        "prefeitura",
        "recursos-humanos",
        "secretaria",
    ):
        response = asyncio.run(
            answer(
                root=tmp_path / f"knowledge-{module_id}",
                module_id=module_id,
                provider="auto",
                question=question,
                history=[],
                external_allowed=True,
            )
        )
        assert response.model == "module-scope-gate"
        assert response.sources == []
        assert "Medicina" in response.answer


def test_legal_time_question_is_conditional_and_calculates_elapsed_time(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito"
    module.mkdir(parents=True)
    (module / "Vade_mecum_Senado_Federal_3ed.md").write_text(
        "Art. 58 trata da jornada e do registro de ponto. Art. 59 trata das horas extras. O repouso semanal remunerado é o DSR.",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="direito",
            provider="auto",
            question="Cheguei às 06:49 e saio às 16:10. Isso gera hora extra? Mexe no meu DSR?",
            history=[],
            external_allowed=False,
        )
    )
    assert "9h21" in response.answer
    assert "não permitem afirmar" in response.answer.casefold()
    assert "DSR" in response.answer


def test_rca_isolated_from_normal_queries_and_marks_causality_boundary(tmp_path: Path) -> None:
    assert is_rca_request("Faça uma RCA do incidente de indisponibilidade")
    assert not is_rca_request("Como configurar um trigger?")
    root = tmp_path / "knowledge"
    module = root / "infraestrutura"
    module.mkdir(parents=True)
    (module / "incidente.md").write_text(
        "O incidente de indisponibilidade ocorreu após uma falha de conectividade. O impacto observado foi a interrupção do serviço.",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question="Faça uma RCA do incidente de indisponibilidade.",
            history=[],
            external_allowed=False,
        )
    )
    assert response.model == "rca-evidence"
    assert "Fatos observados" in response.answer
    assert "causa raiz" in response.answer.casefold()
    assert "Próximos testes" in response.answer


def test_risk_average_typo_is_a_category_filter_not_a_total(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "infraestrutura"
    module.mkdir(parents=True)
    (module / "RiskyUsers.csv").write_text(
        "Nome,Nível de risco\nAlice,Alto\nBruno,Médio\nCarla,Médio\n",
        encoding="utf-8",
    )
    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question="Quantos usuários estão em risco avarege?",
            history=[],
            external_allowed=False,
        )
    )
    assert response.model == "structured-data"
    assert "2" in response.answer
    assert "605" not in response.answer
