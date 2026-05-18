//! Cliente del servicio mesh (Capa 2).
//!
//! El servicio vive en `../mesh/service.py` y mantiene un nodo Reticulum vivo
//! (identidad, anuncios, buzón). La API lo consulta por HTTP para exponer el
//! estado de la mesh, los nodos descubiertos y la mensajería.

use std::time::Duration;

use serde::{Deserialize, Serialize};

/// Estado del nodo mesh local.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MeshStatus {
    pub status: String,
    /// Dirección (hash del destino) del nodo en la mesh.
    pub address: String,
    pub name: String,
    pub peers: u32,
    pub inbox: u32,
}

/// Un nodo descubierto en la mesh.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MeshPeer {
    pub address: String,
    pub name: String,
    pub last_seen: f64,
}

/// Un mensaje recibido por la mesh.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MeshMessage {
    pub id: u64,
    pub from: String,
    pub name: String,
    pub text: String,
    pub ts: f64,
}

#[derive(Deserialize)]
struct PeersResponse {
    #[serde(default)]
    peers: Vec<MeshPeer>,
}

#[derive(Deserialize)]
struct InboxResponse {
    #[serde(default)]
    messages: Vec<MeshMessage>,
}

#[derive(Deserialize)]
struct ErrorBody {
    error: String,
}

/// Cliente HTTP del servicio mesh.
#[derive(Clone)]
pub struct MeshClient {
    http: reqwest::Client,
    base_url: String,
}

impl MeshClient {
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

    /// Estado del nodo mesh local.
    pub async fn status(&self) -> anyhow::Result<MeshStatus> {
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

    /// Nodos descubiertos en la mesh.
    pub async fn peers(&self) -> anyhow::Result<Vec<MeshPeer>> {
        let resp: PeersResponse = self
            .http
            .get(format!("{}/peers", self.base_url))
            .send()
            .await?
            .error_for_status()?
            .json()
            .await?;
        Ok(resp.peers)
    }

    /// Mensajes recibidos con `id` mayor a `since`.
    pub async fn inbox(&self, since: u64) -> anyhow::Result<Vec<MeshMessage>> {
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

    /// Envía un mensaje de texto a otro nodo de la mesh.
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
