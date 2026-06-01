# Anti-Patterns Catalog

Each anti-pattern below includes detection signals that work across languages. When auditing, check every source file against each pattern and report exact file:line locations.

---

## 1. God Class / God File

**Severity:** CRITICAL

**What it is:** A single file or class that handles multiple unrelated responsibilities — data access, business logic, validation, formatting — for multiple domains.

**Detection signals:**
- File exceeds 300 lines of code
- File contains functions/methods for 3+ unrelated domains (e.g., users AND products AND orders)
- Mix of SQL queries, validation logic, and response formatting in the same file
- Class with 10+ public methods spanning different concerns

**Python example:** A `models.py` that contains SQL queries, business rules, and data formatting for products, users, and orders all in one file.

**Node.js example:** An `AppManager.js` class that sets up routes, handles DB queries, processes payments, and manages users.

**Impact:** Impossible to test in isolation, any change risks breaking unrelated functionality, merge conflicts in teams.

**Recommendation:** Split into domain-specific modules — one model/controller per domain entity.

---

## 2. Hardcoded Credentials / Secrets

**Severity:** CRITICAL

**What it is:** Sensitive values (API keys, passwords, secret keys) written directly in source code instead of loaded from environment.

**Detection signals:**
- String literals assigned to variables named `secret`, `key`, `password`, `token`, `api_key`
- `SECRET_KEY = "..."` or `config.secret = "..."` with actual values
- Database passwords in connection strings
- Payment gateway keys in source code

**Python example:** `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`

**Node.js example:** `const paymentGatewayKey = "sk_live_abc123..."`

**Impact:** Credentials exposed in version control, anyone with repo access can compromise the system.

**Recommendation:** Move to environment variables, load via `os.environ` / `process.env`, provide `.env.example` with placeholder values.

---

## 3. SQL Injection Vulnerability

**Severity:** CRITICAL

**What it is:** User input concatenated directly into SQL queries without parameterization.

**Detection signals:**
- f-strings or string concatenation containing SQL keywords: `f"SELECT ... {variable}"`
- Template literals in SQL: `` `SELECT ... ${variable}` ``
- `.execute(query)` where `query` is built from user input
- Endpoints that accept raw SQL from request body

**Python example:** `cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")`

**Node.js example:** `` db.run(`DELETE FROM users WHERE id = ${req.params.id}`) ``

**Impact:** Attackers can read, modify, or delete any data in the database; full system compromise.

**Recommendation:** Use parameterized queries (`?` placeholders) or ORM methods. Never build SQL from user input.

---

## 4. Business Logic in Routes/Handlers

**Severity:** HIGH

**What it is:** Route handlers that contain business rules, database queries, and data transformation instead of delegating to a controller/service layer.

**Detection signals:**
- Route handler functions exceeding 30 lines
- Database queries directly inside route handlers
- Conditional business rules (pricing, validation, status transitions) in route files
- Multiple responsibilities in a single handler: parse request → query DB → apply rules → format response

**Python example:** A Flask route that queries the database, calculates discounts, validates stock, and formats the response all in one function.

**Node.js example:** An Express route callback that does user lookup, payment processing, enrollment creation, and email sending.

**Impact:** Cannot reuse business logic outside HTTP context, cannot unit test without HTTP mocking, routes become unreadable.

**Recommendation:** Extract business logic to controller/service modules. Routes should only: parse request → call controller → send response.

---

## 5. Tight Coupling / No Dependency Injection

**Severity:** HIGH

**What it is:** Modules directly instantiate or import their dependencies instead of receiving them as parameters, making it impossible to swap implementations or mock for testing.

**Detection signals:**
- Database connections created inside business logic functions
- `import` / `require` of concrete implementations inside functions that should be configurable
- Global mutable state shared across modules (e.g., a module-level `db` variable used everywhere)
- No constructor parameters or function arguments for dependencies

**Python example:** Every function calls `get_db()` internally instead of receiving a db connection as a parameter.

**Node.js example:** A class that creates `new sqlite3.Database()` in its constructor with no way to inject a different DB.

**Impact:** Cannot test without real database, cannot swap implementations, hidden dependencies make code unpredictable.

**Recommendation:** Pass dependencies as function/constructor parameters. Create them once at the composition root and inject downward.

---

## 6. N+1 Query Problem

**Severity:** MEDIUM

**What it is:** Executing a database query inside a loop, resulting in N additional queries for N items when a single batch query would suffice.

**Detection signals:**
- Database query calls (`.execute()`, `.query()`, `.get()`, `.find()`) inside `for`/`while` loops
- Pattern: fetch list → loop over list → fetch related data per item
- ORM lazy-loading inside iteration without eager loading

**Python example:**
```python
tasks = Task.query.all()
for task in tasks:
    user = User.query.get(task.user_id)  # N queries!
```

**Node.js example:**
```javascript
const orders = await db.all("SELECT * FROM orders");
for (const order of orders) {
    const items = await db.all("SELECT * FROM items WHERE order_id = ?", [order.id]); // N queries!
}
```

**Impact:** Performance degrades linearly with data size. 100 items = 101 queries instead of 2.

**Recommendation:** Use JOINs, batch queries (`WHERE id IN (...)`), or ORM eager loading (`joinedload`, `include`).

