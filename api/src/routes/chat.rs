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
    /// Documentos del corpus usados como contexto (puede venir vacío si el
    /// servicio RAG no está disponible).
    pub sources: Vec<String>,
}

/// `POST /api/chat` — flujo RAG completo: recupera contexto del corpus de
/// supervivencia y se lo pasa al motor LLM.
pub async fn chat(
    State(state): State<AppState>,
    Json(req): Json<ChatRequest>,
) -> Result<Json<ChatResponse>, (StatusCode, String)> {
    let message = req.message.trim();
    if message.is_empty() {
        return Err((StatusCode::BAD_REQUEST, "el mensaje está vacío".into()));
    }

    // Recuperación RAG. Si el servicio no está disponible se degrada con
    // elegancia: el LLM responde sin contexto en vez de fallar.
    let hits = match state.rag.retrieve(message, state.rag_top_k).await {
        Ok(hits) => {
            for hit in &hits {
                tracing::debug!(doc = %hit.doc, distance = hit.distance, "RAG hit");
            }
            hits
        }
        Err(err) => {
            tracing::warn!(%err, "servicio RAG no disponible — respondiendo sin contexto");
            Vec::new()
        }
    };

    let reply = state
        .llm
        .chat(message, &hits)
        .await
        .map_err(|err| (StatusCode::BAD_GATEWAY, format!("motor LLM: {err}")))?;

    // Fuentes únicas, preservando el orden de relevancia.
    let mut sources: Vec<String> = Vec::new();
    for hit in &hits {
        if !sources.contains(&hit.doc) {
            sources.push(hit.doc.clone());
        }
    }

    Ok(Json(ChatResponse {
        reply: reply.text,
        model: reply.model,
        sources,
    }))
}
