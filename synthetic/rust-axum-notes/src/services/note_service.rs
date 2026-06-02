use sqlx::SqlitePool;

use crate::domain::note::{CreateNote, Note};
use crate::error::AppError;
use crate::repository::note_repo::NoteRepo;

pub struct NoteService;

impl NoteService {
    pub async fn list(pool: &SqlitePool) -> Result<Vec<Note>, AppError> {
        NoteRepo::list(pool).await
    }

    pub async fn search(pool: &SqlitePool, term: &str) -> Result<Vec<Note>, AppError> {
        if term.trim().is_empty() {
            return Err(AppError::BadRequest("search query must not be empty".into()));
        }
        NoteRepo::search(pool, term).await
    }

    pub async fn create(pool: &SqlitePool, input: CreateNote) -> Result<(), AppError> {
        if input.title.trim().is_empty() || input.body.trim().is_empty() {
            return Err(AppError::BadRequest("title and body are required".into()));
        }
        if input.title.len() > 200 || input.body.len() > 10_000 {
            return Err(AppError::BadRequest("title max 200 chars, body max 10000 chars".into()));
        }
        NoteRepo::create(pool, &input.title, &input.body, &input.author).await
    }

    pub async fn delete(pool: &SqlitePool, id: i64) -> Result<(), AppError> {
        NoteRepo::delete(pool, id).await
    }
}
