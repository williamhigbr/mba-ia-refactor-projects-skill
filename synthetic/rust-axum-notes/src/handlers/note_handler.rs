use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use std::sync::Arc;

use crate::domain::note::{CreateNote, SearchQuery};
use crate::error::AppError;
use crate::services::note_service::NoteService;
use crate::state::AppState;

pub async fn list_notes(
    State(state): State<Arc<AppState>>,
) -> Result<impl IntoResponse, AppError> {
    let notes = NoteService::list(&state.pool).await?;
    Ok(Json(notes))
}

pub async fn search_notes(
    State(state): State<Arc<AppState>>,
    Query(q): Query<SearchQuery>,
) -> Result<impl IntoResponse, AppError> {
    let notes = NoteService::search(&state.pool, &q.q).await?;
    Ok(Json(notes))
}

pub async fn create_note(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<CreateNote>,
) -> Result<impl IntoResponse, AppError> {
    NoteService::create(&state.pool, payload).await?;
    Ok(StatusCode::CREATED)
}

pub async fn delete_note(
    State(state): State<Arc<AppState>>,
    Path(id): Path<i64>,
) -> Result<impl IntoResponse, AppError> {
    NoteService::delete(&state.pool, id).await?;
    Ok(StatusCode::NO_CONTENT)
}
