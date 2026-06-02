use sqlx::SqlitePool;

use crate::error::AppError;

pub struct UserRepo;

impl UserRepo {
    pub async fn find_by_credentials(pool: &SqlitePool, email: &str, password: &str) -> Result<Option<i64>, AppError> {
        let row: Option<(i64,)> = sqlx::query_as("SELECT id FROM users WHERE email = $1 AND password = $2")
            .bind(email)
            .bind(password)
            .fetch_optional(pool)
            .await?;
        Ok(row.map(|(id,)| id))
    }

    pub async fn delete_all(pool: &SqlitePool) -> Result<(), AppError> {
        sqlx::query("DELETE FROM users").execute(pool).await?;
        Ok(())
    }
}
