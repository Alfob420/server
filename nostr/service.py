#!/usr/bin/env python3
"""Servicio HTTP del gateway Nostr (transporte global).

Mantiene un gateway Nostr vivo (identidad, relays, buzón) y lo expone por HTTP
para que la API Rust (`../api`) lo consuma.

Uso:
    python3 service.py --secret nostr.key --port 8092

Endpoints:
    GET  /health -> estado del gateway (pubkey, relays, buzón).
    GET  /inbox  -> mensajes recibidos (opcional ?since=<id>).
    POST /send   -> {"to": "<pubkey hex>", "text": "..."} envía un DM cifrado.
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from smnostr.gateway import DEFAULT_RELAYS, NostrGateway

_MAX_BODY = 64 * 1024


class _Handler(BaseHTTPRequestHandler):
    server_version = "SurvivalMeshNostr/0.1"

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/")
        gateway: NostrGateway = self.server.gateway

        if route == "/health":
            self._send_json(200, gateway.status())
        elif route == "/inbox":
            since = int((parse_qs(parsed.query).get("since", ["0"]))[0] or 0)
            self._send_json(200, {"messages": gateway.inbox(since=since)})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path.rstrip("/") != "/send":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        if length > _MAX_BODY:
            self._send_json(413, {"error": "body demasiado grande"})
            return

        try:
            req = json.loads(self.rfile.read(length) or b"{}")
            to = str(req.get("to", "")).strip()
            text = str(req.get("text", ""))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": f"request inválido: {exc}"})
            return

        if not to:
            self._send_json(400, {"error": "falta el destino 'to'"})
            return

        try:
            published = self.server.gateway.send(to, text)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except RuntimeError as exc:
            self._send_json(502, {"error": str(exc)})
            return

        self._send_json(200, {"status": "sent", "relays": published})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[nostr] {self.address_string()} {fmt % args}")


class NostrService(HTTPServer):
    """HTTPServer con el gateway Nostr adjunto (single-threaded)."""

    def __init__(self, addr, gateway: NostrGateway):
        super().__init__(addr, _Handler)
        self.gateway = gateway


def main() -> None:
    parser = argparse.ArgumentParser(description="Servicio HTTP del gateway Nostr.")
    parser.add_argument(
        "--secret",
        type=Path,
        default=Path("nostr.key"),
        help="archivo de clave privada (se crea si no existe)",
    )
    parser.add_argument("--name", default="survival-mesh", help="nombre del nodo")
    parser.add_argument(
        "--relays",
        default=",".join(DEFAULT_RELAYS),
        help="relays separados por coma",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8092)
    args = parser.parse_args()

    relays = [r.strip() for r in args.relays.split(",") if r.strip()]
    gateway = NostrGateway(str(args.secret), relays=relays, name=args.name)

    service = NostrService((args.host, args.port), gateway)
    print(
        f"[nostr] servicio en http://{args.host}:{args.port} "
        f"| pubkey {gateway.pubkey} | {len(relays)} relays"
    )
    try:
        service.serve_forever()
    except KeyboardInterrupt:
        print("\n[nostr] apagando")


if __name__ == "__main__":
    main()
