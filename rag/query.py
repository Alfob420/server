#!/usr/bin/env python3
"""Consulta interactiva del índice RAG (útil para depurar la recuperación).

Uso:
    python3 query.py "como purifico agua"
    python3 query.py --db survival.db --k 3 "construir refugio"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from smrag import store
from smrag.embeddings import get_embedder


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta del índice RAG.")
    parser.add_argument("query", nargs="+", help="texto de la consulta")
    parser.add_argument("--db", type=Path, default=Path("survival.db"))
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--embedder", choices=["auto", "onnx", "hash"], default="auto")
    parser.add_argument(
        "--model", choices=["multilingual", "english"], default="multilingual"
    )
    parser.add_argument("--json", action="store_true", help="salida en JSON")
    args = parser.parse_args()

    if not args.db.exists():
        sys.exit(f"error: el índice no existe: {args.db} (corré ingest.py primero)")

    query = " ".join(args.query)
    embedder = get_embedder(args.embedder, args.model)
    db = store.connect(args.db)
    try:
        indexed = store.get_meta(db, "embedder")
        if indexed and indexed != embedder.backend:
            print(
                f"aviso: el índice se creó con '{indexed}' pero la consulta usa "
                f"'{embedder.backend}'; los resultados pueden ser malos.",
                file=sys.stderr,
            )
        emb = embedder.encode([query])[0]
        hits = store.search(db, emb, k=args.k)
    finally:
        db.close()

    if args.json:
        print(json.dumps({"query": query, "hits": hits}, ensure_ascii=False))
        return

    print(f'consulta: "{query}"  ({len(hits)} resultados)\n')
    for i, hit in enumerate(hits, 1):
        snippet = hit["text"].replace("\n", " ")
        if len(snippet) > 220:
            snippet = snippet[:220] + "..."
        print(f"[{i}] {hit['doc']}  (distancia {hit['distance']:.4f})")
        print(f"    {snippet}\n")


if __name__ == "__main__":
    main()
