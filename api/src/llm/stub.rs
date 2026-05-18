use async_trait::async_trait;

use super::{ChatReply, LlmEngine};
use crate::rag::RagHit;

/// Motor LLM simulado. No invoca inferencia real: confirma que la consulta y la
/// recuperación RAG funcionan, sin necesidad de un `llama-server`. Para
/// respuestas reales, definí `SM_LLM_URL` (ver [`super::LlamaServerEngine`]).
pub struct StubEngine {
    model: String,
}

impl StubEngine {
    pub fn new() -> Self {
        Self { model: "stub-echo-0".to_string() }
    }
}

impl Default for StubEngine {
    fn default() -> Self {
        Self::new()
    }
}

#[async_trait]
impl LlmEngine for StubEngine {
    async fn chat(&self, message: &str, context: &[RagHit]) -> anyhow::Result<ChatReply> {
        let text = if context.is_empty() {
            format!(
                "[STUB LLM] Consulta recibida: \"{message}\". No se recuperó \
                 contexto del corpus (el servicio RAG puede estar apagado o el \
                 índice vacío). Definí SM_LLM_URL para conectar un modelo real."
            )
        } else {
            let docs: Vec<&str> = context.iter().map(|h| h.doc.as_str()).collect();
            format!(
                "[STUB LLM] Consulta recibida: \"{message}\". Se recuperaron {} \
                 fragmentos del corpus de supervivencia ({}). El motor de \
                 inferencia real (llama.cpp + Qwen 2.5) generaría aquí la \
                 respuesta usando ese contexto. Definí SM_LLM_URL para activarlo.",
                context.len(),
                docs.join(", "),
            )
        };

        Ok(ChatReply { text, model: self.model.clone() })
    }

    fn name(&self) -> &str {
        &self.model
    }
}
