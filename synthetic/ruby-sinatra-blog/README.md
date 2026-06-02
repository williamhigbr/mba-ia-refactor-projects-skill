# ruby-sinatra-blog (synthetic)

Single-file Sinatra **blog** API used as a fixture for the refactor-arch skill's agnosticism test. Intentionally riddled with anti-patterns: hardcoded SECRET_KEY, SQL injection in search/login/insert, plaintext password storage, unprotected `/admin/reset` and `/admin/query`, global `$total_views` counter, no validation.

## Endpoints

- `GET /posts` — list posts (N+1)
- `GET /posts/search?q=...` — search (SQL-injectable)
- `POST /posts` — create
- `DELETE /posts/:id` — delete (no auth)
- `POST /users` — create user (plaintext password)
- `POST /login` — login (vulnerable)
- `POST /admin/reset` — wipe all data (no auth)
- `POST /admin/query` — execute arbitrary SQL (no auth)
- `GET /health` — leaks SECRET_KEY in response

## Run

```bash
bundle install
PORT=4567 bundle exec ruby app.rb
```
