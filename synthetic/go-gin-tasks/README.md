# go-gin-tasks (synthetic)

Tiny single-file Go/Gin **tasks tracker** API used as a fixture for the refactor-arch skill's agnosticism test. Intentionally riddled with anti-patterns: hardcoded secrets, SQL injection, no validation, unprotected admin endpoints, a global counter raced from handlers.

## Endpoints

- `GET /tasks` — list tasks
- `POST /tasks` — create task
- `GET /tasks/search?q=...` — search tasks (vulnerable)
- `DELETE /tasks/:id` — delete (no auth)
- `POST /users` — create user (plaintext password)
- `POST /login` — login (vulnerable)
- `POST /admin/reset` — wipe all data (no auth)
- `POST /admin/query` — execute arbitrary SQL (no auth)

## Run

```bash
go mod tidy
go run main.go
```
