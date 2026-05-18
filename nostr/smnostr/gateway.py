"""Gateway Nostr: identidad persistente, conexión a relays y mensajería cifrada.

Cada relay se maneja en su propio hilo, con reconexión automática. Los mensajes
directos (NIP-04) dirigidos a este nodo se descifran y entran a un buzón en
memoria.
"""
from __future__ import annotations

import json
import os
import threading
import time

import websocket

from . import protocol

DEFAULT_RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://relay.primal.net",
]
_SUB_ID = "survival-mesh-dms"
_RECONNECT_SECS = 5


class _RelayConnection:
    """Conexión a un relay con reconexión automática y suscripción a DMs."""

    def __init__(self, url: str, gateway: "NostrGateway"):
        self.url = url
        self.connected = False
        self._gateway = gateway
        self._ws = None
        threading.Thread(
            target=self._run, daemon=True, name=f"nostr-relay"
        ).start()

    def _run(self) -> None:
        while True:
            try:
                self._ws = websocket.create_connection(self.url, timeout=15)
                self._ws.settimeout(None)  # recv bloqueante
                self.connected = True
                self._subscribe()
                while True:
                    raw = self._ws.recv()
                    if not raw:
                        break
                    self._gateway._on_relay_message(raw)
            except Exception:  # noqa: BLE001 - cualquier fallo -> reconectar
                pass
            finally:
                self.connected = False
                try:
                    if self._ws is not None:
                        self._ws.close()
                except Exception:  # noqa: BLE001
                    pass
            time.sleep(_RECONNECT_SECS)

    def _subscribe(self) -> None:
        req = [
            "REQ",
            _SUB_ID,
            {
                "kinds": [protocol.KIND_DM],
                "#p": [self._gateway.pubkey],
                "since": self._gateway.since,
            },
        ]
        self._ws.send(json.dumps(req))

    def send(self, payload: str) -> bool:
        if self.connected and self._ws is not None:
            try:
                self._ws.send(payload)
                return True
            except Exception:  # noqa: BLE001
                return False
        return False


class NostrGateway:
    """Gateway Nostr de Survival Mesh."""

    def __init__(
        self,
        secret_path: str,
        relays: list[str] | None = None,
        name: str = "survival-mesh",
    ):
        self.name = name
        self.since = int(time.time())
        self._lock = threading.Lock()
        self._inbox: list[dict] = []
        self._seq = 0
        self._seen_ids: set[str] = set()

        self.secret = _load_or_create_secret(secret_path)
        self.pubkey = protocol.pubkey_hex(self.secret)

        self._relays = [
            _RelayConnection(url, self) for url in (relays or DEFAULT_RELAYS)
        ]

    # -- recepción ---------------------------------------------------------
    def _on_relay_message(self, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except ValueError:
            return
        if isinstance(msg, list) and len(msg) >= 3 and msg[0] == "EVENT":
            self._handle_event(msg[2])

    def _handle_event(self, event: dict) -> None:
        if not isinstance(event, dict) or event.get("kind") != protocol.KIND_DM:
            return
        event_id = str(event.get("id", ""))
        with self._lock:
            if not event_id or event_id in self._seen_ids:
                return
            self._seen_ids.add(event_id)

        if not protocol.verify_event(event):
            return
        sender = str(event.get("pubkey", ""))
        try:
            text = protocol.decrypt_dm(self.secret, sender, event.get("content", ""))
        except Exception:  # noqa: BLE001 - DM ilegible: se descarta
            return

        with self._lock:
            self._seq += 1
            self._inbox.append(
                {
                    "id": self._seq,
                    "from": sender,
                    "text": text,
                    "ts": int(event.get("created_at", time.time())),
                }
            )
            del self._inbox[:-200]

    # -- envío -------------------------------------------------------------
    def send(self, recipient_pubkey: str, text: str) -> int:
        """Envía un DM cifrado. Devuelve a cuántos relays se publicó."""
        recipient = recipient_pubkey.strip().lower()
        try:
            if len(bytes.fromhex(recipient)) != 32:
                raise ValueError
        except ValueError:
            raise ValueError("clave pública de destino inválida (64 hex)")

        text = (text or "").strip()
        if not text:
            raise ValueError("el texto está vacío")

        event = protocol.dm_event(self.secret, recipient, text)
        payload = json.dumps(["EVENT", event])
        published = sum(1 for relay in self._relays if relay.send(payload))
        if published == 0:
            raise RuntimeError("ningún relay conectado")
        return published

    # -- consultas ---------------------------------------------------------
    def inbox(self, since: int = 0) -> list[dict]:
        with self._lock:
            return [m for m in self._inbox if m["id"] > since]

    def status(self) -> dict:
        relays = [
            {"url": relay.url, "connected": relay.connected}
            for relay in self._relays
        ]
        with self._lock:
            inbox_count = len(self._inbox)
        return {
            "status": "ok",
            "pubkey": self.pubkey,
            "name": self.name,
            "relays": relays,
            "relays_connected": sum(1 for r in relays if r["connected"]),
            "inbox": inbox_count,
        }


def _load_or_create_secret(path: str) -> bytes:
    if os.path.isfile(path):
        data = open(path, encoding="utf-8").read().strip()
        if len(data) == 64:
            try:
                return bytes.fromhex(data)
            except ValueError:
                pass
    secret = protocol.generate_secret()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(secret.hex())
    os.chmod(path, 0o600)
    return secret
