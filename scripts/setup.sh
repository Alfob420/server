#!/usr/bin/env bash
# Setup de Survival Mesh: compila la API, prepara el entorno Python (RAG +
# mesh) e indexa el corpus.
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

# --- 2. Entorno Python (RAG + mesh) ---------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "[setup] error: falta 'python3'" >&2
  exit 1
fi
if [ ! -d .venv ]; then
  echo "[setup] creando el venv (.venv)..."
  python3 -m venv .venv
fi
echo "[setup] instalando dependencias de Python (RAG + mesh + Nostr)..."
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet \
  -r rag/requirements.txt -r mesh/requirements.txt -r nostr/requirements.txt

# --- 3. Configuración de Reticulum (Capa 2) -------------------------------
if [ ! -f mesh/reticulum/config ]; then
  echo "[setup] creando config de Reticulum en mesh/reticulum/config..."
  mkdir -p mesh/reticulum
  cp mesh/reticulum.config.example mesh/reticulum/config
  echo "[setup] editá mesh/reticulum/config para activar interfaces (LoRa/TCP)."
fi

# --- 4. Indexar el corpus (Capa 3) ----------------------------------------
echo "[setup] indexando el corpus (descarga el modelo de embeddings la 1ra vez)..."
( cd rag && "$ROOT/.venv/bin/python3" ingest.py --corpus corpus/ --out survival.db )

cat <<'EOF'

[setup] listo.

Para correr todo en local (mesh + RAG + API + PWA):
    scripts/run-dev.sh

Luego abrí http://localhost:8080

Inferencia LLM real: correr un 'llama-server' aparte y exportar
SM_LLM_URL antes de arrancar la API (ver api/README.md).
EOF
