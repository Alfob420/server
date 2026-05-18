//! Survival Mesh — servidor API local (Capa 4).

mod config;
mod llm;
mod routes;
mod state;

use std::net::SocketAddr;

use tower_http::cors::CorsLayer;
use tower_http::services::ServeDir;
use tower_http::trace::TraceLayer;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::EnvFilter;

use crate::config::Config;
use crate::state::AppState;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(EnvFilter::try_from_default_env().unwrap_or_else(|_| {
            "survival_mesh_api=debug,tower_http=info,info".into()
        }))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let config = Config::from_env();
    let state = AppState::new(&config);

    tracing::info!(?config, "configuración cargada");
    if config.model_path.is_none() {
        tracing::warn!("SM_MODEL_PATH no definido — usando motor LLM stub");
    }

    let app = routes::router(state)
        .fallback_service(ServeDir::new(&config.pwa_dir))
        .layer(CorsLayer::permissive())
        .layer(TraceLayer::new_for_http());

    let addr = SocketAddr::from(([0, 0, 0, 0], config.port));
    let listener = tokio::net::TcpListener::bind(addr).await?;
    tracing::info!("Survival Mesh API escuchando en http://{addr}");

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    Ok(())
}

async fn shutdown_signal() {
    let _ = tokio::signal::ctrl_c().await;
    tracing::info!("señal de apagado recibida, cerrando");
}
