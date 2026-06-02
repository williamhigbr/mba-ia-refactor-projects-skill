use axum::{extract::State, response::IntoResponse, Json};
use serde_json::json;
use std::sync::Arc;

use crate::error::AppError;
use crate::repository::note_repo::NoteRepo;
use crate::repository::user_repo::UserRepo;
use crate::state::AppState;

pub async fn admin_reset(
    State(state): State<Arc<AppState>>,
) -> Result<impl IntoResponse, AppError> {
    NoteRepo::delete_all(&state.pool).await?;
    UserRepo::delete_all(&state.pool).await?;
    Ok(Json(json!({ "reset": true })))
}
