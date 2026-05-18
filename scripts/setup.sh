#!/usr/bin/env bash
# Setup de desarrollo de Survival Mesh.
# Compila el servidor API. Las capas RAG/mesh/transport todavía son stubs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[setup] raíz del proyecto: $ROOT"

if ! command -v cargo >/dev/null 2>&1; then
  echo "[setup] error: falta 'cargo' (instalá Rust: https://rustup.rs)" >&2
  exit 1
fi

echo "[setup] compilando el servidor API (api/)..."
cargo build --manifest-path api/Cargo.toml

cat <<'EOF'

[setup] listo.

Para correr el servidor (sirve también la PWA):
    cd api && cargo run

Luego abrí http://localhost:8080

Pendiente (stubs): rag/, mesh/, transport/. Ver el README de cada carpeta.
EOF
