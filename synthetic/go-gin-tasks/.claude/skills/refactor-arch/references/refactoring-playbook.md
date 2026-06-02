# Refactoring Playbook

Concrete transformation patterns for each anti-pattern. Each pattern in this file follows the same shape:

- **When** — abstract trigger condition.
- **Goal** — what the transformation achieves, framework-free.
- **Abstract recipe** — numbered steps that apply to any language.
- **Examples** — three language showcases (Python and Node always; a rotated third language for breadth).
- **Validation criteria** — observable, language-neutral checks proving the pattern was applied.

For stacks not covered in the examples, follow the **Pattern X on an unknown stack** section at the end of this file.

---

## 1. God Class / God File → Domain Separation

**When:** A single source unit owns 3+ unrelated domains, exceeds 300 LOC, or accounts for > 30% of project LOC.

**Goal:** One source unit per domain entity, separated by responsibility (model / controller / route).

### Abstract recipe

1. List every public function/method in the offending unit.
2. Group functions by the entity they primarily operate on.
3. Within each group, classify each function as **persistence**, **business logic**, or **transport** (HTTP).
4. Create one file per entity per layer: `models/<entity>`, `controllers/<entity>_controller`, `routes/<entity>_routes`.
5. Move functions into their target file, adjusting signatures to take collaborators as parameters (no internal `import` of dependencies).
6. Update import paths in callers.
7. Delete the original god file once empty.

### Example A — Python (Flask + sqlite3)

```python
# Before: models.py (350 LOC) handles products, users, orders
def criar_produto(nome, preco): ...
def criar_usuario(nome, email, senha): ...
def criar_pedido(usuario_id, itens): ...

# After: split by entity, one file per layer
# src/models/product.py
class ProductModel:
    def __init__(self, db): self.db = db
    def create(self, name, price): ...

# src/controllers/product_controller.py
class ProductController:
    def __init__(self, model): self.model = model
    def create(self, data): ...        # returns (payload, status)

# src/routes/product_routes.py
@product_bp.route("/produtos", methods=["POST"])
def create_product():
    payload, status = product_controller.create(request.get_json())
    return jsonify(payload), status
```

### Example B — Node.js (Express + sqlite3)

```javascript
// Before: AppManager.js — class doing routing + DB + payments + users + audit
class AppManager { setupRoutes(app) { /* 200 LOC */ } }

// After
// src/models/userModel.js
class UserModel {
  constructor(db) { this.db = db; }
  findByEmail(email) { /* parameterized query */ }
  create(name, email, password) { /* parameterized query */ }
}
module.exports = UserModel;

// src/controllers/userController.js — HTTP-agnostic
class UserController { constructor(userModel) { this.userModel = userModel; } /* … */ }

// src/routes/userRoutes.js
module.exports = (userController) => {
  const router = require('express').Router();
  router.post('/', async (req, res, next) => { /* parse → call → respond */ });
  return router;
};
```

### Example C — Java / Spring Boot (rotated third language)

```java
// Before: ApplicationService.java — one @Service with 30 methods spanning 4 entities

// After
@RestController @RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {
    private final ProductService productService;

    @PostMapping
    public ResponseEntity<ProductDto> create(@Valid @RequestBody CreateProductRequest req) {
        return ResponseEntity.status(HttpStatus.CREATED).body(productService.create(req));
    }
}

@Service @RequiredArgsConstructor
public class ProductService {
    private final ProductRepository productRepository;
    public ProductDto create(CreateProductRequest req) { /* business logic */ }
}

public interface ProductRepository extends JpaRepository<Product, Long> { }
```

### Validation criteria

- [ ] No source file exceeds 300 LOC after the refactor.
- [ ] No source file references entities from more than one domain.
- [ ] Each entity has a model, a controller, and a route binding (or framework-equivalent layers).
- [ ] All original public symbols still resolve (no broken imports).

---

## 2. Hardcoded Credentials → Config Module

**When:** Sensitive values are literal in source code.

**Goal:** All secrets loaded from environment; safe defaults for dev; nothing real committed.

### Abstract recipe

1. Identify every literal that is, or might be, a secret (passwords, keys, tokens, connection strings).
2. Create a single configuration module that reads from the environment and exposes typed values.
3. Replace every occurrence with a reference to the config module.
4. Add a `.env.example` documenting every variable with a safe placeholder.
5. Add `.env` (and any local-config equivalent) to `.gitignore`.
6. For production, document the deployment mechanism for setting real values (CI secrets, vault, KMS).

