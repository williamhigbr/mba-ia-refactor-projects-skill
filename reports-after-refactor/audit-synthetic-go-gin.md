================================
ARCHITECTURE AUDIT REPORT
================================
Project: go-gin-tasks
Stack:   Go + Gin v1.10.0
Files:   1 analyzed | ~120 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] SQL Injection / Query Injection
File: main.go:56-57
Description: In `listTasks`, owner email is fetched via string concatenation: `"SELECT email FROM users WHERE email = '"+owner+"'"`. This allows injection through stored task owner values.
Impact: Attacker can exfiltrate all user data or corrupt the database through crafted owner fields.
Recommendation: Replace with parameterized query: `db.QueryRow("SELECT email FROM users WHERE email = ?", owner)`.

### [CRITICAL] SQL Injection / Query Injection (multiple endpoints)
File: main.go:64-65, 75-76, 89, 96, 104
Description: Every write and search endpoint uses `fmt.Sprintf` or string concatenation to build SQL. `createTask` concatenates title and owner; `searchTasks` uses `fmt.Sprintf("...%%%s%%", q)`; `deleteTask` concatenates id; `createUser` concatenates email and password; `login` concatenates email and password. All are classic injection vectors.
Impact: Complete database compromise — data exfiltration, authentication bypass, data destruction via any user-facing input.
Recommendation: Use `database/sql` parameterized queries with `?` placeholders for all dynamic values: `db.Exec("INSERT INTO tasks (title, owner, status) VALUES (?, ?, ?)", title, owner, "pending")`.

### [CRITICAL] Unprotected Destructive Endpoints + Raw SQL Execution
File: main.go:109-120
Description: `adminReset` deletes all data from both tables with zero authentication. `adminQuery` accepts raw SQL from the request body and executes it — effectively giving any HTTP client full database control.
Impact: Any unauthenticated client can wipe the database or execute arbitrary DDL/DML. This is the most dangerous vulnerability — raw query endpoints have no safe form.
Recommendation: Remove `adminQuery` entirely. Gate `adminReset` behind auth middleware and an environment flag (`ALLOW_DB_RESET`).

### [HIGH] Hardcoded Credentials / Secrets
File: main.go:16-18
Description: `JWTSecret`, `AdminToken`, and `DBPath` are declared as package-level `const` with literal values. The JWT secret `"super-secret-jwt-key-do-not-share-123"` is exposed in source.
Impact: Compromised source code (or any binary disassembly) reveals authentication secrets. Credential rotation requires a code change and redeployment.
Recommendation: Load from environment via `os.Getenv("JWT_SECRET")` with fail-fast on empty value in production. Use a `config` package with an env-driven struct.

### [HIGH] God File — All Responsibilities in main.go
File: main.go:1-120
Description: A single file contains: struct definitions, database initialization, route registration, HTTP handlers, business logic, SQL queries, and authentication logic for 8 endpoints across 3 domains (tasks, users, admin). Matches Go bad signal: "main.go containing http.HandleFunc calls + SQL queries + business logic + struct definitions".
Impact: Impossible to test any component in isolation. Any change risks breaking unrelated functionality. No separation of concerns.
Recommendation: Split into `internal/{config,handler,service,repository,domain,middleware}/` per the Go/Gin target structure. One handler file per resource, services for business logic, repositories for DB access.

### [HIGH] Mutable Shared State Without Synchronization
File: main.go:21
Description: `var TotalRequests = 0` is a package-level mutable integer incremented from `listTasks` (line 48) without any synchronization (`sync.Mutex`, `sync/atomic`). Under concurrent requests this is a data race.
Impact: Data race detected by Go's race detector (`-race` flag). Undefined behavior in production; counter values unreliable.
Recommendation: Use `atomic.Int64` or protect with `sync.Mutex`. Better: derive metrics from an external store or use a proper metrics library (Prometheus).

### [MEDIUM] N+1 Query Problem
File: main.go:53-57
Description: Inside the `for rows.Next()` loop in `listTasks`, a separate `db.QueryRow` fetches the owner email for each task row. This is the Go N+1 bad signal: `for _, t := range tasks { db.Get(&u, "… WHERE id = ?", t.UserID) }`.
Impact: Response time grows linearly with task count. 100 tasks = 101 queries.
Recommendation: Collect owner values, batch-fetch with `WHERE email IN (?,?,...)`, or use a JOIN: `SELECT t.*, u.email FROM tasks t LEFT JOIN users u ON t.owner = u.email`.

### [MEDIUM] Missing Input Validation
File: main.go:62-65, 91-96
Description: `createTask` and `createUser` bind JSON into untyped `map[string]interface{}` / `map[string]string` with no validation of field presence, type, or format. Empty or malformed bodies are passed directly to SQL.
Impact: Garbage data persisted to DB; empty strings as emails/passwords; potential panics on nil map access.
Recommendation: Define typed Go structs with `binding:"required"` tags and use `c.ShouldBindJSON(&input)` with `go-playground/validator`.

### [LOW] No Centralized Error Handling
File: main.go:67-68, 117-118
Description: Errors are handled ad-hoc: some return `c.String(500, err.Error())` leaking raw DB error messages to clients, others silently ignore errors (line 49: `rows, _ := db.Query(...)`). No Gin recovery middleware or centralized error handler.
Impact: Internal implementation details leaked to attackers; inconsistent error response shapes across endpoints; swallowed errors mask bugs.
Recommendation: Add Gin recovery middleware and a custom error handler middleware that logs internally and returns safe JSON `{"error": "..."}` responses.

================================
Total: 9 findings
================================
