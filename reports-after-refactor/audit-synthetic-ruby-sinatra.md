================================
ARCHITECTURE AUDIT REPORT
================================
Project: ruby-sinatra-blog
Stack:   Ruby + Sinatra ~> 2.2
Files:   1 analyzed | ~95 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] SQL Injection / Query Injection
File: app.rb:29
Description: String interpolation used directly in SQL queries throughout the file. `DB.execute("SELECT email FROM users WHERE email = '#{author}'")` allows arbitrary SQL injection via the `author` field. Same pattern repeats at lines 34, 43, 49, 55, 60.
Impact: Attackers can dump the entire database, modify data, or bypass authentication via crafted input to any endpoint accepting user data.
Recommendation: Use parameterized queries with `?` placeholders: `DB.execute("SELECT email FROM users WHERE email = ?", [author])`.

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.rb:7-9
Description: `SECRET_KEY = 'minha-chave-blog-super-secreta'` and `ADMIN_API_KEY = 'admin-master-token-9999'` are hardcoded constants. The `/health` endpoint at line 82 also leaks `SECRET_KEY` in the JSON response.
Impact: Anyone reading the source or calling `/health` obtains the application secret, enabling token forgery and admin access.
Recommendation: Use `ENV.fetch('SECRET_KEY')` and `ENV.fetch('ADMIN_API_KEY')` with fail-fast if absent. Remove secret from `/health` response.

### [CRITICAL] Unprotected Destructive Endpoints
File: app.rb:62-64, 67-76
Description: `POST /admin/reset` deletes all posts and users without any authentication check. `POST /admin/query` executes arbitrary SQL from the request body with no auth.
Impact: Any unauthenticated client can wipe the database or execute arbitrary queries, leading to total data loss or exfiltration.
Recommendation: Add authentication middleware (API key check via `before` filter) for admin routes. Remove the `/admin/query` endpoint entirely — raw SQL execution has no safe form.

### [HIGH] God Class / God File
File: app.rb:1-83
Description: Single file contains all route definitions (8 endpoints), database initialization, business logic, authentication, and configuration for two unrelated domains (posts and users).
Impact: Impossible to test routes, models, or business logic in isolation. Any change risks side effects across unrelated functionality.
Recommendation: Extract into modular Sinatra apps: `models/post.rb`, `models/user.rb`, `routes/posts_routes.rb`, `routes/users_routes.rb`, `controllers/posts_controller.rb`, with a composition root in `app.rb`.

### [HIGH] N+1 Query Problem
File: app.rb:27-30
Description: Inside `GET /posts`, each post triggers a separate query `SELECT email FROM users WHERE email = '#{author}'` in a `.map` loop, resulting in N+1 queries for N posts.
Impact: Linear database load growth with post count; degrades response time as data grows.
Recommendation: Use a single JOIN query: `SELECT posts.*, users.email FROM posts LEFT JOIN users ON posts.author = users.email`.

### [MEDIUM] Missing Input Validation
File: app.rb:39-44
Description: `POST /posts` parses the request body and inserts `title`, `body`, and `author` directly into the database with no type checking, presence validation, or length constraints.
Impact: Allows empty or malformed records, potential for oversized payloads consuming storage, and aids injection attacks.
Recommendation: Validate required fields and constraints before database insertion. Use a helper method or validation gem.

### [MEDIUM] Mutable Shared State Without Synchronization
File: app.rb:12-13
Description: `$total_views` and `$cache` are global variables mutated from request handlers. Under Puma's multi-threaded mode, `$total_views += 1` is a race condition (read-modify-write is not atomic in Ruby).
Impact: Incorrect view counts; potential data corruption in `$cache` under concurrent load.
Recommendation: Use `Concurrent::AtomicFixnum` from concurrent-ruby for counters, or Redis for shared state across threads/processes.

### [LOW] No Error Handling / Bare Exceptions
File: app.rb:73-76
Description: The `rescue => e` block in `POST /admin/query` returns the raw exception message (`e.message`) directly to the client as JSON, leaking internal database error details.
Impact: Exposes database schema details and internal state to attackers via error messages.
Recommendation: Return a generic error message to the client; log the full error server-side. Add centralized error handling via Rack middleware.

================================
Total: 8 findings
================================
