use std::sync::Arc;
use std::time::Instant;

use crate::config::Config;
use crate::llm::{LlamaServerEngine, LlmEngine, StubEngine};
use crate::mesh::MeshClient;
use crate::nostr::NostrClient;
use crate::rag::RagClient;

/// Estado compartido entre todos los handlers. Es barato de clonar: los campos
/// son `Arc` o `Copy`.
#[derive(Clone)]
pub struct AppState {
    pub started_at: Instant,
    pub llm: Arc<dyn LlmEngine>,
    pub rag: Arc<RagClient>,
    pub rag_top_k: u32,
    pub mesh: Arc<MeshClient>,
    pub nostr: Arc<NostrClient>,
}

impl AppState {
    pub fn new(config: &Config) -> Self {
        let llm: Arc<dyn LlmEngine> = match &config.llm_url {
            Some(url) => {
                tracing::info!(%url, "motor LLM: llama-server");
                Arc::new(LlamaServerEngine::new(url.clone(), config.llm_model.clone()))
            }
            None => {
                tracing::warn!("SM_LLM_URL no definido — usando motor LLM stub");
                Arc::new(StubEngine::new())
            }
        };

        Self {
            started_at: Instant::now(),
            llm,
            rag: Arc::new(RagClient::new(config.rag_url.clone())),
            rag_top_k: config.rag_top_k,
            mesh: Arc::new(MeshClient::new(config.mesh_url.clone())),
            nostr: Arc::new(NostrClient::new(config.nostr_url.clone())),
        }
    }
}
