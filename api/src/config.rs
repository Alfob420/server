use std::path::PathBuf;

/// Configuración del servidor, leída del entorno al arrancar.
#[derive(Clone, Debug)]
pub struct Config {
    pub port: u16,
    pub pwa_dir: PathBuf,
    /// URL del servicio RAG (`../rag/service.py`).
    pub rag_url: String,
    /// Cantidad de fragmentos a recuperar del RAG por consulta.
    pub rag_top_k: u32,
    /// URL del servicio mesh (`../mesh/service.py`).
    pub mesh_url: String,
    /// URL de un servidor llama.cpp (`llama-server`). Si está vacío, se usa el
    /// motor LLM stub.
    pub llm_url: Option<String>,
    /// Nombre de modelo a enviar al servidor llama.cpp.
    pub llm_model: String,
}

fn env_or(key: &str, default: &str) -> String {
    std::env::var(key).ok().filter(|s| !s.is_empty()).unwrap_or_else(|| default.to_string())
}

impl Config {
    pub fn from_env() -> Self {
        let port = std::env::var("SM_PORT")
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or(8080);

        let pwa_dir = std::env::var("SM_PWA_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(|_| PathBuf::from("../pwa"));

        let rag_top_k = std::env::var("SM_RAG_TOP_K")
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or(4);

        let llm_url = std::env::var("SM_LLM_URL").ok().filter(|s| !s.is_empty());

        Self {
            port,
            pwa_dir,
            rag_url: env_or("SM_RAG_URL", "http://127.0.0.1:8090"),
            rag_top_k,
            mesh_url: env_or("SM_MESH_URL", "http://127.0.0.1:8091"),
            llm_url,
            llm_model: env_or("SM_LLM_MODEL", "qwen2.5-3b-instruct"),
        }
    }
}
