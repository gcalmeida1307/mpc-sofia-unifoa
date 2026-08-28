from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import math
import os
import random
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
from dotenv import load_dotenv
from anthropic import Anthropic
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from mcp.server import MCPServer
from ollama import Client as OllamaClient
from pydantic import BaseModel, Field
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .orchestration import answer as orchestrate_answer
from .policies import policy_for
from .retrieval import retrieve

logger = logging.getLogger("sofia.mcp")
ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = ROOT / "knowledge"
ENV_FILE = ROOT / ".env"
# Em desenvolvimento, aceita o arquivo atualmente usado pelo projeto como
# fallback. O arquivo recomendado para segredos continua sendo apenas `.env`.
load_dotenv(ENV_FILE if ENV_FILE.exists() else ROOT / ".env.example", override=False)

MODULES = {
    "almoxarifado": {"name": "Almoxarifado", "category": "Operações"},
    "gestao-empresarial": {"name": "Gestão Empresarial", "category": "Gestão"},
    "infraestrutura": {"name": "Infraestrutura", "category": "Tecnologia"},
    "medicina": {"name": "Medicina", "category": "Saúde"},
}
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".pdf", ".docx"}


def module_path(module_id: str) -> Path:
    if module_id not in MODULES:
        raise HTTPException(404, f"Módulo desconhecido: {module_id}")
    return KNOWLEDGE_ROOT / module_id


def files_for(module_id: str) -> list[Path]:
    return [p for p in module_path(module_id).rglob("*") if p.is_file() and p.name != ".gitkeep" and p.suffix.lower() in ALLOWED_EXTENSIONS]


def extract_text(path: Path) -> str:
    try:
        if path.suffix.lower() == ".pdf":
            return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        if path.suffix.lower() == ".docx":
            return "\n".join(paragraph.text for paragraph in Document(str(path)).paragraphs)
        if path.suffix.lower() == ".csv":
            rows = csv.reader(io.StringIO(path.read_text(encoding="utf-8", errors="ignore")))
            return "\n".join(" | ".join(row) for row in rows)
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return ""


def knowledge_context(module_id: str, query: str = "", limit: int = 5) -> tuple[str, list[str]]:
    chunks: list[tuple[Path, str]] = []
    for path in files_for(module_id):
        text = extract_text(path)
        if text.strip():
            # Blocos menores permitem recuperar o trecho relevante de arquivos grandes.
            lines = text.splitlines()
            for start in range(0, len(lines), 20):
                chunk = "\n".join(lines[start:start + 20]).strip()
                if chunk:
                    chunks.append((path, chunk[:12000]))
    if not chunks:
        return "", []

    if not query.strip():
        selected = chunks[:limit]
    else:
        def normalize(value: str) -> str:
            return "".join(char for char in unicodedata.normalize("NFKD", value.lower()) if not unicodedata.combining(char))

        # ExpansÃ£o leve de termos ajuda consultas naturais em portuguÃªs
        # (por exemplo, "gripe" tambÃ©m recupera registros de influenza).
        synonyms = {
            "gripe": "influenza gripe H1N1 H3N2",
            "resfriado": "resfriado rinofaringite coriza",
            "pressao": "pressÃ£o hipertensÃ£o hipotensÃ£o",
            "dor de cabeca": "cefaleia enxaqueca",
        }
        expanded_query = query + " " + " ".join(value for key, value in synonyms.items() if key in normalize(query))
        normalized_query = normalize(expanded_query)
        normalized_chunks = [normalize(chunk) for _, chunk in chunks]
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
        matrix = vectorizer.fit_transform(normalized_chunks + [normalized_query])
        semantic_scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
        terms = {term for term in re.findall(r"[\w]+", normalized_query) if len(term) > 2}
        ranked = sorted(
            range(len(chunks)),
            key=lambda index: semantic_scores[index] + 1.0 * sum(term in normalized_chunks[index] for term in terms),
            reverse=True,
        )
        selected = [chunks[index] for index in ranked[:limit]]

    context = "\n\n--- DOCUMENTO: ".join(f"{path.name}\n{text}" for path, text in selected)
    sources = list(dict.fromkeys(path.name for path, _ in selected))
    return context[:50000], sources


def module_status(module_id: str) -> dict[str, Any]:
    paths = files_for(module_id)
    return {"id": module_id, **MODULES[module_id], "path": str(module_path(module_id)), "documents": len(paths), "files": [p.name for p in paths], "ready": bool(paths)}


def tensor_matmul(a: list[list[float]], b: list[list[float]]) -> dict[str, Any]:
    left, right = np.array(a, dtype=float), np.array(b, dtype=float)
    if left.ndim != 2 or right.ndim != 2 or left.shape[1] != right.shape[0]:
        raise ValueError("Matrizes incompatíveis para multiplicação")
    result = left @ right
    return {"shape": list(result.shape), "values": result.round(6).tolist()}


def random_sample(distribution: str = "normal", size: int = 10, seed: int | None = None) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    if not 1 <= size <= 10000:
        raise ValueError("size deve estar entre 1 e 10000")
    values = rng.uniform(0, 1, size) if distribution == "uniform" else rng.normal(0, 1, size)
    return {"distribution": distribution, "seed": seed, "size": size, "sample": values.round(6).tolist(), "mean": round(float(values.mean()), 6)}


