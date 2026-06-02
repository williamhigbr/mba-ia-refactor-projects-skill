use axum::{
    middleware,
    routing::{delete, get, post},
    Router,
};
use std::sync::Arc;

use crate::handlers::{admin_handler, auth_handler, note_handler};
use crate::middleware::auth::require_admin;
use crate::state::AppState;

pub fn build_router(state: Arc<AppState>) -> Router {
    let admin_routes = Router::new()
        .route("/admin/reset", post(admin_handler::admin_reset))
        .layer(middleware::from_fn_with_state(state.clone(), require_admin));

    Router::new()
        .route("/notes", get(note_handler::list_notes).post(note_handler::create_note))
        .route("/notes/search", get(note_handler::search_notes))
        .route("/notes/:id", delete(note_handler::delete_note))
        .route("/login", post(auth_handler::login))
        .merge(admin_routes)
        .with_state(state)
}
