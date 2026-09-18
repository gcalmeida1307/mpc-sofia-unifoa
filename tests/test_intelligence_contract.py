import asyncio
from pathlib import Path

import api.retrieval as retrieval_module
from api.evidence import judge_candidates
from api.ingestion import DocumentChunk, ingest_module
from api.orchestration import (
    _compact_answer,
    _compound_evidence_answer,
    _legal_harassment_answer,
    _list_elements_answer,
    _output_token_budget,
    answer,
)
from api.policies import policy_for
from api.query_analysis import (
    QueryPlan,
    decompose_query,
    is_explicit_evidence_request,
    requested_exact_term,
    route_query,
)
from api.retrieval import Evidence, RetrievalResult, retrieve, retrieve_compound

PLAN_CASES = (
    ("direito", "Me ajuda com um problema de direito?", "CONVERSA_DIRETA"),
    ("financeiro", "Bom dia", "CONVERSA_DIRETA"),
    ("recursos-humanos", "Escreva uma mensagem para uma candidata.", "WRITING"),
    ("financeiro", "O que é fluxo de caixa?", "CONVERSA_DIRETA"),
    ("infraestrutura", "Como criar um trigger no Zabbix?", "DOCUMENT_RAG"),
    ("direito", "O que diz o acordo coletivo sobre hora extra?", "DOCUMENT_RAG"),
    ("financeiro", "Resuma o arquivo de orçamento.", "DOCUMENT_RAG"),
    ("financeiro", "Quais outros cursos existem no ENAP?", "LISTA_ELEMENTOS"),
    ("financeiro", "Pode me citar outros cursos relacionados?", "LISTA_ELEMENTOS"),
    ("financeiro", "Em qual linha está o termo \"carga horária\" no arquivo cursos.md?", "BUSCA_EXATA_LINHA"),
    ("financeiro", "Qual linha 62 do arquivo cursos.md?", "BUSCA_EXATA_LINHA"),
    ("direito", "Compare o SAAE com o Vade Mecum.", "COMPARACAO_DOCUMENTOS"),
    ("direito", "Confronte os dois documentos e encontre conflitos.", "COMPARACAO_DOCUMENTOS"),
    ("medicina", "Quantos pacientes estão registrados?", "STRUCTURED_DATA"),
    ("infraestrutura", "Quantos hosts estão ativos no CSV?", "STRUCTURED_DATA"),
    ("financeiro", "Qual é a soma das despesas da planilha?", "STRUCTURED_DATA"),
    ("gestao-empresarial", "Relacione os documentos e encontre padrões.", "COMPARACAO_DOCUMENTOS"),
    ("medicina", "Faça uma inferência sobre os sintomas descritos.", "COMPLEX_REASONING"),
    ("infraestrutura", "Execute a verificação do servidor.", "EXECUCAO_MCP"),
    ("financeiro", "Quais são os documentos disponíveis?", "DOCUMENT_RAG"),
)


def test_twenty_query_plans_are_validated_before_retrieval() -> None:
    for module_id, question, expected_intent in PLAN_CASES:
        payload = route_query(module_id, question)
        plan = QueryPlan.from_mapping(
            payload["query_plan"],
            fallback_intent="DOCUMENT_RAG" if payload["retrieval_required"] else "CONVERSA_DIRETA",
            retrieval_required=payload["retrieval_required"],
            response_mode=payload["response_mode"],
        )
        assert plan.intent == expected_intent, (module_id, question, payload)
        assert plan.target_collection in {
            "ENAP_CURSOS",
            "PEP_PACIENTES",
            "INFRA_ZABBIX",
            "LEIS_VADE_MECUM",
            "MODULE_DOCUMENTS",
            "STRUCTURED_DATA",
        }
        assert plan.public_dict()["intent"] == expected_intent


def test_conversation_memory_does_not_capture_a_substantive_follow_up() -> None:
    history = [
        {
            "role": "assistant",
            "content": "Claro. Me conte o que aconteceu e eu ajudo a organizar o problema.",
        }
    ]
    legal = route_query(
        "direito",
        "É possível ter dois vínculos de carteira assinada? Um no emprego A e outro no emprego B.",
        history=history,
    )
    assert legal["task_route"] == "general_explanation"
    assert legal["retrieval_required"] is True


def test_common_small_talk_variants_stay_conversational() -> None:
    for question in ("Como vc está?", "Como você está?", "Tudo bem?"):
        route = route_query("almoxarifado", question)
        assert route["task_route"] == "conversation"
        assert route["retrieval_required"] is False


