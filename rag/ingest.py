#!/usr/bin/env python3
"""Indexa el corpus de supervivencia en una base SQLite-vec.

Uso:
    python3 ingest.py --corpus corpus/ --out survival.db
    python3 ingest.py --embedder hash      # sin descargar el modelo ONNX
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from smrag.embeddings import get_embedder
from smrag.pipeline import ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta del corpus RAG.")
    parser.add_argument("--corpus", type=Path, default=Path("corpus"))
    parser.add_argument("--out", type=Path, default=Path("survival.db"))
    parser.add_argument(
        "--embedder",
        choices=["auto", "onnx", "hash"],
        default="auto",
        help="backend de embeddings (default: auto)",
    )
    parser.add_argument(
        "--model",
        choices=["multilingual", "english"],
        default="multilingual",
        help="modelo de embeddings (default: multilingual)",
    )
    args = parser.parse_args()

    print(f"[ingest] corpus: {args.corpus}  ->  índice: {args.out}")
    embedder = get_embedder(args.embedder, args.model)
    print(f"[ingest] embedder: {embedder.backend} (dim {embedder.dim})")

    started = time.monotonic()
    try:
        stats = ingest(args.corpus, args.out, embedder)
    except FileNotFoundError as exc:
        sys.exit(f"error: {exc}")

    elapsed = time.monotonic() - started
    print(
        f"[ingest] listo: {stats['docs']} documentos, "
        f"{stats['chunks']} chunks en {elapsed:.1f}s"
    )
    if stats["chunks"] == 0:
        print("[ingest] aviso: el índice quedó vacío (corpus sin documentos).")


if __name__ == "__main__":
    main()
