================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] SQL Injection
File: models.py:27-30
Description: `get_produto_por_id` builds SQL by string concatenation: `"SELECT * FROM produtos WHERE id = " + str(id)`. While `id` comes from a typed route param, the same pattern is used throughout models.py with user-controlled string inputs (e.g., `buscar_produtos`, `login_usuario`, `criar_produto`). The `login_usuario` function at line 101 is especially dangerous: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` — allows authentication bypass via SQL injection.
Impact: Any unauthenticated user can bypass login, extract all data, or drop tables via the login or search endpoints.
Recommendation: Replace all string-concatenated queries with parameterized queries using `?` placeholders and tuple parameters.

### [CRITICAL] Hardcoded Credentials
File: app.py:7
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` is a hardcoded secret key committed in source code.
Impact: Anyone with repository access can forge session cookies or tokens. The secret is permanently leaked in git history.
Recommendation: Load from environment variable: `app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-dev")`. Add `.env.example` with placeholder.

### [CRITICAL] Unprotected Destructive Endpoint (DB Reset)
File: app.py:47-57
Description: `/admin/reset-db` POST endpoint deletes all data from all tables without any authentication, authorization, or environment gating.
Impact: Any network client can wipe the entire database with a single POST request.
Recommendation: Remove or gate behind authentication + admin role check + environment flag (`ALLOW_DB_RESET` defaulting to False).

### [CRITICAL] Unprotected Raw Query Endpoint
File: app.py:59-75
Description: `/admin/query` POST endpoint accepts arbitrary SQL from the request body and executes it directly via `cursor.execute(query)`. No authentication, no query sanitization.
Impact: Full database compromise (read, write, delete, schema manipulation) by any unauthenticated client. This is equivalent to giving every network user a database shell.
Recommendation: Remove this endpoint entirely. No safe form of a raw-query endpoint exists.

### [HIGH] God File — models.py
File: models.py:1-314
Description: Single file handles all SQL queries, business logic (order total calculation, stock validation, discount tiers), and data formatting for 4 unrelated domains: products, users, orders, and sales reports. Contains 17 functions mixing persistence with business rules.
Impact: Impossible to test any domain in isolation. Changes to order logic risk breaking product logic. No separation of concerns.
Recommendation: Split into `models/product.py`, `models/user.py`, `models/order.py` with one class per domain. Extract business logic (discount calculation, stock validation) into controllers.

### [HIGH] Business Logic in Controllers (Fat Handlers)
File: controllers.py:24-79
Description: `criar_produto()` handler (55 LOC) contains input validation, business rules (category validation against hardcoded list, price/stock bounds), database calls via models, response formatting, and logging — all in one function. Same pattern repeats across `atualizar_produto` (lines 81-114), `criar_pedido` (lines 158-196).
Impact: Business rules cannot be unit-tested without HTTP context. Validation logic is scattered and duplicated.
Recommendation: Extract validation to schemas, business logic to controller classes, keep route handlers to parse → call → respond (~10 LOC).

### [HIGH] Tight Coupling / No Dependency Injection
File: models.py:1-314, controllers.py:1-292
Description: Every function in `models.py` calls `get_db()` internally to obtain the database connection. Controllers import `models` module directly. There is no composition root; the dependency graph is implicit and hardcoded. `database.py` uses a global `db_connection` variable.
Impact: Cannot substitute a test database without monkeypatching. Cannot run tests in parallel. No way to swap persistence layer.
Recommendation: Pass `db` as a constructor parameter to model classes. Build dependency graph in a composition root (`create_app` factory).

### [MEDIUM] N+1 Query Problem
File: models.py:163-189
Description: `get_pedidos_usuario` fetches all orders, then for each order fetches items (`cursor2.execute`), then for each item fetches the product name (`cursor3.execute`). For N orders with M items each, this issues 1 + N + N*M queries. Same pattern in `get_todos_pedidos` (lines 191-219).
Impact: Performance degrades quadratically with data growth. Acceptable with 3 orders but catastrophic at scale.
Recommendation: Use JOINs: `SELECT p.*, i.*, pr.nome FROM pedidos p JOIN itens_pedido i ON ... JOIN produtos pr ON ...` in a single query.

### [MEDIUM] No Centralized Error Handling
File: controllers.py:1-292
Description: Every controller function wraps its body in `try/except Exception as e: return jsonify({"erro": str(e)}), 500`. Raw exception messages (including potential SQL errors with schema details) are returned directly to clients. No centralized error handler registered with Flask.
Impact: Internal details leak to attackers (table names, column names, SQL syntax). Inconsistent error response structure if new endpoints forget the try/catch pattern.
Recommendation: Register `@app.errorhandler(Exception)` that logs full details internally and returns safe generic messages. Remove per-function try/except boilerplate.

### [MEDIUM] Credential Exposure in Health Endpoint
File: controllers.py:271-292
Description: The `health_check` endpoint returns `"secret_key": "minha-chave-super-secreta-123"` and `"db_path": "loja.db"` in its JSON response body, exposing sensitive configuration to any caller.
Impact: Secret key exposed via unauthenticated API call; aids attacker reconnaissance.
Recommendation: Remove sensitive fields from health response. Return only operational status and non-sensitive metrics.

### [LOW] Magic Numbers and Strings
File: models.py:240-246
Description: Discount calculation uses hardcoded thresholds: `if faturamento > 10000: desconto = faturamento * 0.1`, `> 5000: * 0.05`, `> 1000: * 0.02`. No named constants explain the business meaning of these tiers.
Impact: Discount rules are buried in code; changing tier thresholds requires reading through SQL report logic.
Recommendation: Extract to named constants: `DISCOUNT_TIER_1 = 10000`, `DISCOUNT_RATE_1 = 0.1`, etc. in a business rules module.

### [LOW] Poor Naming / Passwords Stored in Plaintext
File: models.py:63-78, database.py:60-67
Description: User passwords are stored as plaintext in the database (`senha TEXT`) and returned in API responses (`get_todos_usuarios` and `get_usuario_por_id` include `"senha": row["senha"]`). The `login_usuario` function compares plaintext passwords directly.
Impact: Any database breach or API call to `/usuarios` exposes all user passwords. Violates basic security hygiene.
Recommendation: Hash passwords with bcrypt/argon2 on creation; never return password fields in API responses; compare hashes on login.

================================
Total: 12 findings
================================
