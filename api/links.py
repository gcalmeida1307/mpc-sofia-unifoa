from __future__ import annotations

import hashlib
import ipaddress
import json
import logging
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import httpx

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # The local JSON adapter keeps development usable without PostgreSQL.
    psycopg = None
    dict_row = None

logger = logging.getLogger("sofia.links")
MAX_LINK_CHARS = 250_000
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_CRAWL_PAGES = 20
MAX_CRAWL_DEPTH = 3
LINKS_JSON = "links.json"
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "dclid", "msclkid", "ref", "ref_", "mc_cid", "mc_eid"}
RESPECT_ROBOTS = os.getenv("SOFIA_RESPECT_ROBOTS", "true").strip().casefold() not in {"0", "false", "no", "off"}


class _HTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.links: list[str] = []
        self._ignored = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        if tag in {"script", "style", "noscript", "svg", "template"}:
            self._ignored += 1
        if tag == "title":
            self._in_title = True
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"script", "style", "noscript", "svg", "template"}:
            self._ignored = max(0, self._ignored - 1)
        if tag.casefold() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored:
            return
        value = " ".join(data.split())
        if not value:
            return
        self.text_parts.append(value)
        if self._in_title and len(self.title_parts) < 20:
            self.title_parts.append(value)


@dataclass(frozen=True)
class FetchedLink:
    url: str
    final_url: str
    title: str
    content: str
    pages: tuple[str, ...]
    fetched_at: str
    etag: str = ""
    last_modified: str = ""


def normalize_url(value: str) -> str:
    """Return a stable URL key without tracking parameters or fragments."""
    parsed = urlparse(value.strip())
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("O link deve começar com http:// ou https://")
    hostname = parsed.hostname.casefold()
    port = parsed.port
    netloc = hostname
    if port and not ((parsed.scheme.casefold() == "http" and port == 80) or (parsed.scheme.casefold() == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    query = [
        (key, item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.casefold().startswith("utm_") and key.casefold() not in TRACKING_QUERY_KEYS
    ]
    query.sort()
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.casefold(), netloc, path, "", urlencode(query), ""))


def _dsn() -> str:
    return os.getenv("SOFIA_POSTGRES_URL", os.getenv("DATABASE_URL", "")).strip()


def _validate_url(value: str) -> str:
    normalized = normalize_url(value)
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("O link deve começar com http:// ou https://")
    host = parsed.hostname.casefold()
    if host in {"localhost", "localhost.localdomain"}:
        raise ValueError("Links para localhost não podem ser indexados")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved):
        raise ValueError("Links para redes privadas não podem ser indexados")
    return normalized


