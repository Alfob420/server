use std::path::PathBuf;

/// Configuración del servidor, leída del entorno al arrancar.
#[derive(Clone, Debug)]
pub struct Config {
    pub port: u16,
    pub pwa_dir: PathBuf,
    pub model_path: Option<PathBuf>,
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

        let model_path = std::env::var("SM_MODEL_PATH")
            .ok()
            .filter(|s| !s.is_empty())
            .map(PathBuf::from);

        Self { port, pwa_dir, model_path }
    }
}