---

## 7. Missing Input Validation

**Severity:** MEDIUM

**What it is:** Request parameters used directly in business logic or database queries without type checking, sanitization, or bounds validation.

**Detection signals:**
- `request.get_json()` or `req.body` values used directly without checks
- No validation of required fields before processing
- No type coercion or format validation (email, dates, numeric ranges)
- Route parameters used without existence checks

**Python example:** `preco = dados.get("preco")` used directly in SQL without checking if it's a valid number.

**Node.js example:** `let cid = req.body.c_id` used in a DB query without verifying it's a positive integer.

**Impact:** Unexpected data causes crashes, corrupted database entries, or security vulnerabilities.

**Recommendation:** Validate all inputs at the route/controller boundary. Check required fields, types, formats, and ranges before processing.

---

## 8. Deprecated API Usage

**Severity:** MEDIUM

**What it is:** Using obsolete APIs or patterns that have been superseded by modern equivalents, often with security or performance implications.

**Detection signals:**

### Python/Flask
- `from flask.ext.*` (removed in Flask 1.0)
- `flask.json.jsonify` patterns that are unnecessary in modern Flask
- `app.config["DEBUG"] = True` in production code (use env vars)

### Node.js/Express
- `require('body-parser')` (built into Express since 4.16)
- `new Buffer()` (deprecated, use `Buffer.from()`)
- `require('querystring')` (deprecated, use `URLSearchParams`)
- Callback-based APIs where Promise/async versions exist

### General
- Synchronous file I/O in async contexts
- MD5/SHA1 for security purposes (use SHA256+)
- `eval()` or `exec()` for data parsing

**Impact:** Deprecated APIs may be removed in future versions, often have known security issues, and signal unmaintained code.

**Recommendation:** Replace with the modern equivalent. Document the migration in comments if the change is non-trivial.

---

## 9. Magic Numbers and Strings

**Severity:** LOW

**What it is:** Unexplained numeric literals or repeated string constants scattered through the code without named constants.

**Detection signals:**
- Numeric literals other than 0, 1, -1 used in conditions or calculations without explanation
- Status strings like `"pending"`, `"active"`, `"paid"` repeated across multiple files
- HTTP status codes used as raw numbers without comments
- Timeout/retry values without named constants

**Python example:** `if quantidade > 0 and preco > 0.01` — what does 0.01 represent?

**Node.js example:** `setTimeout(retry, 3000)` — why 3000ms specifically?

**Impact:** Difficult to understand intent, easy to introduce inconsistencies when values need to change.

**Recommendation:** Extract to named constants (`MIN_PRICE`, `RETRY_DELAY_MS`) or configuration values.

---

## 10. Poor Naming Conventions

**Severity:** LOW

**What it is:** Variables, functions, or files with names that don't communicate their purpose.

**Detection signals:**
- Single-letter variables outside of loop counters: `u`, `e`, `p`, `d`
- Abbreviations that aren't universally understood: `usr`, `eml`, `pwd`, `cid`
- Generic names: `data`, `result`, `temp`, `info`, `manager`, `handler`, `utils` (when overly broad)
- Inconsistent naming style within the same file (mixing camelCase and snake_case)

**Python example:** `def proc(d):` — what does it process? What is `d`?

**Node.js example:** `let u = req.body.usr; let e = req.body.eml;` — unclear without context.

**Impact:** Increases cognitive load, slows onboarding, makes code reviews harder.

**Recommendation:** Use descriptive names that reveal intent. `user_email` over `e`, `course_id` over `cid`.

---

## 11. Unprotected Destructive Endpoints

**Severity:** HIGH

**What it is:** Administrative or destructive operations (database reset, raw query execution, bulk delete) exposed without authentication or authorization.

**Detection signals:**
- Endpoints with names like `/admin/reset`, `/admin/query`, `/debug/`
- DELETE or destructive operations without auth middleware
- Endpoints that accept raw SQL or arbitrary commands
- No role/permission checks before destructive actions

**Python example:** `@app.route("/admin/reset-db", methods=["POST"])` with no auth check.

**Node.js example:** `app.delete('/api/users/:id', (req, res) => { ... })` without verifying caller identity.

**Impact:** Anyone with network access can destroy data or execute arbitrary queries.

**Recommendation:** Add authentication middleware, require admin role, or remove from production entirely. Raw SQL endpoints should never exist in production.

---

## 12. No Error Handling / Bare Exceptions

**Severity:** MEDIUM

**What it is:** Missing try/catch blocks around operations that can fail, or catching all exceptions without proper handling.

**Detection signals:**
- Database operations without error handling
- `except Exception as e: return str(e)` — leaks internal details
- No global error handler middleware
- Errors returned with inconsistent formats across endpoints
- `catch(err) { res.status(500).send(err.message) }` — exposes internals

**Python example:** `cursor.execute(query)` with no try/except, crashes on any DB error.

**Node.js example:** Callback-based code where `if (err)` returns raw error to client.

**Impact:** Unhandled errors crash the application, inconsistent error responses confuse API consumers, leaked details aid attackers.

**Recommendation:** Add centralized error handling middleware. Catch specific exceptions, log details internally, return safe generic messages to clients.