### Example A — Python

```python
# Before
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
DB_PATH = "loja.db"

# After: src/config/settings.py
import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-development")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    PORT = int(os.environ.get("PORT", 5000))
```

### Example B — Node.js

```javascript
// Before
const config = { jwtSecret: "my-jwt-secret", paymentKey: "sk_live_xyz" };

// After: src/config/settings.js
require('dotenv').config();
module.exports = {
    jwtSecret: process.env.JWT_SECRET || 'change-me-in-development',
    paymentKey: process.env.PAYMENT_KEY || 'set-in-env',
    port: parseInt(process.env.PORT || '3000', 10),
};
```

### Example C — Go (rotated)

```go
// Before
const SecretKey = "abc123"
var DSN = "user:password@tcp(localhost)/app"

// After: internal/config/config.go
package config
import "os"

type Config struct {
    SecretKey string
    DSN       string
    Addr      string
}

func Load() *Config {
    return &Config{
        SecretKey: getenv("SECRET_KEY", ""),       // fail at startup if empty in prod
        DSN:       getenv("DSN", ""),
        Addr:      getenv("ADDR", ":8080"),
    }
}

func getenv(k, def string) string {
    if v, ok := os.LookupEnv(k); ok { return v }
    return def
}
```

### Validation criteria

- [ ] `git grep -E "(secret|password|api[_-]?key|token).*=.*['\"]" -- *.py *.js *.ts *.go *.rb *.java *.cs *.rs *.php` returns no real secret values.
- [ ] `.env.example` exists at the project root with placeholders for every required variable.
- [ ] `.gitignore` excludes `.env` and any local-only config files.
- [ ] Application fails to start (or warns loudly) if a required env var is missing in production mode.

---

## 3. SQL Injection → Parameterized Queries

**When:** User input is concatenated/interpolated into a query string.

**Goal:** All queries use the database driver's parameter binding mechanism; no raw query endpoints exposed.

### Abstract recipe

1. Find every site where a query string is constructed dynamically.
2. For each, identify the variables being interpolated.
3. Replace the string-construction with the driver's parameterized form (`?`, `$1`, `:name`, etc.) and pass values as a separate sequence/dict.
4. For ORMs, use the typed query builders or named-parameter forms — never the "raw" escape hatch.
5. Remove any endpoint accepting raw query text from clients (no safe form exists).
6. Re-test endpoints with payloads containing SQL metacharacters (`'`, `"`, `;`, `--`).

### Example A — Python (sqlite3)

```python
# Before
cursor.execute(f"SELECT * FROM produtos WHERE nome LIKE '%{termo}%'")

# After
cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", (f"%{termo}%",))
```

### Example B — Node.js (sqlite3 / pg)

```javascript
// Before
db.all(`SELECT * FROM users WHERE name LIKE '%${name}%'`, (err, rows) => {});

// After (sqlite3)
db.all("SELECT * FROM users WHERE name LIKE ?", [`%${name}%`], (err, rows) => {});

// After (pg)
await pool.query("SELECT * FROM users WHERE name LIKE $1", [`%${name}%`]);
```

### Example C — Java (JDBC PreparedStatement, rotated)

```java
// Before
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE email = '" + email + "'");

// After
String sql = "SELECT * FROM users WHERE email = ?";
try (PreparedStatement ps = conn.prepareStatement(sql)) {
    ps.setString(1, email);
    try (ResultSet rs = ps.executeQuery()) { /* … */ }
}
```

### Validation criteria

- [ ] No string-concatenation operators feed values into `execute`/`query`/equivalent.
- [ ] No template literals with `${...}` inside query strings passed to a DB driver.
- [ ] Endpoints that accepted raw queries are removed.
- [ ] Sample injection payloads (`' OR '1'='1`, `; DROP TABLE users; --`) return safe responses (rows containing the literal text or empty results), not 500s.

---

## 4. Fat Route → Controller Extraction

**When:** Route handlers exceed ~30 LOC, contain DB calls, or implement branching business rules.

**Goal:** Routes do parse → call → respond. Controllers own business logic and are HTTP-agnostic.

### Abstract recipe

