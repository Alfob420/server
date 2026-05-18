//! Capa de inteligencia (Capa 3): abstracción del motor LLM.
//!
//! Las rutas dependen del trait [`LlmEngine`], no de una implementación
//! concreta. Implementaciones:
//!
//! - [`StubEngine`] — respuestas simuladas, sin inferencia. Default.
//! - [`LlamaServerEngine`] — cliente de un `llama-server` (llama.cpp) con API
//!   compatible OpenAI. Se activa definiendo `SM_LLM_URL`.

mod llama_server;
mod stub;

pub use llama_server::LlamaServerEngine;
pub use stub::StubEngine;

use async_trait::async_trait;

use crate::rag::RagHit;

/// Instrucción de sistema compartida por todos los motores. Acota el rol del
/// asistente e incluye el disclaimer educativo (mitigación de riesgo del
/// Documento 1: "LLM dice algo peligroso").
pub const SYSTEM_PROMPT: &str = "Sos el asistente de Survival Mesh, un \
dispositivo de supervivencia que funciona sin internet. Respondé en español, \
de forma concisa, práctica y ordenada. Cuando se te provea CONTEXTO del corpus \
de supervivencia, basá la respuesta en ese material. Esta información es \
educativa y no reemplaza el criterio de un profesional médico o de rescate.";

/// Respuesta del motor LLM.
#[derive(Debug, Clone)]
pub struct ChatReply {
    /// Texto generado.
    pub text: String,
    /// Identificador del modelo que produjo la respuesta.
    pub model: String,
}

/// Motor de inferencia.
#[async_trait]
pub trait LlmEngine: Send + Sync {
    /// Procesa la consulta del usuario con el contexto recuperado del RAG.
    async fn chat(&self, message: &str, context: &[RagHit]) -> anyhow::Result<ChatReply>;

    /// Nombre del modelo activo, para diagnóstico.
    fn name(&self) -> &str;
}

/// Arma el bloque de CONTEXTO que se antepone a la pregunta del usuario.
/// Devuelve cadena vacía si no hay fragmentos recuperados.
pub fn build_context_block(context: &[RagHit]) -> String {
    if context.is_empty() {
        return String::new();
    }
    let mut block = String::from("CONTEXTO del corpus de supervivencia:\n");
    for (i, hit) in context.iter().enumerate() {
        block.push_str(&format!("\n[{}] fuente: {}\n{}\n", i + 1, hit.doc, hit.text));
    }
    block
}
