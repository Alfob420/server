use std::sync::Arc;
use std::time::Instant;

use crate::config::Config;
use crate::llm::{LlmEngine, StubEngine};

/// Estado compartido entre todos los handlers. Es barato de clonar: los campos
/// son `Arc` o `Copy`.
#[derive(Clone)]
pub struct AppState {
    pub started_at: Instant,
    pub llm: Arc<dyn LlmEngine>,
}

impl AppState {
    pub fn new(_config: &Config) -> Self {
        Self {
            started_at: Instant::now(),
            llm: Arc::new(StubEngine::new()),
        }
    }
}
