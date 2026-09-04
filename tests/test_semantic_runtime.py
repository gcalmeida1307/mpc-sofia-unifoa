from __future__ import annotations

from api.embeddings import _cosine
from api.expansion import _postgres_schema, _postgres_sql


def test_postgres_adapter_translates_sqlite_placeholders_and_functions() -> None:
    sql = _postgres_sql("BEGIN IMMEDIATE; UPDATE sources SET reliability = MAX(reliability, ?), pages = MAX(pages, ?) WHERE id = ?")

    assert "BEGIN;" in sql
    assert "GREATEST(reliability, %s)" in sql
    assert "GREATEST(pages, %s)" in sql
    assert sql.count("%s") == 3


def test_postgres_adapter_qualifies_upsert_confidence_column() -> None:
    sql = _postgres_sql(
        "INSERT INTO topic_keywords (confidence) VALUES (?) "
        "ON CONFLICT(topic_id, term) DO UPDATE SET "
        "confidence = MAX(confidence, excluded.confidence)"
    )

    assert "GREATEST(topic_keywords.confidence, excluded.confidence)" in sql
    assert "MAX(confidence, excluded.confidence)" not in sql


def test_postgres_schema_removes_sqlite_autoincrement() -> None:
    schema = _postgres_schema()

    assert "AUTOINCREMENT" not in schema
    assert "BIGSERIAL PRIMARY KEY" in schema


def test_cosine_embedding_is_bounded_and_directional() -> None:
    assert _cosine([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert _cosine([1.0, 0.0], [0.0, 1.0]) == 0.0
