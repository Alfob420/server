use std::time::Duration;

use async_trait::async_trait;
use serde::Deserialize;

use super::{build_context_block, ChatReply, LlmEngine, SYSTEM_PROMPT};
use crate::rag::RagHit;

/// Motor LLM que delega la inferencia a un `llama-server` (llama.cpp) vía su
/// API compatible con OpenAI (`POST /v1/chat/completions`).
///
/// En el dispositivo, `llama-server` corre como un proceso aparte cargando el
/// modelo GGUF (Qwen 2.5 3B). La API solo necesita su URL (`SM_LLM_URL`).
pub struct LlamaServerEngine {
    http: reqwest::Client,
    base_url: String,
    model: String,
}

impl LlamaServerEngine {
    pub fn new(base_url: String, model: String) -> Self {
        let http = reqwest::Client::builder()
            .timeout(Duration::from_secs(120))
            .build()
            .expect("construir cliente HTTP");
        Self {
            http,
            base_url: base_url.trim_end_matches('/').to_string(),
            model,
        }
    }
}

#[derive(Deserialize)]
struct CompletionResponse {
    choices: Vec<Choice>,
}

#[derive(Deserialize)]
struct Choice {
    message: Message,
}

#[derive(Deserialize)]
struct Message {
    content: String,
}

#[async_trait]
impl LlmEngine for LlamaServerEngine {
    async fn chat(&self, message: &str, context: &[RagHit]) -> anyhow::Result<ChatReply> {
        let context_block = build_context_block(context);
        let user_content = if context_block.is_empty() {
            format!("Pregunta: {message}")
        } else {
            format!("{context_block}\nPregunta: {message}")
        };

        let body = serde_json::json!({
            "model": self.model,
            "messages": [
                { "role": "system", "content": SYSTEM_PROMPT },
                { "role": "user", "content": user_content },
            ],
            "temperature": 0.4,
            "stream": false,
        });

        let resp = self
            .http
            .post(format!("{}/v1/chat/completions", self.base_url))
            .json(&body)
            .send()
            .await?
            .error_for_status()?;

        let parsed: CompletionResponse = resp.json().await?;
        let text = parsed
            .choices
            .into_iter()
            .next()
            .map(|c| c.message.content)
            .ok_or_else(|| anyhow::anyhow!("respuesta sin choices del servidor LLM"))?;

        Ok(ChatReply { text: text.trim().to_string(), model: self.model.clone() })
    }

    fn name(&self) -> &str {
        &self.model
    }
}
