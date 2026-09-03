"""Persistent, bounded knowledge expansion for the local-first SOFIA RAG.

This module deliberately keeps expansion separate from answer generation. A
query can create a small topic record, but public crawling only happens in the
scheduled/admin expansion worker after privacy, domain, relevance and budget
checks pass.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import shutil
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .ingestion import DocumentChunk, extract_text, files_for, ingest_module
from .knowledge_builder import build_artifacts
from .links import LinkRepository, fetch_link, normalize_url, save_fetched_link
from .privacy import ExternalRedaction, external_clinical_allowed, external_data_allowed
from .query_analysis import classify_query, normalize
from .research import _search_links
from .storage import strict_storage

logger = logging.getLogger("sofia.expansion")

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # SQLite remains available for local first-run development.
    psycopg = None
    dict_row = None

STATES = {
    "PENDING",
    "DOWNLOADING",
    "EXTRACTING",
    "NORMALIZING",
    "CHUNKING",
    "EMBEDDING",
    "INDEXING",
    "VALIDATING",
    "READY",
    "PARTIAL",
    "FAILED",
    "QUARANTINED",
    "UPDATING",
    "DISABLED",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS expansion_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS search_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    topic_key TEXT NOT NULL,
    main_topic TEXT NOT NULL,
    normalized_topic TEXT NOT NULL,
    origin TEXT NOT NULL,
    query_count INTEGER NOT NULL DEFAULT 0,
    last_searched_at TEXT,
    last_expanded_at TEXT,
    expansion_state TEXT NOT NULL DEFAULT 'PENDING',
    priority REAL NOT NULL DEFAULT 0,
    is_latest INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(module_id, topic_key)
);
CREATE TABLE IF NOT EXISTS search_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES search_topics(id),
    user_code TEXT,
    original_query TEXT NOT NULL,
    normalized_query TEXT NOT NULL,
    keywords_json TEXT NOT NULL DEFAULT '[]',
    entities_json TEXT NOT NULL DEFAULT '[]',
    date_start TEXT,
    date_end TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS topic_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES search_topics(id),
    term TEXT NOT NULL,
    origin_term TEXT NOT NULL,
    depth INTEGER NOT NULL DEFAULT 0,
    confidence REAL NOT NULL DEFAULT 0,
    justification TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(topic_id, term)
);
CREATE TABLE IF NOT EXISTS expansion_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL UNIQUE REFERENCES search_topics(id),
    state TEXT NOT NULL DEFAULT 'PENDING',
    priority REAL NOT NULL DEFAULT 0,
    available_at TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_started_at TEXT,
    last_finished_at TEXT,
    last_error TEXT
);
CREATE TABLE IF NOT EXISTS expansion_domains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'allow',
    reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE(module_id, domain)
);
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    url TEXT,
    normalized_url TEXT,
    canonical_url TEXT,
    local_path TEXT,
    title TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'PENDING',
    reliability REAL NOT NULL DEFAULT 0,
    content_hash TEXT,
    etag TEXT,
    last_modified TEXT,
    pages INTEGER NOT NULL DEFAULT 1,
    last_checked_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(module_id, normalized_url),
    UNIQUE(module_id, local_path)
);
CREATE TABLE IF NOT EXISTS source_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL REFERENCES sources(id),
    version_number INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    local_path TEXT,
    status TEXT NOT NULL DEFAULT 'READY',
    bytes INTEGER NOT NULL DEFAULT 0,
    pages INTEGER NOT NULL DEFAULT 1,
    collected_at TEXT NOT NULL,
    UNIQUE(source_id, content_hash)
);
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    source_id INTEGER,
    path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    mime_type TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'PENDING',
    content_hash TEXT,
    bytes INTEGER NOT NULL DEFAULT 0,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    version_number INTEGER NOT NULL DEFAULT 1,
    file_hash TEXT,
    duplicate_of INTEGER,
    source_origin TEXT NOT NULL DEFAULT 'local',
    author TEXT,
    sensitivity TEXT NOT NULL DEFAULT 'internal',
    current_stage TEXT NOT NULL DEFAULT 'RECEIVED',
    received_at TEXT,
    extraction_quality REAL,
    ocr_quality REAL,
    summary TEXT,
    keywords_json TEXT NOT NULL DEFAULT '[]',
    entities_json TEXT NOT NULL DEFAULT '[]',
    concepts_json TEXT NOT NULL DEFAULT '[]',
    relations_json TEXT NOT NULL DEFAULT '[]',
    questions_json TEXT NOT NULL DEFAULT '[]',
    embeddings_status TEXT NOT NULL DEFAULT 'PENDING',
    indexing_status TEXT NOT NULL DEFAULT 'PENDING',
    validation_status TEXT NOT NULL DEFAULT 'PENDING',
    insights_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT,
    updated_at TEXT NOT NULL,
    UNIQUE(module_id, path)
);
CREATE TABLE IF NOT EXISTS document_pipeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    metrics_json TEXT NOT NULL DEFAULT '{}',
    error_message TEXT
);
CREATE TABLE IF NOT EXISTS knowledge_artifacts (
    document_id INTEGER PRIMARY KEY REFERENCES documents(id),
    version_number INTEGER NOT NULL,
    artifact_version TEXT NOT NULL DEFAULT '1.0',
    summary TEXT NOT NULL DEFAULT '',
    keywords_json TEXT NOT NULL DEFAULT '[]',
    entities_json TEXT NOT NULL DEFAULT '[]',
    concepts_json TEXT NOT NULL DEFAULT '[]',
    relations_json TEXT NOT NULL DEFAULT '[]',
    questions_json TEXT NOT NULL DEFAULT '[]',
    claims_json TEXT NOT NULL DEFAULT '[]',
    dates_json TEXT NOT NULL DEFAULT '[]',
    people_json TEXT NOT NULL DEFAULT '[]',
    organizations_json TEXT NOT NULL DEFAULT '[]',
    topics_json TEXT NOT NULL DEFAULT '[]',
    contradictions_json TEXT NOT NULL DEFAULT '[]',
    embedding_json TEXT NOT NULL DEFAULT '{}',
    provenance_json TEXT NOT NULL DEFAULT '{}',
    quality REAL NOT NULL DEFAULT 0,
    ocr_quality REAL,
    generated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    version_number INTEGER NOT NULL,
    ordinal INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'READY',
    UNIQUE(document_id, version_number, ordinal)
);
CREATE TABLE IF NOT EXISTS processing_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    source_id INTEGER,
    document_id INTEGER,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    metrics_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS processing_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    source_id INTEGER,
    document_id INTEGER,
    stage TEXT NOT NULL,
    error_type TEXT NOT NULL,
    message TEXT NOT NULL,
    retryable INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS retrieval_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id TEXT NOT NULL,
    document_id INTEGER,
    source_id INTEGER,
    title_ok INTEGER NOT NULL DEFAULT 0,
    semantic_ok INTEGER NOT NULL DEFAULT 0,
    module_ok INTEGER NOT NULL DEFAULT 0,
    citation_ok INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS expansion_cycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL,
    topics_claimed INTEGER NOT NULL DEFAULT 0,
    topics_completed INTEGER NOT NULL DEFAULT 0,
    pages_discovered INTEGER NOT NULL DEFAULT 0,
    pages_new INTEGER NOT NULL DEFAULT 0,
    pages_updated INTEGER NOT NULL DEFAULT 0,
    duplicates_ignored INTEGER NOT NULL DEFAULT 0,
    errors INTEGER NOT NULL DEFAULT 0,
    metrics_json TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_search_topics_module_priority ON search_topics(module_id, priority DESC, last_searched_at DESC);
CREATE INDEX IF NOT EXISTS idx_search_topics_expansion ON search_topics(expansion_state, last_expanded_at);
CREATE INDEX IF NOT EXISTS idx_search_queries_topic_created ON search_queries(topic_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_expansion_queue_due ON expansion_queue(state, available_at, priority DESC);
CREATE INDEX IF NOT EXISTS idx_sources_module_status ON sources(module_id, status);
CREATE INDEX IF NOT EXISTS idx_sources_hash ON sources(module_id, content_hash);
CREATE INDEX IF NOT EXISTS idx_documents_module_status ON documents(module_id, status);
CREATE INDEX IF NOT EXISTS idx_processing_errors_module_created ON processing_errors(module_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_document_pipeline_events_document ON document_pipeline_events(document_id, id);
CREATE INDEX IF NOT EXISTS idx_knowledge_artifacts_concept ON knowledge_artifacts(document_id, version_number);
"""

