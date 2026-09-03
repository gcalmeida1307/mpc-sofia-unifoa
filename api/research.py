from __future__ import annotations

import hashlib
import json
import logging
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from .ingestion import IMAGE_EXTENSIONS
from .links import MAX_RESPONSE_BYTES, _validate_url, ingest_link
from .privacy import ExternalRedaction, external_clinical_allowed, external_data_allowed
from .query_analysis import assess_module_scope

logger = logging.getLogger("sofia.research")

MAX_SEARCH_RESULTS = 5
MAX_IMAGE_RESULTS = 2
MAX_LINKS_TO_INGEST = 3
MAX_STORED_ITEMS = 6
RESEARCH_TIMEOUT_SECONDS = 12
_SEARCH_URL = "https://html.duckduckgo.com/html/"
_WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"


class _DuckDuckGoParser(HTMLParser):
    """Read only result anchors; never treat search-result HTML as knowledge."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.results: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() != "a":
            return
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if "result__a" in classes and values.get("href"):
            self._current = {"url": str(values["href"]), "title": ""}

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["title"] += " ".join(data.split())

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self._current is not None:
            item = {key: value.strip() for key, value in self._current.items()}
            if item["url"] and item["title"]:
                self.results.append(item)
            self._current = None


def _unwrap_search_url(value: str) -> str:
    """Convert a DuckDuckGo redirect into its public destination URL."""
    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    target = query.get("uddg", [""])[0]
    if target:
        return unquote(target)
    return value


def _search_links(query: str, limit: int = MAX_SEARCH_RESULTS) -> list[dict[str, str]]:
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=RESEARCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "SofiaLocalResearch/1.0 (local-rag@example.invalid)"},
        ) as client:
            response = client.get(_SEARCH_URL, params={"q": query, "kl": "br-pt"})
            response.raise_for_status()
        parser = _DuckDuckGoParser()
        parser.feed(response.text)
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Public link research unavailable: %s", exc)
        return []

    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in parser.results:
        try:
            url = _validate_url(_unwrap_search_url(item["url"]))
        except ValueError:
            continue
        if url in seen:
            continue
        seen.add(url)
        results.append({"url": url, "title": item["title"][:240]})
        if len(results) >= limit:
            break
    return results


def _search_images(query: str, limit: int = MAX_IMAGE_RESULTS) -> list[dict[str, str]]:
    """Find public Wikimedia Commons images; the binary is kept local."""
    params = {
        "action": "query",
        "format": "json",
        "origin": "*",
        "generator": "search",
        "gsrnamespace": "6",
        "gsrsearch": query,
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|mime|size",
        "iiurlwidth": "1400",
    }
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=RESEARCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "SofiaLocalResearch/1.0 (local-rag@example.invalid)"},
        ) as client:
            response = client.get(_WIKIMEDIA_API, params=params)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError, json.JSONDecodeError) as exc:
        # Some networks deny the Commons API while allowing its public media
        # search page. Fall back to that page without sending the query to a
        # second commercial image broker.
        logger.warning("Public image API unavailable; using Commons HTML search: %s", exc)
        return _search_images_html(query, limit)

    results: list[dict[str, str]] = []
    pages = payload.get("query", {}).get("pages", {}) if isinstance(payload, dict) else {}
    for page in pages.values() if isinstance(pages, dict) else []:
        info = (page.get("imageinfo") or [{}])[0]
        if not isinstance(info, dict):
            continue
        image_url = str(info.get("thumburl") or info.get("url") or "").strip()
        mime = str(info.get("mime") or "").casefold()
        if not image_url or not mime.startswith("image/"):
            continue
        try:
            image_url = _validate_url(image_url)
        except ValueError:
            continue
        results.append(
            {
                "url": image_url,
                "title": str(page.get("title") or "Imagem Wikimedia Commons")[:240],
                "mime": mime,
                "source": "Wikimedia Commons",
            }
        )
        if len(results) >= limit:
            break
    return results


def _search_images_html(query: str, limit: int) -> list[dict[str, str]]:
    """Fallback for environments where the Wikimedia API answers 403."""
    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=RESEARCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "SofiaLocalResearch/1.0 (local-rag@example.invalid)"},
        ) as client:
            response = client.get(
                "https://commons.wikimedia.org/w/index.php",
                params={"search": query, "title": "Special:MediaSearch", "type": "image"},
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Public image HTML research unavailable: %s", exc)
        return []

    # MediaSearch embeds thumbnail metadata in a JSON blob. We only accept
    # Wikimedia thumbnails and discard every other URL in the HTML page.
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_url in re.findall(r'"src":"(https://thumb\.wikimedia\.org/[^"\\]+)"', response.text):
        image_url = raw_url.replace("\\/", "/").replace("\\u0026", "&")
        try:
            image_url = _validate_url(image_url)
        except ValueError:
            continue
        if image_url in seen:
            continue
        seen.add(image_url)
        results.append(
            {
                "url": image_url,
                "title": "Imagem pública do Wikimedia Commons",
                "mime": "image/png" if image_url.casefold().split("?", 1)[0].endswith(".png") else "image/jpeg",
                "source": "Wikimedia Commons",
            }
        )
        if len(results) >= limit:
            break
    return results


def _media_extension(url: str, mime: str) -> str | None:
    suffix = Path(urlparse(url).path).suffix.casefold()
    if suffix in IMAGE_EXTENSIONS:
        return suffix
    return {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/tiff": ".tiff"}.get(mime)


def _download_image(root: Path, module_id: str, item: dict[str, str]) -> dict[str, str] | None:
    url = _validate_url(item["url"])
    extension = _media_extension(url, item.get("mime", ""))
    if extension is None:
        return None
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    file_name = f"sofia-pesquisa-{digest}{extension}"
    destination = root / module_id / "research" / file_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with httpx.Client(
            follow_redirects=True,
            timeout=RESEARCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "SofiaLocalResearch/1.0 (local-rag@example.invalid)"},
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise ValueError("A imagem excede o limite de 8 MB")
            content_type = response.headers.get("content-type", "").split(";", 1)[0].casefold()
            if not content_type.startswith("image/"):
                raise ValueError("A fonte não retornou uma imagem")
            destination.write_bytes(response.content)

    manifest_name = f"{file_name}.md"
    manifest = destination.with_name(manifest_name)
    if not manifest.exists():
        manifest.write_text(
            "\n".join(
                (
                    f"# {item.get('title', 'Imagem de pesquisa pública')}",
                    "",
                    "Tipo: imagem pública para consulta offline; conteúdo não é autoridade normativa.",
                    f"Fonte: {url}",
                    f"Arquivo local: {file_name}",
                    "OCR: a imagem será lida pelo indexador local quando o Tesseract estiver disponível.",
                    "",
                )
            ),
            encoding="utf-8",
        )
    return {"file_name": f"research/{file_name}", "manifest": f"research/{manifest_name}", "url": url, "type": "image"}


def _safe_error(exc: Exception) -> str:
    message = re.sub(r"https?://\S+", "[fonte externa]", str(exc)).strip()
    return message[:180] or "fonte não pôde ser armazenada"


def research_module(root: Path, module_id: str, question: str) -> dict[str, Any]:
    """Run one bounded, admin-triggered public research pass for a module.

    The question is redacted before leaving the process. Only public pages and
    Wikimedia image metadata are considered. Downloaded pages/images are
    stored under the active module, so the normal local index sees them on the
    next retrieval. No provider-generated URL is trusted automatically.
    """
    base = {
        "status": "blocked",
        "module_id": module_id,
        "searched": 0,
        "stored": 0,
        "items": [],
        "errors": [],
        "query_was_masked": False,
    }
    if not external_data_allowed():
        return {**base, "reason": "external_data_disabled", "note": "Pesquisa pública está desativada pela política LGPD local."}

    scope = assess_module_scope(module_id, question)
    if scope["status"] == "outside":
        return {
            **base,
            "reason": "module_scope_outside",
            "scope": scope,
            "note": f"A pergunta parece pertencer ao módulo {scope['module_name']} e não foi pesquisada neste módulo.",
        }
    if module_id == "medicina" and not external_clinical_allowed():
        return {**base, "reason": "clinical_external_disabled", "scope": scope, "note": "Pesquisa clínica externa exige autorização explícita; nenhum dado saiu da máquina."}

    redaction = ExternalRedaction()
    safe_query = redaction.clean(question).strip()
    base["query_was_masked"] = redaction.used
    if not safe_query:
        return {**base, "reason": "empty_safe_query", "scope": scope, "note": "A pesquisa foi interrompida porque a pergunta não gerou uma consulta segura."}

    # The module name improves recall without storing or sending the original
    # question anywhere. The active module remains the authority boundary.
    module_name = str(scope.get("module_name") or module_id)
    search_query = f"{safe_query} {module_name} documentação orientação"
    links = _search_links(search_query)
    images = _search_images(f"{safe_query} {module_name}")
    base["searched"] = len(links) + len(images)
    stored_items: list[dict[str, str]] = []

    for link in links[:MAX_LINKS_TO_INGEST]:
        if len(stored_items) >= MAX_STORED_ITEMS:
            break
        try:
            result = ingest_link(
                root,
                module_id,
                link["url"],
                max_pages=1,
                timeout_seconds=RESEARCH_TIMEOUT_SECONDS,
                content_transform=ExternalRedaction().clean,
            )
            stored_items.append(
                {
                    "type": "text",
                    "title": link["title"],
                    "file_name": str(result["file_name"]),
                    "url": str(result["final_url"]),
                    "storage": str(result.get("storage", "local-json")),
                }
            )
        except (httpx.HTTPError, OSError, RuntimeError, ValueError) as exc:  # one unavailable source must not cancel the pass
            base["errors"].append(_safe_error(exc))

    for image in images:
        if len(stored_items) >= MAX_STORED_ITEMS:
            break
        try:
            result = _download_image(root, module_id, image)
            if result:
                stored_items.append({"type": "image", "title": image["title"], **result})
        except (httpx.HTTPError, OSError, ValueError) as exc:  # public image hosts can reject individual files
            base["errors"].append(_safe_error(exc))

    if not stored_items:
        return {
            **base,
            "status": "no_results",
            "scope": scope,
            "note": "A pesquisa pública não encontrou uma fonte que pudesse ser incorporada com segurança.",
        }
    return {
        **base,
        "status": "completed",
        "scope": scope,
        "stored": len(stored_items),
        "items": stored_items,
        "note": "As páginas e imagens foram armazenadas no módulo ativo e serão indexadas pelo RAG local na próxima consulta.",
    }
