use axum::{
    extract::State,
    response::IntoResponse,
    Json,
};
use serde_json::json;
use std::sync::Arc;

use crate::domain::user::LoginRequest;
use crate::error::AppError;
use crate::services::auth_service::AuthService;
use crate::state::AppState;

pub async fn login(
    State(state): State<Arc<AppState>>,
    Json(body): Json<LoginRequest>,
) -> Result<impl IntoResponse, AppError> {
    let token = AuthService::login(&state.pool, &state.secret_key, &body.email, &body.password).await?;
    Ok(Json(json!({ "token": token })))
}
