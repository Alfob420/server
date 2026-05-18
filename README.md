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
| `docs/`        | —    | Arquitectura técnica y roadmap.                          |
| `scripts/`     | —    | Scripts de setup y aprovisionamiento.                    |

## Estado actual

Este es el **scaffold inicial**. Lo que ya funciona y lo que es stub:

- ✅ `api/` — servidor Axum que compila y corre, con endpoints `/api/health`
  y `/api/chat`. El motor LLM es un **stub** (`StubEngine`) que aún no invoca
  llama.cpp.
- ✅ `pwa/` — interfaz de chat mínima que consume la API local.
- 🚧 `rag/`, `mesh/`, `transport/` — READMEs y stubs documentados, sin
  implementación todavía.

## Arranque rápido

```sh
# 1. Levantar el servidor API (sirve también la PWA)
cd api
cargo run

# 2. Abrir la PWA
#    http://localhost:8080
```

## Licencias

Software bajo licencias permisivas compatibles con uso comercial (MIT /
Apache 2.0). Hardware propio bajo CERN-OHL-v2. Ver
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#6-licencias-y-consideraciones-legales).