1. Inventory the responsibilities inside the offending handler: input parsing, validation, persistence, business rules, response shaping.
2. Extract everything except parsing and response shaping into a controller method.
3. Define the controller method's contract: it accepts plain values/DTOs and returns a structured result (payload + status).
4. Reduce the handler to: parse the request → call the controller → format the response.
5. If the controller needs collaborators (models, services), inject them via constructor.

### Example A — Python (Flask)

```python
# Before
@app.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    if not dados.get("nome") or dados.get("preco", 0) <= 0:
        return jsonify({"erro": "Dados inválidos"}), 400
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)",
                   (dados["nome"], dados["preco"]))
    db.commit()
    return jsonify({"id": cursor.lastrowid, **dados}), 201

# After
# routes/product_routes.py
@product_bp.route("/produtos", methods=["POST"])
def create_product():
    payload, status = product_controller.create(request.get_json() or {})
    return jsonify(payload), status

# controllers/product_controller.py
class ProductController:
    def __init__(self, product_model): self.model = product_model
    def create(self, data):
        if not data.get("nome") or data.get("preco", 0) <= 0:
            return {"erro": "Dados inválidos"}, 400
        product_id = self.model.create(data["nome"], data["preco"])
        return {"id": product_id, **data}, 201
```

### Example B — Node.js (Express)

```javascript
// Before: 60-line handler doing user creation + payment + enrollment

// After
// routes/checkoutRoutes.js
module.exports = (checkoutController) => {
  const router = require('express').Router();
  router.post('/checkout', async (req, res, next) => {
    try {
      const { status, body } = await checkoutController.process(req.body);
      res.status(status).json(body);
    } catch (err) { next(err); }
  });
  return router;
};

// controllers/checkoutController.js
class CheckoutController {
  constructor(userModel, courseModel, paymentSvc) { /* … */ }
  async process({ userName, email, password, courseId, cardNumber }) {
    /* business logic; returns { status, body } */
  }
}
```

### Example C — Ruby on Rails (rotated)

```ruby
# Before: app/controllers/orders_controller.rb action with 50 LOC of logic

# After
# app/controllers/orders_controller.rb (thin)
class OrdersController < ApplicationController
  def create
    result = Orders::Create.call(order_params, current_user: current_user)
    render json: result.payload, status: result.status
  end

  private
  def order_params
    params.require(:order).permit(:product_id, :quantity, :address_id)
  end
end

# app/services/orders/create.rb (Service Object — POROs)
module Orders
  class Create
    Result = Struct.new(:payload, :status)
    def self.call(attrs, current_user:)
      # business logic; returns Result.new(...)
    end
  end
end
```

### Validation criteria

- [ ] No route handler exceeds 15 LOC.
- [ ] No route handler imports or references a database driver/ORM.
- [ ] Each controller/service method is callable from a unit test without an HTTP request object.
- [ ] Each route's behavior is unchanged (same input → same output).

---

## 5. Tight Coupling → Dependency Injection

**When:** Modules construct their own dependencies internally.

**Goal:** Dependencies arrive via parameters; the composition root wires the graph.

### Abstract recipe

1. Find every dependency creation inside business code (DB connections, HTTP clients, hashing services).
2. Move creation to the composition root.
3. Add constructor/function parameters for each dependency in the consuming class.
4. In the composition root, instantiate dependencies once and pass them down.
5. For framework-managed DI (Spring, NestJS, Symfony, ASP.NET Core), register dependencies with the container instead of the manual approach.

### Example A — Python (manual DI)

```python
# Before
def listar_produtos():
    db = get_db()
    return db.execute("SELECT * FROM produtos").fetchall()

# After
class ProductModel:
    def __init__(self, db): self.db = db
    def list_all(self):
        return self.db.execute("SELECT * FROM produtos").fetchall()

# composition root: app.py
db = get_db(Config.DB_PATH)
product_model = ProductModel(db)
```

### Example B — Node.js (factory pattern)

```javascript
// Before
class AppManager { constructor() { this.db = new sqlite3.Database(':memory:'); } }

// After
class UserModel { constructor(db) { this.db = db; } }
class UserController { constructor(userModel) { this.userModel = userModel; } }

// composition root: app.js
const db = new sqlite3.Database(config.dbPath);
const userModel = new UserModel(db);
const userController = new UserController(userModel);
```

### Example C — Java / Spring Boot (constructor injection, rotated)