def test_concrete_legal_reporting_question_overrides_conversation_history() -> None:
    history = [
        {"role": "user", "content": "Bom dia"},
        {"role": "assistant", "content": "Bom dia! Como posso ajudar?"},
    ]
    route = route_query(
        "direito",
        "Como posso protocolar uma denúncia de abuso de poder ou assédio moral no trabalho sem me expor?",
        history=history,
    )
    assert route["task_route"] == "general_explanation"
    assert route["retrieval_required"] is True
    assert route["response_mode"] == "evidence"


def test_workplace_harassment_and_importunation_stay_in_legal_scope() -> None:
    question = "Qual a diferença entre assédio e importunação no trabalho? Posso processar a empresa?"
    route = route_query("direito", question, history=[{"role": "assistant", "content": "Bom dia! Como posso ajudar?"}])
    assert route["retrieval_required"] is True
    assert route["task_route"] in {"general_explanation", "multi_document"}


def test_legal_reporting_question_rejects_generic_employment_excerpt(tmp_path: Path) -> None:
    source = tmp_path / "Vade_mecum_Senado_Federal_3ed.pdf"
    source.write_bytes(b"placeholder")
    chunk = DocumentChunk(
        source,
        "O contrato de trabalho deve ser anotado na carteira e a rescisão deve observar os prazos legais.",
        0,
        None,
        "página 570",
        None,
        None,
        "Direito do trabalho",
        "prose",
    )
    candidate = Evidence(chunk, 0.95, 0.95, 0.7, 0.8, 0.8)
    decision = judge_candidates(
        "Como protocolar denúncia de abuso de poder ou assédio moral sem me expor?",
        "direito",
        policy_for("direito"),
        (candidate,),
    )
    assert not decision.accepted
    assert decision.rejected[0].rejection_reason == "o trecho pertence à fonte indicada, mas não trata do tema específico da pergunta"


def test_legal_reporting_answer_declares_missing_anonymity_rule() -> None:
    root = Path(__file__).resolve().parents[1] / "knowledge"
    question = "Como posso protocolar uma denúncia de abuso de poder ou assédio moral sem me expor?"
    result = retrieve(root, "direito", question, policy_for("direito"), limit=6)
    response = _legal_harassment_answer(question, result, "pt-BR")
    assert response is not None
    assert "CIPA" in response
    assert "não encontrei" in response.casefold()
    assert "anônima" in response


