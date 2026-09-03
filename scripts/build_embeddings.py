"""Build local Ollama embedding indexes sequentially."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from api.embeddings import build_all_embeddings, build_module_embeddings


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera embeddings locais por módulo")
    parser.add_argument("--module", help="Módulo específico; sem este parâmetro usa todos")
    parser.add_argument("--max-chunks", type=int, help="Limite de chunks por módulo nesta execução")
    parser.add_argument("--force", action="store_true", help="Ignora o cache atual")
    args = parser.parse_args()
    if args.max_chunks is not None:
        os.environ["SOFIA_EMBEDDING_MAX_CHUNKS"] = str(args.max_chunks)
    root = Path(__file__).resolve().parents[1] / "knowledge"
    if args.module:
        result = build_module_embeddings(root, args.module, force=args.force)
    else:
        modules = sorted(path.name for path in root.iterdir() if path.is_dir())
        result = build_all_embeddings(root, modules, force=args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