```java
// Before — bad: field injection + new'd dependency
@Service public class ProductService {
    @Autowired private ProductRepository repo;
    private PaymentClient client = new PaymentClient(); // hardcoded
}

// After — good: constructor injection, all deps managed by Spring
@Service @RequiredArgsConstructor
public class ProductService {
    private final ProductRepository repo;
    private final PaymentClient paymentClient;  // Spring resolves this
}
```

### Validation criteria

- [ ] No business class has a no-arg constructor that internally creates collaborators.
- [ ] No business function calls a "global" `get_db()` / `Database.instance()` style accessor.
- [ ] The composition root contains the only place where infrastructure singletons are created.
- [ ] Tests can replace any collaborator with a stub by passing a different argument.

---

## 6. N+1 Queries → Batch Query

**When:** A database call appears inside a loop body iterating over a previously-fetched collection.

**Goal:** A bounded number of queries (1–3) regardless of collection size.

### Abstract recipe

1. Identify the inner query and the IDs/keys it uses.
2. Collect all the IDs from the outer collection up-front.
3. Issue one batch query (`WHERE id IN (...)`) or a JOIN.
4. Build a lookup map keyed by the join column.
5. Replace the per-iteration query with a lookup-map access.

### Example A — Python (SQLAlchemy)

```python
# Before
tasks = Task.query.all()
out = [{"title": t.title, "user": User.query.get(t.user_id).name} for t in tasks]

# After (eager loading)
tasks = Task.query.options(joinedload(Task.user)).all()
out = [{"title": t.title, "user": t.user.name if t.user else None} for t in tasks]
```

### Example B — Node.js (sqlite3)

```javascript
// Before
const orders = await db.all("SELECT * FROM orders");
for (const o of orders) {
  o.items = await db.all("SELECT * FROM items WHERE order_id = ?", [o.id]);
}

// After
const orders = await db.all("SELECT * FROM orders");
const ids = orders.map(o => o.id);
const placeholders = ids.map(() => '?').join(',');
const items = await db.all(`SELECT * FROM items WHERE order_id IN (${placeholders})`, ids);
const byOrder = items.reduce((m, i) => ((m[i.order_id] ??= []).push(i), m), {});
orders.forEach(o => { o.items = byOrder[o.id] || []; });
```

### Example C — Ruby on Rails (rotated, eager loading)

```ruby
# Before
@tasks = Task.all
@tasks.each { |t| t.user.name }   # N+1

# After
@tasks = Task.includes(:user).all
@tasks.each { |t| t.user.name }   # single JOIN under the hood
```

### Validation criteria

- [ ] No DB call appears inside a `for`/`while`/`forEach`/`map` body that already iterates DB results.
- [ ] Database query count for the affected endpoint is bounded (1–3) regardless of input size.
- [ ] Profiling tools (or simple logging) confirm constant query count under varying load.

---

## 7. Missing Validation → Input Sanitization Layer

**When:** Request data flows to business logic without checks for presence, type, format, or bounds.

**Goal:** Validation happens at the transport boundary; downstream layers receive guaranteed-shape data.

### Abstract recipe

1. Define a schema (DTO, type, dataclass, struct) for each endpoint's input.
2. Validate before the controller is called: rejected requests get a structured 400 response.
3. Use a validation library when the ecosystem has a well-supported one; do not hand-roll string checks.
4. Apply the schema at the route boundary; pass the validated DTO into the controller.

### Example A — Python (pydantic)

```python
# After: schemas/product.py
from pydantic import BaseModel, condecimal, conint
class CreateProductRequest(BaseModel):
    nome: str
    preco: condecimal(gt=0, max_digits=10, decimal_places=2)
    estoque: conint(ge=0)

# routes/product_routes.py
@product_bp.route("/produtos", methods=["POST"])
def create_product():
    try:
        req = CreateProductRequest(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    payload, status = product_controller.create(req)
    return jsonify(payload), status
```

### Example B — Node.js (zod)

```javascript
// After: schemas/checkout.js
const z = require('zod');
const CheckoutSchema = z.object({
  userName: z.string().min(1).max(100),
  email: z.string().email(),
  password: z.string().min(8),
  courseId: z.number().int().positive(),
  cardNumber: z.string().regex(/^\d{13,19}$/),
});

// routes/checkoutRoutes.js
router.post('/checkout', async (req, res, next) => {
  const parsed = CheckoutSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ errors: parsed.error.issues });
  try {
    const { status, body } = await checkoutController.process(parsed.data);
    res.status(status).json(body);
  } catch (err) { next(err); }
});
```

