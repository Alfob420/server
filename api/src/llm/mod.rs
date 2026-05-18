//! Capa de inteligencia (Capa 3): abstracción del motor LLM.
//!
//! Las rutas dependen del trait [`LlmEngine`], no de una implementación
//! concreta. Hoy se usa [`StubEngine`]; la integración real con
//! llama.cpp + Qwen 2.5 3B + RAG se enchufará detrás del mismo trait.

mod stub;

pub use stub::StubEngine;

use async_trait::async_trait;

/// Respuesta del motor LLM a una consulta.
#[derive(Debug, Clone)]
pub struct ChatReply {
    /// Texto generado.
    pub text: String,
    /// Identificador del modelo que produjo la respuesta.
    pub model: String,
    /// Documentos del corpus RAG citados (vacío mientras no haya RAG).
    pub sources: Vec<String>,
}

/// Motor de inferencia. Implementaciones futuras: `LlamaCppEngine`.
#[async_trait]
pub trait LlmEngine: Send + Sync {
    /// Procesa un mensaje del usuario y devuelve la respuesta.
    async fn chat(&self, prompt: &str) -> ChatReply;

    /// Nombre del modelo activo, para diagnóstico.
    fn name(&self) -> &str;
}
