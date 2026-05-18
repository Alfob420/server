#!/usr/bin/env python3
"""Servicio HTTP del RAG (Capa 3).

Mantiene el modelo de embeddings y el índice cargados en memoria, y expone la
recuperación para que la API Rust (`../api`) la consulte por HTTP.

Uso:
    python3 service.py --db survival.db --port 8090

Endpoints:
    GET  /health    -> estado del servicio.
    POST /retrieve  -> {"query": "...", "k": 4} -> {"hits": [...]}
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from smrag import store
from smrag.embeddings import get_embedder

_MAX_BODY = 64 * 1024


class _Handler(BaseHTTPRequestHandler):
    server_version = "SurvivalMeshRAG/0.1"

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - nombre impuesto por BaseHTTPRequestHandler
        if self.path.rstrip("/") == "/health":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "backend": self.server.embedder.backend,
                    "chunks": store.count(self.server.db),
                },
            )
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/retrieve":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        if length > _MAX_BODY:
            self._send_json(413, {"error": "body demasiado grande"})
            return

        try:
            req = json.loads(self.rfile.read(length) or b"{}")
            query = str(req.get("query", "")).strip()
            k = max(1, min(20, int(req.get("k", 4))))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": f"request inválido: {exc}"})
            return

        if not query:
            self._send_json(400, {"error": "query vacía"})
            return

        emb = self.server.embedder.encode([query])[0]
        hits = store.search(self.server.db, emb, k=k)
        self._send_json(200, {"query": query, "hits": hits})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[rag] {self.address_string()} {fmt % args}")


class RagService(HTTPServer):
    """HTTPServer con el embedder y el índice adjuntos (single-threaded)."""

    def __init__(self, addr, db, embedder):
        super().__init__(addr, _Handler)
        self.db = db
        self.embedder = embedder


def main() -> None:
    parser = argparse.ArgumentParser(description="Servicio HTTP del RAG.")
    parser.add_argument("--db", type=Path, default=Path("survival.db"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--embedder", choices=["auto", "onnx", "hash"], default="auto")
    parser.add_argument(
        "--model", choices=["multilingual", "english"], default="multilingual"
    )
    args = parser.parse_args()

    if not args.db.exists():
        raise SystemExit(f"error: el índice no existe: {args.db} (corré ingest.py)")

    embedder = get_embedder(args.embedder, args.model)
    db = store.connect(args.db)

    indexed = store.get_meta(db, "embedder")
    if indexed and indexed != embedder.backend:
        print(
            f"[rag] aviso: índice creado con '{indexed}', servicio usa "
            f"'{embedder.backend}'."
        )

    service = RagService((args.host, args.port), db, embedder)
    print(
        f"[rag] servicio en http://{args.host}:{args.port} "
        f"| backend {embedder.backend} | {store.count(db)} chunks"
    )
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print("\n[rag] apagando")
    finally:
        db.close()


if __name__ == "__main__":
    main()
