from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .embeddings import semantic_scores
from .ingestion import DocumentChunk, files_for, ingest_module
from .policies import ModulePolicy, expand_query
from .query_analysis import is_medical_sleep_query


@dataclass(frozen=True)
class Evidence:
    chunk: DocumentChunk
    score: float
    lexical_score: float
    semantic_score: float
    coverage: float
    bm25_score: float = 0.0


@dataclass(frozen=True)
class RetrievalResult:
    evidence: tuple[Evidence, ...]
    sources: tuple[str, ...]
    query: str
    expanded_query: str

    @property
    def has_quality_evidence(self) -> bool:
        return bool(self.evidence)

    @property
    def context(self) -> str:
        return "\n\n--- DOCUMENTO: ".join(f"{item.chunk.path.name}\n{item.chunk.text}" for item in self.evidence)


def normalize(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(char))


def _terms(query: str) -> set[str]:
    stopwords = {
        "a", "as", "ao", "aos", "de", "do", "dos", "da", "das", "e", "em", "um", "uma", "o", "os", "que", "me",
        "fale", "falar", "sobre", "como", "qual", "quais", "para", "por", "indica", "indicar", "significa", "significado",
        "explique", "explicar", "diga", "dizer", "mostre", "mostrar", "pode", "ser", "sao", "tem", "existe",
    }
    return {
        term
        for term in re.findall(r"[\w]+", normalize(query))
        if (len(term) > 2 or term.isdigit()) and term not in stopwords
    }


def _token_set(text: str) -> set[str]:
    return set(re.findall(r"[\w]+", normalize(text)))


def _matched_terms(terms: set[str], tokens: set[str], normalized_text: str) -> int:
    """Match full tokens and simple inflections without inventing evidence."""
    matched = 0
    for term in terms:
        if term in tokens or any(token.startswith(term) or term.startswith(token) for token in tokens if len(token) > 3) or term in normalized_text:
            matched += 1
    return matched


def _bm25_score(query_terms: set[str], text: str, average_length: float) -> float:
    """Small dependency-free BM25 scorer used before the vector reranker.

    TF-IDF remains the local vector representation; BM25 adds term frequency
    and document-length awareness so a long, loosely related PDF chunk cannot
    beat a short chunk that actually answers the question.
    """
    tokens = re.findall(r"[\w]+", text)
    if not tokens or not query_terms:
        return 0.0
    counts = Counter(tokens)
    length = len(tokens)
    k1, b = 1.35, 0.75
    total = 0.0
    for term in query_terms:
        frequency = counts.get(term, 0)
        if frequency:
            total += (frequency * (k1 + 1)) / (frequency + k1 * (1 - b + b * length / max(1.0, average_length)))
    return min(1.0, total / max(1.0, len(query_terms) * 1.5))


def _is_classification_source(path: Path) -> bool:
    name = normalize(path.name)
    return any(marker in name for marker in ("cid-", "cid_", "icd-", "icd_", "cif", "classific"))


def _is_clinical_source(path: Path) -> bool:
    name = normalize(path.name)
    return any(
        marker in name
        for marker in (
            "clinical",
            "guideline",
            "guidance",
            "sleep",
            "sono",
            "protocol",
            "protocolo",
            "consensus",
            "consenso",
            "nih",
            "nhlbi",
            "cdc",
        )
    )


def _summary_quality(text: str) -> float:
    """Score a chunk for a knowledge summary, not for a user question."""
    normalized = normalize(text).strip()
    words = re.findall(r"[\w]+", normalized)
    if not words:
        return -1.0
    score = min(1.0, len(words) / 90)
    sentence_count = len(re.findall(r"[.!?](?:\s|$)", text))
    score += min(0.75, sentence_count * 0.15)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    short_line_ratio = sum(len(line) < 45 for line in lines) / max(1, len(lines))
    score -= min(0.90, short_line_ratio * 1.10)
    if text.lstrip().startswith(("#", "##")):
        score += 0.12
    if any(marker in normalized for marker in ("fonte:", "capturado em:", "paginas no dominio:", "url:")):
        score -= 0.8
    chrome_markers = (
        "menu",
        "buscar",
        "filtrar",
        "ir para",
        "chevron",
        "expand less",
        "rolar para",
        "termos mais buscados",
        "carga horaria",
        "comunicados em destaque",
        "resultados da pesquisa",
        "servicos relacionados",
        "mais informacoes",
        "links de compartilhamento",
        "redefinir cookies",
        "todo o conteudo deste site",
        "redes sociais",
    )
    score -= min(0.65, sum(marker in normalized for marker in chrome_markers) * 0.10)
    if normalized.startswith(("comunicados em destaque", "servicos relacionados", "do govbr", "home acesso a informacao", "siconfi - api de dados abertos acessibilidade", "pronunciamentos cbps")):
        score -= 0.90
    # A chunk made mostly of labels, links or catalogue navigation is not a
    # useful explanation even when it is long.
    if len(words) < 12 and not re.search(r"[.!?]", text):
        score -= 0.35
    return score