def neural_forward(values: list[float]) -> dict[str, Any]:
    x = np.array(values, dtype=float)
    weights = np.array([[0.5, -0.2, 0.1], [0.3, 0.4, -0.5], [-0.1, 0.6, 0.2]])
    bias = np.array([0.1, -0.1, 0.05])
    hidden = np.tanh(x[:3] @ weights + bias)
    output = 1 / (1 + np.exp(-hidden.mean()))
    return {"input": x[:3].round(6).tolist(), "hidden": hidden.round(6).tolist(), "output": round(float(output), 6), "architecture": [3, 3, 1]}


def monte_carlo_pi(samples: int = 10000, seed: int | None = None) -> dict[str, Any]:
    if not 100 <= samples <= 2_000_000:
        raise ValueError("samples deve estar entre 100 e 2.000.000")
    rng = np.random.default_rng(seed)
    points = rng.uniform(-1, 1, (samples, 2))
    inside = np.sum(np.sum(points * points, axis=1) <= 1)
    estimate = 4 * inside / samples
    error = 1.96 * math.sqrt(max(estimate * (1 - estimate), 1e-12) / samples)
    return {"samples": samples, "seed": seed, "pi": round(float(estimate), 8), "confidence_95": [round(float(estimate - error), 8), round(float(estimate + error), 8)]}


mcp = MCPServer(name="sofia-local", version="1.0.0", description="Sofia local knowledge and AI tools")


@mcp.tool()
async def search_knowledge(module_id: str, query: str, limit: int = 5) -> dict[str, Any]:
    """Search the local knowledge folder for relevant documents."""
    result = retrieve(KNOWLEDGE_ROOT, module_id, query, policy_for(module_id), limit)
    return {"module": module_id, "sources": list(result.sources), "context": result.context, "documents_found": len(result.sources), "evidence_found": result.has_quality_evidence}


@mcp.tool()
async def list_knowledge_modules() -> list[dict[str, Any]]:
    """List local RAG modules and their real indexed files."""
    return [module_status(module_id) for module_id in MODULES]


@mcp.tool()
async def tensor_multiply(left: list[list[float]], right: list[list[float]]) -> dict[str, Any]:
    """Multiply two numeric tensors using NumPy."""
    return tensor_matmul(left, right)


@mcp.tool()
async def random_generate(distribution: str = "normal", size: int = 10, seed: int | None = None) -> dict[str, Any]:
    """Generate reproducible random samples."""
    return random_sample(distribution, size, seed)


@mcp.tool()
async def neural_infer(values: list[float]) -> dict[str, Any]:
    """Run a deterministic NumPy neural-network forward pass."""
    return neural_forward(values)


@mcp.tool()
async def monte_carlo_estimate(samples: int = 10000, seed: int | None = None) -> dict[str, Any]:
    """Estimate Pi with a Monte Carlo simulation and confidence interval."""
    return monte_carlo_pi(samples, seed)


@mcp.resource("knowledge://{module_id}", mime_type="text/plain")
async def knowledge_resource(module_id: str) -> str:
    """Expose the selected local knowledge as an MCP resource."""
    context, _ = knowledge_context(module_id)
    return context or "Este módulo ainda não possui documentos."


class ChatRequest(BaseModel):
    module_id: str
    provider: str = Field(default="gemini", pattern="^(gemini|claude|ollama)$")
    message: str = Field(min_length=1, max_length=20000)
    history: list[dict[str, str]] = Field(default_factory=list)


