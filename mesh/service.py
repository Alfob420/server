#!/usr/bin/env python3
"""Servicio HTTP de la capa mesh (Capa 2).

Mantiene un nodo Reticulum vivo (identidad, anuncios, buzón) y expone su
funcionalidad por HTTP para que la API Rust (`../api`) la consuma.

Uso:
    python3 service.py --configdir ./reticulum --port 8091

Endpoints:
    GET  /health   -> estado del nodo.
    GET  /peers    -> nodos descubiertos.
    GET  /inbox    -> mensajes recibidos (opcional ?since=<id>).
    POST /send     -> {"to": "<address>", "text": "..."} envía un mensaje.
    POST /announce -> fuerza un anuncio inmediato.
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from smmesh.node import MeshNode

_MAX_BODY = 64 * 1024


class _Handler(BaseHTTPRequestHandler):
    server_version = "SurvivalMeshMesh/0.1"

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length > _MAX_BODY:
            raise ValueError("body demasiado grande")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/")
        node: MeshNode = self.server.node

        if route == "/health":
            self._send_json(
                200,
                {
                    "status": "ok",
                    "address": node.address,
                    "name": node.display_name,
                    "peers": len(node.peers()),
                    "inbox": len(node.inbox()),
                },
            )
        elif route == "/peers":
            self._send_json(200, {"peers": node.peers()})
        elif route == "/inbox":
            since = int((parse_qs(parsed.query).get("since", ["0"]))[0] or 0)
            self._send_json(200, {"messages": node.inbox(since=since)})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        route = urlparse(self.path).path.rstrip("/")
        node: MeshNode = self.server.node

        if route == "/announce":
            node.announce()
            self._send_json(200, {"status": "announced"})
            return

        if route != "/send":
            self._send_json(404, {"error": "not found"})
            return

        try:
            req = self._read_json()
            to = str(req.get("to", "")).strip()
            text = str(req.get("text", ""))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": f"request inválido: {exc}"})
            return

        if not to:
            self._send_json(400, {"error": "falta el destino 'to'"})
            return

        try:
            node.send(to, text)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except RuntimeError as exc:
            self._send_json(502, {"error": str(exc)})
            return

        self._send_json(200, {"status": "sent"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[mesh] {self.address_string()} {fmt % args}")


class MeshService(HTTPServer):
    """HTTPServer con el nodo mesh adjunto (single-threaded)."""

    def __init__(self, addr, node: MeshNode):
        super().__init__(addr, _Handler)
        self.node = node


def main() -> None:
    parser = argparse.ArgumentParser(description="Servicio HTTP de la capa mesh.")
    parser.add_argument(
        "--configdir",
        type=Path,
        default=Path("reticulum"),
        help="directorio de configuración de Reticulum",
    )
    parser.add_argument(
        "--identity",
        type=Path,
        default=None,
        help="archivo de identidad (default: <configdir>/identity)",
    )
    parser.add_argument("--name", default="survival-mesh-node", help="nombre del nodo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8091)
    parser.add_argument(
        "--announce-interval", type=int, default=30, help="segundos entre anuncios"
    )
    args = parser.parse_args()

    identity_path = args.identity or (args.configdir / "identity")
    node = MeshNode(str(args.configdir), str(identity_path), display_name=args.name)
    node.start_announce_loop(interval=args.announce_interval)
    node.announce()

    service = MeshService((args.host, args.port), node)
    print(
        f"[mesh] servicio en http://{args.host}:{args.port} "
        f"| nodo '{node.display_name}' | dirección {node.address}"
    )
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print("\n[mesh] apagando")


if __name__ == "__main__":
    main()