def _has_any_marker(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _explicit_source_paths(paths: list[Path], query: str, query_terms: set[str]) -> list[Path]:
    """Select a named local source when the user mentions its filename."""
    ignored = {
        "arquivo", "arquivos", "documento", "documentos", "fonte", "fontes",
        "base", "bases", "dados", "texto", "textos", "imagem", "imagens",
        "link", "links", "pdf", "docx", "xlsx", "csv", "json", "pt",
        "documentation", "documentacao", "senado", "federal",
    }
    ranked: list[tuple[int, Path]] = []
    normalized_query = normalize(query)
    # File names are frequently typed with underscores, hyphens or spaces
    # (for example, ``vade_mecum``). Compare a separator-free token view so a
    # source name is not silently lost before the RAG search starts.
    source_query_terms = set(re.findall(r"[\w]+", normalized_query.replace("_", " ").replace("-", " ")))
    for path in paths:
        source_tokens = {
            token
            for token in re.findall(r"[\w]+", normalize(path.stem).replace("_", " ").replace("-", " "))
            if len(token) >= 3 and not token.isdigit() and token not in ignored
        }
        overlap = source_tokens & source_query_terms
        if not overlap:
            continue
        score = len(overlap)
        source_label = re.sub(r"[_-]+", " ", normalize(path.stem)).strip()
        if source_label and source_label.replace("_", " ").replace("-", " ") in normalized_query.replace("_", " ").replace("-", " "):
            score += 3
        ranked.append((score, path))
    if not ranked:
        return []
    # If the user names multiple files, preserve all of them. Choosing only
    # the highest lexical score made a question combining Vade Mecum + SAAE
    # discard one of the requested sources before topic retrieval.
    if len(ranked) > 1:
        return [path for _, path in ranked]
    best = max(score for score, _ in ranked)
    return [path for score, path in ranked if score == best]


@lru_cache(maxsize=32)
def _index(root_text: str, module_id: str, signature: tuple[tuple[str, int, int], ...], source_paths: tuple[str, ...] = ()) -> tuple[DocumentChunk, ...]:
    del signature
    selected_paths = tuple(Path(path) for path in source_paths) if source_paths else None
    return tuple(ingest_module(Path(root_text), module_id, selected_paths=selected_paths))


@lru_cache(maxsize=32)
def _normalized_index(root_text: str, module_id: str, signature: tuple[tuple[str, int, int], ...], source_paths: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Cache normalized chunks; normalizing all PDF text was the hot path."""
    return tuple(normalize(chunk.text) for chunk in _index(root_text, module_id, signature, source_paths))


def retrieve(root: Path, module_id: str, query: str, policy: ModulePolicy, limit: int = 6, retry: bool = False) -> RetrievalResult:
    expanded = expand_query(module_id, query)
    query_terms = _terms(query)
    expanded_terms = _terms(expanded)
    normalized_query = normalize(query)
    medical_sleep_intent = module_id == "medicina" and is_medical_sleep_query(query)
    thirteenth_intent = any(term in normalized_query for term in ("adiantamento", "decimo terceiro", "13"))
    summary_intent = any(
        phrase in normalize(query)
        for phrase in (
            "resuma o conhecimento",
            "resumo do conhecimento",
            "resuma o conteudo",
            "resumo do conteudo",
            "resuma o documento",
            "resumo do documento",
            "resumir o documento",
            "resumir documento",
            "resuma o arquivo",
            "resumo do arquivo",
            "resumir o arquivo",
            "resumir arquivo",
            "leia o documento",
            "ler o documento",
            "leia o arquivo",
            "ler o arquivo",
            "ler e responder",
            "leia e responda",
            "documentos disponiveis",
            "listar documentos",
            "liste os documentos",
            "pontos positivos",
            "pontos negativos",
            "aspectos positivos",
            "aspectos negativos",
            "o que aborda",
        )
    )
    procedural_phrases = (
        "assistente de host",
        "configurando um host",
        "hosts e grupos de hosts",
        "novo host",
        "criar e configurar um host",
        "interfaces do host",
        "clique em criar para adicionar o host",
        "adicionar o host ao zabbix",
    )
    requested_version = re.search(r"\b7[.]4\b", normalize(query))
    overtime_intent = module_id in {"direito", "departamento-pessoal"} and any(term in query_terms for term in ("hora", "horas", "extra", "extras", "jornada"))
    host_document_intent = module_id == "infraestrutura" and "host" in query_terms
    host_procedure_intent = host_document_intent and any(term in query_terms for term in ("adicionar", "adiciono", "faco", "faço", "configurar", "criar", "cadastrar"))
    legal_comparison_intent = module_id in {"direito", "departamento-pessoal"} and any(
        term in query_terms
        for term in ("brecha", "brechas", "artigo", "jurisprudencia", "sustentar", "argumento", "argumentos")
    )
    legal_review_intent = module_id in {"direito", "departamento-pessoal"} and any(
        term in query_terms
        for term in (
            "problema",
            "problemas",
            "interpretacao",
            "inconclusivo",
            "inconclusiva",
            "ambiguo",
            "ambiguidade",
            "lacuna",
            "conflito",
            "contradicao",
            "divergencia",
            "duvida",
            "duvidas",
        )
    ) and any(
        phrase in normalized_query
        for phrase in ("acordo coletivo", "convencao coletiva", "convenção coletiva")
    )
    link_source_intent = module_id in {"direito", "departamento-pessoal"} and any(
        term in query_terms for term in ("link", "links", "jurisprudencia", "jurisprudencial", "precedente", "precedentes")
    )
    all_paths = files_for(root, module_id)
    source_paths = all_paths
    named_source_paths = _explicit_source_paths(all_paths, query, query_terms)
    legal_link_paths = [path for path in all_paths if path.parent.name.casefold() == "links"]
    hr_hiring_intent = module_id == "recursos-humanos" and any(
        term.startswith(("contrat", "admiss", "recrut", "selec")) for term in query_terms
    )
    accounting_balance_intent = module_id == "contabilidade" and (
        any(term.startswith(("balan", "patrimonial")) for term in query_terms)
        or "balanco patrimonial" in normalized_query
    )
    dp_definition_intent = module_id == "departamento-pessoal" and "departamento pessoal" in normalized_query
    source_overview_intent = False
    if named_source_paths:
        source_paths = named_source_paths
        if retry:
            # A negative-feedback recovery pass may have just added public
            # links, OCR images or anonymized offline candidates. Preserve
            # the explicitly named file but allow those newly captured items
            # to participate in the retry RAG.
            recovery_paths = [
                path
                for path in all_paths
                if path.parent.name.casefold() in {"links", "research", "offline"}
            ]
            source_paths = list(dict.fromkeys([*source_paths, *recovery_paths]))
        if link_source_intent and legal_link_paths:
            # “Links” é uma classe de fontes, não um arquivo único. Mantemos
            # SAAE/Vade e adicionamos os artefatos offline dessa classe para a
            # comparação poder separar lei, acordo e jurisprudência.
            source_paths = list(dict.fromkeys([*source_paths, *legal_link_paths]))
        source_request_terms = {
            "responda", "responder", "baseado", "baseada", "arquivo", "documento",
            "fonte", "fontes", "leia", "ler", "consulte", "consultar", "use", "usar",
            "conhecimento", "disponivel", "disponiveis", "pontos", "positivo", "positivos",
            "negativo", "negativos", "aspectos", "aborda", "abordados", "quais", "fale", "fala",
            "faca", "fazer", "resumir", "consegue", "base", "existir", "existe",
        }
        # Um pedido que só identifica o arquivo, sem formular um tema, deve
        # resumir o arquivo selecionado. O nome do arquivo não aparece no
        # texto extraído do PDF e, portanto, não pode ser usado como termo
        # lexical para encontrar um chunk.
        source_name_terms = {
            token
            for path in named_source_paths
            for token in re.findall(r"[\w]+", normalize(path.stem).replace("_", " ").replace("-", " "))
            if len(token) >= 3
        }
        if not (query_terms - source_request_terms - source_name_terms):
            summary_intent = True
        if module_id in {"direito", "departamento-pessoal"} and any(term in query_terms for term in ("direito", "direitos")):
            source_overview_intent = True
            summary_intent = True
    elif module_id in {"direito", "departamento-pessoal"} and any(
        phrase in normalize(query)
        for phrase in ("acordo coletivo", "convencao coletiva", "convenção coletiva")
    ):
        # Quando o usuário diz apenas “o arquivo do acordo coletivo”, use o
        # documento local cujo nome identifica o instrumento (SAAE, acordo,
        # convenção ou sindicato), em vez do Vade Mecum genérico.
        agreement_paths = [
            path
            for path in all_paths
            if any(marker in normalize(path.stem) for marker in ("saae", "acordo", "convenc", "coletiv", "sindicato"))
        ]
        if agreement_paths:
            source_paths = agreement_paths
            if any(term in query_terms for term in ("direito", "direitos")):
                source_overview_intent = True
                summary_intent = True
    elif link_source_intent and legal_link_paths:
        source_paths = legal_link_paths
    if legal_comparison_intent and legal_link_paths and named_source_paths:
        source_paths = list(dict.fromkeys([*named_source_paths, *legal_link_paths]))
    if host_document_intent:
        zabbix_paths = [path for path in all_paths if "zabbix_documentation" in path.name.casefold()]
        if requested_version:
            versioned_paths = [path for path in zabbix_paths if "7.4" in path.name]
            source_paths = versioned_paths or zabbix_paths or all_paths
        elif zabbix_paths:
            preferred = [path for path in zabbix_paths if "7.4" in path.name]
            source_paths = preferred or zabbix_paths
    bridge_day_intent = module_id in {"direito", "departamento-pessoal"} and (
        "dia ponte" in normalized_query or "dias ponte" in normalized_query
    )
    if bridge_day_intent and not named_source_paths:
        agreement_paths = [
            path
            for path in all_paths
            if any(marker in normalize(path.stem) for marker in ("saae", "acordo", "convenc", "coletiv", "sindicato"))
        ]
        if agreement_paths:
            source_paths = agreement_paths
    if medical_sleep_intent:
        # CID/CIF/ICD are classification vocabularies. They can support a
        # code lookup, but cannot be the primary evidence for a symptom
        # assessment. Prefer explicitly named clinical guidance and let the
        # chunk-level filter below catch newly ingested clinical files whose
        # filename does not follow a convention.
        clinical_paths = [
            path for path in source_paths
            if _is_clinical_source(path) and not _is_classification_source(path)
        ]
        if clinical_paths:
            source_paths = clinical_paths
    signature = tuple(sorted((str(path), path.stat().st_mtime_ns, path.stat().st_size) for path in source_paths))
    source_path_keys = tuple(str(path) for path in source_paths)
    chunks = _index(str(root), module_id, signature, source_path_keys)
    normalized_index = _normalized_index(str(root), module_id, signature, source_path_keys)
    if medical_sleep_intent:
        clinical_markers = (
            "microssono",
            "microsleep",
            "sonolencia diurna",
            "privacao de sono",
            "sono insuficiente",
            "apneia obstrutiva do sono",
            "sleep deprivation",
            "driver fatigue",
        )
        eligible = [
            (chunk, text)
            for chunk, text in zip(chunks, normalized_index)
            if not _is_classification_source(chunk.path)
            and (_is_clinical_source(chunk.path) or any(marker in text for marker in clinical_markers))
        ]
        chunks = tuple(chunk for chunk, _ in eligible)
        normalized_index = tuple(text for _, text in eligible)
        if not chunks:
            return RetrievalResult((), (), query, expanded)
    if not summary_intent and hr_hiring_intent:
        # The HR captures currently contain catalogue navigation and public
        # procurement courses. Do not let the word “contratação” make those
        # pages answer a people/admission question.
        hiring_markers = (
            "recrutamento",
            "admissao",
            "documentos admissionais",
            "vinculo empregaticio",
            "contratacao de pessoal",
            "contratacao de servidor",
            "integracao de novos",
            "selecao de pessoas",
            "entrevista de selecao",
        )
        eligible = [(chunk, text) for chunk, text in zip(chunks, normalized_index) if _has_any_marker(text, hiring_markers)]
        if not eligible:
            return RetrievalResult((), (), query, expanded)
        chunks = tuple(chunk for chunk, _ in eligible)
        normalized_index = tuple(text for _, text in eligible)
    if not summary_intent and accounting_balance_intent:
        # A list of CPC titles or a government “balanço” dashboard is not a
        # step-by-step balance-sheet source. Require accounting vocabulary that
        # can actually support the requested explanation.
        balance_markers = (
            "balanco patrimonial",
            "ativo circulante",
            "passivo circulante",
            "patrimonio liquido",
            "demontracoes contabeis",
            "demonstracoes contabeis",
            "notas explicativas",
        )
        eligible = [
            (chunk, text)
            for chunk, text in zip(chunks, normalized_index)
            if sum(marker in text for marker in balance_markers) >= 2
        ]
        if not eligible:
            return RetrievalResult((), (), query, expanded)
        chunks = tuple(chunk for chunk, _ in eligible)
        normalized_index = tuple(text for _, text in eligible)
    if not summary_intent and dp_definition_intent:
        # eSocial menu pages are relevant to a DP operation but do not explain
        # the role of the department. Require a definition or a cluster of
        # concrete routines before returning an answer to “o que faz”.
        role_markers = (
            "departamento pessoal",
            "rotinas trabalhistas",
            "folha de pagamento",
            "admissao",
            "ferias",
            "rescisao",
            "registro de empregados",
        )
        definition_markers = ("responsavel", "atribuicoes", "compete", "rotinas", "setor", "area")
        eligible = [
            (chunk, text)
            for chunk, text in zip(chunks, normalized_index)
            if _has_any_marker(text, ("departamento pessoal",))
            or (sum(marker in text for marker in role_markers) >= 3 and _has_any_marker(text, definition_markers))
        ]
        if not eligible:
            return RetrievalResult((), (), query, expanded)
        chunks = tuple(chunk for chunk, _ in eligible)
        normalized_index = tuple(text for _, text in eligible)
    if not chunks:
        return RetrievalResult((), (), query, query)
    if summary_intent:
        # A summary request has no single lexical topic. Select the best
        # explanatory chunk per source, instead of taking ordinal 0 (which is
        # commonly the website menu captured before the article).
        summary_chunks = chunks
        text_by_key = {(str(chunk.path), chunk.ordinal): text for chunk, text in zip(chunks, normalized_index)}
        if source_overview_intent:
            overview_terms = ("direito", "direitos", "remuneracao", "salario", "jornada", "ferias", "beneficio", "adicional", "licenca")
            relevant_chunks = [
                chunk
                for chunk in chunks
                if any(term in text_by_key[(str(chunk.path), chunk.ordinal)] for term in overview_terms)
            ]
            if relevant_chunks:
                summary_chunks = tuple(relevant_chunks)
        representatives: list[DocumentChunk] = []
        seen_sources: set[str] = set()
        best_by_source: dict[str, DocumentChunk] = {}
        for chunk in summary_chunks:
            source = chunk.path.name.casefold()
            current = best_by_source.get(source)
            if current is None or _summary_quality(text_by_key[(str(chunk.path), chunk.ordinal)]) > _summary_quality(text_by_key[(str(current.path), current.ordinal)]):
                best_by_source[source] = chunk
        for chunk in summary_chunks:
            source = chunk.path.name.casefold()
            if source not in seen_sources and best_by_source.get(source) == chunk:
                representatives.append(chunk)
                seen_sources.add(source)
        remaining = sorted(
            (chunk for chunk in summary_chunks if chunk not in representatives),
            key=lambda chunk: _summary_quality(text_by_key[(str(chunk.path), chunk.ordinal)]),
            reverse=True,
        )
        for chunk in remaining:
            if chunk not in representatives:
                representatives.append(chunk)
            if len(representatives) >= limit:
                break
        evidence = tuple(Evidence(chunk, 0.55, 0.55, 0.0, 1.0) for chunk in representatives[:limit])
        return RetrievalResult(evidence, tuple(dict.fromkeys(chunk.path.name for chunk in representatives[:limit])), query, expanded)
    pre_ranked: list[tuple[float, int, str, int, int, float, float]] = []
    for index, chunk in enumerate(chunks):
        text = normalized_index[index]
        # A substring prefilter is deliberately used here: tokenization of
        # thousands of PDF chunks is expensive. Exact token/inflection checks
        # are applied only to the small semantic candidate pool below.
        tokens = _token_set(text)
        matched = _matched_terms(query_terms, tokens, text)
        expanded_matched = _matched_terms(expanded_terms, tokens, text)
        direct_coverage = matched / max(1, len(query_terms))
        expansion_coverage = min(1.0, (matched + expanded_matched * 0.35) / max(1, len(query_terms)))
        coverage = max(direct_coverage, expansion_coverage)
        lexical = min(1.0, (matched * 0.65 + expanded_matched * 0.12) / max(1, len(query_terms)))
        procedure_boost = 0.18 if any(phrase in text for phrase in procedural_phrases) and any(term in query_terms for term in ("host", "adiciono", "adicionar", "configurar", "configurando", "criar")) else 0.0
        version_boost = 0.16 if requested_version and "7.4" in chunk.path.name else 0.0
        host_page_boost = 0.30 if "/config/hosts/host" in text else 0.0
        overtime_boost = 0.42 if overtime_intent and ("art. 59." in text or "duracao diaria do trabalho podera ser acrescida" in text or "numero nao excedente de duas" in text) else 0.0
        zabbix_pdf_boost = 0.36 if host_procedure_intent and "zabbix_documentation" in chunk.path.name.casefold() else 0.0
        medical_boost = 0.34 if module_id == "medicina" and any(term in text for term in ("gripe", "influenza")) else 0.0
        medical_sleep_boost = 0.62 if medical_sleep_intent and any(term in text for term in ("microssono", "privacao de sono", "7 a 9", "apneia obstrutiva do sono", "nao dirija")) else 0.0
        thirteenth_boost = 0.48 if thirteenth_intent and "decimo terceiro salario" in text else 0.0
        cheap_score = 0.28 * lexical + 0.22 * coverage + procedure_boost + version_boost + host_page_boost + overtime_boost + zabbix_pdf_boost + medical_boost + medical_sleep_boost + thirteenth_boost
        if matched or expanded_matched:
            pre_ranked.append((cheap_score, index, text, matched, expanded_matched, lexical, coverage))
    if legal_comparison_intent:
        # Uma pergunta de comparação pode não repetir o assunto da cláusula
        # (“quais brechas...?”). Semeamos candidatos pelos marcadores legais
        # dos arquivos selecionados para não depender de uma palavra temática
        # que o usuário não foi obrigado a informar.
        comparison_markers = (
            "horas extras",
            "horas suplementares",
            "horas extraordinarias",
            "dias pontes",
            "jornada de trabalho",
            "banco de horas",
            "compensacao",
            "art. 59.",
            "jurisprudencia",
            "precedentes",
            "acordao",
            "recurso especial",
        )
        existing_indexes = {item[1] for item in pre_ranked}
        for index, text in enumerate(normalized_index):
            if index not in existing_indexes and any(marker in text for marker in comparison_markers):
                pre_ranked.append((0.12, index, text, 1, 0, 0.10, 0.10))
    if legal_review_intent:
        # Perguntas de revisão (“há ambiguidade?”, “o texto é conclusivo?”)
        # não repetem necessariamente o assunto de uma cláusula. Semeamos
        # as cláusulas que definem escopo, compensação, solução de conflitos,
        # controle de jornada e vigência para que a análise compare o texto
        # real do instrumento, em vez de cair no gate de evidência vazia.
        review_markers = (
            "regula as relacoes de trabalho",
            "clausula 5",
            "360 dias",
            "horas extras nao compensadas",
            "dias pontes",
            "problemas oriundos da aplicacao",
            "clausula 25",
            "portaria 671",
            "clausula 31",
            "clausula 32",
            "vigencia da presente convencao",
        )
        existing_indexes = {item[1] for item in pre_ranked}
        for index, text in enumerate(normalized_index):
            if index not in existing_indexes and any(marker in text for marker in review_markers):
                pre_ranked.append((0.14, index, text, 1, 0, 0.10, 0.10))
    if not pre_ranked:
        return RetrievalResult((), (), query, expanded)
    absence_terms = ("falta", "faltas", "faltou", "faltar", "faltando", "ausencia", "ausencias", "ausente")
    absence_intent = any(term in query_terms for term in absence_terms)
    compensation_intent = any(term in query_terms for term in ("compensacao", "compensar", "compensada", "compensadas", "compense", "diferenca", "repor", "devendo", "negativas", "negativa", "saldo"))
    negative_hours_intent = any(term in query_terms for term in ("negativas", "negativa", "saldo", "devedoras", "devedor"))
    explicit_overtime_context = any(
        phrase in normalized_query
        for phrase in (
            "hora extra",
            "horas extras",
            "hora suplementar",
            "horas suplementares",
            "banco de horas",
        )
    )
    topic_terms = [term for term in ("assedio",) if term in query_terms]
    if absence_intent:
        # "faltar" também aparece em dispositivos legais com outro sentido
        # (por exemplo, faltar ao serviço em uma hipótese específica). Não
        # devemos transformar esse match isolado em uma resposta sobre falta
        # parcial, desconto ou punição. Só liberamos a evidência quando o
        # trecho realmente trata de uma consequência trabalhista da ausência.
        absence_policy_terms = (
            "falta injustificada",
            "faltas injustificadas",
            "ausencia injustificada",
            "desconto salarial",
            "desconto do salario",
            "desconto de salario",
            "perda do salario",
            "falta grave",
            "desconto do repouso",
            "repouso semanal remunerado",
        )
        explicit_absence_policy_query = any(
            phrase in normalized_query
            for phrase in (
                "falta injustificada",
                "faltas injustificadas",
                "ausencia injustificada",
                "abandono de emprego",
            )
        )
        if not explicit_absence_policy_query:
            return RetrievalResult((), (), query, expanded)
        pre_ranked = [
            item
            for item in pre_ranked
            if any(marker in item[2] for marker in absence_policy_terms)
        ]
        if not pre_ranked:
            return RetrievalResult((), (), query, expanded)
    if compensation_intent:
        compensation_terms = ("compens", "banco de horas", "saldo", "repor", "diferenca")
        if not explicit_overtime_context and any(
            term in query_terms
            for term in ("diferenca", "repor", "devendo")
        ):
            # Mantém a evidência sobre compensação de horas suplementares para
            # que a resposta possa explicar a diferença entre esse instituto
            # e a reposição de uma ausência, sem tratá-los como equivalentes.
            pre_ranked = [
                item
                for item in pre_ranked
                if "horas suplementares" in item[2]
                and "semana imediatamente posterior" in item[2]
            ]
        else:
            pre_ranked = [item for item in pre_ranked if any(term in item[2] for term in compensation_terms)]
        if not pre_ranked:
            return RetrievalResult((), (), query, expanded)
    if negative_hours_intent:
        # Acordos coletivos nem sempre usam a expressão informal “hora
        # negativa”. Também podem tratar o tema como compensação, diminuição
        # correspondente ou hora extra não compensada. Mantemos esses
        # equivalentes para que a resposta explique a terminologia real da
        # fonte, sem inventar uma cláusula com o nome usado na pergunta.
        negative_hour_markers = (
            "negativ",
            "saldo devedor",
            "compensacao",
            "diminuicao correspondente",
            "horas extras nao compensadas",
            "horas suplementares nao compensadas",
        )
        pre_ranked = [item for item in pre_ranked if any(marker in item[2] for marker in negative_hour_markers)]
        if not pre_ranked:
            return RetrievalResult((), (), query, expanded)
    if topic_terms:
        pre_ranked = [item for item in pre_ranked if any(topic in item[2] for topic in topic_terms)]
        if not pre_ranked:
            return RetrievalResult((), (), query, expanded)
        sanction_terms = ("puni", "sancao", "pena", "penalidade", "advertencia", "demissao", "justa causa", "multa")
        if any(term in query_terms for term in ("punicao", "puni", "pena", "penalidade", "sancao")):
            topic_pattern = "|".join(topic_terms)
            pre_ranked = [
                item
                for item in pre_ranked
                if re.search(rf"(?:{topic_pattern}).{{0,800}}(?:{'|'.join(sanction_terms)})", item[2])
            ]
            if not pre_ranked:
                return RetrievalResult((), (), query, expanded)
    # O índice semântico só precisa comparar os candidatos que têm relação
    # lexical ou por intenção. Isso mantém PDFs extensos responsivos sem
    # eliminar a busca em todos os módulos físicos.
    candidate_pool = max(60, limit * 25)
    pre_ranked = sorted(pre_ranked, key=lambda item: item[0], reverse=True)[:candidate_pool]
    normalized_chunks = [item[2] for item in pre_ranked]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    matrix = vectorizer.fit_transform(normalized_chunks + [normalize(expanded)])
    semantic = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    neural_scores = semantic_scores(root, module_id, expanded)
    neural_weight = 0.16 if neural_scores else 0.0
    tfidf_weight = 0.34 - neural_weight
    average_length = sum(len(text.split()) for text in normalized_chunks) / max(1, len(normalized_chunks))
    candidates: list[Evidence] = []
    for local_index, (_, index, text, matched, expanded_matched, lexical, coverage) in enumerate(pre_ranked):
        chunk = chunks[index]
        # A semantic expansion can map “adiciono” a “novo/configurando” e
        # “host” a “dispositivo/monitorado”, mas o contexto final continua
        # sendo exclusivamente o texto do documento.
        procedure_boost = 0.18 if any(phrase in text for phrase in procedural_phrases) and any(term in query_terms for term in ("host", "adiciono", "adicionar", "configurar", "configurando", "criar")) else 0.0
        version_boost = 0.16 if requested_version and "7.4" in chunk.path.name else 0.0
        host_page_boost = 0.30 if "/config/hosts/host" in text else 0.0
        overtime_boost = 0.42 if overtime_intent and ("art. 59." in text or "duracao diaria do trabalho podera ser acrescida" in text or "numero nao excedente de duas" in text) else 0.0
        zabbix_pdf_boost = 0.36 if host_procedure_intent and "zabbix_documentation" in chunk.path.name.casefold() else 0.0
        medical_boost = 0.34 if module_id == "medicina" and any(term in text for term in ("gripe", "influenza")) else 0.0
        medical_sleep_boost = 0.62 if medical_sleep_intent and any(term in text for term in ("microssono", "privacao de sono", "7 a 9", "apneia obstrutiva do sono", "nao dirija")) else 0.0
        thirteenth_boost = 0.48 if thirteenth_intent and "decimo terceiro salario" in text else 0.0
        # O reranker privilegia cobertura e frase exata, sem deixar similaridade
        # genérica de TF-IDF passar sozinha pelo gate.
        exact_phrase = 0.25 if normalize(query) in text else 0.0
        bm25 = _bm25_score(query_terms, text, average_length)
        neural_score = neural_scores.get((str(chunk.path), chunk.ordinal), 0.0)
        score = tfidf_weight * float(semantic[local_index]) + neural_weight * neural_score + 0.24 * lexical + 0.20 * coverage + 0.14 * bm25 + procedure_boost + version_boost + host_page_boost + overtime_boost + zabbix_pdf_boost + medical_boost + medical_sleep_boost + thirteenth_boost + exact_phrase
        candidates.append(Evidence(chunk, score, max(lexical, bm25), max(float(semantic[local_index]), neural_score), coverage, bm25))
    if requested_version:
        versioned = [item for item in candidates if "7.4" in item.chunk.path.name]
        if versioned:
            candidates = versioned
    ranked = sorted(candidates, key=lambda item: item.score, reverse=True)
    source_specific_multi_topic = False
    multi_topic_source_intent = (
        len(named_source_paths) > 1
        and any(term in query_terms for term in ("hora", "horas", "extra", "extras", "jornada"))
        and any(term in query_terms for term in ("adiantamento", "13", "decimo", "terceiro"))
    )
    if multi_topic_source_intent:
        # Uma pergunta que cita mais de uma fonte e mais de um assunto precisa
        # manter uma evidência por assunto. O ranking global costumava deixar
        # um Vade Mecum extenso ocupar todas as posições e descartava o SAAE.
        topic_definitions = (
            (("horas extras", "hora extra", "horas suplementares", "jornada"), ("saae", "acordo", "coletiv")),
            (("decimo terceiro", "gratificacao natalina", "adiantamento", "13o"), ("vade",)),
        )
        topic_items: list[Evidence] = []
        for markers, preferred_sources in topic_definitions:
            pool = [item for item in candidates if any(marker in normalize(item.chunk.text) for marker in markers)]
            preferred = [item for item in pool if any(marker in normalize(item.chunk.path.stem) for marker in preferred_sources)]
            pool = preferred or pool
            # Um trecho representativo por assunto evita que um documento
            # extenso ocupe todo o contexto e reduz ruído para o provider.
            topic_items.extend(sorted(pool, key=lambda item: item.score, reverse=True)[:1])
        if topic_items:
            seen_chunks: set[tuple[str, int]] = set()
            ordered: list[Evidence] = []
            for item in topic_items + ranked:
                key = (str(item.chunk.path), item.chunk.ordinal)
                if key in seen_chunks:
                    continue
                seen_chunks.add(key)
                ordered.append(item)
            ranked = ordered
            source_specific_multi_topic = True
    if legal_comparison_intent and (named_source_paths or link_source_intent):
        # Comparações jurídicas têm três papéis documentais diferentes. Um
        # ranking global tende a devolver apenas o Vade Mecum; aqui garantimos
        # um trecho representativo do acordo, da lei e da base jurisprudencial.
        comparison_markers = (
            "horas extras",
            "horas suplementares",
            "dias pontes",
            "jornada de trabalho",
            "banco de horas",
            "compensacao",
            "art. 59.",
            "jurisprudencia",
            "precedentes",
            "acordao",
            "recurso especial",
        )
        candidate_keys = {(str(item.chunk.path), item.chunk.ordinal) for item in candidates}
        forced_candidates = [
            Evidence(chunk, 0.16, 0.12, 0.0, 0.12)
            for index, chunk in enumerate(chunks)
            if (str(chunk.path), chunk.ordinal) not in candidate_keys
            and any(marker in normalized_index[index] for marker in comparison_markers)
        ]
        comparison_candidates = [*candidates, *forced_candidates]
        agreement_markers = (
            ("horas extras", "horas suplementares", "jornada", "compensacao", "compensação", "dias pontes")
            if overtime_intent
            else ("horas extras", "horas suplementares", "jornada de trabalho", "compensacao", "dias pontes", "banco de horas")
        )
        law_markers = (
            ("duracao diaria do trabalho", "horas extras", "banco de horas", "compensacao", "art. 59")
            if overtime_intent
            else ("duracao diaria do trabalho", "horas extras", "banco de horas", "compensacao", "art. 59.", "artigo 59")
        )
        legal_topics = (
            (agreement_markers, ("saae", "acordo", "coletiv")),
            (law_markers, ("vade",)),
            (("jurisprudencia", "precedentes", "acordao", "recurso", "stj", "trf"), ("stj", "trf", "oab", "lexml")),
        )
        legal_topic_items: list[Evidence] = []
        for markers, preferred_sources in legal_topics:
            pool = [item for item in comparison_candidates if any(marker in normalize(item.chunk.text) for marker in markers)]
            preferred = [item for item in pool if any(marker in normalize(item.chunk.path.stem) for marker in preferred_sources)]
            pool = preferred or pool
            legal_topic_items.extend(
                sorted(
                    pool,
                    key=lambda item: (
                        sum(len(marker.split()) for marker in markers if marker in normalize(item.chunk.text)),
                        item.score,
                    ),
                    reverse=True,
                )[:1]
            )
        if legal_topic_items:
            seen_chunks: set[tuple[str, int]] = set()
            ordered: list[Evidence] = []
            for item in legal_topic_items + ranked:
                key = (str(item.chunk.path), item.chunk.ordinal)
                if key in seen_chunks:
                    continue
                seen_chunks.add(key)
                ordered.append(item)
            ranked = ordered
            source_specific_multi_topic = True
    if legal_review_intent:
        # Uma revisão interpretativa precisa de um recorte equilibrado. O
        # ranking global favoreceria apenas a cláusula 5ª e esconderia, por
        # exemplo, a comissão criada para solucionar problemas de aplicação
        # e a regra de vigência.
        review_markers = (
            (("regula as relacoes de trabalho", "auxiliares de administracao escolar"), ("saae", "acordo", "convenc")),
            (("clausula 5", "360 dias", "horas extras nao compensadas", "dias pontes"), ("saae", "acordo", "convenc")),
            (("problemas oriundos da aplicacao", "clausula 25"), ("saae", "acordo", "convenc")),
            (("portaria 671", "clausula 31", "clausula 32", "vigencia da presente convencao"), ("saae", "acordo", "convenc")),
        )
        review_candidates = list(candidates)
        candidate_keys = {(str(item.chunk.path), item.chunk.ordinal) for item in review_candidates}
        review_candidates.extend(
            Evidence(chunk, 0.16, 0.12, 0.0, 0.12)
            for index, chunk in enumerate(chunks)
            if (str(chunk.path), chunk.ordinal) not in candidate_keys
            and any(marker in normalized_index[index] for markers, _ in review_markers for marker in markers)
        )
        review_items: list[Evidence] = []
        for markers, preferred_sources in review_markers:
            pool = [item for item in review_candidates if any(marker in normalize(item.chunk.text) for marker in markers)]
            preferred = [item for item in pool if any(marker in normalize(item.chunk.path.stem) for marker in preferred_sources)]
            pool = preferred or pool
            if pool:
                review_items.append(
                    max(
                        pool,
                        key=lambda item: (
                            sum(len(marker.split()) for marker in markers if marker in normalize(item.chunk.text)),
                            item.score,
                        ),
                    )
                )
        if review_items:
            seen_chunks: set[tuple[str, int]] = set()
            ordered: list[Evidence] = []
            for item in review_items + ranked:
                key = (str(item.chunk.path), item.chunk.ordinal)
                if key in seen_chunks:
                    continue
                seen_chunks.add(key)
                ordered.append(item)
            ranked = ordered
            source_specific_multi_topic = True
    if module_id in {"direito", "departamento-pessoal"} and negative_hours_intent:
        precise_negative = [
            item
            for item in ranked
            if "correspondente diminuicao" in normalize(item.chunk.text)
            or "horas extras nao compensadas" in normalize(item.chunk.text)
        ]
        if precise_negative:
            ranked = precise_negative
    source_specific_jornada = False
    if module_id in {"direito", "departamento-pessoal"} and any(term in query_terms for term in ("jornada", "jornadas")):
        precise_jornada = [
            item
            for item in ranked
            if "clausula 19" in normalize(item.chunk.text)
            or "jornada de trabalho" in normalize(item.chunk.text)
        ]
        if precise_jornada:
            # Quando a pergunta nomeia um acordo/arquivo, a cláusula com o
            # título correspondente é uma evidência válida mesmo que o OCR
            # tenha perdido acentos e reduza a pontuação lexical.
            clause_19 = [item for item in precise_jornada if "clausula 19" in normalize(item.chunk.text)]
            if clause_19 and (named_source_paths or "acordo coletivo" in normalized_query or "convencao coletiva" in normalized_query):
                ranked = clause_19
                source_specific_jornada = True
            else:
                ranked = precise_jornada
    source_specific_compensation = False
    if (
        module_id in {"direito", "departamento-pessoal"}
        and explicit_overtime_context
        and compensation_intent
    ):
        precise_compensation = [
            item
            for item in ranked
            if "horas extras nao compensadas" in normalize(item.chunk.text)
            or "horas suplementares nao compensadas" in normalize(item.chunk.text)
            or "adicional de cinquenta por cento" in normalize(item.chunk.text)
        ]
        if precise_compensation:
            ranked = precise_compensation
            source_specific_compensation = bool(
                named_source_paths
                or "acordo coletivo" in normalized_query
                or "convencao coletiva" in normalized_query
            )
    source_specific_bridge = False
    if bridge_day_intent:
        precise_bridge = [
            item
            for item in ranked
            if "dias pontes" in normalize(item.chunk.text)
            and ("nao havera onerosidade" in normalize(item.chunk.text) or "desconto" in normalize(item.chunk.text))
        ]
        if precise_bridge:
            ranked = precise_bridge
            source_specific_bridge = True
    # Só force a cláusula do limite diário quando a pergunta realmente trata
    # do limite de duas horas. Perguntas sobre adicional, compensação ou
    # horas não compensadas precisam permanecer nos trechos do acordo que
    # tratam desses assuntos (por exemplo, a cláusula 5 do SAAE).
    overtime_limit_intent = overtime_intent and any(
        term in query_terms
        for term in (
            "2",
            "duas",
            "limite",
            "exceder",
            "excedente",
            "ultrapassar",
            "ultrapasse",
            "excedentes",
        )
    )
    if overtime_limit_intent:
        precise_overtime = [item for item in ranked if "duracao diaria do trabalho podera ser acrescida de horas extras" in normalize(item.chunk.text)]
        if precise_overtime:
            ranked = precise_overtime
    if module_id == "medicina" and any(term in query_terms for term in ("gripe", "influenza")):
        precise_medical = [item for item in ranked if any(term in normalize(item.chunk.text) for term in ("gripe", "influenza"))]
        if precise_medical:
            ranked = precise_medical
    if host_document_intent and not host_procedure_intent:
        precise_host = [item for item in ranked if "uma entidade no zabbix que representa" in normalize(item.chunk.text) or "representa seu alvo de monitoramento" in normalize(item.chunk.text)]
        if precise_host:
            ranked = precise_host
    # A resposta só pode usar um trecho que contenha pelo menos um termo da
    # pergunta. Similaridade sem correspondência lexical deixa passar assuntos
    # genéricos e quebra o isolamento entre módulos.
    selected = tuple(
        item
        for item in ranked
        if (source_specific_jornada or source_specific_compensation or source_specific_bridge or source_specific_multi_topic or item.score >= policy.min_evidence_score)
        and item.coverage > 0
        and item.lexical_score > 0
    )[:limit]
    is_host_procedure = host_procedure_intent or ("host" in query_terms and any(term in query_terms for term in ("adiciono", "adicionar", "configurar", "configurando", "criar")))
    if selected and is_host_procedure:
        # Manuais técnicos distribuem um procedimento em páginas/chunks
        # consecutivos. Recompõe a janela da seção encontrada para o LLM
        # receber a sequência real (assistente, template, host, interface,
        # criação), em vez de misturar trechos de descoberta e macros.
        specific_anchors = [item for item in ranked if "/config/hosts/host" in normalize(item.chunk.text)]
        if not specific_anchors:
            specific_anchors = [item for item in ranked if "data collection > hosts" in normalize(item.chunk.text) or "clique em host wizard" in normalize(item.chunk.text)]
        if not specific_anchors:
            specific_anchors = [item for item in ranked if "assistente de host" in normalize(item.chunk.text)]
        anchors = specific_anchors or [item for item in ranked if "hosts e grupos de hosts" in normalize(item.chunk.text)]
        anchor = min(anchors or list(selected), key=lambda item: item.chunk.ordinal)
        window = tuple(item for item in candidates if item.chunk.path == anchor.chunk.path and anchor.chunk.ordinal <= item.chunk.ordinal <= anchor.chunk.ordinal + 5 and item.coverage > 0)
        if len(window) >= 2:
            selected = tuple(sorted(window, key=lambda item: item.chunk.ordinal)[:limit])
    sources = tuple(dict.fromkeys(item.chunk.path.name for item in selected))
    return RetrievalResult(selected, sources, query, expanded)
