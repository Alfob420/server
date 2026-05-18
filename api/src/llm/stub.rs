use async_trait::async_trait;

use super::{ChatReply, LlmEngine};

/// Motor LLM simulado. No invoca inferencia real: devuelve una respuesta fija
/// que confirma que la consulta llegó. Permite desarrollar la API y la PWA sin
/// compilar llama.cpp ni descargar el modelo de ~2 GB.
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
    async fn chat(&self, prompt: &str) -> ChatReply {
        let text = format!(
            "[STUB LLM] Recibí tu consulta: \"{prompt}\". El motor de \
             inferencia real (llama.cpp + Qwen 2.5 3B) todavía no está \
             conectado. Cuando lo esté, esta respuesta vendrá del modelo \
             local con contexto del corpus RAG de supervivencia."
        );

        ChatReply {
            text,
            model: self.model.clone(),
            sources: Vec::new(),
        }
    }

    fn name(&self) -> &str {
        &self.model
    }
}
