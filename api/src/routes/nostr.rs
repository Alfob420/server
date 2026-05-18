use axum::extract::{Query, State};
use axum::http::StatusCode;
use axum::Json;
use serde::{Deserialize, Serialize};

use crate::nostr::{NostrMessage, NostrStatus};
use crate::state::AppState;

type ApiError = (StatusCode, String);

fn gateway_error(err: anyhow::Error) -> ApiError {
    (StatusCode::BAD_GATEWAY, format!("gateway Nostr: {err}"))
}

/// `GET /api/nostr/status` — estado del gateway Nostr.
pub async fn status(State(state): State<AppState>) -> Result<Json<NostrStatus>, ApiError> {
    state.nostr.status().await.map(Json).map_err(gateway_error)
}

#[derive(Deserialize)]
pub struct InboxQuery {
    #[serde(default)]
    since: u64,
}

/// `GET /api/nostr/inbox` — mensajes recibidos por Nostr (opcional `?since=<id>`).
pub async fn inbox(
    State(state): State<AppState>,
    Query(query): Query<InboxQuery>,
) -> Result<Json<Vec<NostrMessage>>, ApiError> {
    state
        .nostr
        .inbox(query.since)
        .await
        .map(Json)
        .map_err(gateway_error)
}

#[derive(Deserialize)]
pub struct SendRequest {
    pub to: String,
    pub text: String,
}

#[derive(Serialize)]
pub struct SendResponse {
    status: &'static str,
}

/// `POST /api/nostr/send` — envía un mensaje directo cifrado por Nostr.
pub async fn send(
    State(state): State<AppState>,
    Json(req): Json<SendRequest>,
) -> Result<Json<SendResponse>, ApiError> {
    let to = req.to.trim();
    if to.is_empty() {
        return Err((StatusCode::BAD_REQUEST, "falta la clave pública de destino".into()));
    }
    if req.text.trim().is_empty() {
        return Err((StatusCode::BAD_REQUEST, "el mensaje está vacío".into()));
    }

    state
        .nostr
        .send(to, req.text.trim())
        .await
        .map_err(gateway_error)?;
    Ok(Json(SendResponse { status: "sent" }))
}
