//! Definición del router HTTP (Capa 4).

mod chat;
mod health;
mod mesh;

use axum::routing::{get, post};
use axum::Router;

use crate::state::AppState;

/// Construye el router con las rutas de la API. Las rutas estáticas de la PWA
/// se montan como `fallback_service` en `main`.
pub fn router(state: AppState) -> Router {
    Router::new()
        .route("/api/health", get(health::health))
        .route("/api/chat", post(chat::chat))
        .route("/api/mesh/status", get(mesh::status))
        .route("/api/mesh/peers", get(mesh::peers))
        .route("/api/mesh/inbox", get(mesh::inbox))
        .route("/api/mesh/send", post(mesh::send))
        .with_state(state)
}
