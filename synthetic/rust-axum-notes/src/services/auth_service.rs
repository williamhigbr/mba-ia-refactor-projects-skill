use sqlx::SqlitePool;

use crate::error::AppError;
use crate::repository::user_repo::UserRepo;

pub struct AuthService;

impl AuthService {
    pub async fn login(pool: &SqlitePool, secret_key: &str, email: &str, password: &str) -> Result<String, AppError> {
        if email.is_empty() || password.is_empty() {
            return Err(AppError::BadRequest("email and password are required".into()));
        }
        let user_id = UserRepo::find_by_credentials(pool, email, password)
            .await?
            .ok_or(AppError::Unauthorized)?;
        let token = format!("{secret_key}-uid-{user_id}");
        Ok(token)
    }
}
