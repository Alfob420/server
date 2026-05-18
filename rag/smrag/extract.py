"""Extracción de texto plano desde los formatos del corpus."""
from __future__ import annotations

from pathlib import Path

SUPPORTED_SUFFIXES = {".txt", ".md", ".pdf"}


def extract_text(path: Path) -> str:
    """Devuelve el texto plano de un documento soportado."""
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return _extract_pdf(path)
    raise ValueError(f"formato no soportado: {suffix}")


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "falta 'pypdf' para leer PDFs (pip install -r requirements.txt)"
        ) from exc

    reader = PdfReader(str(path))
    return "\n\n".join((page.extract_text() or "") for page in reader.pages)
