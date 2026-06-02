# rust-axum-notes (synthetic, negative test)

Single-file Rust/Axum **notes** API used as a fixture for the refactor-arch skill's **negative test** — proving the skill degrades gracefully on a stack for which the playbook has no rotation example.

Anti-patterns intentionally embedded: hardcoded SECRET_KEY, SQL injection via `format!` in 5+ queries, plaintext password storage, `lazy_static!` global cache, no validation, unprotected `/admin/reset` and `/admin/query`.

## Endpoints

- `GET /notes` — list (N+1)
- `GET /notes/search?q=...` — search (vulnerable)
- `POST /notes` — create
- `DELETE /notes/:id` — delete (no auth)
- `POST /login` — login (vulnerable)
- `POST /admin/reset` — wipe all data (no auth)
- `POST /admin/query` — execute arbitrary SQL (no auth)

## Note on toolchain

`cargo` is not installed on the test environment, so the skill is expected to:

1. Detect Rust + Axum in Phase 1 (registry + Cargo.toml).
2. Produce a Phase 2 audit using abstract concepts plus the Rust column of the cross-language signal grid.
3. Produce Phase 3 refactored source files in idiomatic Rust without compiling.
4. **Skip the boot-validation step**, reporting the toolchain absence honestly.

If `cargo` is available, `cargo run` should also boot the original.
