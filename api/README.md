# api/ — Servidor API local (Capa 4)

Servidor HTTP en Rust/Axum que corre en el dispositivo. Orquesta el motor LLM
(Capa 3), expone una API local y sirve la PWA (`../pwa`).

## Correr

```sh
cargo run
```

Por defecto escucha en `0.0.0.0:8080` y sirve la PWA desde `../pwa`.

## Variables de entorno

| Variable        | Default     | Descripción                              |
|-----------------|-------------|------------------------------------------|
| `SM_PORT`       | `8080`      | Puerto HTTP.                             |
| `SM_PWA_DIR`    | `../pwa`    | Carpeta de la PWA a servir como estática. |
| `SM_MODEL_PATH` | *(vacío)*   | Ruta al modelo GGUF (aún no usada).      |
| `RUST_LOG`      | `info`      | Nivel de logging (`tracing`).            |

## Endpoints

| Método | Ruta          | Descripción                                  |
|--------|---------------|----------------------------------------------|
| GET    | `/api/health` | Estado del servidor, uptime y motor LLM.     |
| POST   | `/api/chat`   | Envía un mensaje al LLM. Body: `{"message": "..."}`. |
| GET    | `/*`          | Archivos estáticos de la PWA.                |

### Ejemplo

```sh
curl localhost:8080/api/health
curl -X POST localhost:8080/api/chat \
  -H 'content-type: application/json' \
  -d '{"message":"¿cómo purifico agua?"}'
```

## Motor LLM

Hoy el motor es `StubEngine` (`src/llm/stub.rs`): devuelve respuestas
simuladas. La integración real con llama.cpp + Qwen 2.5 3B y el corpus RAG se
hará detrás del trait `LlmEngine` (`src/llm/mod.rs`) sin tocar las rutas.
