from __future__ import annotations

import json
import re
from collections import deque
from hashlib import sha1
from html.parser import HTMLParser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, urlunparse

import requests

from config.settings import settings
from services.qdrant_store import qdrant_store
from services.vector_store import vector_store


DEFAULT_DOCS_ROOT = Path("/app/docs")
FALLBACK_DOCS_ROOT = Path(__file__).resolve().parents[1] / ".." / "docs"
DOCS_ROOT = DEFAULT_DOCS_ROOT if DEFAULT_DOCS_ROOT.exists() else FALLBACK_DOCS_ROOT
EXTERNAL_DOCS_ROOT_NAME = "_external"
UPLOADS_ROOT_NAME = "_uploads"
KNOWLEDGE_STATE_FILE = "_knowledge_sources.json"
DEFAULT_CRAWL_MAX_PAGES = 12
DEFAULT_CRAWL_MAX_DEPTH = 2
DEFAULT_USER_AGENT = "SOFIA-Knowledge/1.0"


class _DocumentationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.links: list[str] = []
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_map = dict(attrs)
        if tag in {"script", "style", "nav", "footer", "header", "aside"}:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        if tag == "a":
            href = attrs_map.get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "nav", "footer", "header", "aside"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str):
        text = data.strip()
        if not text or self._skip_depth > 0:
            return
        if self._in_title:
            self.title_parts.append(text)
        else:
            self.text_parts.append(text)


def _external_docs_root() -> Path:
    return DOCS_ROOT / EXTERNAL_DOCS_ROOT_NAME


def _uploads_root() -> Path:
    return DOCS_ROOT / UPLOADS_ROOT_NAME


def _state_file() -> Path:
    return DOCS_ROOT / KNOWLEDGE_STATE_FILE


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _shorten_text(text: str, limit: int = 180) -> str:
    cleaned = _normalize_whitespace(text)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug or "document"


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized = parsed._replace(fragment="", query="")
    return urlunparse(normalized)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_source_name(url: str) -> str:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if parts:
        return _slugify(parts[-1].replace(".html", "").replace(".md", ""))
    return _slugify(parsed.netloc or "external_docs")


def _seed_path_prefix(url: str) -> str:
    path = urlparse(url).path or "/"
    if path.endswith("/"):
        return path.rstrip("/") or "/"
    tail = path.rsplit("/", 1)[-1]
    if "." in tail:
        return path.rsplit("/", 1)[0] or "/"
    return path.rstrip("/") or "/"


def _load_knowledge_state() -> dict[str, Any]:
    path = _state_file()
    if not path.exists():
        return {"sources": [], "uploads": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data.setdefault("sources", [])
            data.setdefault("uploads", [])
            return data
    except Exception:
        pass
    return {"sources": [], "uploads": []}


def _save_knowledge_state(state: dict[str, Any]) -> None:
    path = _state_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _unique_sequence(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _normalize_allowed_domains(url: str, payload: dict[str, Any]) -> list[str]:
    parsed = urlparse(url)
    fallback = [parsed.netloc.lower()] if parsed.netloc else []
    provided = payload.get("allowed_domains") or payload.get("scope_domains") or []
    if isinstance(provided, str):
        provided = [provided]
    domains = [str(domain).strip().lower() for domain in provided if str(domain).strip()]
    if not domains:
        domains = fallback
    return _unique_sequence(domains)


def _normalize_allowed_paths(url: str, payload: dict[str, Any]) -> list[str]:
    provided = payload.get("allowed_paths") or payload.get("scope_paths") or []
    if isinstance(provided, str):
        provided = [provided]
    paths = [str(path).strip() for path in provided if str(path).strip()]
    if not paths:
        paths = [_seed_path_prefix(url)]
    normalized = []
    for path in paths:
        if not path.startswith("/"):
            path = f"/{path}"
        normalized.append(path.rstrip("/") or "/")
    return _unique_sequence(normalized)


def _source_record_defaults(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or payload.get("source") or "")
    name = str(payload.get("name") or payload.get("source") or _default_source_name(url))
    allowed_domains = _normalize_allowed_domains(url, payload)
    allowed_paths = _normalize_allowed_paths(url, payload)
    refresh_seconds = max(300, int(payload.get("refresh_seconds") or 86400))
    return {
        "name": _slugify(name),
        "label": payload.get("label") or name,
        "url": url,
        "enabled": bool(payload.get("enabled", True)),
        "refresh_seconds": refresh_seconds,
        "pages_per_refresh": max(1, int(payload.get("pages_per_refresh") or payload.get("max_pages") or DEFAULT_CRAWL_MAX_PAGES)),
        "crawl_depth": max(0, int(payload.get("crawl_depth") or payload.get("max_depth") or DEFAULT_CRAWL_MAX_DEPTH)),
        "allowed_domains": allowed_domains,
        "allowed_paths": allowed_paths,
        "metadata": payload.get("metadata") or {},
        "created_at": payload.get("created_at") or _now_iso(),
        "updated_at": _now_iso(),
        "last_refresh_at": payload.get("last_refresh_at"),
        "next_refresh_at": payload.get("next_refresh_at"),
        "last_status": payload.get("last_status") or "pending",
        "pages_indexed": int(payload.get("pages_indexed") or 0),
        "chunks_indexed": int(payload.get("chunks_indexed") or 0),
    }


def _list_source_records() -> list[dict[str, Any]]:
    state = _load_knowledge_state()
    records = state.get("sources", [])
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, dict)]


