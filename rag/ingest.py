#!/usr/bin/env python3
"""Pipeline de ingesta del corpus de supervivencia (Capa 3).

STUB: define la estructura del pipeline pero todavía no ejecuta embeddings
reales. Cada paso marcado con TODO debe implementarse antes de usarse.

Uso previsto:
    python3 ingest.py --corpus corpus/ --out survival.db
"""

import argparse
import sys
from pathlib import Path

SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf"}


def discover(corpus_dir: Path) -> list[Path]:
    """Lista los documentos del corpus soportados."""
    if not corpus_dir.is_dir():
        sys.exit(f"error: el directorio de corpus no existe: {corpus_dir}")
    return sorted(
        p for p in corpus_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )


def extract_text(doc: Path) -> str:
    """Extrae texto plano de un documento."""
    if doc.suffix.lower() in {".txt", ".md"}:
        return doc.read_text(encoding="utf-8", errors="ignore")
    # TODO: extraer texto de PDF con pypdf.
    raise NotImplementedError(f"extracción de {doc.suffix} no implementada")


def chunk(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Parte el texto en fragmentos con solapamiento."""
    # TODO: chunking sensible a párrafos en vez de corte fijo por caracteres.
    step = max(1, size - overlap)
    return [text[i:i + size] for i in range(0, len(text), step) if text[i:i + size].strip()]


def embed(chunks: list[str]) -> list[list[float]]:
    """Genera embeddings de los fragmentos con all-MiniLM-L6-v2."""
    # TODO: cargar SentenceTransformer("all-MiniLM-L6-v2") y codificar.
    raise NotImplementedError("embeddings aún no implementados")


def write_index(db_path: Path, rows: list[tuple]) -> None:
    """Escribe los vectores en SQLite + sqlite-vec."""
    # TODO: crear la tabla virtual vec0 y volcar los embeddings.
    raise NotImplementedError("escritura a sqlite-vec aún no implementada")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingesta del corpus RAG.")
    parser.add_argument("--corpus", type=Path, default=Path("corpus"))
    parser.add_argument("--out", type=Path, default=Path("survival.db"))
    args = parser.parse_args()

    docs = discover(args.corpus)
    print(f"[ingest] documentos encontrados: {len(docs)}")
    for doc in docs:
        print(f"  - {doc}")

    if not docs:
        print("[ingest] corpus vacío — nada que indexar.")
        return

    print("[ingest] STUB: extracción/embeddings/índice aún no implementados.")
    print("[ingest] ver los TODO en ingest.py.")


if __name__ == "__main__":
    main()