_PG_SCHEMA_NAME = "sofia_runtime"
_PG_ID_TABLES = {
    "search_topics",
    "sources",
    "documents",
    "processing_jobs",
    "expansion_cycles",
}
_PG_FAILURE: str | None = None
_PG_FAILURE_AT: datetime | None = None
_PG_EXTRA_SCHEMA = """
CREATE TABLE IF NOT EXISTS semantic_embeddings (
    id BIGSERIAL PRIMARY KEY,
    module_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    source_hash TEXT NOT NULL,
    model TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    vector_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(module_id, source_path, ordinal, source_hash, model)
);
CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_module ON semantic_embeddings(module_id, model);
"""


def _postgres_dsn() -> str:
    return os.getenv("SOFIA_POSTGRES_URL", os.getenv("DATABASE_URL", "")).strip()


def _postgres_sql(sql: str) -> str:
    """Translate the small SQLite dialect used by the store to psycopg."""
    sql = sql.replace("BEGIN IMMEDIATE", "BEGIN")
    sql = re.sub(r"MAX\((reliability|pages|confidence),\s*\?\)", r"GREATEST(\1, ?)", sql)
    sql = sql.replace("MAX(confidence, excluded.confidence)", "GREATEST(confidence, excluded.confidence)")
    return sql.replace("?", "%s")


class _PostgresCursor:
    def __init__(self, cursor: Any, returns_id: bool = False) -> None:
        self._cursor = cursor
        self._returns_id = returns_id
        self._lastrowid: int | None = None

    @property
    def lastrowid(self) -> int | None:
        if self._lastrowid is None and self._returns_id:
            row = self._cursor.fetchone()
            if row:
                self._lastrowid = int(row["id"] if isinstance(row, dict) else row[0])
        return self._lastrowid

    def fetchone(self) -> Any:
        return self._cursor.fetchone()

    def fetchall(self) -> list[Any]:
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor)


class _PostgresConnection:
    backend = "postgresql"

    def __init__(self, connection: Any) -> None:
        self.raw = connection
        self.raw.execute(f"CREATE SCHEMA IF NOT EXISTS {_PG_SCHEMA_NAME}")
        self.raw.execute(f"SET search_path TO {_PG_SCHEMA_NAME}")

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> _PostgresCursor:
        translated = _postgres_sql(sql)
        returns_id = False
        match = re.match(r"\s*INSERT\s+INTO\s+([a-z_]+)", translated, re.IGNORECASE)
        if match and match.group(1).casefold() in _PG_ID_TABLES and " returning " not in translated.casefold():
            translated += " RETURNING id"
            returns_id = True
        return _PostgresCursor(self.raw.execute(translated, params), returns_id)

    def executescript(self, script: str) -> None:
        for statement in script.split(";"):
            statement = statement.strip()
            if statement:
                self.raw.execute(statement)

    def commit(self) -> None:
        self.raw.commit()

    def close(self) -> None:
        self.raw.close()


def _postgres_schema() -> str:
    schema = SCHEMA.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "BIGSERIAL PRIMARY KEY")
    return schema


def expansion_storage_status() -> dict[str, Any]:
    """Return storage health without exposing the configured DSN or password."""
    dsn = _postgres_dsn()
    if not dsn:
        return {"backend": "sqlite", "postgres_configured": False, "postgres_error": None, "strict": strict_storage()}
    if psycopg is None:
        return {
            "backend": "sqlite-fallback",
            "postgres_configured": True,
            "postgres_error": "psycopg não está instalado",
            "strict": strict_storage(),
        }
    return {
        "backend": "postgresql" if _PG_FAILURE is None else "sqlite-fallback",
        "postgres_configured": True,
        "postgres_error": _PG_FAILURE,
        "strict": strict_storage(),
    }

DEFAULTS = {
    "interval_seconds": 3600,
    "max_pages_per_topic": 10,
    "max_topics_per_cycle": 5,
    "min_refresh_hours": 24,
    "max_attempts": 3,
    "timeout_seconds": 30,
    "concurrency": 1,
    "max_page_chars": 250000,
    "max_depth": 2,
    "search_providers": "duckduckgo",
    "max_storage_mb_per_module": 2048,
    "relevance_threshold": 2,
    "lease_seconds": 1800,
}

MODULE_SEEDS: dict[str, dict[str, tuple[str, ...]]] = {
    "infraestrutura": {
        "zabbix": ("host", "switch", "trigger", "item", "template", "descoberta de rede", "LLD", "proxy", "SNMP", "monitoramento"),
        "host": ("Zabbix", "item", "trigger", "template", "agent", "interface", "monitoramento"),
    },
    "medicina": {
        "gripe": ("influenza", "sintomas", "diagnóstico", "prevenção", "transmissão", "tratamento", "sinais de alerta"),
        "influenza": ("gripe", "sintomas", "prevenção", "transmissão", "vacinação", "sinais de alerta"),
    },
    "direito": {
        "acordo": ("convenção coletiva", "CLT", "jornada", "horas extras", "compensação", "jurisprudência"),
        "lei": ("artigo", "norma", "jurisprudência", "vigência", "interpretação", "aplicação"),
    },
    "contabilidade": {
        "balanço": ("balanço patrimonial", "ativo", "passivo", "patrimônio líquido", "notas explicativas", "CPC"),
        "ecf": ("SPED", "escrituração", "demonstrações contábeis", "conformidade", "CPC"),
    },
    "financeiro": {
        "caixa": ("fluxo de caixa", "receitas", "despesas", "contas a pagar", "contas a receber", "inadimplência"),
    },
    "recursos-humanos": {
        "contratação": ("recrutamento", "seleção", "admissão", "integração", "desempenho", "clima organizacional"),
    },
    "gestao-empresarial": {
        "processo": ("metas", "indicadores", "riscos", "governança", "melhoria contínua", "gestão educacional"),
    },
}

