"""Small PostgreSQL adapter shared by operational SOFIA stores."""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType
from typing import Any, Self

try:
    import psycopg
except ImportError:  # pragma: no cover - developer environments may omit PG
    psycopg = None

from .storage import postgres_dsn, strict_storage


class HybridRow(dict[str, Any]):
    """A row compatible with both sqlite's named and positional access."""

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def _row_factory(cursor: Any) -> Any:
    if cursor.description is None:
        return lambda values: None
    names = [column.name for column in cursor.description]

    def make_row(values: Any) -> HybridRow:
        return HybridRow(zip(names, values))

    return make_row


class PostgresConnection:
    backend = "postgresql"

    def __init__(self, raw: Any) -> None:
        self.raw = raw
        self.raw.execute("CREATE SCHEMA IF NOT EXISTS sofia_runtime")
        self.raw.execute("SET search_path TO sofia_runtime")

    def execute(self, sql: str, params: Any = ()) -> Any:
        translated = re.sub(r"\?", "%s", sql.replace("BEGIN IMMEDIATE", "BEGIN"))
        return self.raw.execute(translated, params)

    def executemany(self, sql: str, params: Any) -> Any:
        translated = re.sub(r"\?", "%s", sql.replace("BEGIN IMMEDIATE", "BEGIN"))
        with self.raw.cursor() as cursor:
            return cursor.executemany(translated, params)

    def executescript(self, script: str) -> None:
        for statement in script.split(";"):
            if statement.strip():
                self.execute(statement)

    def commit(self) -> None:
        self.raw.commit()

    def rollback(self) -> None:
        self.raw.rollback()

    def close(self) -> None:
        self.raw.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


def _connect_raw() -> PostgresConnection | None:
    dsn = postgres_dsn()
    if not dsn or psycopg is None:
        return None
    try:
        # A custom row factory is used because the existing domain code reads
        # rows by both column name and ordinal position.
        raw = psycopg.connect(dsn, connect_timeout=5, row_factory=_row_factory)
        return PostgresConnection(raw)
    except Exception:
        if strict_storage():
            raise
        return None


@contextmanager
def postgres_connection(required: bool = False) -> Iterator[PostgresConnection | None]:
    connection = _connect_raw()
    if required and connection is None:
        raise RuntimeError("PostgreSQL não está disponível")
    try:
        yield connection
    finally:
        if connection is not None:
            connection.close()


def is_postgres(connection: Any) -> bool:
    return getattr(connection, "backend", None) == "postgresql"


__all__ = ["PostgresConnection", "is_postgres", "postgres_connection"]
