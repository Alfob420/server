#!/usr/bin/env bash
# Setup de Survival Mesh: compila la API, prepara el RAG e indexa el corpus.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo "[setup] raíz del proyecto: $ROOT"

# --- 1. API Rust (Capa 4) -------------------------------------------------
if ! command -v cargo >/dev/null 2>&1; then
  echo "[setup] error: falta 'cargo' (instalá Rust: https://rustup.rs)" >&2
  exit 1
fi
echo "[setup] compilando la API (api/)..."
cargo build --release --manifest-path api/Cargo.toml

# --- 2. Entorno Python del RAG (Capa 3) -----------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "[setup] error: falta 'python3'" >&2
  exit 1
fi
if [ ! -d rag/.venv ]; then
  echo "[setup] creando el venv del RAG (rag/.venv)..."
  python3 -m venv rag/.venv
fi
echo "[setup] instalando dependencias del RAG..."
rag/.venv/bin/pip install --quiet --upgrade pip
rag/.venv/bin/pip install --quiet -r rag/requirements.txt

# --- 3. Indexar el corpus -------------------------------------------------
echo "[setup] indexando el corpus (descarga el modelo de embeddings la 1ra vez)..."
( cd rag && .venv/bin/python3 ingest.py --corpus corpus/ --out survival.db )

cat <<'EOF'

[setup] listo.

Para correr todo en local (servicio RAG + API + PWA):
    scripts/run-dev.sh

Luego abrí http://localhost:8080

Inferencia LLM real: correr un 'llama-server' aparte y exportar
SM_LLM_URL antes de arrancar la API (ver api/README.md).
EOF