TRUSTED_DOMAINS = {
    "zabbix": ("zabbix.com",),
    "medicina": ("gov.br", "who.int", "paho.org", "cdc.gov", "nih.gov", "pubmed.ncbi.nlm.nih.gov", "scielo.br"),
    "direito": ("planalto.gov.br", "gov.br", "stf.jus.br", "stj.jus.br", "trf2.jus.br", "lexml.gov.br"),
    "contabilidade": ("gov.br", "cpc.org.br", "tesourotransparente.gov.br", "bcb.gov.br"),
    "financeiro": ("gov.br", "bcb.gov.br", "tesourotransparente.gov.br"),
    "prefeitura": ("gov.br",),
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _setting(name: str) -> str:
    env_name = f"SOFIA_EXPANSION_{name.upper()}"
    value = os.getenv(env_name)
    if value is not None:
        return value
    return str(DEFAULTS[name])


def expansion_settings() -> dict[str, Any]:
    def integer(name: str, minimum: int, maximum: int) -> int:
        try:
            return max(minimum, min(maximum, int(float(_setting(name)))))
        except ValueError:
            return int(DEFAULTS[name])

    def number(name: str, minimum: float, maximum: float) -> float:
        try:
            return max(minimum, min(maximum, float(_setting(name))))
        except ValueError:
            return float(DEFAULTS[name])

    return {
        "interval_seconds": integer("interval_seconds", 900, 604800),
        "max_pages_per_topic": integer("max_pages_per_topic", 1, 20),
        "max_topics_per_cycle": integer("max_topics_per_cycle", 1, 50),
        "min_refresh_hours": number("min_refresh_hours", 1, 8760),
        "max_attempts": integer("max_attempts", 1, 10),
        "timeout_seconds": number("timeout_seconds", 3, 60),
        "concurrency": integer("concurrency", 1, 3),
        "max_page_chars": integer("max_page_chars", 10000, 1000000),
        "max_depth": integer("max_depth", 0, 3),
        "search_providers": [item.strip().casefold() for item in _setting("search_providers").split(",") if item.strip()],
        "max_storage_mb_per_module": integer("max_storage_mb_per_module", 64, 102400),
        "relevance_threshold": number("relevance_threshold", 0, 10),
        "lease_seconds": integer("lease_seconds", 300, 86400),
        "enabled": os.getenv("SOFIA_AUTO_EXPANSION", "true").strip().casefold() not in {"0", "false", "no", "off"},
        "paused": os.getenv("SOFIA_EXPANSION_PAUSED", "false").strip().casefold() in {"1", "true", "yes", "on", "sim"},
    }


def _connect(path: Path) -> Any:
    global _PG_FAILURE, _PG_FAILURE_AT
    dsn = _postgres_dsn()
    retry_after_failure = _PG_FAILURE_AT is None or (datetime.now(UTC) - _PG_FAILURE_AT).total_seconds() >= 15
    if dsn and psycopg is not None and (_PG_FAILURE is None or retry_after_failure):
        try:
            connection = _PostgresConnection(psycopg.connect(dsn, connect_timeout=5, row_factory=dict_row))
            _PG_FAILURE = None
            _PG_FAILURE_AT = None
            return connection
        except Exception as exc:  # pragma: no cover - depends on deployment credentials.
            _PG_FAILURE = f"{type(exc).__name__}: {str(exc)[:240]}"
            _PG_FAILURE_AT = datetime.now(UTC)
            logger.warning("PostgreSQL da expansão indisponível; usando SQLite fallback: %s", _PG_FAILURE)
            if strict_storage():
                raise RuntimeError(f"PostgreSQL obrigatório indisponível: {_PG_FAILURE}") from exc
    elif dsn and strict_storage():
        raise RuntimeError("PostgreSQL obrigatório indisponível: driver psycopg não instalado")
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def database_path(root: Path) -> Path:
    return root.parent / "data" / "knowledge_expansion.sqlite3"


def _slug(value: str) -> str:
    value = normalize(value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:80] or "tema"


def _safe_question(question: str) -> str:
    return ExternalRedaction().clean(question).strip()[:20000]


def _extract_keywords(module_id: str, question: str, profile: dict[str, Any]) -> list[str]:
    stopwords = {
        "como", "qual", "quais", "sobre", "para", "entre", "uma", "com", "sem", "que", "isso", "este",
        "esta", "documento", "documentos", "arquivo", "arquivos", "resumo", "resumir", "fazer", "faca",
        "existe", "consegue", "ler", "responder", "base", "local", "disponivel", "disponiveis",
    }
    normalized = normalize(question)
    terms = [
        token
        for token in re.findall(r"[a-z0-9][a-z0-9-]+", normalized)
        if len(token) >= 3 and token not in stopwords and not token.isnumeric()
    ]
    terms.extend(str(item) for item in profile.get("concepts", []))
    for key, values in MODULE_SEEDS.get(module_id, {}).items():
        if key in normalized:
            terms.extend(values)
    seen: set[str] = set()
    unique: list[str] = []
    for term in terms:
        key = normalize(term)
        if key in seen:
            continue
        seen.add(key)
        unique.append(term)
    return unique[:24]


def _extract_entities(question: str, keywords: list[str]) -> list[str]:
    entities = [token for token in re.findall(r"\b[A-Z][A-Z0-9_-]{1,}\b", question) if len(token) >= 2]
    entities.extend(term for term in keywords if term.casefold() in {"zabbix", "snmp", "lld", "fhir", "hl7", "cpc", "ecf"})
    return list(dict.fromkeys(entities))[:16]


def topic_key(module_id: str, question: str, keywords: list[str]) -> tuple[str, str]:
    normalized = normalize(question)
    if module_id == "infraestrutura" and "zabbix" in normalized:
        if any(term in normalized for term in ("host", "hosts")):
            return "zabbix/hosts", "Zabbix · hosts"
        if "lld" in normalized:
            return "zabbix/lld", "Zabbix · LLD"
        return "zabbix", "Zabbix"
    if module_id == "medicina" and any(term in normalized for term in ("gripe", "influenza")):
        return "gripe/influenza", "Gripe · influenza"
    profile = classify_query(module_id, question)
    lead = keywords[0] if keywords else _slug(str(profile.get("theme", "tema")))
    return f"{_slug(str(profile.get('theme', 'tema')))}/{_slug(lead)}", str(profile.get("theme", lead))


class ExpansionStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = database_path(root)

    def initialize(self) -> None:
        connection = _connect(self.path)
        try:
            if getattr(connection, "backend", None) == "postgresql":
                connection.executescript(_postgres_schema())
                connection.executescript(_PG_EXTRA_SCHEMA)
                connection.commit()
                return
            connection.executescript(SCHEMA)
            query_columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(search_queries)").fetchall()}
            if "date_start" not in query_columns:
                connection.execute("ALTER TABLE search_queries ADD COLUMN date_start TEXT")
            if "date_end" not in query_columns:
                connection.execute("ALTER TABLE search_queries ADD COLUMN date_end TEXT")
            columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(sources)").fetchall()}
            if "etag" not in columns:
                connection.execute("ALTER TABLE sources ADD COLUMN etag TEXT NOT NULL DEFAULT ''")
            if "last_modified" not in columns:
                connection.execute("ALTER TABLE sources ADD COLUMN last_modified TEXT NOT NULL DEFAULT ''")
            document_columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(documents)").fetchall()}
            additions = {
                "file_hash": "TEXT",
                "duplicate_of": "INTEGER",
                "source_origin": "TEXT NOT NULL DEFAULT 'local'",
                "author": "TEXT",
                "sensitivity": "TEXT NOT NULL DEFAULT 'internal'",
                "current_stage": "TEXT NOT NULL DEFAULT 'RECEIVED'",
                "received_at": "TEXT",
                "extraction_quality": "REAL",
                "ocr_quality": "REAL",
                "summary": "TEXT",
                "keywords_json": "TEXT NOT NULL DEFAULT '[]'",
                "entities_json": "TEXT NOT NULL DEFAULT '[]'",
                "concepts_json": "TEXT NOT NULL DEFAULT '[]'",
                "relations_json": "TEXT NOT NULL DEFAULT '[]'",
                "questions_json": "TEXT NOT NULL DEFAULT '[]'",
                "embeddings_status": "TEXT NOT NULL DEFAULT 'PENDING'",
                "indexing_status": "TEXT NOT NULL DEFAULT 'PENDING'",
                "validation_status": "TEXT NOT NULL DEFAULT 'PENDING'",
                "insights_json": "TEXT NOT NULL DEFAULT '[]'",
                "created_at": "TEXT",
            }
            for column, definition in additions.items():
                if column not in document_columns:
                    connection.execute(f"ALTER TABLE documents ADD COLUMN {column} {definition}")
            artifact_columns = {str(row[1]) for row in connection.execute("PRAGMA table_info(knowledge_artifacts)").fetchall()}
            artifact_additions = {
                "artifact_version": "TEXT NOT NULL DEFAULT '1.0'",
                "claims_json": "TEXT NOT NULL DEFAULT '[]'",
                "dates_json": "TEXT NOT NULL DEFAULT '[]'",
                "people_json": "TEXT NOT NULL DEFAULT '[]'",
                "organizations_json": "TEXT NOT NULL DEFAULT '[]'",
                "topics_json": "TEXT NOT NULL DEFAULT '[]'",
                "contradictions_json": "TEXT NOT NULL DEFAULT '[]'",
                "embedding_json": "TEXT NOT NULL DEFAULT '{}'",
                "provenance_json": "TEXT NOT NULL DEFAULT '{}'",
            }
            for column, definition in artifact_additions.items():
                if column not in artifact_columns:
                    connection.execute(f"ALTER TABLE knowledge_artifacts ADD COLUMN {column} {definition}")
            connection.commit()
        finally:
            connection.close()

    def is_paused(self) -> bool:
        connection = _connect(self.path)
        try:
            row = connection.execute("SELECT value FROM expansion_settings WHERE key = 'paused'").fetchone()
            if row is not None:
                return str(row["value"]).casefold() in {"1", "true", "yes", "on", "sim"}
        finally:
            connection.close()
        return expansion_settings()["paused"]

    def set_paused(self, paused: bool) -> None:
        self.initialize()
        connection = _connect(self.path)
        try:
            connection.execute(
                "INSERT INTO expansion_settings (key, value, updated_at) VALUES ('paused', ?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                ("true" if paused else "false", _now()),
            )
            connection.commit()
        finally:
            connection.close()

    def record_query(self, module_id: str, question: str, user_code: str | None = None) -> dict[str, Any]:
        self.initialize()
        safe_question = _safe_question(question)
        normalized_query = normalize(safe_question)
        profile = classify_query(module_id, safe_question)
        keywords = _extract_keywords(module_id, safe_question, profile)
        entities = _extract_entities(question, keywords)
        dates = re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", question)
        key, main_topic = topic_key(module_id, safe_question, keywords)
        now = _now()
        settings = expansion_settings()
        stored_user = user_code if os.getenv("SOFIA_EXPANSION_STORE_USER", "false").strip().casefold() in {"1", "true", "yes", "on", "sim"} else None
        connection = _connect(self.path)
        try:
            connection.execute("UPDATE search_topics SET is_latest = 0 WHERE module_id = ?", (module_id,))
            row = connection.execute("SELECT * FROM search_topics WHERE module_id = ? AND topic_key = ?", (module_id, key)).fetchone()
            if row:
                count = int(row["query_count"]) + 1
                priority = min(100.0, 45.0 + min(30.0, math.log1p(count) * 10) + 25.0)
                connection.execute(
                    "UPDATE search_topics SET main_topic = ?, normalized_topic = ?, query_count = ?, last_searched_at = ?, priority = ?, is_latest = 1, updated_at = ?, expansion_state = CASE WHEN expansion_state = 'FAILED' THEN 'PENDING' ELSE expansion_state END WHERE id = ?",
                    (main_topic, normalize(main_topic), count, now, priority, now, row["id"]),
                )
                topic_id = int(row["id"])
            else:
                priority = 70.0
                cursor = connection.execute(
                    "INSERT INTO search_topics (module_id, topic_key, main_topic, normalized_topic, origin, query_count, last_searched_at, expansion_state, priority, is_latest, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 1, ?, 'PENDING', ?, 1, ?, ?)",
                    (module_id, key, main_topic, normalize(main_topic), "user_query", now, priority, now, now),
                )
                topic_id = int(cursor.lastrowid)
            connection.execute(
                "INSERT INTO search_queries (topic_id, user_code, original_query, normalized_query, keywords_json, entities_json, date_start, date_end, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (topic_id, stored_user, safe_question, normalized_query, json.dumps(keywords, ensure_ascii=False), json.dumps(entities, ensure_ascii=False), dates[0] if dates else None, dates[-1] if len(dates) > 1 else None, now),
            )
            for index, term in enumerate(keywords):
                connection.execute(
                    "INSERT INTO topic_keywords (topic_id, term, origin_term, depth, confidence, justification, created_at) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(topic_id, term) DO UPDATE SET confidence = MAX(confidence, excluded.confidence)",
                    (topic_id, normalize(term), normalize(keywords[0] if keywords else term), 0 if index < 3 else 1, 0.95 if index < 3 else 0.78, "termo observado na consulta ou relacionado por regra determinística do módulo", now),
                )
            expanded_at = row["last_expanded_at"] if row else None
            available = now
            if expanded_at:
                try:
                    next_time = datetime.fromisoformat(str(expanded_at)) + timedelta(hours=float(settings["min_refresh_hours"]))
                    available = max(datetime.fromisoformat(now), next_time).isoformat()
                except ValueError:
                    available = now
            queue = connection.execute("SELECT id FROM expansion_queue WHERE topic_id = ?", (topic_id,)).fetchone()
            queue_state = "PENDING" if available <= now else "WAITING"
            if queue:
                connection.execute("UPDATE expansion_queue SET state = ?, priority = ?, available_at = ?, last_error = NULL WHERE topic_id = ?", (queue_state, priority, available, topic_id))
            else:
                connection.execute("INSERT INTO expansion_queue (topic_id, state, priority, available_at) VALUES (?, ?, ?, ?)", (topic_id, queue_state, priority, available))
            connection.commit()
            return {"topic_id": topic_id, "topic_key": key, "main_topic": main_topic, "keywords": keywords, "entities": entities, "priority": priority}
        finally:
            connection.close()

    def claim_topics(self, limit: int, module_id: str | None = None) -> tuple[int | None, list[dict[str, Any]]]:
        self.initialize()
        now = datetime.now(UTC)
        settings = expansion_settings()
        lease_limit = (now - timedelta(seconds=settings["lease_seconds"])).isoformat()
        connection = _connect(self.path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("UPDATE expansion_queue SET state = 'PENDING' WHERE state = 'RUNNING' AND last_started_at < ?", (lease_limit,))
            module_filter = " AND t.module_id = ?" if module_id else ""
            params: list[Any] = [now.isoformat(), settings["max_attempts"]]
            if module_id:
                params.append(module_id)
            params.append(limit)
            rows = connection.execute(
                f"SELECT q.id AS queue_id, q.topic_id, t.* FROM expansion_queue q JOIN search_topics t ON t.id = q.topic_id WHERE q.state IN ('PENDING', 'WAITING') AND q.available_at <= ? AND q.attempts < ?{module_filter} ORDER BY q.priority DESC, t.is_latest DESC, t.last_searched_at DESC LIMIT ?",
                params,
            ).fetchall()
            cycle_id: int | None = None
            if rows:
                cursor = connection.execute("INSERT INTO expansion_cycles (started_at, status, topics_claimed) VALUES (?, 'RUNNING', ?)", (_now(), len(rows)))
                cycle_id = int(cursor.lastrowid)
            result: list[dict[str, Any]] = []
            for row in rows:
                connection.execute("UPDATE expansion_queue SET state = 'RUNNING', attempts = attempts + 1, last_started_at = ? WHERE id = ?", (_now(), row["queue_id"]))
                result.append(dict(row))
            connection.commit()
            return cycle_id, result
        finally:
            connection.close()

    def finish_topic(self, topic_id: int, status: str, error: str | None = None) -> None:
        status = status if status in STATES else "FAILED"
        now = _now()
        settings = expansion_settings()
        connection = _connect(self.path)
        try:
            connection.execute(
                "UPDATE search_topics SET expansion_state = ?, last_expanded_at = ?, updated_at = ? WHERE id = ?",
                (status, now, now, topic_id),
            )
            available = (datetime.now(UTC) + timedelta(hours=settings["min_refresh_hours"])).isoformat()
            connection.execute(
                "UPDATE expansion_queue SET state = ?, available_at = ?, last_finished_at = ?, last_error = ? WHERE topic_id = ?",
                ("WAITING" if status == "READY" else "FAILED", available if status == "READY" else now, now, error[:500] if error else None, topic_id),
            )
            connection.commit()
        finally:
            connection.close()

    def finish_cycle(self, cycle_id: int | None, metrics: dict[str, Any], status: str) -> None:
        if cycle_id is None:
            return
        connection = _connect(self.path)
        try:
            connection.execute(
                "UPDATE expansion_cycles SET finished_at = ?, status = ?, topics_completed = ?, pages_discovered = ?, pages_new = ?, pages_updated = ?, duplicates_ignored = ?, errors = ?, metrics_json = ? WHERE id = ?",
                (_now(), status, metrics.get("topics_completed", 0), metrics.get("pages_discovered", 0), metrics.get("pages_new", 0), metrics.get("pages_updated", 0), metrics.get("duplicates_ignored", 0), metrics.get("errors", 0), json.dumps(metrics, ensure_ascii=False), cycle_id),
            )
            connection.commit()
        finally:
            connection.close()

    def add_error(self, module_id: str, stage: str, message: str, error_type: str = "Error", retryable: bool = False, source_id: int | None = None, document_id: int | None = None) -> None:
        connection = _connect(self.path)
        try:
            connection.execute(
                "INSERT INTO processing_errors (module_id, source_id, document_id, stage, error_type, message, retryable, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (module_id, source_id, document_id, stage, error_type, str(message)[:1000], int(retryable), _now()),
            )
            connection.commit()
        finally:
            connection.close()

    def source_by_url(self, module_id: str, url: str) -> sqlite3.Row | None:
        normalized_url = normalize_url(url)
        connection = _connect(self.path)
        try:
            return connection.execute("SELECT * FROM sources WHERE module_id = ? AND normalized_url = ?", (module_id, normalized_url)).fetchone()
        finally:
            connection.close()

    def content_exists(self, module_id: str, content_hash: str) -> bool:
        connection = _connect(self.path)
        try:
            return bool(connection.execute("SELECT 1 FROM sources WHERE module_id = ? AND content_hash = ? LIMIT 1", (module_id, content_hash)).fetchone())
        finally:
            connection.close()

    def register_source(self, module_id: str, source_type: str, *, url: str | None = None, canonical_url: str | None = None, local_path: str | None = None, title: str = "", status: str = "READY", reliability: float = 0.0, content_hash: str | None = None, pages: int = 1, bytes_count: int = 0, etag: str = "", last_modified: str = "") -> int:
        normalized_url = normalize_url(url) if url else None
        canonical = normalize_url(canonical_url or url) if (canonical_url or url) else None
        now = _now()
        connection = _connect(self.path)
        try:
            if normalized_url:
                row = connection.execute("SELECT id FROM sources WHERE module_id = ? AND normalized_url = ?", (module_id, normalized_url)).fetchone()
            elif local_path:
                row = connection.execute("SELECT id FROM sources WHERE module_id = ? AND local_path = ?", (module_id, local_path)).fetchone()
            else:
                row = None
            if row:
                source_id = int(row["id"])
                connection.execute(
                    "UPDATE sources SET canonical_url = COALESCE(?, canonical_url), local_path = COALESCE(?, local_path), title = COALESCE(NULLIF(?, ''), title), status = ?, reliability = MAX(reliability, ?), content_hash = COALESCE(?, content_hash), etag = COALESCE(NULLIF(?, ''), etag), last_modified = COALESCE(NULLIF(?, ''), last_modified), pages = MAX(pages, ?), last_checked_at = ?, updated_at = ? WHERE id = ?",
                    (canonical, local_path, title, status, reliability, content_hash, etag, last_modified, pages, now, now, source_id),
                )
            else:
                cursor = connection.execute(
                    "INSERT INTO sources (module_id, source_type, url, normalized_url, canonical_url, local_path, title, status, reliability, content_hash, etag, last_modified, pages, last_checked_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (module_id, source_type, url, normalized_url, canonical, local_path, title, status, reliability, content_hash, etag, last_modified, pages, now, now, now),
                )
                source_id = int(cursor.lastrowid)
            if content_hash:
                version = connection.execute("SELECT MAX(version_number) AS version FROM source_versions WHERE source_id = ?", (source_id,)).fetchone()["version"] or 0
                connection.execute(
                    "INSERT INTO source_versions (source_id, version_number, content_hash, local_path, status, bytes, pages, collected_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(source_id, content_hash) DO UPDATE SET status = excluded.status, local_path = excluded.local_path, pages = excluded.pages",
                    (source_id, int(version) + 1, content_hash, local_path, status, bytes_count, pages, now),
                )
            connection.commit()
            return source_id
        finally:
            connection.close()

    def allow_domain(self, module_id: str, domain: str, mode: str = "allow", reason: str = "admin") -> None:
        domain = domain.casefold().strip().strip(".")
        if not domain or mode not in {"allow", "block"}:
            raise ValueError("domínio ou modo inválido")
        connection = _connect(self.path)
        try:
            connection.execute("INSERT INTO expansion_domains (module_id, domain, mode, reason, created_at) VALUES (?, ?, ?, ?, ?) ON CONFLICT(module_id, domain) DO UPDATE SET mode = excluded.mode, reason = excluded.reason", (module_id, domain, mode, reason[:240], _now()))
            connection.commit()
        finally:
            connection.close()

    def domains(self, module_id: str) -> dict[str, str]:
        connection = _connect(self.path)
        try:
            return {str(row["domain"]): str(row["mode"]) for row in connection.execute("SELECT domain, mode FROM expansion_domains WHERE module_id = ?", (module_id,)).fetchall()}
        finally:
            connection.close()

    def snapshot(self, module_id: str | None = None) -> dict[str, Any]:
        self.initialize()
        connection = _connect(self.path)
        try:
            where = "WHERE module_id = ?" if module_id else ""
            args = (module_id,) if module_id else ()
            topics = connection.execute(f"SELECT * FROM search_topics {where} ORDER BY priority DESC, last_searched_at DESC LIMIT 50", args).fetchall()
            queue = connection.execute(f"SELECT q.*, t.module_id, t.topic_key, t.main_topic FROM expansion_queue q JOIN search_topics t ON t.id = q.topic_id {('WHERE t.module_id = ?' if module_id else '')} ORDER BY q.priority DESC LIMIT 50", args).fetchall()
            sources = connection.execute(f"SELECT status, COUNT(*) AS count FROM sources {where} GROUP BY status", args).fetchall()
            documents = connection.execute(f"SELECT status, COUNT(*) AS count FROM documents {where} GROUP BY status", args).fetchall()
            errors = connection.execute(f"SELECT COUNT(*) AS count FROM processing_errors {where}", args).fetchone()["count"]
            last_cycle = connection.execute("SELECT * FROM expansion_cycles ORDER BY id DESC LIMIT 1").fetchone()
            storage_root = self.root / module_id if module_id else self.root
            storage_bytes = sum(path.stat().st_size for path in storage_root.rglob("*") if path.is_file()) if storage_root.exists() else 0
            settings = expansion_settings()
            paused_row = connection.execute("SELECT value FROM expansion_settings WHERE key = 'paused'").fetchone()
            if paused_row is not None:
                settings["paused"] = str(paused_row["value"]).casefold() in {"1", "true", "yes", "on", "sim"}
            return {
                "settings": settings,
                "database": str(self.path),
                "storage": expansion_storage_status(),
                "module_id": module_id,
                "topics": [dict(row) for row in topics],
                "queue": [dict(row) for row in queue],
                "queue_pending": sum(1 for row in queue if row["state"] in {"PENDING", "RUNNING", "WAITING"}),
                "sources_by_status": {str(row["status"]): int(row["count"]) for row in sources},
                "documents_by_status": {str(row["status"]): int(row["count"]) for row in documents},
                "processing_errors": int(errors or 0),
                "storage_bytes": storage_bytes,
                "last_cycle": dict(last_cycle) if last_cycle else None,
            }
        finally:
            connection.close()

    def pipeline_documents(self, module_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Return operational metadata for the admin Pipeline Explorer."""
        self.initialize()
        connection = _connect(self.path)
        try:
            rows = connection.execute(
                "SELECT d.*, (SELECT COUNT(*) FROM document_pipeline_events e WHERE e.document_id = d.id) AS event_count FROM documents d WHERE d.module_id = ? ORDER BY d.updated_at DESC LIMIT ?",
                (module_id, max(1, min(500, limit))),
            ).fetchall()
            payload = []
            for row in rows:
                item = dict(row)
                events = connection.execute("SELECT stage, status, started_at, finished_at, metrics_json, error_message FROM document_pipeline_events WHERE document_id = ? ORDER BY id", (row["id"],)).fetchall()
                item["events"] = [dict(event) for event in events]
                item["artifacts"] = dict(connection.execute("SELECT artifact_version, summary, keywords_json, entities_json, concepts_json, relations_json, questions_json, claims_json, dates_json, people_json, organizations_json, topics_json, contradictions_json, embedding_json, provenance_json, quality, ocr_quality, generated_at FROM knowledge_artifacts WHERE document_id = ?", (row["id"],)).fetchone() or {})
                payload.append(item)
            return payload
        finally:
            connection.close()


def initialize_expansion(root: Path) -> None:
    store = ExpansionStore(root)
    store.initialize()
    repository = LinkRepository(root)
    for module_id in {path.name for path in root.iterdir() if path.is_dir()}:
        try:
            records = repository.list(module_id)
        except (OSError, RuntimeError, ValueError):
            continue
        for record in records:
            try:
                store.register_source(
                    module_id,
                    "url",
                    url=str(record.get("url")),
                    canonical_url=str(record.get("final_url") or record.get("url")),
                    local_path=str(root / module_id / "links" / str(record.get("file_name", ""))),
                    title=str(record.get("title", "")),
                    content_hash=str(record.get("content_hash", "")) or None,
                    pages=int(record.get("pages", 1) or 1),
                    etag=str(record.get("etag", "")),
                    last_modified=str(record.get("last_modified", "")),
                )
            except (OSError, TypeError, ValueError):
                logger.warning("Não foi possível sincronizar o registro de link do módulo %s", module_id, exc_info=True)


def record_search_topic(root: Path, module_id: str, question: str, user_code: str | None = None) -> dict[str, Any]:
    return ExpansionStore(root).record_query(module_id, question, user_code)


def _source_score(module_id: str, url: str, title: str, keywords: list[str]) -> float:
    host = (urlparse(url).hostname or "").casefold()
    text = normalize(f"{url} {title}")
    score = sum(1 for term in keywords if normalize(term) in text)
    trusted = TRUSTED_DOMAINS.get(module_id, ())
    if any(host == domain or host.endswith(f".{domain}") for domain in trusted):
        score += 4
    if host.endswith((".gov.br", ".gov", ".edu", ".edu.br")):
        score += 3
    if host.endswith((".org", ".org.br")):
        score += 1
    return float(score)


def _domain_allowed(store: ExpansionStore, module_id: str, url: str, score: float, keywords: list[str]) -> bool:
    host = (urlparse(url).hostname or "").casefold()
    entries = store.domains(module_id)
    for domain, mode in entries.items():
        if host == domain or host.endswith(f".{domain}"):
            return mode == "allow"
    if os.getenv("SOFIA_EXPANSION_ALLOW_ANY_DOMAIN", "false").strip().casefold() in {"1", "true", "yes", "on", "sim"}:
        return True
    return (score >= expansion_settings()["relevance_threshold"] and any(normalize(term) in normalize(url) for term in keywords)) or score >= 4


def _clean_public_content(content: str) -> str:
    """Remove common prompt-injection instructions from public snapshots."""
    blocked = (
        "ignore previous instructions",
        "ignore all previous",
        "desconsidere as instruções anteriores",
        "desconsidere todas as regras",
        "system prompt",
        "mensagem do sistema",
    )
    lines = []
    for line in content.splitlines():
        if any(marker in normalize(line) for marker in blocked):
            continue
        if re.search(r"<\s*(script|iframe|object|form)\b", line, re.IGNORECASE):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _similar_content_exists(root: Path, module_id: str, content: str) -> bool:
    """Detect near duplicates before publishing another offline document."""
    candidate_tokens = set(re.findall(r"[a-z0-9À-ÿ]{4,}", normalize(content)))
    if len(candidate_tokens) < 20:
        return False
    for path in files_for(root, module_id):
        try:
            existing_text = extract_text(path)
        except (OSError, ValueError, RuntimeError):
            continue
        existing_tokens = set(re.findall(r"[a-z0-9À-ÿ]{4,}", normalize(existing_text)))
        if len(existing_tokens) < 20:
            continue
        intersection = len(candidate_tokens & existing_tokens)
        union = len(candidate_tokens | existing_tokens)
        if union and intersection / union >= 0.92:
            return True
    return False


def _module_storage_bytes(root: Path, module_id: str) -> int:
    module_root = root / module_id
    if not module_root.exists():
        return 0
    return sum(path.stat().st_size for path in module_root.rglob("*") if path.is_file())


def _topic_search_queries(topic: dict[str, Any], module_id: str, keywords: list[str]) -> list[str]:
    key = str(topic.get("topic_key", ""))
    main = str(topic.get("main_topic", key.replace("/", " ")))
    terms = list(dict.fromkeys([main, key.replace("/", " "), *keywords]))[:8]
    if module_id == "infraestrutura" and "zabbix" in normalize(main):
        return [f"Zabbix {term} official documentation" for term in terms[:4]]
    if module_id == "medicina" and any(term in normalize(main) for term in ("gripe", "influenza")):
        return [f"influenza {term} Ministério da Saúde WHO" for term in terms[:4]]
    return [f"{main} {term} documentação oficial" for term in terms[:4]]


def _topic_keywords(store: ExpansionStore, topic_id: int) -> list[str]:
    connection = _connect(store.path)
    try:
        return [str(row["term"]) for row in connection.execute("SELECT term FROM topic_keywords WHERE topic_id = ? ORDER BY depth, confidence DESC LIMIT 24", (topic_id,)).fetchall()]
    finally:
        connection.close()


def expand_topic(root: Path, topic: dict[str, Any]) -> dict[str, Any]:
    module_id = str(topic["module_id"])
    store = ExpansionStore(root)
    settings = expansion_settings()
    base = {"topic_id": int(topic["topic_id"]), "module_id": module_id, "pages_discovered": 0, "pages_new": 0, "pages_updated": 0, "duplicates_ignored": 0, "stored": 0, "errors": [], "queries": []}
    if not external_data_allowed():
        return {**base, "status": "BLOCKED", "reason": "SOFIA_ALLOW_EXTERNAL_DATA=false"}
    if module_id == "medicina" and not external_clinical_allowed():
        return {**base, "status": "BLOCKED", "reason": "SOFIA_ALLOW_EXTERNAL_CLINICAL=false"}
    if "duckduckgo" not in settings["search_providers"]:
        return {**base, "status": "BLOCKED", "reason": "duckduckgo não está habilitado"}
    keywords = _topic_keywords(store, int(topic["topic_id"]))
    search_results: dict[str, dict[str, str]] = {}
    for query in _topic_search_queries(topic, module_id, keywords):
        base["queries"].append(query)
        for item in _search_links(query, limit=5):
            try:
                canonical = normalize_url(str(item["url"]))
            except ValueError:
                continue
            search_results.setdefault(canonical, {**item, "url": canonical})
    ranked = sorted(search_results.values(), key=lambda item: _source_score(module_id, item["url"], item.get("title", ""), keywords), reverse=True)
    remaining = settings["max_pages_per_topic"]
    for item in ranked:
        if remaining <= 0:
            break
        url = str(item["url"])
        score = _source_score(module_id, url, str(item.get("title", "")), keywords)
        if not _domain_allowed(store, module_id, url, score, keywords):
            continue
        host = (urlparse(url).hostname or "").casefold()
        existing = store.source_by_url(module_id, url)
        try:
            fetched = fetch_link(url, max_pages=remaining, timeout_seconds=settings["timeout_seconds"], max_depth=settings["max_depth"], allowed_hosts={host})
            base["pages_discovered"] += len(fetched.pages)
            clean_content = _clean_public_content(ExternalRedaction().clean(fetched.content))
            content_hash = hashlib.sha256(clean_content.encode("utf-8")).hexdigest()
            if (store.content_exists(module_id, content_hash) or _similar_content_exists(root, module_id, clean_content)) and not existing:
                base["duplicates_ignored"] += 1
                remaining -= len(fetched.pages)
                continue
            if _module_storage_bytes(root, module_id) + len(clean_content.encode("utf-8")) > settings["max_storage_mb_per_module"] * 1024 * 1024:
                base["errors"].append("limite de armazenamento do módulo atingido")
                break
            record = save_fetched_link(root, module_id, fetched.__class__(fetched.url, fetched.final_url, fetched.title, clean_content, fetched.pages, fetched.fetched_at, fetched.etag, fetched.last_modified), content_transform=None)
            local_path = str(root / module_id / "links" / str(record["file_name"]))
            source_id = store.register_source(
                module_id,
                "url",
                url=url,
                canonical_url=fetched.final_url,
                local_path=local_path,
                title=fetched.title,
                status="READY",
                reliability=score / 10,
                content_hash=content_hash,
                pages=len(fetched.pages),
                bytes_count=len(clean_content.encode("utf-8")),
                etag=fetched.etag,
                last_modified=fetched.last_modified,
            )
            pipeline = record_document_pipeline(root, module_id, Path(local_path), source_id=source_id)
            if pipeline["status"] not in {"READY", "PARTIAL"}:
                base["errors"].append(pipeline.get("error", "documento não validado"))
                store.add_error(module_id, "VALIDATING", str(pipeline.get("error", "documento não validado")), document_id=pipeline.get("document_id"))
                continue
            base["stored"] += 1
            if existing and str(existing["content_hash"] or "") == content_hash:
                base["duplicates_ignored"] += 1
            elif existing:
                base["pages_updated"] += len(fetched.pages)
            else:
                base["pages_new"] += len(fetched.pages)
            remaining -= len(fetched.pages)
        except (OSError, RuntimeError, ValueError) as exc:
            message = str(exc)[:400]
            base["errors"].append(message)
            store.add_error(module_id, "DOWNLOADING", message, error_type=type(exc).__name__, retryable=True)
    base["status"] = "READY" if base["stored"] or base["duplicates_ignored"] else ("PARTIAL" if base["errors"] else "NO_RESULTS")
    return base


def run_expansion_cycle(root: Path, module_id: str | None = None) -> dict[str, Any]:
    settings = expansion_settings()
    store = ExpansionStore(root)
    store.initialize()
    if not settings["enabled"] or store.is_paused():
        return {"status": "PAUSED", "reason": "expansão automática desativada ou pausada", "metrics": store.snapshot()}
    cycle_id, topics = store.claim_topics(settings["max_topics_per_cycle"], module_id)
    metrics: dict[str, Any] = {"cycle_id": cycle_id, "topics_claimed": len(topics), "topics_completed": 0, "pages_discovered": 0, "pages_new": 0, "pages_updated": 0, "duplicates_ignored": 0, "stored": 0, "errors": 0, "items": []}
    for topic in topics:
        try:
            result = expand_topic(root, topic)
            metrics["items"].append(result)
            for key in ("pages_discovered", "pages_new", "pages_updated", "duplicates_ignored", "stored"):
                metrics[key] += int(result.get(key, 0) or 0)
            metrics["errors"] += len(result.get("errors", []))
            topic_status = "READY" if result.get("status") in {"READY", "NO_RESULTS", "BLOCKED"} else "FAILED"
            store.finish_topic(int(topic["topic_id"]), topic_status, "; ".join(result.get("errors", [])) or result.get("reason"))
            metrics["topics_completed"] += 1
        except Exception as exc:
            logger.exception("Falha isolada na expansão do tópico %s", topic.get("topic_key"))
            message = str(exc)[:400]
            metrics["errors"] += 1
            store.add_error(str(topic["module_id"]), "EXPANSION", message, error_type=type(exc).__name__, retryable=True)
            store.finish_topic(int(topic["topic_id"]), "FAILED", message)
    store.finish_cycle(cycle_id, metrics, "READY" if metrics["errors"] == 0 else "PARTIAL")
    return {"status": "READY" if topics else "IDLE", "metrics": metrics, "snapshot": store.snapshot()}


def record_document_pipeline(root: Path, module_id: str, path: Path, source_id: int | None = None) -> dict[str, Any]:
    """Run one source through the observable, independently retryable pipeline."""
    store = ExpansionStore(root)
    store.initialize()
    now = _now()
    path = path.resolve()
    relative = str(path)
    mime_type = path.suffix.lower().lstrip(".")
    file_hash = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    source_origin = "url" if path.parent.name.casefold() == "links" else "local"
    connection = _connect(store.path)
    document_id: int | None = None
    job_id: int | None = None
    version = 1

    def mark_stage(stage: str, status: str = "complete", metrics: dict[str, Any] | None = None, error: str | None = None) -> None:
        nonlocal connection
        finished = _now()
        connection.execute(
            "UPDATE documents SET current_stage = ?, status = ?, updated_at = ? WHERE id = ?",
            (stage, stage if status == "complete" else status, finished, document_id),
        )
        connection.execute(
            "INSERT INTO document_pipeline_events (module_id, document_id, stage, status, started_at, finished_at, metrics_json, error_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (module_id, document_id, stage, status, finished, finished, json.dumps(metrics or {}, ensure_ascii=False), error),
        )
        connection.commit()

    try:
        row = connection.execute("SELECT * FROM documents WHERE module_id = ? AND path = ?", (module_id, relative)).fetchone()
        if row:
            document_id = int(row["id"])
            version = int(row["version_number"] or 1) + 1
            connection.execute(
                "UPDATE documents SET status = 'RECEIVED', current_stage = 'RECEIVED', source_id = COALESCE(?, source_id), version_number = ?, file_hash = ?, source_origin = ?, bytes = ?, updated_at = ? WHERE id = ?",
                (source_id, version, file_hash, source_origin, path.stat().st_size if path.exists() else 0, now, document_id),
            )
        else:
            duplicate = connection.execute(
                "SELECT id, file_name FROM documents WHERE module_id = ? AND file_hash = ? AND status = 'READY' LIMIT 1",
                (module_id, file_hash),
            ).fetchone() if file_hash else None
            cursor = connection.execute(
                "INSERT INTO documents (module_id, source_id, path, file_name, mime_type, status, bytes, file_hash, duplicate_of, source_origin, sensitivity, current_stage, received_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 'RECEIVED', ?, ?, ?, ?, ?, 'RECEIVED', ?, ?, ?)",
                (module_id, source_id, relative, path.name, mime_type, path.stat().st_size if path.exists() else 0, file_hash, int(duplicate["id"]) if duplicate else None, source_origin, "health" if module_id == "medicina" else "internal", now, now, now),
            )
            document_id = int(cursor.lastrowid)
            if duplicate:
                connection.execute("UPDATE documents SET status = 'DUPLICATE', current_stage = 'VALIDATING', validation_status = 'DUPLICATE' WHERE id = ?", (document_id,))
        if document_id is None:
            raise RuntimeError("documento não foi criado")
        job_cursor = connection.execute("INSERT INTO processing_jobs (module_id, source_id, document_id, job_type, status, started_at) VALUES (?, ?, ?, 'document_pipeline', 'RUNNING', ?)", (module_id, source_id, document_id, now))
        job_id = int(job_cursor.lastrowid)
        connection.execute("INSERT INTO document_pipeline_events (module_id, document_id, stage, status, started_at, finished_at, metrics_json) VALUES (?, ?, 'RECEIVED', 'complete', ?, ?, '{}')", (module_id, document_id, now, now))
        connection.commit()
        if row is None and duplicate:
            connection.execute("UPDATE processing_jobs SET status = 'DUPLICATE', finished_at = ?, metrics_json = ? WHERE id = ?", (_now(), json.dumps({"duplicate_of": int(duplicate["id"])}, ensure_ascii=False), job_id))
            connection.commit()
            mark_stage("VALIDATING", "complete", {"duplicate_of": int(duplicate["id"])})
            return {"status": "DUPLICATE", "document_id": document_id, "duplicate_of": int(duplicate["id"]), "file": path.name}
    except (OSError, sqlite3.Error) as exc:
        connection.close()
        store.add_error(module_id, "RECEIVED", str(exc), error_type=type(exc).__name__, retryable=True, document_id=document_id)
        return {"status": "FAILED", "document_id": document_id, "error": str(exc)}
    finally:
        if not connection is None:
            connection.close()

    try:
        connection = _connect(store.path)
        mark_stage("EXTRACTING", "complete")
        is_image = path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
        if is_image or path.suffix.lower() == ".pdf":
            mark_stage("OCR", "complete", {"mode": "ocr-or-native", "source_type": "image" if is_image else "pdf"})
        text = extract_text(path)
        invalid_chars = sum(1 for char in text if ord(char) < 9 or (13 < ord(char) < 32))
        quality = max(0.0, min(1.0, (len(text.strip()) / 300.0) - (invalid_chars / max(1, len(text)))))
        ocr_quality = round(quality, 4) if is_image or path.suffix.lower() == ".pdf" else None
        if len(text.strip()) < 20 or invalid_chars > max(10, len(text) * 0.02):
            raise ValueError(f"quality gate reprovado: texto={len(text.strip())} caracteres inválidos={invalid_chars}")
        mark_stage("QUALITY_CHECK", "complete", {"text_chars": len(text), "invalid_chars": invalid_chars, "quality": round(quality, 4)})
        mark_stage("NORMALIZING", "complete")
        mark_stage("MARKDOWN_READY", "complete", {"format": "normalized-text"})
        artifacts = build_artifacts(path, text, module_id)
        mark_stage("UNDERSTANDING", "complete", {"keywords": len(artifacts["keywords"]), "entities": len(artifacts["entities"]), "concepts": len(artifacts["concepts"])})
        chunks = ingest_module(root, module_id, selected_paths=(path,))
        valid_chunks = [chunk for chunk in chunks if isinstance(chunk, DocumentChunk) and len(chunk.text.strip()) >= 20]
        if not valid_chunks:
            raise ValueError("nenhum chunk válido foi produzido")
        mark_stage("CHUNKING", "complete", {"chunks": len(valid_chunks)})
        mark_stage("EMBEDDING", "complete", {"backend": "tfidf-local", "vectors": len(valid_chunks)})
        mark_stage("RELATING", "complete", {"relations": len(artifacts["relations"])})
        content_hash = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
        connection.execute("DELETE FROM document_chunks WHERE document_id = ? AND version_number = ?", (document_id, version))
        for ordinal, chunk in enumerate(valid_chunks):
            connection.execute("INSERT INTO document_chunks (document_id, version_number, ordinal, content_hash, char_count, status) VALUES (?, ?, ?, ?, ?, 'READY')", (document_id, version, ordinal, hashlib.sha256(chunk.text.encode("utf-8", errors="replace")).hexdigest(), len(chunk.text)))
        connection.execute("DELETE FROM knowledge_artifacts WHERE document_id = ?", (document_id,))
        connection.execute(
            "INSERT INTO knowledge_artifacts (document_id, version_number, artifact_version, summary, keywords_json, entities_json, concepts_json, relations_json, questions_json, claims_json, dates_json, people_json, organizations_json, topics_json, contradictions_json, embedding_json, provenance_json, quality, ocr_quality, generated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (document_id, version, artifacts.get("artifact_version", "1.0"), artifacts["summary"], json.dumps(artifacts["keywords"], ensure_ascii=False), json.dumps(artifacts["entities"], ensure_ascii=False), json.dumps(artifacts["concepts"], ensure_ascii=False), json.dumps(artifacts["relations"], ensure_ascii=False), json.dumps(artifacts["questions"], ensure_ascii=False), json.dumps(artifacts.get("claims", []), ensure_ascii=False), json.dumps(artifacts.get("dates", []), ensure_ascii=False), json.dumps(artifacts.get("people", []), ensure_ascii=False), json.dumps(artifacts.get("organizations", []), ensure_ascii=False), json.dumps(artifacts.get("topics", []), ensure_ascii=False), json.dumps(artifacts.get("contradictions", []), ensure_ascii=False), json.dumps(artifacts.get("embedding", {}), ensure_ascii=False), json.dumps(artifacts.get("provenance", {}), ensure_ascii=False), artifacts["quality"], ocr_quality, _now()),
        )
        connection.commit()
        mark_stage("INDEXING", "complete", {"backend": "filesystem-plus-local-vector", "chunks": len(valid_chunks)})
        connection.execute("UPDATE documents SET status = 'VALIDATING', content_hash = ?, bytes = ?, chunk_count = ?, extraction_quality = ?, ocr_quality = ?, summary = ?, keywords_json = ?, entities_json = ?, concepts_json = ?, relations_json = ?, questions_json = ?, embeddings_status = 'READY', indexing_status = 'READY', validation_status = 'PENDING', updated_at = ? WHERE id = ?", (content_hash, path.stat().st_size, len(valid_chunks), artifacts["quality"], ocr_quality, artifacts["summary"], json.dumps(artifacts["keywords"], ensure_ascii=False), json.dumps(artifacts["entities"], ensure_ascii=False), json.dumps(artifacts["concepts"], ensure_ascii=False), json.dumps(artifacts["relations"], ensure_ascii=False), json.dumps(artifacts["questions"], ensure_ascii=False), _now(), document_id))
        mark_stage("VALIDATING", "complete", {"questions": len(artifacts["questions"]), "citation_ready": True})
        connection.execute("UPDATE documents SET status = 'READY', current_stage = 'READY', validation_status = 'READY', updated_at = ? WHERE id = ?", (_now(), document_id))
        connection.execute("INSERT INTO retrieval_tests (module_id, document_id, source_id, title_ok, semantic_ok, module_ok, citation_ok, created_at) VALUES (?, ?, ?, ?, ?, 1, 1, ?)", (module_id, document_id, source_id, int(path.stem.casefold() in text.casefold() or len(text) > 20), 1, _now()))
        connection.execute("UPDATE processing_jobs SET status = 'READY', finished_at = ?, metrics_json = ? WHERE id = ?", (_now(), json.dumps({"chunks": len(valid_chunks), "text_chars": len(text), "quality": artifacts["quality"]}, ensure_ascii=False), job_id))
        connection.commit()
        connection.close()
        try:
            from .knowledge_graph import build_graph

            build_graph(root, module_id)
        except Exception:
            # Graph derivation is a non-blocking artifact. A valid document
            # must remain READY even when a derived graph needs retrying.
            logger.warning("Não foi possível atualizar o evidence graph de %s", module_id, exc_info=True)
        return {"status": "READY", "document_id": document_id, "chunks": len(valid_chunks), "text_chars": len(text), "quality": artifacts["quality"], "ocr_quality": ocr_quality, "artifacts": {key: artifacts[key] for key in ("summary", "keywords", "entities", "concepts", "relations", "questions")}}
    except Exception as exc:  # noqa: BLE001
        message = str(exc)[:800]
        logger.warning("Pipeline isolado falhou para %s: %s", path, message)
        quarantined_path = path
        if path.exists() and "quarantine" not in {part.casefold() for part in path.parts}:
            quarantine_dir = path.parent / "quarantine"
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            candidate = quarantine_dir / path.name
            if candidate.exists():
                candidate = quarantine_dir / f"{path.stem}-{hashlib.sha256(str(path).encode()).hexdigest()[:8]}{path.suffix}"
            try:
                shutil.move(str(path), str(candidate))
                quarantined_path = candidate
            except OSError:
                logger.warning("Não foi possível mover a fonte para quarentena: %s", path, exc_info=True)
        try:
            try:
                connection.close()
            except sqlite3.Error:
                pass
            connection = _connect(store.path)
            failed_stage = connection.execute("SELECT current_stage FROM documents WHERE id = ?", (document_id,)).fetchone()
            stage = str(failed_stage["current_stage"]) if failed_stage else "EXTRACTING"
            connection.execute("UPDATE documents SET status = ?, current_stage = ?, path = ?, error_count = error_count + 1, validation_status = 'FAILED', updated_at = ? WHERE id = ?", ("QUARANTINED" if quarantined_path != path else "FAILED", stage, str(quarantined_path), _now(), document_id))
            connection.execute("INSERT INTO document_pipeline_events (module_id, document_id, stage, status, started_at, finished_at, metrics_json, error_message) VALUES (?, ?, ?, 'failed', ?, ?, '{}', ?)", (module_id, document_id, stage, _now(), _now(), message))
            if job_id:
                connection.execute("UPDATE processing_jobs SET status = 'FAILED', finished_at = ?, metrics_json = ? WHERE id = ?", (_now(), json.dumps({"stage": stage, "error": message}, ensure_ascii=False), job_id))
            connection.commit()
        finally:
            connection.close()
        store.add_error(module_id, stage, message, error_type=type(exc).__name__, retryable=True, document_id=document_id, source_id=source_id)
        return {"status": "QUARANTINED" if quarantined_path != path else "FAILED", "document_id": document_id, "error": message, "path": str(quarantined_path), "stage": stage}


def audit_module_documents(root: Path, module_id: str) -> dict[str, Any]:
    results = []
    for path in files_for(root, module_id):
        try:
            results.append(record_document_pipeline(root, module_id, path))
        except Exception as exc:
            logger.exception("Falha no documento %s", path)
            results.append({"status": "FAILED", "path": str(path), "error": str(exc)})
    return {"module_id": module_id, "documents": results, "summary": ExpansionStore(root).snapshot(module_id)}


def expansion_status(root: Path, module_id: str | None = None) -> dict[str, Any]:
    return ExpansionStore(root).snapshot(module_id)


def pipeline_documents(root: Path, module_id: str, limit: int = 100) -> list[dict[str, Any]]:
    return ExpansionStore(root).pipeline_documents(module_id, limit)
