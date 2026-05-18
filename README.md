# Survival Mesh

Dispositivo de bolsillo de código abierto que combina **LLM offline**,
**comunicación mesh descentralizada multi-transporte** y **autonomía total**
sin depender de internet, antenas celulares ni servidores.

> El hardware se vende ensamblado y como kit DIY. El software es 100% open
> source. Ver [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) para el detalle.

## Estructura del monorepo

El proyecto está organizado en las 4 capas de la arquitectura, más carpetas
de hardware y documentación:

| Carpeta        | Capa | Descripción                                              |
|----------------|------|----------------------------------------------------------|
| `api/`         | 4    | Servidor API local en Rust/Axum. **Único componente funcional hoy.** |
| `pwa/`         | 4    | PWA cyberpunk servida desde el hotspot del dispositivo.  |
| `rag/`         | 3    | Pipeline RAG: ingesta de corpus + embeddings + SQLite-vec. |
| `mesh/`        | 2    | Integración Reticulum (RNS) y bridges a BitChat/Meshtastic. |
| `transport/`   | 1    | Configuración de transportes físicos (LoRa, BLE, WiFi, Nostr). |
| `hardware/`    | —    | BOM, tiers de hardware y notas de fabricación.           |
| `deploy/`      | —    | Unidades systemd para correr en el dispositivo.          |
| `docs/`        | —    | Arquitectura técnica y roadmap.                          |
| `scripts/`     | —    | Scripts de setup y arranque.                             |

## Estado actual

Lo que ya funciona y lo que sigue siendo stub:

- ✅ **Mesh (Capa 2)** — nodo de mensajería sobre Reticulum: identidad
  persistente, descubrimiento de nodos, envío/recepción de mensajes cifrados y
  servicio HTTP. Probado entre dos nodos sobre TCP.
- ✅ **Inteligencia (Capa 3)** — pipeline RAG funcional: ingesta de corpus,
  embeddings ONNX multilingües, índice SQLite-vec y servicio HTTP.
- ✅ **API (Capa 4)** — servidor Axum con flujo RAG + LLM y rutas de mesh.
  Motor `StubEngine` por defecto; `LlamaServerEngine` real activable con
  `SM_LLM_URL`.
- ✅ **PWA (Capa 4)** — interfaz con dos vistas: asistente (LLM + RAG) y mesh
  (mensajería).
- 🚧 **Transporte LoRa/BLE (Capa 1)** — Reticulum funciona sobre TCP hoy; el
  transporte LoRa (`RNodeInterface`) y los bridges BitChat/Meshtastic/Nostr
  requieren hardware físico.

## Arranque rápido

```sh
# 1. Setup: compila la API, prepara el RAG e indexa el corpus
scripts/setup.sh

# 2. Levantar servicio RAG + API + PWA
scripts/run-dev.sh

# 3. Abrir la PWA en http://localhost:8080
```

Para inferencia LLM real, correr un `llama-server` (llama.cpp) aparte y exportar
`SM_LLM_URL` — ver [`api/README.md`](api/README.md#motores-llm).

## Licencias

Software bajo licencias permisivas compatibles con uso comercial (MIT /
Apache 2.0). Hardware propio bajo CERN-OHL-v2. Ver
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#6-licencias-y-consideraciones-legales).