### Example C — PHP / Laravel (FormRequest, rotated)

```php
// app/Http/Requests/CreateProductRequest.php
class CreateProductRequest extends FormRequest {
    public function rules(): array {
        return [
            'nome'    => ['required', 'string', 'max:255'],
            'preco'   => ['required', 'numeric', 'gt:0'],
            'estoque' => ['required', 'integer', 'min:0'],
        ];
    }
}

// app/Http/Controllers/ProductController.php
public function store(CreateProductRequest $req): JsonResponse {
    $payload = $this->productService->create($req->validated());
    return response()->json($payload, 201);
}
```

### Validation criteria

- [ ] Every endpoint with a request body has an explicit schema.
- [ ] Invalid bodies return 400 with a structured error list, not a 500.
- [ ] Controllers/services can assume data is valid (no defensive re-checks needed for the same fields).

---

## 8. Deprecated APIs → Modern Equivalents

**When:** Code uses APIs marked deprecated by the framework or language.

**Goal:** Use the current, supported equivalent; document non-trivial migrations inline.

### Abstract recipe

1. List the deprecated symbols detected (use `cross-language-signals.md` §8 as a checklist).
2. For each, identify the replacement from the framework's migration guide.
3. Replace usages, preserving behavior.
4. Run the test suite (or at least exercise affected endpoints) to confirm parity.
5. If behavior subtly changed (e.g., MD5 → bcrypt, error format changed), add a comment explaining the migration and any compatibility shims.

### Example A — Python / Flask

```python
# Before
from flask.ext.cors import CORS         # removed in Flask 1.0
app.before_first_request(seed_db)       # deprecated in Flask 2.3

# After
from flask_cors import CORS
with app.app_context():
    seed_db()
```

### Example B — Node.js / Express

```javascript
// Before
const bodyParser = require('body-parser');
app.use(bodyParser.json());
const buf = new Buffer(data);

// After
app.use(express.json());                // built-in since 4.16
const buf = Buffer.from(data);
```

### Example C — Go (`ioutil` → `io`/`os`, rotated)

```go
// Before (Go < 1.16)
import "io/ioutil"
data, err := ioutil.ReadFile(path)
body, err := ioutil.ReadAll(resp.Body)

// After (Go 1.16+)
import (
    "io"
    "os"
)
data, err := os.ReadFile(path)
body, err := io.ReadAll(resp.Body)
```

### Validation criteria

- [ ] No imports of deprecated modules remain.
- [ ] No deprecation warnings appear in build/runtime logs.
- [ ] Replacement-equivalent behavior verified for each migrated symbol.

---

## 9. Magic Numbers → Named Constants

**When:** Numeric thresholds or repeated string status values appear inline in business logic.

**Goal:** Every meaningful literal has a name that explains its purpose; identical values are deduplicated.

### Abstract recipe

1. Identify literals appearing in conditions, calculations, retry logic, or status comparisons.
2. Group by domain (pricing rules, retry policy, status enumeration, HTTP codes).
3. Extract to a constants module or a typed enum.
4. Replace all in-code usages with the named reference.

### Example A — Python

```python
# Before
if quantidade > 0 and preco > 0.01: ...
if status == "pending": ...

# After: src/config/business_rules.py
MIN_PRICE = 0.01
MIN_QUANTITY = 1

# src/models/order.py
class OrderStatus:
    PENDING   = "pending"
    PAID      = "paid"
    CANCELLED = "cancelled"
```

### Example B — Node.js / TypeScript

```typescript
// constants/payment.ts
export const enum PaymentStatus { Paid = 'PAID', Denied = 'DENIED' }
export const RETRY_DELAY_MS = 3000;
export const MAX_RETRIES = 5;
```

### Example C — C# / .NET (rotated)

```csharp
// Domain/PaymentStatus.cs
public enum PaymentStatus { Paid, Denied, Pending }

// Constants/PricingRules.cs
public static class PricingRules {
    public const decimal MinPrice = 0.01m;
    public const int MaxQuantityPerOrder = 100;
}
```

### Validation criteria

- [ ] No numeric literal other than `0`, `1`, `-1` appears in business-logic conditions.
- [ ] No string status value is repeated in two or more files; all reference a single source.
- [ ] Renaming a constant (e.g., `MIN_PRICE` → `MINIMUM_PRICE`) requires changes only in the constants file and its references.

