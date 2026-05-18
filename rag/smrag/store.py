"""Almacén vectorial sobre SQLite + sqlite-vec.

El índice es un único archivo `.db` portable que se copia entre dispositivos.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import sqlite_vec

from .embeddings import EMBED_DIM

_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS chunks (
    id   INTEGER PRIMARY KEY,
    doc  TEXT NOT NULL,
    ord  INTEGER NOT NULL,
    text TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunk_vec USING vec0(
    embedding float[{EMBED_DIM}]
);
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    """Abre la base con la extensión sqlite-vec cargada."""
    db = sqlite3.connect(str(path))
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


def init(db: sqlite3.Connection) -> None:
    db.executescript(_SCHEMA)
    db.commit()


def reset(db: sqlite3.Connection) -> None:
    """Borra el índice y lo recrea vacío."""
    db.executescript(
        "DROP TABLE IF EXISTS chunks;"
        "DROP TABLE IF EXISTS chunk_vec;"
        "DROP TABLE IF EXISTS meta;"
    )
    init(db)


def add_chunks(
    db: sqlite3.Connection,
    doc: str,
    chunks: list[str],
    embeddings: np.ndarray,
) -> None:
    """Inserta los fragmentos de un documento con sus embeddings."""
    cur = db.cursor()
    for ordinal, (text, emb) in enumerate(zip(chunks, embeddings)):
        cur.execute(
            "INSERT INTO chunks(doc, ord, text) VALUES (?, ?, ?)",
            (doc, ordinal, text),
        )
        cur.execute(
            "INSERT INTO chunk_vec(rowid, embedding) VALUES (?, ?)",
            (cur.lastrowid, sqlite_vec.serialize_float32(emb.tolist())),
        )
    db.commit()


def set_meta(db: sqlite3.Connection, key: str, value: object) -> None:
    db.execute(
        "INSERT INTO meta(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    db.commit()


def get_meta(db: sqlite3.Connection, key: str) -> str | None:
    row = db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row[0] if row else None


def count(db: sqlite3.Connection) -> int:
    try:
        return db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    except sqlite3.OperationalError:
        return 0


def search(db: sqlite3.Connection, query_emb: np.ndarray, k: int = 4) -> list[dict]:
    """Devuelve los `k` fragmentos más cercanos a `query_emb`."""
    rows = db.execute(
        """
        SELECT c.doc, c.ord, c.text, v.distance
        FROM chunk_vec v
        JOIN chunks c ON c.id = v.rowid
        WHERE v.embedding MATCH ? AND k = ?
        ORDER BY v.distance
        """,
        (sqlite_vec.serialize_float32(query_emb.tolist()), k),
    ).fetchall()
    return [
        {"doc": doc, "ord": ordinal, "text": text, "distance": distance}
        for doc, ordinal, text, distance in rows
    ]
