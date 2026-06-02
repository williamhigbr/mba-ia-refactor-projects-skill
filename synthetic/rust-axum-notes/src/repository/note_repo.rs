use sqlx::SqlitePool;

use crate::domain::note::Note;
use crate::error::AppError;

pub struct NoteRepo;

impl NoteRepo {
    pub async fn list(pool: &SqlitePool) -> Result<Vec<Note>, AppError> {
        let notes = sqlx::query_as::<_, Note>(
            "SELECT n.id, n.title, n.body, COALESCE(u.email, n.author) AS author \
             FROM notes n LEFT JOIN users u ON n.author = u.email"
        )
        .fetch_all(pool)
        .await?;
        Ok(notes)
    }

    pub async fn search(pool: &SqlitePool, term: &str) -> Result<Vec<Note>, AppError> {
        let pattern = format!("%{term}%");
        let notes = sqlx::query_as::<_, Note>(
            "SELECT id, title, body, author FROM notes WHERE title LIKE $1"
        )
        .bind(&pattern)
        .fetch_all(pool)
        .await?;
        Ok(notes)
    }

    pub async fn create(pool: &SqlitePool, title: &str, body: &str, author: &str) -> Result<(), AppError> {
        sqlx::query("INSERT INTO notes (title, body, author) VALUES ($1, $2, $3)")
            .bind(title)
            .bind(body)
            .bind(author)
            .execute(pool)
            .await?;
        Ok(())
    }

    pub async fn delete(pool: &SqlitePool, id: i64) -> Result<(), AppError> {
        let result = sqlx::query("DELETE FROM notes WHERE id = $1")
            .bind(id)
            .execute(pool)
            .await?;
        if result.rows_affected() == 0 {
            return Err(AppError::NotFound(format!("note {id} not found")));
        }
        Ok(())
    }

    pub async fn delete_all(pool: &SqlitePool) -> Result<(), AppError> {
        sqlx::query("DELETE FROM notes").execute(pool).await?;
        Ok(())
    }
}