---

## 10. Unprotected Endpoints → Auth Middleware

**When:** Destructive or admin endpoints are exposed without authentication / authorization / environment gating.

**Goal:** No destructive operation is callable by an unauthenticated client; raw-query endpoints are removed entirely.

### Abstract recipe

1. List every `DELETE`, `/admin/*`, raw-SQL, or destructive endpoint.
2. Remove raw-query endpoints unconditionally.
3. For destructive endpoints that must remain, apply auth middleware (auth → role check).
4. Gate environment-specific endpoints (e.g., DB reset) behind an env flag that defaults to OFF in production.
5. Add audit logging for every successful destructive action.

### Example A — Python (decorators)

```python
# Before
@app.route("/admin/reset-db", methods=["POST"])
def reset(): cursor.execute("DELETE FROM produtos"); ...

# After
@admin_bp.route("/reset-db", methods=["POST"])
@require_admin
def reset_db():
    if not Config.ALLOW_DB_RESET:
        return jsonify({"error": "Disabled in this environment"}), 403
    # … with audit logging
```

### Example B — Node.js (middleware chain)

```javascript
// After
router.delete('/:id', requireAuth, requireRole('admin'), auditLog, async (req, res, next) => {
  /* … */
});
```

### Example C — PHP / Laravel (route middleware, rotated)

```php
// routes/api.php
Route::middleware(['auth:sanctum', 'role:admin'])->group(function () {
    Route::delete('/users/{id}', [UserController::class, 'destroy']);
    Route::post('/admin/reset', [AdminController::class, 'reset'])
         ->middleware('env:dev,staging');     // custom middleware checking APP_ENV
});
```

### Validation criteria

- [ ] No endpoint accepts arbitrary query text.
- [ ] Calling any destructive endpoint without credentials returns 401.
- [ ] Calling any destructive endpoint without the admin role returns 403.
- [ ] Environment-gated endpoints return 403 in production by default.
- [ ] Successful destructive calls are recorded in an audit log.

---

## 11. No Error Handling → Centralized Error Middleware

**When:** Errors are swallowed, propagated raw to clients, or handled inconsistently across endpoints.

**Goal:** A single error pipeline that logs internally and returns safe, structured responses.

### Abstract recipe

1. Define a central error handler (middleware / filter / advice / `IntoResponse` impl, depending on the framework).
2. Define the error response shape (typically `{ "error": "...", "code": "...", "details": [...] }`).
3. Replace ad-hoc try/catch returns with throwing typed errors that the central handler maps to status codes.
4. Log full error details (stack trace, request id) internally.
5. Return generic safe messages in production; rich messages only in dev.

### Example A — Python / Flask

```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e): return jsonify({"error": "Not found"}), 404

    @app.errorhandler(Exception)
    def unhandled(e):
        app.logger.exception("Unhandled exception")
        msg = str(e) if app.config["DEBUG"] else "Internal server error"
        return jsonify({"error": msg}), 500
```

### Example B — Node.js / Express

```javascript
// middlewares/errorHandler.js
module.exports = (err, req, res, next) => {
  console.error(`[${req.id || '-'}] ${err.stack}`);
  const isProd = process.env.NODE_ENV === 'production';
  res.status(err.status || 500).json({
    error: isProd ? 'Internal server error' : err.message,
    code: err.code,
  });
};
```

### Example C — Go / Gin (rotated)

```go
// internal/middleware/error.go
func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()
        if len(c.Errors) == 0 { return }
        err := c.Errors.Last().Err
        log.Printf("[%s] %v", c.GetString("request_id"), err)
        var notFound *NotFoundError
        switch {
        case errors.As(err, &notFound):
            c.JSON(404, gin.H{"error": "not found"})
        default:
            c.JSON(500, gin.H{"error": "internal server error"})
        }
    }
}
```

### Validation criteria

- [ ] Exactly one error-handling registration in the composition root.
- [ ] No handler returns raw exception/error messages to clients in production mode.
- [ ] Every endpoint returns the same error response shape.
- [ ] Internal logs preserve full stack traces with request correlation IDs when available.

---

## 12. Sync I/O in Async → Async-Aware I/O

**When:** Blocking I/O calls execute inside an async runtime.

**Goal:** All I/O on the request path is non-blocking; unavoidably blocking work runs on a worker pool.

### Abstract recipe

