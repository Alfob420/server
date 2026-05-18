use axum::extract::State;
use axum::http::StatusCode;
use axum::Json;
use serde::{Deserialize, Serialize};

use crate::state::AppState;

#[derive(Deserialize)]
pub struct ChatRequest {
    pub message: String,
}

#[derive(Serialize)]
pub struct ChatResponse {
    pub reply: String,
    pub model: String,
    pub sources: Vec<String>,
}

/// `POST /api/chat` — envía un mensaje al motor LLM.
pub async fn chat(
    State(state): State<AppState>,
    Json(req): Json<ChatRequest>,
) -> Result<Json<ChatResponse>, (StatusCode, String)> {
    let message = req.message.trim();
    if message.is_empty() {
        return Err((StatusCode::BAD_REQUEST, "el mensaje está vacío".into()));
    }

    let reply = state.llm.chat(message).await;
    Ok(Json(ChatResponse {
        reply: reply.text,
        model: reply.model,
        sources: reply.sources,
    }))
}
