use sqlx::sqlite::SqlitePool;

use crate::config::Config;

#[derive(Clone)]
pub struct AppState {
    pub pool: SqlitePool,
    pub secret_key: String,
    pub admin_token: String,
}

impl AppState {
    pub async fn new(config: &Config) -> Self {
        let pool = SqlitePool::connect(&config.database_url)
            .await
            .expect("Failed to connect to database");
        Self {
            pool,
            secret_key: config.secret_key.clone(),
            admin_token: config.admin_token.clone(),
        }
    }
}
