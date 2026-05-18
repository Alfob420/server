//! Definición del router HTTP (Capa 4).

mod chat;
mod health;

use axum::routing::{get, post};
use axum::Router;

use crate::state::AppState;

/// Construye el router con las rutas de la API. Las rutas estáticas de la PWA
/// se montan como `fallback_service` en `main`.
pub fn router(state: AppState) -> Router {
    Router::new()
        .route("/api/health", get(health::health))
        .route("/api/chat", post(chat::chat))
        .with_state(state)
}
