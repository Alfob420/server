# api/ — Servidor API local (Capa 4)

Servidor HTTP en Rust/Axum que corre en el dispositivo. Orquesta el flujo RAG +
LLM, expone una API local y sirve la PWA (`../pwa`).

## Correr

```sh
cargo run
```

Por defecto escucha en `0.0.0.0:8080` y sirve la PWA desde `../pwa`. Para el
flujo completo necesita el servicio RAG (`../rag/service.py`) y, opcionalmente,
un `llama-server`.

## Variables de entorno

| Variable        | Default                   | Descripción                                   |
|-----------------|---------------------------|-----------------------------------------------|
| `SM_PORT`       | `8080`                    | Puerto HTTP.                                  |
| `SM_PWA_DIR`    | `../pwa`                  | Carpeta de la PWA servida como estática.      |
| `SM_RAG_URL`    | `http://127.0.0.1:8090`   | URL del servicio RAG.                         |
| `SM_RAG_TOP_K`  | `4`                       | Fragmentos a recuperar por consulta.          |
| `SM_MESH_URL`   | `http://127.0.0.1:8091`   | URL del servicio mesh.                        |
| `SM_LLM_URL`    | *(vacío)*                 | URL de un `llama-server`. Vacío → motor stub. |
| `SM_LLM_MODEL`  | `qwen2.5-3b-instruct`     | Nombre de modelo enviado al `llama-server`.   |
| `RUST_LOG`      | `info`                    | Nivel de logging.                             |

## Endpoints

| Método | Ruta          | Descripción                                       |
|--------|---------------|---------------------------------------------------|
| GET    | `/api/health`       | Estado del servidor, uptime y motor LLM.       |
| POST   | `/api/chat`         | Flujo RAG + LLM. Body: `{"message": "..."}`.   |
| GET    | `/api/mesh/status`  | Estado del nodo mesh local.                    |
| GET    | `/api/mesh/peers`   | Nodos descubiertos en la mesh.                 |
| GET    | `/api/mesh/inbox`   | Mensajes recibidos (opcional `?since=<id>`).   |
| POST   | `/api/mesh/send`    | Envía un mensaje. Body: `{"to": "...", "text": "..."}`. |
| GET    | `/*`                | Archivos estáticos de la PWA.                  |

`POST /api/chat` recupera contexto del corpus vía el servicio RAG, se lo pasa
al motor LLM y devuelve `{reply, model, sources}`. Si el servicio RAG no está
disponible, responde igual pero sin contexto (degradación elegante).

### Ejemplo

```sh
curl -X POST localhost:8080/api/chat \
  -H 'content-type: application/json' \
  -d '{"message":"¿cómo purifico agua?"}'
```

## Motores LLM

Detrás del trait `LlmEngine` (`src/llm/mod.rs`):

- **`StubEngine`** (default) — respuestas simuladas; confirma que la API y el
  RAG funcionan sin necesidad de un modelo.
- **`LlamaServerEngine`** — cliente de un `llama-server` (llama.cpp) con API
  compatible OpenAI. Se activa definiendo `SM_LLM_URL`.

Para inferencia real, correr aparte:

```sh
llama-server -m qwen2.5-3b-instruct-q4_k_m.gguf --port 9001
# y arrancar la API con SM_LLM_URL=http://127.0.0.1:9001
```

## Estructura

```
src/
├── main.rs           arranque, router, capas tower-http
├── config.rs         configuración desde entorno
├── state.rs          estado compartido; selección de motor LLM
├── rag.rs            cliente HTTP del servicio RAG
├── mesh.rs           cliente HTTP del servicio mesh
├── llm/
│   ├── mod.rs        trait LlmEngine, system prompt, armado de contexto
│   ├── stub.rs       StubEngine
│   └── llama_server.rs  LlamaServerEngine
└── routes/
    ├── mod.rs        router
    ├── health.rs     GET /api/health
    ├── chat.rs       POST /api/chat (flujo RAG + LLM)
    └── mesh.rs       rutas /api/mesh/* (estado, peers, inbox, send)
```
