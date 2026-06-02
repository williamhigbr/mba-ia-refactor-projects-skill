use std::env;

pub struct Config {
    pub database_url: String,
    pub secret_key: String,
    pub admin_token: String,
    pub host: String,
    pub port: u16,
}

impl Config {
    pub fn from_env() -> Self {
        dotenvy::dotenv().ok();
        Self {
            database_url: env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite::memory:".into()),
            secret_key: env::var("SECRET_KEY").expect("SECRET_KEY must be set"),
            admin_token: env::var("ADMIN_TOKEN").expect("ADMIN_TOKEN must be set"),
            host: env::var("HOST").unwrap_or_else(|_| "0.0.0.0".into()),
            port: env::var("PORT").unwrap_or_else(|_| "3000".into()).parse().expect("PORT must be a number"),
        }
    }

    pub fn addr(&self) -> String {
        format!("{}:{}", self.host, self.port)
    }
}
