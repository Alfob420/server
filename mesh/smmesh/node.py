"""Nodo de mensajería Reticulum.

Cada nodo:
- tiene una identidad criptográfica persistente (su "dirección" en la mesh);
- publica un destino `survivalmesh.message` y lo anuncia periódicamente;
- recibe mensajes de texto en un buzón en memoria;
- descubre otros nodos a partir de sus anuncios;
- envía mensajes a la dirección de otro nodo.

El transporte físico (TCP, LoRa, etc.) se define en la configuración de
Reticulum (`configdir/config`), no acá.
"""
from __future__ import annotations

import json
import os
import threading
import time

import RNS

APP_NAME = "survivalmesh"
ASPECT = "message"

# Límite conservador de texto por mensaje. Un paquete RNS único (SINGLE)
# transporta unos ~380 bytes; el resto se reserva para el sobre JSON.
MAX_TEXT_LEN = 230
_PATH_WAIT_SECS = 12


class _AnnounceHandler:
    """Registra los nodos descubiertos a partir de sus anuncios."""

    aspect_filter = f"{APP_NAME}.{ASPECT}"

    def __init__(self, node: "MeshNode"):
        self._node = node

    def received_announce(self, destination_hash, announced_identity, app_data):
        name = app_data.decode("utf-8", "replace") if app_data else ""
        self._node._register_peer(destination_hash.hex(), name)


class MeshNode:
    """Nodo de mensajería sobre Reticulum."""

    def __init__(
        self,
        configdir: str,
        identity_path: str,
        display_name: str = "survival-mesh-node",
    ):
        self.display_name = display_name
        self._lock = threading.Lock()
        self._inbox: list[dict] = []
        self._peers: dict[str, dict] = {}
        self._seq = 0

        os.makedirs(configdir, exist_ok=True)
        self.reticulum = RNS.Reticulum(configdir)

        self.identity = _load_or_create_identity(identity_path)
        self.destination = RNS.Destination(
            self.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            APP_NAME,
            ASPECT,
        )
        self.destination.set_packet_callback(self._on_packet)
        RNS.Transport.register_announce_handler(_AnnounceHandler(self))

    @property
    def address(self) -> str:
        """Dirección del nodo (hash del destino) en hexadecimal."""
        return self.destination.hash.hex()

    # -- anuncios ----------------------------------------------------------
    def announce(self) -> None:
        self.destination.announce(app_data=self.display_name.encode("utf-8"))

    def start_announce_loop(self, interval: int = 30) -> None:
        def loop() -> None:
            while True:
                try:
                    self.announce()
                except Exception as exc:  # noqa: BLE001
                    RNS.log(f"[smmesh] fallo al anunciar: {exc}", RNS.LOG_ERROR)
                time.sleep(interval)

        threading.Thread(target=loop, daemon=True, name="smmesh-announce").start()

    # -- envío / recepción -------------------------------------------------
    def send(self, dest_hash_hex: str, text: str) -> None:
        """Envía un mensaje de texto a otro nodo. Lanza RuntimeError si falla."""
        text = (text or "").strip()
        if not text:
            raise ValueError("el texto está vacío")
        if len(text) > MAX_TEXT_LEN:
            raise ValueError(f"el texto excede {MAX_TEXT_LEN} caracteres")

        try:
            dest_hash = bytes.fromhex(dest_hash_hex)
        except ValueError as exc:
            raise ValueError(f"dirección inválida: {dest_hash_hex}") from exc

        if not RNS.Transport.has_path(dest_hash):
            RNS.Transport.request_path(dest_hash)
            deadline = time.time() + _PATH_WAIT_SECS
            while not RNS.Transport.has_path(dest_hash) and time.time() < deadline:
                time.sleep(0.2)
        if not RNS.Transport.has_path(dest_hash):
            raise RuntimeError("sin ruta al destino (nodo no descubierto aún)")

        recipient = RNS.Identity.recall(dest_hash)
        if recipient is None:
            raise RuntimeError("no se conoce la identidad del destino")

        out = RNS.Destination(
            recipient,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            APP_NAME,
            ASPECT,
        )
        payload = json.dumps(
            {"from": self.address, "name": self.display_name, "text": text},
            ensure_ascii=False,
        ).encode("utf-8")
        RNS.Packet(out, payload).send()

    def _on_packet(self, data: bytes, packet) -> None:
        try:
            msg = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            msg = {"text": data.decode("utf-8", "replace")}
        with self._lock:
            self._seq += 1
            self._inbox.append(
                {
                    "id": self._seq,
                    "from": str(msg.get("from", "")),
                    "name": str(msg.get("name", "")),
                    "text": str(msg.get("text", "")),
                    "ts": time.time(),
                }
            )
            del self._inbox[:-200]  # conservar los últimos 200

    def _register_peer(self, address: str, name: str) -> None:
        with self._lock:
            self._peers[address] = {"name": name, "last_seen": time.time()}

    # -- consultas ---------------------------------------------------------
    def peers(self) -> list[dict]:
        with self._lock:
            items = [
                {"address": addr, "name": p["name"], "last_seen": p["last_seen"]}
                for addr, p in self._peers.items()
            ]
        items.sort(key=lambda p: p["last_seen"], reverse=True)
        return items

    def inbox(self, since: int = 0) -> list[dict]:
        with self._lock:
            return [m for m in self._inbox if m["id"] > since]


def _load_or_create_identity(path: str) -> RNS.Identity:
    if os.path.isfile(path):
        identity = RNS.Identity.from_file(path)
        if identity is not None:
            return identity
    identity = RNS.Identity()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    identity.to_file(path)
    return identity