async def legacy_provider_chat(request: ChatRequest, system: str, context: str) -> tuple[str, str]:
    prompt = f"{request.message}\n\nCONTEXTO LOCAL DO RAG ({request.module_id}):\n{context or 'Nenhum documento disponível.'}"
    history = request.history[-10:] + [{"role": "user", "content": prompt}]
    if request.provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(503, "GEMINI_API_KEY não configurada")
        client = genai.Client(api_key=api_key)
        response = await asyncio.to_thread(client.models.generate_content, model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt, config={"system_instruction": system})
        return response.text or "O Gemini não retornou texto.", os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if request.provider == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(503, "ANTHROPIC_API_KEY não configurada")
        client = Anthropic(api_key=api_key)
        response = await asyncio.to_thread(client.messages.create, model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"), max_tokens=2048, system=system, messages=history)
        return "".join(block.text for block in response.content if hasattr(block, "text")), os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    client = OllamaClient(host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"))
    response = await asyncio.to_thread(client.chat, model=os.getenv("OLLAMA_MODEL", "llama3.2"), messages=[{"role": "system", "content": system}, *history])
    return response["message"]["content"], os.getenv("OLLAMA_MODEL", "llama3.2")


async def provider_chat(request: ChatRequest, system: str, context: str) -> tuple[str, str]:
    """Use o provider escolhido e tenta outro provider configurado como fallback."""
    prompt = f"{request.message}\n\nCONTEXTO LOCAL DO RAG ({request.module_id}):\n{context or 'Nenhum documento disponÃ­vel.'}"
    history = request.history[-10:] + [{"role": "user", "content": prompt}]
    configured = {"gemini": bool(os.getenv("GEMINI_API_KEY")), "claude": bool(os.getenv("ANTHROPIC_API_KEY")), "ollama": True}
    providers = [request.provider] + [name for name in ("gemini", "claude", "ollama") if name != request.provider and configured[name]]
    errors: list[str] = []
    for provider in providers:
        try:
            if provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise RuntimeError("GEMINI_API_KEY nÃ£o configurada")
                model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
                client = genai.Client(api_key=api_key)
                response = await asyncio.to_thread(client.models.generate_content, model=model, contents=prompt, config={"system_instruction": system})
                return response.text or "O Gemini nÃ£o retornou texto.", model
            if provider == "claude":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise RuntimeError("ANTHROPIC_API_KEY nÃ£o configurada")
                model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
                client = Anthropic(api_key=api_key)
                response = await asyncio.to_thread(client.messages.create, model=model, max_tokens=2048, system=system, messages=history)
                return "".join(block.text for block in response.content if hasattr(block, "text")), model
            model = os.getenv("OLLAMA_MODEL", "llama3.2")
            client = OllamaClient(host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"))
            response = await asyncio.to_thread(client.chat, model=model, messages=[{"role": "system", "content": system}, *history])
            return response["message"]["content"], model
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
    raise HTTPException(503, "Nenhum provider respondeu. " + " | ".join(errors))


def local_rag_answer(question: str, context: str, sources: list[str]) -> str:
    """Resposta útil mesmo sem um LLM instalado: extrai evidências do RAG local."""
    if not context:
        return "Não encontrei documentos disponíveis neste módulo para responder à pergunta."
    terms = [term for term in re.findall(r"[\wÀ-ÿ]+", question.lower()) if len(term) > 3]
    lines = [line.strip() for line in context.splitlines() if line.strip() and not line.startswith("--- DOCUMENTO")]
    relevant = [line for line in lines if any(term in line.lower() for term in terms)]
    evidence = list(dict.fromkeys(relevant))[:8] or lines[:5]
    source_text = ", ".join(sources)
    return "Encontrei estas informações nos documentos locais (" + source_text + "):\n\n" + "\n".join(f"• {line}" for line in evidence) + "\n\nEsta é uma extração do conteúdo, não substitui a interpretação de um profissional de saúde."


app = FastAPI(title="Sofia Local MCP", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5174", "http://localhost:5174"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "server": "sofia-local", "mcp": "/mcp", "knowledge": str(KNOWLEDGE_ROOT)}


@app.get("/api/modules")
async def modules_endpoint() -> list[dict[str, Any]]:
    return [module_status(module_id) for module_id in MODULES]


@app.post("/api/modules/{module_id}/upload")
async def upload(module_id: str, file: UploadFile = File(...)) -> dict[str, Any]:
    target_root = module_path(module_id) / "textos"
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Formato não suportado: {suffix or 'sem extensão'}")
    safe_name = Path(file.filename or "arquivo").name
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "Arquivo maior que 50 MB")
    target_root.mkdir(parents=True, exist_ok=True)
    destination = target_root / safe_name
    destination.write_bytes(content)
    return {"uploaded": True, "module": module_id, "file": safe_name, "bytes": len(content), "status": module_status(module_id)}


async def legacy_chat(request: ChatRequest) -> dict[str, Any]:
    context, sources = knowledge_context(request.module_id, request.message)
    system = "Você é Sofia. Responda em português, use somente o contexto local quando ele existir, cite os nomes dos arquivos utilizados e diga claramente quando não houver informação suficiente. Não invente dados."
    try:
        answer, model = await provider_chat(request, system, context)
    except HTTPException as exc:
        if exc.status_code != 503:
            raise
        answer, model = local_rag_answer(request.message, context, sources), "local-rag"
    return {"answer": answer, "provider": "local-rag" if model == "local-rag" else request.provider, "model": model, "sources": sources, "module": request.module_id}


@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict[str, Any]:
    result = await orchestrate_answer(root=KNOWLEDGE_ROOT, module_id=request.module_id, provider=request.provider, question=request.message, history=request.history)
    return {"answer": result.answer, "provider": result.provider, "model": result.model, "sources": result.sources, "evidence_found": result.evidence_found, "evidence_score": result.evidence_score, "verified": result.verified, "module": request.module_id}


@app.get("/api/modules/{module_id}/tools/{tool_name}")
async def module_tool(module_id: str, tool_name: str) -> dict[str, Any]:
    module_path(module_id)
    if tool_name == "status":
        return module_status(module_id)
    raise HTTPException(404, "Ferramenta desconhecida")


app.mount("/mcp", mcp.streamable_http_app())

if __name__ == "__main__":
    if os.getenv("SOFIA_TRANSPORT") == "stdio":
        mcp.run(transport="stdio")
    else:
        import uvicorn
        uvicorn.run("api.server:app", host="127.0.0.1", port=8787, reload=True)
