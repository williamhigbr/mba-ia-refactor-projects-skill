mod config;
mod domain;
mod error;
mod handlers;
mod middleware;
mod repository;
mod routes;
mod services;
mod state;

use std::sync::Arc;

use crate::config::Config;
use crate::routes::build_router;
use crate::state::AppState;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let config = Config::from_env();
    let state = Arc::new(AppState::new(&config).await);

    // Run migrations
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, author TEXT)"
    )
    .execute(&state.pool)
    .await
    .expect("Failed to create notes table");

    sqlx::query(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT)"
    )
    .execute(&state.pool)
    .await
    .expect("Failed to create users table");

    let app = build_router(state);
    let addr = config.addr();

    tracing::info!("Listening on {addr}");
    let listener = tokio::net::TcpListener::bind(&addr).await.expect("Failed to bind");
    axum::serve(listener, app).await.expect("Server error");
}
