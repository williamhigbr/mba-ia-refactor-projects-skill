use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, sqlx::FromRow)]
pub struct Note {
    pub id: i64,
    pub title: String,
    pub body: String,
    pub author: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateNote {
    pub title: String,
    pub body: String,
    pub author: String,
}

#[derive(Debug, Deserialize)]
pub struct SearchQuery {
    pub q: String,
}