def _write_source_records(records: list[dict[str, Any]]) -> None:
    state = _load_knowledge_state()
    state["sources"] = records
    _save_knowledge_state(state)


def _upsert_source_record(record: dict[str, Any]) -> dict[str, Any]:
    records = _list_source_records()
    current = _source_record_defaults(record)
    updated = False
    for index, existing in enumerate(records):
        if existing.get("name") == current["name"]:
            current["created_at"] = existing.get("created_at") or current["created_at"]
            current["pages_indexed"] = existing.get("pages_indexed", current["pages_indexed"])
            current["chunks_indexed"] = existing.get("chunks_indexed", current["chunks_indexed"])
            current["last_refresh_at"] = existing.get("last_refresh_at")
            current["next_refresh_at"] = existing.get("next_refresh_at")
            current["last_status"] = existing.get("last_status", current["last_status"])
            records[index] = {**existing, **current, "updated_at": _now_iso()}
            updated = True
            break
    if not updated:
        records.append(current)
    _write_source_records(records)
    return current


def _touch_source_record(name: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    records = _list_source_records()
    for index, existing in enumerate(records):
        if existing.get("name") != name:
            continue
        updated = {**existing, **updates, "updated_at": _now_iso()}
        records[index] = updated
        _write_source_records(records)
        return updated
    return None


def _upload_target_path(file_name: str) -> Path:
    safe_name = _slugify(Path(file_name).stem) or "upload"
    suffix = Path(file_name).suffix.lower() or ".txt"
    unique = sha1(f"{file_name}:{_now_iso()}".encode("utf-8")).hexdigest()[:10]
    target = _uploads_root() / f"{safe_name}-{unique}{suffix}"
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _store_upload(file_name: str, raw_bytes: bytes, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = metadata or {}
    target = _upload_target_path(file_name)
    target.write_bytes(raw_bytes)
    text = raw_bytes.decode("utf-8", errors="ignore")
    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return {
            "status": "error",
            "message": "Arquivo recebido, mas sem texto legível para treinamento.",
            "path": str(target),
        }

    page = {
        "url": f"upload://{target.name}",
        "title": Path(file_name).stem or "Upload",
        "text": cleaned,
        "links": [],
    }
    chunk_count = _index_page(page, {"source": "user_upload", "type": "upload", **metadata})
    state = _load_knowledge_state()
    uploads = state.get("uploads", []) if isinstance(state.get("uploads", []), list) else []
    uploads.append(
        {
            "file_name": file_name,
            "stored_path": str(target),
            "metadata": metadata,
            "created_at": _now_iso(),
            "chunks_indexed": chunk_count,
        }
    )
    state["uploads"] = uploads[-100:]
    _save_knowledge_state(state)
    return {
        "status": "indexed",
        "source": "user_upload",
        "stored_path": str(target),
        "chunks_indexed": chunk_count,
        "message": "Upload incorporado ao conhecimento local do SOFIA.",
    }


def list_knowledge_sources() -> dict[str, Any]:
    sources = _list_source_records()
    return {
        "status": "ready",
        "count": len(sources),
        "sources": sources,
    }


def register_knowledge_source(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or "").strip()
    if not url:
        return {"status": "error", "message": "URL obrigatoria para registrar provider."}
    if not url.startswith(("http://", "https://")):
        return {"status": "error", "message": "Somente fontes HTTP/HTTPS sao suportadas."}
    record = _upsert_source_record(payload)
    return {
        "status": "registered",
        "source": record,
    }


def _refresh_source_record(name: str, force: bool = False) -> dict[str, Any]:
    records = _list_source_records()
    record = next((item for item in records if item.get("name") == name), None)
    if record is None:
        return {"status": "error", "message": f"Fonte nao encontrada: {name}"}
    if not force and record.get("enabled") is False:
        return {"status": "skipped", "source": name, "message": "Fonte desabilitada."}

    result = _crawl_documentation_site(
        record["url"],
        source_name=name,
        metadata=record.get("metadata") or {},
        max_pages=max(1, int(record.get("pages_per_refresh") or DEFAULT_CRAWL_MAX_PAGES)),
        max_depth=max(0, int(record.get("crawl_depth") or DEFAULT_CRAWL_MAX_DEPTH)),
        allowed_domains=record.get("allowed_domains") or [],
        allowed_paths=record.get("allowed_paths") or [],
    )
    updated = _touch_source_record(
        name,
        {
            "last_refresh_at": _now_iso(),
            "next_refresh_at": datetime.fromtimestamp(
                datetime.now(timezone.utc).timestamp() + int(record.get("refresh_seconds") or 86400)
            , tz=timezone.utc).isoformat(),
            "last_status": result.get("status", "unknown"),
            "pages_indexed": int(record.get("pages_indexed", 0)) + int(result.get("pages_indexed", 0)),
            "chunks_indexed": int(record.get("chunks_indexed", 0)) + int(result.get("chunks_indexed", 0)),
        },
    )
    return {**result, "source_record": updated or record}


def refresh_due_knowledge_sources(force: bool = False) -> dict[str, Any]:
    refreshed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for record in _list_source_records():
        if record.get("enabled") is False:
            skipped.append({"source": record.get("name"), "reason": "disabled"})
            continue
        next_refresh_at = record.get("next_refresh_at")
        if not force and next_refresh_at:
            try:
                scheduled = datetime.fromisoformat(str(next_refresh_at))
                if scheduled > now:
                    skipped.append({"source": record.get("name"), "reason": "not_due"})
                    continue
            except Exception:
                pass
        refreshed.append(_refresh_source_record(str(record.get("name")), force=force))
    return {"status": "ok", "refreshed": refreshed, "skipped": skipped}


def _extract_document(html_text: str) -> dict[str, Any]:
    parser = _DocumentationParser()
    parser.feed(html_text)
    title = _normalize_whitespace(" ".join(parser.title_parts))
    body = _normalize_whitespace(" ".join(parser.text_parts))
    return {
        "title": title,
        "text": body,
        "links": parser.links,
    }


def _allowed_path_prefix(seed_url: str) -> str:
    path = urlparse(seed_url).path or "/"
    if path.endswith("/"):
        return path.rstrip("/") or "/"
    tail = path.rsplit("/", 1)[-1]
    if "." in tail:
        return path.rsplit("/", 1)[0] or "/"
    return path.rstrip("/") or "/"


def _chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> list[str]:
    cleaned = _normalize_whitespace(text)
    if not cleaned:
        return []
    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    step = max(chunk_size - overlap, 1)
    start = 0
    while start < len(cleaned):
        chunk = cleaned[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def _page_path(source_name: str, page_url: str, title: str) -> Path:
    parsed = urlparse(page_url)
    path_slug = _slugify(parsed.path.strip("/") or "index")
    title_slug = _slugify(title or path_slug)
    unique = sha1(page_url.encode("utf-8")).hexdigest()[:8]
    return _external_docs_root() / _slugify(source_name) / f"{title_slug}-{path_slug}-{unique}.md"


def _page_markdown(page: dict[str, Any]) -> str:
    title = page.get("title") or "Documentation"
    url = page.get("url") or ""
    body = page.get("text") or ""
    return f"# {title}\n\nSource: {url}\n\n{body}\n"


def _save_page(source_name: str, page: dict[str, Any]) -> Path:
    path = _page_path(source_name, page["url"], page.get("title") or "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_page_markdown(page), encoding="utf-8")
    return path


def _index_page(page: dict[str, Any], metadata: dict[str, Any]) -> int:
    chunks = _chunk_text(page.get("text", ""))
    for index, chunk in enumerate(chunks):
        chunk_metadata = {
            **metadata,
            "chunk_index": index,
            "chunk_count": len(chunks),
            "title": page.get("title", ""),
            "url": page.get("url", ""),
        }
        vector_store.add(chunk, chunk_metadata)
        qdrant_store.add_text(chunk, chunk_metadata)
    return len(chunks)


def _fetch_html(url: str) -> str:
    response = requests.get(
        url,
        timeout=settings.REQUEST_TIMEOUT,
        headers={"User-Agent": DEFAULT_USER_AGENT},
    )
    response.raise_for_status()
    content_type = (response.headers.get("content-type") or "").lower()
    if "html" not in content_type and "text" not in content_type:
        raise ValueError(f"unsupported content type: {content_type or 'unknown'}")
    return response.text


def _internal_links(
    base_url: str,
    links: list[str],
    allowed_hosts: set[str],
    allowed_prefixes: list[str],
) -> list[str]:
    discovered: list[str] = []
    for link in links:
        absolute = _normalize_url(urljoin(base_url, link))
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.netloc.lower() not in allowed_hosts:
            continue
        if not any(parsed.path == prefix or parsed.path.startswith(f"{prefix}/") for prefix in allowed_prefixes):
            continue
        discovered.append(absolute)
    return _unique_sequence(discovered)


def _crawl_documentation_site(
    url: str,
    *,
    source_name: str,
    metadata: dict[str, Any] | None = None,
    max_pages: int = DEFAULT_CRAWL_MAX_PAGES,
    max_depth: int = DEFAULT_CRAWL_MAX_DEPTH,
    allowed_domains: list[str] | None = None,
    allowed_paths: list[str] | None = None,
) -> dict[str, Any]:
    metadata = metadata or {}
    queue = deque([(url, 0)])
    visited: set[str] = set()
    pages: list[dict[str, Any]] = []
    saved_files: list[str] = []
    indexed_chunks = 0
    skipped: list[dict[str, str]] = []
    allowed_prefixes = _unique_sequence((allowed_paths or [_seed_path_prefix(url)]))
    allowed_hosts = {domain.lower() for domain in (allowed_domains or [urlparse(url).netloc]) if domain}

    while queue and len(pages) < max_pages:
        current_url, depth = queue.popleft()
        normalized_url = _normalize_url(current_url)
        if normalized_url in visited:
            continue
        visited.add(normalized_url)

        try:
            html_text = _fetch_html(normalized_url)
            document = _extract_document(html_text)
            text = document.get("text", "")
            if not text:
                skipped.append({"url": normalized_url, "reason": "empty_document"})
                continue

            page = {
                "url": normalized_url,
                "title": document.get("title") or urlparse(normalized_url).path.rstrip("/").split("/")[-1] or "Documentation",
                "text": text,
                "links": document.get("links", []),
            }
            saved_path = _save_page(source_name, page)
            saved_files.append(str(saved_path))
            indexed_chunks += _index_page(page, {"source": source_name, "type": "documentation_site", **metadata})
            pages.append({"url": normalized_url, "title": page["title"], "path": str(saved_path)})

            if depth < max_depth:
                for link in _internal_links(normalized_url, page.get("links", []), allowed_hosts, allowed_prefixes):
                    if link not in visited:
                        queue.append((link, depth + 1))
        except Exception as exc:
            skipped.append({"url": normalized_url, "reason": str(exc)})

    return {
        "status": "indexed",
        "source": source_name,
        "pages_indexed": len(pages),
        "chunks_indexed": indexed_chunks,
        "saved_files": saved_files,
        "pages": pages,
        "skipped": skipped,
        "metadata": metadata,
    }


def get_knowledge_index():
    return {
        "module": "Knowledge",
        "indexed_sources": [
            "Markdown",
            "PDF",
            "DOCX",
            "Wiki",
            "Runbooks",
            "GLPI",
            "RFC",
            "Scripts",
            "Histórico",
            "Incidentes",
            "External documentation sites",
        ],
        "search_backend": "Local docs + Vector Store + Qdrant",
        "status": "indexing-ready",
        "storage_root": str(DOCS_ROOT),
        "providers": list_knowledge_sources(),
    }


def ingest_source(payload: dict):
    source_type = str(payload.get("source_type") or "").strip().lower()
    url = payload.get("url") or payload.get("source")
    metadata = payload.get("metadata") or {}

    if source_type in {"url", "site", "documentation", "documentation_site", "docs_site"} or str(url).startswith(("http://", "https://")):
        if not url:
            return {
                "status": "error",
                "message": "URL obrigatória para ingestão de documentação externa.",
            }
        source_record = _upsert_source_record({
            "name": payload.get("name") or payload.get("source") or _default_source_name(str(url)),
            "label": payload.get("label") or payload.get("source") or _default_source_name(str(url)),
            "url": str(url),
            "enabled": payload.get("enabled", True),
            "refresh_seconds": payload.get("refresh_seconds") or payload.get("refresh") or 86400,
            "allowed_domains": payload.get("allowed_domains") or payload.get("scope_domains"),
            "allowed_paths": payload.get("allowed_paths") or payload.get("scope_paths"),
            "metadata": metadata,
            "pages_per_refresh": payload.get("max_pages") or DEFAULT_CRAWL_MAX_PAGES,
            "crawl_depth": payload.get("max_depth") or DEFAULT_CRAWL_MAX_DEPTH,
        })
        result = _crawl_documentation_site(
            str(url),
            source_name=source_record["name"],
            metadata=metadata,
            max_pages=max(1, int(payload.get("max_pages") or source_record.get("pages_per_refresh") or DEFAULT_CRAWL_MAX_PAGES)),
            max_depth=max(0, int(payload.get("max_depth") or source_record.get("crawl_depth") or DEFAULT_CRAWL_MAX_DEPTH)),
            allowed_domains=source_record.get("allowed_domains") or [],
            allowed_paths=source_record.get("allowed_paths") or [],
        )
        _touch_source_record(
            source_record["name"],
            {
                "last_refresh_at": _now_iso(),
                "next_refresh_at": datetime.fromtimestamp(
                    datetime.now(timezone.utc).timestamp() + int(source_record.get("refresh_seconds") or 86400)
                , tz=timezone.utc).isoformat(),
                "last_status": result.get("status", "unknown"),
                "pages_indexed": int(source_record.get("pages_indexed", 0)) + int(result.get("pages_indexed", 0)),
                "chunks_indexed": int(source_record.get("chunks_indexed", 0)) + int(result.get("chunks_indexed", 0)),
            },
        )
        return result

    if source_type == "upload":
        raw_text = payload.get("text")
        raw_bytes = payload.get("content_bytes")
        if raw_bytes is not None and isinstance(raw_bytes, str):
            raw_bytes = raw_bytes.encode("utf-8", errors="ignore")
        if raw_bytes is None:
            if raw_text is None:
                return {"status": "error", "message": "Conteudo do upload ausente."}
            raw_bytes = str(raw_text).encode("utf-8")
        return _store_upload(
            str(payload.get("source") or payload.get("file_name") or "upload.txt"),
            raw_bytes if isinstance(raw_bytes, bytes) else bytes(raw_bytes),
            metadata,
        )

    return {
        "status": "queued",
        "source": payload.get("source"),
        "source_type": payload.get("source_type"),
        "path": payload.get("path"),
        "metadata": payload.get("metadata") or {},
        "message": "Documento recebido para indexação pelo módulo Knowledge.",
    }


def _iter_docs():
    if not DOCS_ROOT.exists():
        return []
    return [path for path in DOCS_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"}]


def search_knowledge(query: str):
    search_terms = query.lower().split()
    results = []
    for doc_path in _iter_docs():
        try:
            text = doc_path.read_text(encoding="utf-8")
        except Exception:
            continue

        lowered = text.lower()
        score = sum(1 for term in search_terms if term in lowered)
        if score > 0:
            snippet = _shorten_text(text.replace("\n", " "))
            results.append({
                "source": str(doc_path.relative_to(DOCS_ROOT)),
                "score": round(score / max(len(search_terms), 1), 2),
                "snippet": snippet,
            })

    try:
        qdrant_hits = qdrant_store.search(query, limit=5)
    except Exception:
        qdrant_hits = []

    for hit in qdrant_hits:
        payload = hit.get("payload", {}) if isinstance(hit, dict) else {}
        results.append({
            "source": payload.get("source") or payload.get("url") or "qdrant",
            "score": round(float(hit.get("score", 0.0)), 2) if isinstance(hit, dict) else 0.0,
            "snippet": _shorten_text(hit.get("text", "") if isinstance(hit, dict) else ""),
            "metadata": payload,
        })

    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in sorted(results, key=lambda row: row.get("score", 0.0), reverse=True):
        identity = (str(item.get("source", "")), str(item.get("snippet", "")))
        if identity in seen:
            continue
        seen.add(identity)
        deduped.append(item)

    return {"query": query, "results": deduped[:5], "sources": ["docs", "qdrant"]}
