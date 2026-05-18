"""Primitivas del protocolo Nostr.

- Claves: secp256k1 x-only (NIP-01).
- Eventos: serialización, id (sha256), firma Schnorr (BIP-340).
- Mensajes directos cifrados: NIP-04 (ECDH + AES-256-CBC).
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time

import coincurve
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

KIND_DM = 4  # NIP-04 — mensaje directo cifrado


# -- claves ---------------------------------------------------------------
def generate_secret() -> bytes:
    """Genera una clave privada nueva (32 bytes)."""
    return coincurve.PrivateKey().secret


def pubkey_hex(secret: bytes) -> str:
    """Clave pública x-only en hexadecimal (la identidad Nostr del nodo)."""
    return coincurve.PublicKeyXOnly.from_secret(secret).format().hex()


# -- eventos (NIP-01) -----------------------------------------------------
def _serialized_id(pubkey, created_at, kind, tags, content) -> bytes:
    payload = json.dumps(
        [0, pubkey, created_at, kind, tags, content],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return payload.encode("utf-8")


def build_event(
    secret: bytes,
    kind: int,
    content: str,
    tags: list | None = None,
    created_at: int | None = None,
) -> dict:
    """Construye un evento Nostr firmado."""
    pubkey = pubkey_hex(secret)
    created_at = created_at if created_at is not None else int(time.time())
    tags = tags or []
    event_id = hashlib.sha256(
        _serialized_id(pubkey, created_at, kind, tags, content)
    ).digest()
    signature = coincurve.PrivateKey(secret).sign_schnorr(event_id)
    return {
        "id": event_id.hex(),
        "pubkey": pubkey,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": content,
        "sig": signature.hex(),
    }


def verify_event(event: dict) -> bool:
    """Valida el id y la firma de un evento recibido."""
    try:
        event_id = hashlib.sha256(
            _serialized_id(
                event["pubkey"],
                event["created_at"],
                event["kind"],
                event["tags"],
                event["content"],
            )
        ).digest()
        if event_id.hex() != event["id"]:
            return False
        pub = coincurve.PublicKeyXOnly(bytes.fromhex(event["pubkey"]))
        return pub.verify(bytes.fromhex(event["sig"]), event_id)
    except (KeyError, ValueError, TypeError):
        return False


# -- mensajes directos cifrados (NIP-04) ----------------------------------
def _shared_secret(my_secret: bytes, their_pubkey_hex: str) -> bytes:
    # x-only -> punto comprimido (se asume y par, convención BIP-340).
    pub = coincurve.PublicKey(b"\x02" + bytes.fromhex(their_pubkey_hex))
    point = pub.multiply(my_secret)
    return point.format(compressed=False)[1:33]  # coordenada x cruda


def encrypt_dm(my_secret: bytes, their_pubkey_hex: str, text: str) -> str:
    key = _shared_secret(my_secret, their_pubkey_hex)
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    data = padder.update(text.encode("utf-8")) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return (
        base64.b64encode(ciphertext).decode()
        + "?iv="
        + base64.b64encode(iv).decode()
    )


def decrypt_dm(my_secret: bytes, their_pubkey_hex: str, content: str) -> str:
    if "?iv=" not in content:
        raise ValueError("contenido NIP-04 inválido")
    ct_b64, iv_b64 = content.split("?iv=", 1)
    key = _shared_secret(my_secret, their_pubkey_hex)
    decryptor = Cipher(
        algorithms.AES(key), modes.CBC(base64.b64decode(iv_b64))
    ).decryptor()
    data = decryptor.update(base64.b64decode(ct_b64)) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(data) + unpadder.finalize()).decode("utf-8")


def dm_event(my_secret: bytes, their_pubkey_hex: str, text: str) -> dict:
    """Construye un evento de mensaje directo cifrado (kind 4)."""
    content = encrypt_dm(my_secret, their_pubkey_hex, text)
    return build_event(my_secret, KIND_DM, content, tags=[["p", their_pubkey_hex]])