1. Identify each blocking call inside an `async` function or event-loop runtime.
2. Replace with the framework's async equivalent if one exists.
3. If no async equivalent exists, offload to a worker pool / thread pool.
4. Audit third-party libraries: many "modern" libs ship sync-only or async-only variants; pick the right one.

### Example A — Python (asyncio + httpx)

```python
# Before (FastAPI handler)
import requests, time
async def fetch(): r = requests.get(URL); time.sleep(1); return r.json()

# After
import httpx, asyncio
async def fetch():
    async with httpx.AsyncClient() as c:
        r = await c.get(URL)
    await asyncio.sleep(1)
    return r.json()
```

### Example B — Node.js

```javascript
// Before
const fs = require('fs');
app.get('/file', (req, res) => { res.send(fs.readFileSync('/big')); });

// After
const fs = require('fs/promises');
app.get('/file', async (req, res) => { res.send(await fs.readFile('/big')); });
```

### Example C — Rust / Tokio (rotated)

```rust
// Before
async fn handler() -> impl IntoResponse {
    std::thread::sleep(std::time::Duration::from_secs(1));        // blocks the runtime
    let data = std::fs::read_to_string("/big").unwrap();          // blocks
    data
}

// After
async fn handler() -> impl IntoResponse {
    tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    let data = tokio::fs::read_to_string("/big").await.unwrap();
    data
}
```

### Validation criteria

- [ ] No blocking I/O appears inside async functions on the request path.
- [ ] Concurrent throughput scales with concurrency, not flat-lining at 1.
- [ ] Long-running CPU work is delegated to a worker pool (`asyncio.to_thread`, `tokio::task::spawn_blocking`, `worker_threads`).

---

## 13. Mutable Shared State → Synchronization or Immutability

**When:** Multiple concurrent execution units mutate shared in-memory state without synchronization.

**Goal:** Eliminate the shared state, make it immutable, or protect every access.

### Abstract recipe

1. Catalog every module-/static-scoped mutable variable touched by handlers.
2. For each, choose the cheapest correct option:
    - **Eliminate** — derive the value from the database on read.
    - **Make immutable** — replace with a constant or a snapshot.
    - **Synchronize** — wrap in the language's standard concurrency primitive.
3. For caches, use a proper cache library with bounded size and eviction policy.
4. Add tests that exercise concurrent access to verify correctness under load.

### Example A — Python (per-process counter → Redis)

```python
# Before
total_revenue = 0
@app.route("/checkout", methods=["POST"])
def checkout():
    global total_revenue
    total_revenue += amount  # race under multi-worker WSGI
    ...

# After
@app.route("/checkout", methods=["POST"])
def checkout():
    redis.incrby("total_revenue", int(amount * 100))   # atomic on Redis
```

### Example B — Node.js (compute from DB instead of cache)

```javascript
// Before: module-level revenue counter mutated from handlers

// After: derive from data on demand
async function getTotalRevenue() {
  const { sum } = await db.get("SELECT SUM(amount) AS sum FROM payments WHERE status='PAID'");
  return sum || 0;
}
```

### Example C — Go (sync.RWMutex around shared map, rotated)

```go
// Before
var cache = map[string]string{}
func Set(k, v string) { cache[k] = v }     // race
func Get(k string) string { return cache[k] }

// After
type Cache struct {
    mu    sync.RWMutex
    items map[string]string
}
func (c *Cache) Set(k, v string) { c.mu.Lock();   c.items[k] = v; c.mu.Unlock() }
func (c *Cache) Get(k string) string { c.mu.RLock(); v := c.items[k]; c.mu.RUnlock(); return v }
```

### Validation criteria

- [ ] No `global` / module-level mutable variable is mutated from request handlers without synchronization.
- [ ] Counters are derived from the database, an atomic primitive, or an external store (Redis/Memcached).
- [ ] Concurrency tests (50+ parallel requests touching the same key) produce the expected outcome (no lost updates).

---

## 14. Layer-Violation Untangling for Non-MVC-Native Architectures

**When:** The detected project uses an opinionated architecture (Hexagonal, Clean, CQRS, Modular Monolith) where leaky responsibilities should be fixed *within* the existing structure, not by collapsing into MVC.

**Goal:** Preserve the architectural choice; relocate leaks to the correct layer of *that* architecture.

### Abstract recipe

