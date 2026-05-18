"""Orquestación de la ingesta del corpus."""
from __future__ import annotations

from pathlib import Path

from . import store
from .chunking import chunk_text
from .embeddings import Embedder
from .extract import SUPPORTED_SUFFIXES, extract_text


def discover(corpus_dir: Path) -> list[Path]:
    """Lista los documentos del corpus con formato soportado."""
    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"el directorio de corpus no existe: {corpus_dir}")
    return sorted(
        p
        for p in corpus_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )


def ingest(
    corpus_dir: Path,
    db_path: Path,
    embedder: Embedder,
    reset_db: bool = True,
    verbose: bool = True,
) -> dict:
    """Indexa el corpus en `db_path`. Devuelve estadísticas de la corrida."""
    docs = discover(corpus_dir)

    db = store.connect(db_path)
    try:
        store.reset(db) if reset_db else store.init(db)

        total_chunks = 0
        for doc in docs:
            text = extract_text(doc)
            chunks = chunk_text(text)
            if not chunks:
                if verbose:
                    print(f"  {doc.name}: sin texto, omitido")
                continue
            embeddings = embedder.encode(chunks)
            store.add_chunks(db, doc.name, chunks, embeddings)
            total_chunks += len(chunks)
            if verbose:
                print(f"  {doc.name}: {len(chunks)} chunks")

        store.set_meta(db, "embedder", embedder.backend)
        store.set_meta(db, "dim", embedder.dim)
    finally:
        db.close()

    return {"docs": len(docs), "chunks": total_chunks, "embedder": embedder.backend}
