"""Embeddings de texto para el RAG.

Backend principal: un modelo tipo MiniLM en formato ONNX, ejecutado con
onnxruntime. Es la opción correcta para el producto: corre en ARM64 (Raspberry
Pi) y x86 sin PyTorch.

Modelos disponibles (ambos producen vectores de 384 dimensiones):

- `multilingual` (default) — paraphrase-multilingual-MiniLM-L12-v2. Soporta
  español y ~50 idiomas. El corpus de supervivencia y las consultas son en
  español, así que este es el modelo correcto para el producto.
- `english` — all-MiniLM-L6-v2. Más liviano pero solo inglés; la recuperación
  en español es pobre. Documento 1 lo nombraba, pero es inadecuado para un
  corpus en español.

Fallback: `HashEmbedder`, determinista y sin red. NO produce embeddings
semánticos — solo permite ejercitar el pipeline sin descargar el modelo.
"""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

import numpy as np

EMBED_DIM = 384

_HF = "https://huggingface.co"
_MODELS = {
    "multilingual": {
        "backend": "onnx-paraphrase-multilingual-MiniLM-L12-v2",
        "repo": "Xenova/paraphrase-multilingual-MiniLM-L12-v2",
        "onnx": "onnx/model_quantized.onnx",
    },
    "english": {
        "backend": "onnx-all-MiniLM-L6-v2",
        "repo": "Xenova/all-MiniLM-L6-v2",
        "onnx": "onnx/model.onnx",
    },
}
DEFAULT_MODEL = "multilingual"

_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


class Embedder:
    """Interfaz común. `encode` devuelve una matriz (n, EMBED_DIM) L2-normalizada."""

    dim = EMBED_DIM
    backend = "abstract"

    def encode(self, texts: list[str]) -> np.ndarray:  # pragma: no cover
        raise NotImplementedError


def _l2_normalize(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (mat / norms).astype(np.float32)


class HashEmbedder(Embedder):
    """Fallback determinista: bag-of-words con hashing. Solo para desarrollo."""

    backend = "hash-fallback"

    def encode(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for token in text.lower().split():
                bucket = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.dim
                out[i, bucket] += 1.0
        return _l2_normalize(out)


class OnnxEmbedder(Embedder):
    """Embedder MiniLM vía onnxruntime. Descarga el modelo al primer uso."""

    def __init__(self, model: str = DEFAULT_MODEL, models_dir: Path = _MODELS_DIR):
        import onnxruntime as ort
        from tokenizers import Tokenizer

        if model not in _MODELS:
            raise ValueError(f"modelo desconocido: {model}")
        spec = _MODELS[model]
        self.backend = spec["backend"]

        model_path = _ensure_file(
            models_dir, f"{model}-model.onnx", f"{_HF}/{spec['repo']}/resolve/main/{spec['onnx']}"
        )
        tok_path = _ensure_file(
            models_dir,
            f"{model}-tokenizer.json",
            f"{_HF}/{spec['repo']}/resolve/main/tokenizer.json",
        )

        self._tok = Tokenizer.from_file(str(tok_path))
        self._tok.enable_truncation(max_length=256)
        self._tok.enable_padding()
        self._sess = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self._input_names = {i.name for i in self._sess.get_inputs()}

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)

        encs = self._tok.encode_batch(list(texts))
        ids = np.array([e.ids for e in encs], dtype=np.int64)
        mask = np.array([e.attention_mask for e in encs], dtype=np.int64)

        feed = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in self._input_names:
            feed["token_type_ids"] = np.zeros_like(ids)
        feed = {k: v for k, v in feed.items() if k in self._input_names}

        hidden = self._sess.run(None, feed)[0]  # (n, seq, dim)
        mask_f = mask.astype(np.float32)[:, :, None]
        summed = (hidden * mask_f).sum(axis=1)
        counts = np.clip(mask_f.sum(axis=1), 1e-9, None)
        return _l2_normalize(summed / counts)


def _ensure_file(models_dir: Path, name: str, url: str) -> Path:
    models_dir.mkdir(parents=True, exist_ok=True)
    dest = models_dir / name
    if dest.exists() and dest.stat().st_size > 0:
        return dest

    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"[embeddings] descargando {name} ...")
    urllib.request.urlretrieve(url, tmp)
    tmp.rename(dest)
    return dest


def get_embedder(prefer: str = "auto", model: str = DEFAULT_MODEL) -> Embedder:
    """Devuelve un embedder.

    `prefer`: 'auto' (ONNX con fallback a hash) | 'onnx' (falla si no hay) | 'hash'.
    `model`:  'multilingual' | 'english'.
    """
    if prefer == "hash":
        return HashEmbedder()
    try:
        return OnnxEmbedder(model=model)
    except Exception as exc:  # noqa: BLE001 - degradar a fallback es intencional
        if prefer == "onnx":
            raise
        print(f"[embeddings] backend ONNX no disponible ({exc}); usando fallback hash")
        return HashEmbedder()