1. Identify the project's actual architecture from `project-analysis.md` §5 and `mvc-architecture-guide.md` (Mapping section).
2. For each finding, decide where its fix belongs **in that architecture's vocabulary** (e.g., a "fat handler" in Clean lands in the Use Case layer, not a "controller").
3. Apply the corresponding playbook pattern, but place the result in the architecture-correct directory.
4. Do **not** introduce `controllers/` / `routes/` / `models/` folders alongside `application/` / `domain/` / `infrastructure/` — that's two architectures fighting.

### Concrete examples

**Hexagonal (DDD):**
- Fat HTTP handler → move logic to an `application/` Use Case; the handler in `infrastructure/inbound/http/` becomes a thin adapter.
- Direct DB access in domain entity → move to `infrastructure/outbound/persistence/` repository implementation; domain code depends on a repository interface in `application/ports/`.

**Clean Architecture:**
- Business logic in framework adapter → move to Use Case (interactor) class.
- Cross-layer references that violate the dependency rule (inner depends on outer) → invert with an interface owned by the inner layer.

**CQRS:**
- Read/write logic merged in one handler → split into a Command handler and a Query handler.
- N+1 in a write path → fix on the read model side (denormalize), don't introduce JOINs in the write side.

**Modular Monolith / NestJS:**
- Fat module file → split inside the same feature folder; do not extract to a top-level shared layer.
- Cross-module direct calls bypassing public APIs → introduce a published contract (interface, event, DTO) in the source module.

### Validation criteria

- [ ] No folder names from a foreign architecture are introduced.
- [ ] The dependency direction of the original architecture is preserved.
- [ ] Each fixed finding lands in the architecturally-correct layer.
- [ ] An architecture-aware reader (someone familiar with Hexagonal/Clean/CQRS/etc.) would say "yes, that's where this belongs".

---

## Pattern X on an Unknown Stack

When the detected stack is **not** documented in this playbook's examples or `cross-language-signals.md`, follow this procedure.

### Step 1 — Identify the ecosystem's idiomatic equivalents

For each of these MVC-layer concepts, find the host language/framework's equivalent:

| Concept | Find the equivalent for: |
|---|---|
| HTTP route declaration | annotations, function attributes, builder methods, macro-based routers |
| Middleware / filter | interceptors, decorators, request lifecycle hooks |
| Dependency wiring | container, factory, constructor parameters, manual instantiation |
| Error handling | exception filters, error monads, panic recovery, error middleware |
| Configuration loading | env-reading library, config struct, framework's settings module |
| Persistence access | ORM, query builder, raw driver, repository pattern |
| Transport-layer DTOs | type-safe records/structs, validators, serializers |

Use the abstract probes in `project-analysis.md` §7 (HTTP idiom regex, entry-point heuristics) to anchor the search.

### Step 2 — Apply the abstract recipe verbatim

The abstract recipes for each pattern in this file are intentionally framework-free. Apply them step-by-step, substituting the equivalents identified in Step 1.

### Step 3 — Choose idiomatic constructs over forced conventions

If the host language has a strong idiom (e.g., Go's `interface` for DI, Rust's `Arc<RwLock<T>>` for shared state, Erlang/Elixir's actors for concurrent state), use it. Do **not** transliterate Python or Node patterns into the target language — that produces non-idiomatic code that future readers will reject.

### Step 4 — Document gaps explicitly

If a needed construct doesn't exist in the host language (e.g., Rust's borrow checker means certain singleton patterns are intentionally hard), document the gap in the audit report. State the trade-off you chose.

### Step 5 — Validate functionally, not structurally

The validation criteria for each pattern are language-neutral observations: "no SQL string concatenation feeds a query call", "no handler exceeds 15 LOC". These hold regardless of language. Verify against them.

---

## Validation Checklist (whole-project, post-refactor)

After applying transformations, the project as a whole should satisfy:

- [ ] Application starts without errors.
- [ ] All original endpoints return the same response shape (no API contract regression).
- [ ] No hardcoded secrets remain in source files.
- [ ] Every file has a single, clear responsibility.
- [ ] Database access is confined to the model/repository layer.
- [ ] Business logic lives in controllers/services, not in route handlers or models.
- [ ] Route handlers are thin (≤ 15 LOC).
- [ ] Error responses are consistent across endpoints and don't leak internals in production mode.
- [ ] No CRITICAL or HIGH anti-patterns from `anti-patterns-catalog.md` remain (re-run Phase 2 to confirm).
