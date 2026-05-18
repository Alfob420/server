#!/usr/bin/env bash
# Levanta el servicio RAG y la API juntos para desarrollo local.
# El servicio RAG corre en segundo plano; la API queda en primer plano.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Intérprete: venv del RAG si existe, si no python3 del sistema.
PY="$ROOT/rag/.venv/bin/python3"
[ -x "$PY" ] || PY="python3"

if [ ! -f "$ROOT/rag/survival.db" ]; then
  echo "error: falta rag/survival.db — corré scripts/setup.sh primero." >&2
  exit 1
fi

echo "[run] iniciando servicio RAG en :8090 ..."
( cd "$ROOT/rag" && "$PY" service.py --db survival.db --port 8090 ) &
RAG_PID=$!
trap 'echo; echo "[run] deteniendo servicio RAG"; kill $RAG_PID 2>/dev/null' EXIT

# Esperar a que el servicio RAG responda.
for _ in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8090/health >/dev/null 2>&1; then break; fi
  sleep 0.5
done

echo "[run] iniciando API en :8080 (Ctrl-C para salir) ..."
cd "$ROOT/api"
SM_RAG_URL="http://127.0.0.1:8090" exec cargo run --release
