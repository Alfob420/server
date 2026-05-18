//! Cliente del servicio RAG (Capa 3).
//!
//! El servicio vive en `../rag/service.py` y mantiene el modelo de embeddings y
//! el índice cargados. La API lo consulta por HTTP para recuperar fragmentos
//! del corpus de supervivencia relevantes a la consulta del usuario.

use std::time::Duration;

use serde::Deserialize;

/// Un fragmento del corpus recuperado por el RAG.
#[derive(Debug, Clone, Deserialize)]
pub struct RagHit {
    pub doc: String,
    pub text: String,
    #[serde(default)]
    pub distance: f32,
}

#[derive(Deserialize)]
struct RetrieveResponse {
    #[serde(default)]
    hits: Vec<RagHit>,
}

/// Cliente HTTP del servicio RAG.
#[derive(Clone)]
pub struct RagClient {
    http: reqwest::Client,
    base_url: String,
}

impl RagClient {
    pub fn new(base_url: String) -> Self {
        let http = reqwest::Client::builder()
            .timeout(Duration::from_secs(10))
            .build()
            .expect("construir cliente HTTP");
        Self {
            http,
            base_url: base_url.trim_end_matches('/').to_string(),
        }
    }

    /// Recupera hasta `k` fragmentos relevantes a `query`.
    pub async fn retrieve(&self, query: &str, k: u32) -> anyhow::Result<Vec<RagHit>> {
        let body = serde_json::json!({ "query": query, "k": k });
        let resp = self
            .http
            .post(format!("{}/retrieve", self.base_url))
            .json(&body)
            .send()
            .await?
            .error_for_status()?;
        let parsed: RetrieveResponse = resp.json().await?;
        Ok(parsed.hits)
    }
}
