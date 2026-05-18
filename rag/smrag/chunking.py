"""Fragmentación de documentos en chunks para indexar."""
from __future__ import annotations

import re

_PARA_SPLIT = re.compile(r"\n\s*\n")


def chunk_text(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    """Parte el texto en fragmentos de ~`size` caracteres.

    Agrupa por párrafos para no cortar ideas a la mitad. Arrastra `overlap`
    caracteres del fragmento anterior para preservar continuidad. Un párrafo
    más largo que ~1.5x `size` se parte de forma dura.
    """
    paragraphs = [p.strip() for p in _PARA_SPLIT.split(text) if p.strip()]

    grouped: list[str] = []
    buf = ""
    for para in paragraphs:
        if buf and len(buf) + len(para) + 2 > size:
            grouped.append(buf)
            tail = buf[-overlap:] if overlap else ""
            buf = f"{tail}\n\n{para}" if tail else para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
    if buf.strip():
        grouped.append(buf)

    out: list[str] = []
    hard_limit = int(size * 1.5)
    step = max(1, size - overlap)
    for chunk in grouped:
        if len(chunk) <= hard_limit:
            out.append(chunk)
        else:
            out.extend(chunk[i : i + size] for i in range(0, len(chunk), step))

    return [c.strip() for c in out if c.strip()]
