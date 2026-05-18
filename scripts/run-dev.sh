#!/usr/bin/env bash
# Levanta los servicios mesh + RAG y la API juntos para desarrollo local.
# Los servicios de Python corren en segundo plano; la API queda en primer plano.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Intérprete: venv del proyecto si existe, si no python3 del sistema.
PY="$ROOT/.venv/bin/python3"
[ -x "$PY" ] || PY="python3"

if [ ! -f "$ROOT/rag/survival.db" ]; then
  echo "error: falta rag/survival.db — corré scripts/setup.sh primero." >&2
  exit 1
fi

PIDS=()
cleanup() {
  echo
  echo "[run] deteniendo servicios"
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done
}
trap cleanup EXIT

echo "[run] iniciando servicio mesh en :8091 ..."
( cd "$ROOT/mesh" && exec "$PY" service.py --configdir reticulum --port 8091 ) &
PIDS+=($!)

echo "[run] iniciando gateway Nostr en :8092 ..."
( cd "$ROOT/nostr" && exec "$PY" service.py --secret nostr.key --port 8092 ) &
PIDS+=($!)

echo "[run] iniciando servicio RAG en :8090 ..."
( cd "$ROOT/rag" && exec "$PY" service.py --db survival.db --port 8090 ) &
PIDS+=($!)

# Esperar a que el servicio RAG responda.
for _ in $(seq 1 40); do
  if curl -sf http://127.0.0.1:8090/health >/dev/null 2>&1; then break; fi
  sleep 0.5
done

echo "[run] iniciando API en :8080 (Ctrl-C para salir) ..."
cd "$ROOT/api"
SM_RAG_URL="http://127.0.0.1:8090" \
SM_MESH_URL="http://127.0.0.1:8091" \
SM_NOSTR_URL="http://127.0.0.1:8092" \
  exec cargo run --release
