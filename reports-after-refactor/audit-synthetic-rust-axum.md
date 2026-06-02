================================
ARCHITECTURE AUDIT REPORT
================================
Project: rust-axum-notes
Stack:   Rust + Axum 0.7
Files:   1 analyzed | ~120 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] SQL Injection via format!
File: src/main.rs:71-73
Description: `list_notes` builds SQL with `format!("SELECT email FROM users WHERE email = '{}'", author)` — user-controlled `author` field is interpolated directly into the query string, enabling full SQL injection.
Impact: Attacker can exfiltrate or destroy all data in the SQLite database via crafted note author values.
Recommendation: Replace with `sqlx::query_as("SELECT email FROM users WHERE email = $1").bind(&author)`.

### [CRITICAL] SQL Injection via format! (multiple endpoints)
File: src/main.rs:78-79, 85-86, 92-95, 101, 108
Description: Every write/read handler (`search_notes`, `create_note`, `delete_note`, `login`) constructs SQL via `format!` with unsanitized user input. The `admin_query` endpoint executes arbitrary SQL from the request body verbatim.
Impact: Complete database compromise from any of 5 different attack surfaces; `admin_query` allows arbitrary DDL/DML.
Recommendation: Use parameterized queries with `sqlx::query!("... $1 ...", value)` or `.bind(value)` for all endpoints. Remove `admin_query` entirely — raw SQL execution endpoints have no safe form.

### [CRITICAL] Hardcoded Credentials
File: src/main.rs:18-20
Description: `SECRET_KEY`, `ADMIN_TOKEN`, and `DB_URL` are hardcoded as `const` string literals (`"rust-notes-super-secret-key-12345"`, `"admin-master-rust-token"`, `"sqlite::memory:"`).
Impact: Secrets are visible in version control; cannot rotate without recompilation; anyone with repo access has admin credentials.
Recommendation: Use `dotenvy` crate to load from `.env` file; read via `std::env::var("SECRET_KEY")` at startup; fail fast if missing in production.

### [HIGH] God File — All Responsibilities in main.rs
File: src/main.rs:1-120
Description: A single file contains route definitions, all handler logic, all SQL queries, domain structs, auth logic, and shared state. It spans 4 distinct domains (notes CRUD, user auth, admin operations, search).
Impact: Impossible to test handlers in isolation, any change risks affecting unrelated functionality, no reuse of business logic.
Recommendation: Split into `src/{handlers/, services/, repository/, domain/, config.rs, state.rs, error.rs, routes.rs}` with one module per domain entity.

### [HIGH] Unprotected Destructive Endpoints
File: src/main.rs:101-105 (admin_reset), src/main.rs:99 (delete_note)
Description: `admin_reset` deletes all notes and users with zero authentication. `delete_note` allows anyone to delete any note without ownership or auth checks. No middleware protects these routes.
Impact: Any unauthenticated HTTP client can wipe the entire database or delete arbitrary notes.
Recommendation: Add tower auth middleware layer on admin routes; require ownership verification on `delete_note`.

### [HIGH] No Error Handling — unwrap() in Request Paths
File: src/main.rs:47, 49, 51, 69, 73, 79, 86, 95, 101, 103
Description: Every database operation uses `.unwrap()` which will panic the entire Tokio runtime on any DB error, crashing the server for all clients.
Impact: A single malformed query or transient DB error takes down the entire application.
Recommendation: Implement a custom error enum with `IntoResponse`; use `?` operator in handlers returning `Result<impl IntoResponse, AppError>`.

### [MEDIUM] N+1 Query in list_notes
File: src/main.rs:68-74
Description: `list_notes` fetches all notes, then executes a separate `SELECT email FROM users` query for each note's `author` field inside a loop.
Impact: Performance degrades linearly with the number of notes; 100 notes = 101 queries.
Recommendation: Use a single JOIN query: `SELECT n.*, u.email FROM notes n LEFT JOIN users u ON n.author = u.email`.

### [MEDIUM] Missing Input Validation
File: src/main.rs:87-95
Description: `create_note` accepts `Json<CreateNote>` and inserts directly without any length, format, or content validation on title, body, or author fields.
Impact: Allows empty notes, excessively long fields causing storage issues, or injection of malicious content.
Recommendation: Add `validator` crate with `#[derive(Validate)]` on `CreateNote`; enforce length constraints and required fields.

### [LOW] Mutable Shared State (unused but dangerous)
File: src/main.rs:23-25
Description: A `lazy_static!` global `Mutex<HashMap<String, String>>` named `CACHE` is declared but never used. If used in the future without `Arc` wrapping, holding the lock across `.await` points would deadlock.
Impact: Dead code that sets a dangerous pattern for future contributors; holding a `std::sync::Mutex` across await is undefined behavior in async Rust.
Recommendation: Remove the unused `CACHE` global. If caching is needed, use `Arc<tokio::sync::RwLock<HashMap<...>>>` in `AppState`.

================================
Total: 9 findings
================================
