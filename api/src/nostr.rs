//! Cliente del gateway Nostr (transporte global).
//!
//! El servicio vive en `../nostr/service.py` y mantiene un gateway Nostr vivo
//! (identidad, conexión a relays públicos, buzón). La API lo consulta por HTTP
//! para dar alcance global cuando el dispositivo tiene internet.

use std::time::Duration;

use serde::{Deserialize, Serialize};

/// Estado de la conexión a un relay Nostr.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NostrRelay {
    pub url: String,
    pub connected: bool,
}

/// Estado del gateway Nostr local.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NostrStatus {
    pub status: String,
    /// Clave pública Nostr del nodo (su dirección global, hex x-only).
    pub pubkey: String,
    pub name: String,
    pub relays: Vec<NostrRelay>,
    pub relays_connected: u32,
    pub inbox: u32,
}

/// Un mensaje recibido por Nostr.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NostrMessage {
    pub id: u64,
    pub from: String,
    pub text: String,
    pub ts: i64,
}

#[derive(Deserialize)]
struct InboxResponse {
    #[serde(default)]
    messages: Vec<NostrMessage>,
}

#[derive(Deserialize)]
struct ErrorBody {
    error: String,
}

/// Cliente HTTP del gateway Nostr.
#[derive(Clone)]
pub struct NostrClient {
    http: reqwest::Client,
    base_url: String,
}

impl NostrClient {
    pub fn new(base_url: String) -> Self {
        let http = reqwest::Client::builder()
            .timeout(Duration::from_secs(20))
            .build()
            .expect("construir cliente HTTP");
        Self {
            http,
            base_url: base_url.trim_end_matches('/').to_string(),
        }
    }

    /// Estado del gateway Nostr local.
    pub async fn status(&self) -> anyhow::Result<NostrStatus> {
        let status = self
            .http
            .get(format!("{}/health", self.base_url))
            .send()
            .await?
            .error_for_status()?
            .json()
            .await?;
        Ok(status)
    }

    /// Mensajes recibidos con `id` mayor a `since`.
    pub async fn inbox(&self, since: u64) -> anyhow::Result<Vec<NostrMessage>> {
        let resp: InboxResponse = self
            .http
            .get(format!("{}/inbox", self.base_url))
            .query(&[("since", since)])
            .send()
            .await?
            .error_for_status()?
            .json()
            .await?;
        Ok(resp.messages)
    }

    /// Envía un mensaje directo cifrado a una clave pública Nostr.
    pub async fn send(&self, to: &str, text: &str) -> anyhow::Result<()> {
        let resp = self
            .http
            .post(format!("{}/send", self.base_url))
            .json(&serde_json::json!({ "to": to, "text": text }))
            .send()
            .await?;

        if resp.status().is_success() {
            return Ok(());
        }
        let status = resp.status();
        let detail = resp
            .json::<ErrorBody>()
            .await
            .map(|e| e.error)
            .unwrap_or_else(|_| status.to_string());
        anyhow::bail!("{detail}")
    }
}