def test_exact_term_plan_and_source_lookup_use_real_lines(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "financeiro" / "textos"
    module.mkdir(parents=True)
    source = module / "cursos.md"
    source.write_text("Cabeçalho\n\nCarga horária\n20h\n", encoding="utf-8")
    question = 'Em qual linha está o termo "Carga horária" no arquivo cursos.md?'

    assert requested_exact_term(question) == "Carga horária"
    plan = route_query("financeiro", question)["query_plan"]
    assert plan["intent"] == "BUSCA_EXATA_LINHA"
    assert plan["requires_exact_match"] is True

    result = retrieve(root, "financeiro", question, policy_for("financeiro"), limit=4)
    assert result.has_quality_evidence
    assert result.sources == ("cursos.md",)
    assert result.evidence[0].chunk.locator == "linha 3"
    assert result.evidence[0].chunk.start_line == 3


def test_named_source_query_keeps_the_complete_module_index(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "knowledge"
    module = root / "financeiro" / "textos"
    module.mkdir(parents=True)
    first = module / "manual-a.md"
    second = module / "manual-b.md"
    first.write_text("# Manual A\n\nProcedimento para conciliação bancária.\n", encoding="utf-8")
    second.write_text("# Manual B\n\nProcedimento para fechamento mensal.\n", encoding="utf-8")
    calls: list[tuple[Path, ...]] = []
    original = retrieval_module.ingest_module

    def spy_ingest(root_path, module_id, selected_paths=None, **kwargs):
        calls.append(tuple(selected_paths or ()))
        return original(root_path, module_id, selected_paths=selected_paths, **kwargs)

    monkeypatch.setattr(retrieval_module, "ingest_module", spy_ingest)
    retrieval_module._index.cache_clear()
    retrieval_module._normalized_index.cache_clear()
    result = retrieve(
        root,
        "financeiro",
        "Resuma o arquivo manual-a.md.",
        policy_for("financeiro"),
        limit=4,
    )

    assert result.sources == ("manual-a.md",)
    assert calls
    assert set(calls[-1]) == {first, second}


def test_generic_legal_question_does_not_select_a_marketing_slug_as_source() -> None:
    root = Path(__file__).resolve().parents[1] / "knowledge"
    result = retrieve(
        root,
        "direito",
        "o que é direito trabalhista?",
        policy_for("direito"),
        limit=6,
    )
    assert result.sources == ("Vade_mecum_Senado_Federal_3ed.pdf",)
    assert all("iatrabalhista" not in source.casefold() for source in result.sources)


def test_quoted_term_without_line_request_does_not_trigger_exact_lookup() -> None:
    payload = route_query("direito", 'Explique o termo "mandado de segurança".')
    assert payload["query_plan"]["intent"] != "BUSCA_EXATA_LINHA"


def test_catalog_chunks_keep_section_and_content_metadata(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "financeiro" / "links"
    module.mkdir(parents=True)
    source = module / "catalogo.md"
    source.write_text(
        "# Catálogo\n\nCursos Relacionados\n\nCurso de Orçamento Público\nCurso de Gestão de Riscos\n",
        encoding="utf-8",
    )

    chunks = ingest_module(root, "financeiro")
    assert chunks
    assert all(chunk.content_type == "list_catalog" for chunk in chunks)
    assert any(chunk.start_line is not None and chunk.end_line is not None for chunk in chunks)
    assert any(chunk.section_header == "Catálogo" for chunk in chunks)


def test_list_composer_does_not_use_comparison_envelope() -> None:
    path = Path("catalogo.md")
    chunks = (
        DocumentChunk(
            path,
            "Cursos Relacionados\nCurso de Orçamento Público\nCurso de Gestão de Riscos",
            0,
            None,
            "linhas 10-12",
            10,
            12,
            "Cursos Relacionados",
            "list_catalog",
        ),
    )
    result = RetrievalResult(
        (Evidence(chunks[0], 0.9, 0.9, 0.9, 0.9, 0.9),),
        (path.name,),
        "pergunta",
        "pergunta",
        judge_confidence=0.9,
    )
    response = _list_elements_answer("Pode me citar outros cursos?", result, "pt-BR")
    assert response is not None
    assert "Curso de Orçamento Público" in response
    assert "Curso de Gestão de Riscos" in response
    assert "[E1]" not in response and "[E2]" not in response
    assert "leitura conjunta" not in response.casefold()


def test_answer_cleanup_preserves_response_structure_and_length() -> None:
    answer_text = (
        "Procedimento:\n"
        "1. Identifique o alvo.\n"
        "2. Valide a conectividade.\n"
        "3. Confira os logs.\n"
        "4. Compare o horário do incidente.\n"
        "5. Registre a evidência.\n"
        "6. Aplique a correção.\n"
        "7. Confirme a recuperação."
    )
    cleaned = _compact_answer(answer_text, "como investigar", "")
    assert "6. Aplique a correção." in cleaned
    assert "7. Confirme a recuperação." in cleaned
    assert "→" not in cleaned


def test_output_budget_is_configurable_without_the_old_silent_ceiling(monkeypatch) -> None:
    monkeypatch.delenv("SOFIA_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("SOFIA_DETAILED_OUTPUT_TOKENS", raising=False)
    assert _output_token_budget("detailed") >= 4096
    monkeypatch.setenv("SOFIA_DETAILED_OUTPUT_TOKENS", "8192")
    assert _output_token_budget("detailed") == 8192


def test_source_gate_uses_word_boundaries_for_single_word_markers() -> None:
    assert is_explicit_evidence_request("O que diz a lei sobre jornada?")
    assert not is_explicit_evidence_request("Leia esta explicação com calma.")


def test_real_enap_list_question_uses_list_composer() -> None:
    root = Path(__file__).resolve().parents[1] / "knowledge"
    question = "Eu vi que existem temas relacionados ao ENAP, como Introdução à Regularização Fundiária Urbana, pode me citar outros?"
    response = asyncio.run(
        answer(
            root=root,
            module_id="financeiro",
            provider="auto",
            question=question,
            history=[],
            response_style="structured",
            external_allowed=False,
        )
    )
    assert response.model == "local-source-evidence"
    assert "Introdução à Regularização Fundiária Urbana" not in response.answer.split("Além do curso citado", 1)[-1].split("Esses itens", 1)[0]
    assert "Instrumentos de Desenvolvimento Urbano Sustentável" in response.answer
    assert "[E1]" not in response.answer and "[E2]" not in response.answer
    assert "leitura conjunta" not in response.answer.casefold()


def test_named_prose_summary_cannot_fall_into_unrelated_structured_file(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "infraestrutura" / "textos"
    module.mkdir(parents=True)
    (module / "manual-rede.md").write_text(
        "# Manual de rede\n\nO procedimento registra a disponibilidade dos servidores diariamente.\n"
        "A equipe deve revisar os alertas e documentar cada incidente.\n",
        encoding="utf-8",
    )
    (module / "RiskyUsers.csv").write_text(
        "Nome,Nível de risco\nAlice,Alto\nBruno,Médio\n",
        encoding="utf-8",
    )

    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question="Resuma em duas frases o documento manual-rede.md.",
            history=[],
            response_style="concise",
            external_allowed=False,
        )
    )
    assert response.sources == ["manual-rede.md"]
    assert "RiskyUsers.csv" not in response.answer
    assert "servidores" in response.answer.casefold()
    assert response.model != "structured-data"


def test_structured_file_summary_reports_schema_without_returning_rows(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "infraestrutura" / "textos"
    module.mkdir(parents=True)
    (module / "RiskyUsers.csv").write_text(
        "Nome,Nível de risco\nAlice,Alto\nBruno,Médio\n",
        encoding="utf-8",
    )

    response = asyncio.run(
        answer(
            root=root,
            module_id="infraestrutura",
            provider="auto",
            question="Resuma o arquivo RiskyUsers.csv.",
            history=[],
            response_style="concise",
            external_allowed=False,
        )
    )
    assert response.model == "structured-data"
    assert "RiskyUsers.csv" in response.answer
    assert "Nível de risco" in response.answer
    assert "Alice" not in response.answer and "Bruno" not in response.answer


def test_compound_query_decomposes_topic_and_source_handoffs() -> None:
    question = "Posso eu exceder duas horas extras no dia? O que o SAAE? E o que diz o VADE? O que há de comum e diferente entre os dois nesse ponto?"
    parts = decompose_query(question)
    assert len(parts) == 4
    assert "horas extras" in parts[0].casefold()
    assert "saae" in parts[1].casefold()
    assert "vade" in parts[2].casefold()
    assert "comum" in parts[3].casefold()


def test_compound_retrieval_requires_and_keeps_both_named_documents(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito" / "textos"
    module.mkdir(parents=True)
    (module / "SAAE.md").write_text(
        "Cláusula 5ª: o excesso de horas em um dia pode ser compensado em outro, dentro de 360 dias.\n",
        encoding="utf-8",
    )
    (module / "Vade_Mecum.md").write_text(
        "Art. 59. A duração diária pode ser acrescida de horas extras, em número não excedente de duas, com adicional de 50%.\n",
        encoding="utf-8",
    )
    question = "Posso exceder duas horas extras? O que o SAAE e o Vade dizem? Compare os dois."
    result = retrieve_compound(
        root, "direito", question, decompose_query(question), policy_for("direito"), limit=6
    )
    assert result.has_quality_evidence
    assert result.missing_sources == ()
    assert set(result.sources) == {"SAAE.md", "Vade_Mecum.md"}
    assert result.subqueries


def test_compound_local_composer_answers_points_and_labels_inference(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    module = root / "direito" / "textos"
    module.mkdir(parents=True)
    (module / "SAAE.md").write_text(
        "Cláusula 5ª: o excesso de horas em um dia pode ser compensado em outro, dentro de 360 dias.\n",
        encoding="utf-8",
    )
    (module / "Vade_Mecum.md").write_text(
        "Art. 59. A duração diária pode ser acrescida de horas extras, em número não excedente de duas, com adicional de 50%.\n",
        encoding="utf-8",
    )
    question = "Posso exceder duas horas extras? O que o SAAE e o Vade dizem? Compare os dois."
    result = retrieve_compound(
        root, "direito", question, decompose_query(question), policy_for("direito"), limit=6
    )
    response = _compound_evidence_answer(question, result, "pt-BR")
    assert response is not None
    assert "Resposta por ponto" in response
    assert "Leitura da Sofia (inferência)" in response
    assert "SAAE.md" in response and "Vade_Mecum.md" in response
