use axum::extract::{Query, State};
use axum::http::StatusCode;
use axum::Json;
use serde::{Deserialize, Serialize};

use crate::mesh::{MeshMessage, MeshPeer, MeshStatus};
use crate::state::AppState;

type ApiError = (StatusCode, String);

fn gateway_error(err: anyhow::Error) -> ApiError {
    (StatusCode::BAD_GATEWAY, format!("servicio mesh: {err}"))
}

/// `GET /api/mesh/status` — estado del nodo mesh local.
pub async fn status(State(state): State<AppState>) -> Result<Json<MeshStatus>, ApiError> {
    state.mesh.status().await.map(Json).map_err(gateway_error)
}

/// `GET /api/mesh/peers` — nodos descubiertos en la mesh.
pub async fn peers(State(state): State<AppState>) -> Result<Json<Vec<MeshPeer>>, ApiError> {
    state.mesh.peers().await.map(Json).map_err(gateway_error)
}

#[derive(Deserialize)]
pub struct InboxQuery {
    #[serde(default)]
    since: u64,
}

/// `GET /api/mesh/inbox` — mensajes recibidos (opcional `?since=<id>`).
pub async fn inbox(
    State(state): State<AppState>,
    Query(query): Query<InboxQuery>,
) -> Result<Json<Vec<MeshMessage>>, ApiError> {
    state
        .mesh
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

/// `POST /api/mesh/send` — envía un mensaje de texto a otro nodo.
pub async fn send(
    State(state): State<AppState>,
    Json(req): Json<SendRequest>,
) -> Result<Json<SendResponse>, ApiError> {
    let to = req.to.trim();
    if to.is_empty() {
        return Err((StatusCode::BAD_REQUEST, "falta la dirección de destino".into()));
    }
    if req.text.trim().is_empty() {
        return Err((StatusCode::BAD_REQUEST, "el mensaje está vacío".into()));
    }

    state
        .mesh
        .send(to, req.text.trim())
        .await
        .map_err(gateway_error)?;
    Ok(Json(SendResponse { status: "sent" }))
}
