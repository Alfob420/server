# pwa/ — Interfaz web (Capa 4)

PWA cyberpunk que el dispositivo sirve desde su hotspot. Es estática (HTML/CSS/
JS vanilla, sin build) y consume la API local de `../api`.

## Servir

El servidor Rust (`../api`) sirve esta carpeta automáticamente como
`fallback_service`. Levantá `cargo run` en `../api` y abrí
`http://localhost:8080`.

Para iterar solo el frontend también sirve cualquier servidor estático:

```sh
python3 -m http.server 5173
```

(en ese modo las llamadas a `/api/*` fallan salvo que el servidor Rust corra
en paralelo y se ajuste la URL base).

## Archivos

| Archivo               | Rol                                       |
|-----------------------|-------------------------------------------|
| `index.html`          | Estructura de la terminal de chat.        |
| `styles.css`          | Tema cyberpunk (neón sobre fondo oscuro). |
| `app.js`              | Lógica: polling de `/api/health`, envío a `/api/chat`. |
| `manifest.webmanifest`| Metadatos PWA (instalable).               |

## Pendiente

- Service worker para cache offline real.
- Íconos de la app.
- Vista de estado de la mesh (nodos, transportes activos).