def _fetch_one_meta(client: httpx.Client, url: str) -> tuple[str, str, str, list[str], dict[str, str], int]:
    try:
        response = client.get(url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValueError(f"Não foi possível acessar o link: {exc}") from exc
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise ValueError("A página excede o limite de 8 MB")
    content_type = response.headers.get("content-type", "").casefold()
    if "text/html" in content_type:
        parser = _HTMLParser()
        parser.feed(response.text)
        title = " ".join(parser.title_parts[:8]).strip() or urlparse(str(response.url)).netloc
        content = "\n".join(parser.text_parts)
        return str(response.url), title, content[:MAX_LINK_CHARS], parser.links, dict(response.headers), response.status_code
    if content_type.startswith("text/") or "json" in content_type or "xml" in content_type:
        return str(response.url), urlparse(str(response.url)).path.rsplit("/", 1)[-1] or str(response.url), response.text[:MAX_LINK_CHARS], [], dict(response.headers), response.status_code
    raise ValueError("O link precisa apontar para HTML, texto, JSON ou XML")


def _fetch_one(client: httpx.Client, url: str) -> tuple[str, str, str, list[str]]:
    """Compatibility wrapper used by callers that do not need HTTP metadata."""
    final_url, title, content, links, _, _ = _fetch_one_meta(client, url)
    return final_url, title, content, links


def _robots_allowed(client: httpx.Client, url: str, cache: dict[str, RobotFileParser | None]) -> bool:
    """Honor robots.txt when enabled; an unavailable policy is fail-closed."""
    if not RESPECT_ROBOTS:
        return True
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin not in cache:
        robots = RobotFileParser()
        robots.set_url(f"{origin}/robots.txt")
        try:
            response = client.get(robots.url)
            if response.status_code in {401, 403}:
                cache[origin] = None
            elif response.status_code >= 400:
                cache[origin] = RobotFileParser()
                cache[origin].parse([])
            else:
                robots.parse(response.text.splitlines())
                cache[origin] = robots
        except httpx.HTTPError:
            cache[origin] = None
    policy = cache[origin]
    return policy is not None and policy.can_fetch("SofiaLocalKnowledgeBot", url)


def fetch_link(
    url: str,
    max_pages: int = 1,
    timeout_seconds: float = 20.0,
    max_depth: int = 1,
    allowed_hosts: set[str] | None = None,
) -> FetchedLink:
    """Fetch one page or a bounded same-domain set for dense domain research."""
    start_url = _validate_url(url)
    if not 1 <= max_pages <= MAX_CRAWL_PAGES:
        raise ValueError(f"max_pages deve estar entre 1 e {MAX_CRAWL_PAGES}")
    if not 0 <= max_depth <= MAX_CRAWL_DEPTH:
        raise ValueError(f"max_depth deve estar entre 0 e {MAX_CRAWL_DEPTH}")
    timeout_seconds = max(3.0, min(60.0, float(timeout_seconds)))
    start_host = (urlparse(start_url).hostname or "").casefold()
    hosts = {host.casefold() for host in (allowed_hosts or {start_host})}
    if start_host not in hosts:
        hosts.add(start_host)
    start_path = urlparse(start_url).path.rstrip("/") or "/"
    queue: list[tuple[str, int]] = [(start_url, 0)]
    attempted: set[str] = set()
    visited: list[str] = []
    sections: list[str] = []
    first_title = ""
    first_etag = ""
    first_last_modified = ""
    headers = {"User-Agent": "SofiaLocalKnowledgeBot/1.0 (+local RAG)"}
    robots_cache: dict[str, RobotFileParser | None] = {}
    with httpx.Client(follow_redirects=True, timeout=timeout_seconds, headers=headers) as client:
        while queue and len(visited) < max_pages:
            current, depth = queue.pop(0)
            current = _validate_url(current)
            if current in attempted or current in visited:
                continue
            attempted.add(current)
            if not _robots_allowed(client, current, robots_cache):
                message = f"robots.txt não autoriza a captura de {current}"
                if not visited:
                    raise ValueError(message)
                logger.info(message)
                continue
            try:
                final_url, title, content, links, response_headers, _ = _fetch_one_meta(client, current)
            except ValueError as exc:
                if not visited:
                    raise
                # Documentation indexes often retain links to retired
                # versions. One dead internal page must not discard the
                # successful pages already collected.
                logger.warning("Skipping internal link %s: %s", current, exc)
                continue
            final_url = _validate_url(final_url)
            if (urlparse(final_url).hostname or "").casefold() not in hosts:
                logger.warning("Skipping redirect outside the allowlist: %s", final_url)
                continue
            visited.append(final_url)
            first_title = first_title or title
            first_etag = first_etag or response_headers.get("etag", "")
            first_last_modified = first_last_modified or response_headers.get("last-modified", "")
            sections.append(f"## {title}\nURL: {final_url}\n\n{content}")
            if depth >= max_depth:
                continue
            for href in links:
                try:
                    candidate = _validate_url(urljoin(final_url, href))
                except ValueError:
                    continue
                if (urlparse(candidate).hostname or "").casefold() not in hosts:
                    continue
                if candidate not in visited and all(candidate != item[0] for item in queue):
                    queue.append((candidate, depth + 1))
            queue.sort(key=lambda item: _crawl_priority(item[0], start_path))
    if not sections:
        raise ValueError("O link não retornou conteúdo consultável")
    return FetchedLink(start_url, visited[0], first_title, "\n\n".join(sections)[:MAX_LINK_CHARS], tuple(visited), datetime.now(UTC).isoformat(), first_etag, first_last_modified)


def link_not_modified(
    url: str,
    etag: str = "",
    last_modified: str = "",
    timeout_seconds: float = 20.0,
) -> bool:
    """Check a registered URL with HTTP validators without downloading it."""
    if not etag and not last_modified:
        return False
    target = _validate_url(url)
    headers = {"User-Agent": "SofiaLocalKnowledgeBot/1.0 (+local RAG)"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    timeout_seconds = max(3.0, min(60.0, float(timeout_seconds)))
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout_seconds, headers=headers) as client:
            response = client.get(target)
            return response.status_code == 304
    except httpx.HTTPError as exc:
        raise ValueError(f"Não foi possível validar o link: {exc}") from exc


def _crawl_priority(candidate: str, start_path: str) -> tuple[int, int, str]:
    """Prefer child documentation pages before version menus and home links."""
    path = urlparse(candidate).path.rstrip("/") or "/"
    child_prefix = f"{start_path}/" if start_path != "/" else "/"
    if path.startswith(child_prefix):
        rank = 0
    elif "/documentation/7.4/pt/manual" in path:
        rank = 1
    elif path.startswith("/documentation/"):
        rank = 2
    else:
        rank = 3
    return rank, len(path), candidate


def _safe_file_name(url: str) -> str:
    host = re.sub(r"[^a-z0-9]+", "-", (urlparse(url).hostname or "link").casefold()).strip("-")[:42] or "link"
    digest = hashlib.sha256(url.encode()).hexdigest()[:12]
    return f"{host}-{digest}.md"


class LinkRepository:
    """PostgreSQL repository with a small local fallback for first-run development."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.json_path = root.parent / "data" / LINKS_JSON

    @property
    def backend(self) -> str:
        return "postgresql" if _dsn() else "local-json"

    def _ensure_postgres(self, connection: psycopg.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sofia_knowledge_links (
                id BIGSERIAL PRIMARY KEY,
                module_id TEXT NOT NULL,
                url TEXT NOT NULL,
                final_url TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                pages INTEGER NOT NULL DEFAULT 1,
                fetched_at TIMESTAMPTZ NOT NULL,
                file_name TEXT NOT NULL,
                UNIQUE (module_id, url)
            )
            """
        )
        connection.execute("ALTER TABLE sofia_knowledge_links ADD COLUMN IF NOT EXISTS normalized_url TEXT")
        connection.execute("ALTER TABLE sofia_knowledge_links ADD COLUMN IF NOT EXISTS etag TEXT NOT NULL DEFAULT ''")
        connection.execute("ALTER TABLE sofia_knowledge_links ADD COLUMN IF NOT EXISTS last_modified TEXT NOT NULL DEFAULT ''")
        connection.execute("UPDATE sofia_knowledge_links SET normalized_url = url WHERE normalized_url IS NULL OR normalized_url = ''")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS sofia_knowledge_links_module_normalized_unique ON sofia_knowledge_links(module_id, normalized_url)")

    def save(self, module_id: str, fetched: FetchedLink, file_name: str) -> dict[str, str | int]:
        record: dict[str, str | int] = {
            "module_id": module_id,
            "url": normalize_url(fetched.url),
            "final_url": normalize_url(fetched.final_url),
            "title": fetched.title,
            "content_hash": hashlib.sha256(fetched.content.encode()).hexdigest(),
            "pages": len(fetched.pages),
            "fetched_at": fetched.fetched_at,
            "file_name": file_name,
            "etag": fetched.etag,
            "last_modified": fetched.last_modified,
            "storage": self.backend,
        }
        dsn = _dsn()
        if dsn:
            if psycopg is None:
                raise RuntimeError("psycopg não está instalado para usar PostgreSQL")
            try:
                with psycopg.connect(dsn, connect_timeout=5) as connection:
                    self._ensure_postgres(connection)
                    connection.execute(
                        """
                        INSERT INTO sofia_knowledge_links (module_id, url, normalized_url, final_url, title, content, content_hash, pages, fetched_at, file_name, etag, last_modified)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (module_id, normalized_url) DO UPDATE SET
                            final_url = EXCLUDED.final_url, title = EXCLUDED.title, content = EXCLUDED.content,
                            content_hash = EXCLUDED.content_hash, pages = EXCLUDED.pages, fetched_at = EXCLUDED.fetched_at,
                            file_name = EXCLUDED.file_name, etag = EXCLUDED.etag, last_modified = EXCLUDED.last_modified,
                            url = EXCLUDED.url
                        """,
                        (module_id, record["url"], record["url"], record["final_url"], fetched.title, fetched.content, record["content_hash"], len(fetched.pages), fetched.fetched_at, file_name, fetched.etag, fetched.last_modified),
                    )
                    connection.commit()
            except Exception as exc:
                raise RuntimeError(f"PostgreSQL indisponível: {exc}") from exc
            return record
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        records: list[dict[str, str | int]] = []
        if self.json_path.exists():
            records = json.loads(self.json_path.read_text(encoding="utf-8"))
        normalized_url = str(record["url"])
        records = [item for item in records if not (item.get("module_id") == module_id and normalize_url(str(item.get("normalized_url") or item.get("url", ""))) == normalized_url)]
        records.append(record)
        self.json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return record

    def list(self, module_id: str) -> list[dict[str, str | int]]:
        dsn = _dsn()
        if dsn:
            if psycopg is None:
                raise RuntimeError("psycopg não está instalado para usar PostgreSQL")
            try:
                with psycopg.connect(dsn, connect_timeout=5, row_factory=dict_row) as connection:
                    self._ensure_postgres(connection)
                    rows = connection.execute(
                        "SELECT module_id, url, final_url, normalized_url, title, content_hash, pages, fetched_at::text, file_name, etag, last_modified FROM sofia_knowledge_links WHERE module_id = %s ORDER BY fetched_at DESC",
                        (module_id,),
                    ).fetchall()
                return [dict(row) for row in rows]
            except Exception as exc:
                raise RuntimeError(f"PostgreSQL indisponível: {exc}") from exc
        if not self.json_path.exists():
            return []
        records = json.loads(self.json_path.read_text(encoding="utf-8"))
        return [item for item in records if item.get("module_id") == module_id]

    def mark_checked(self, module_id: str, url: str) -> None:
        """Record a validator check without creating a new document version."""
        normalized = normalize_url(url)
        checked_at = datetime.now(UTC).isoformat()
        dsn = _dsn()
        if dsn:
            if psycopg is None:
                raise RuntimeError("psycopg não está instalado para usar PostgreSQL")
            try:
                with psycopg.connect(dsn, connect_timeout=5) as connection:
                    self._ensure_postgres(connection)
                    connection.execute(
                        "UPDATE sofia_knowledge_links SET fetched_at = %s WHERE module_id = %s AND normalized_url = %s",
                        (checked_at, module_id, normalized),
                    )
                    connection.commit()
                return
            except Exception as exc:
                raise RuntimeError(f"PostgreSQL indisponível: {exc}") from exc
        if not self.json_path.exists():
            return
        records = json.loads(self.json_path.read_text(encoding="utf-8"))
        for item in records:
            try:
                item_url = normalize_url(str(item.get("normalized_url") or item.get("url", "")))
            except ValueError:
                continue
            if item.get("module_id") == module_id and item_url == normalized:
                item["fetched_at"] = checked_at
        self.json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def save_fetched_link(
    root: Path,
    module_id: str,
    fetched: FetchedLink,
    content_transform: Callable[[str], str] | None = None,
) -> dict[str, str | int | list[str]]:
    """Persist an already fetched page set exactly once after validation."""
    if content_transform is not None:
        # Public pages may still contain names, emails or clinical examples.
        # Transform before both the offline file and the PostgreSQL payload
        # are written, never after persistence.
        fetched = replace(fetched, content=content_transform(fetched.content))
    file_name = _safe_file_name(fetched.url)
    destination = root / module_id / "links" / file_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    material = f"# {fetched.title}\n\nFonte: {fetched.final_url}\nCapturado em: {fetched.fetched_at}\nPáginas no domínio: {len(fetched.pages)}\n\n{fetched.content}\n"
    if destination.exists():
        previous = destination.read_text(encoding="utf-8")
        if previous != material:
            history_dir = destination.parent.parent / ".versions"
            history_dir.mkdir(parents=True, exist_ok=True)
            history_name = f"{destination.stem}-{hashlib.sha256(previous.encode()).hexdigest()[:16]}.md"
            history_path = history_dir / history_name
            if not history_path.exists():
                history_path.write_text(previous, encoding="utf-8")
    temporary = destination.with_name(f".{destination.name}.{hashlib.sha256(material.encode()).hexdigest()[:10]}.tmp")
    temporary.write_text(material, encoding="utf-8")
    os.replace(temporary, destination)
    record = LinkRepository(root).save(module_id, fetched, file_name)
    return {**record, "pages_urls": list(fetched.pages)}


def ingest_link(
    root: Path,
    module_id: str,
    url: str,
    max_pages: int = 1,
    timeout_seconds: float = 20.0,
    content_transform: Callable[[str], str] | None = None,
    max_depth: int = 1,
    allowed_hosts: set[str] | None = None,
) -> dict[str, str | int | list[str]]:
    fetched = fetch_link(url, max_pages, timeout_seconds, max_depth, allowed_hosts)
    return save_fetched_link(root, module_id, fetched, content_transform)
