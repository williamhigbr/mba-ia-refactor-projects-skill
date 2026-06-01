# Refactoring Playbook

Concrete transformation patterns for each anti-pattern. Apply these during Phase 3 to eliminate findings from the audit.

Each pattern shows before/after in both Python and Node.js. Match the transformation to the detected stack.

---

## 1. God Class → Domain Separation

**When:** A single file handles multiple unrelated domains (users + products + orders).

**Steps:**
1. Identify distinct domains by grouping functions that operate on the same data
2. Create one model file per domain entity
3. Create one controller file per domain entity
4. Move DB access to models, business logic to controllers
5. Update imports in routes

### Python — Before
```python
# models.py (350 lines — handles everything)
def criar_produto(nome, preco):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
    db.commit()
    return cursor.lastrowid

def criar_usuario(nome, email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
    db.commit()
    return cursor.lastrowid

def criar_pedido(usuario_id, itens):
    # 50 lines of order logic mixed with DB access...
```

### Python — After
```python
# models/product.py
class ProductModel:
    def __init__(self, db):
        self.db = db

    def create(self, name, price):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (name, price))
        self.db.commit()
        return cursor.lastrowid

    def find_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos")
        return [dict(row) for row in cursor.fetchall()]
```

### Node.js — Before
```javascript
// AppManager.js (200+ lines — one class does everything)
class AppManager {
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            // 80 lines: user creation + payment + enrollment + audit
        });
        app.get('/api/users', (req, res) => { /* ... */ });
        app.get('/api/courses', (req, res) => { /* ... */ });
    }
}
```

### Node.js — After
```javascript
// models/user.js
class UserModel {
    constructor(db) { this.db = db; }

    findByEmail(email) {
        return new Promise((resolve, reject) => {
            this.db.get("SELECT * FROM users WHERE email = ?", [email], (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    }

    create(name, email, password) {
        return new Promise((resolve, reject) => {
            this.db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
                [name, email, password], function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                });
        });
    }
}
module.exports = UserModel;
```

---

## 2. Hardcoded Credentials → Config Module

**When:** Secrets are written directly in source code.

**Steps:**
1. Create a config module that reads from environment variables
2. Replace all hardcoded values with config references
3. Create a `.env.example` file documenting required variables
4. Add `.env` to `.gitignore`

### Python — Before
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
DB_PATH = "loja.db"
```

### Python — After
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
```

### Node.js — Before
```javascript
const config = {
    paymentGatewayKey: "sk_live_SUPER_SECRET_KEY_123",
    jwtSecret: "my-jwt-secret",
    port: 3000
};
```

### Node.js — After
```javascript
// config/settings.js
module.exports = {
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "set-in-env",
    jwtSecret: process.env.JWT_SECRET || "change-me-in-production",
    port: parseInt(process.env.PORT || "3000", 10),
    dbPath: process.env.DB_PATH || ":memory:"
};
```

---

## 3. SQL Injection → Parameterized Queries

**When:** User input is concatenated into SQL strings.

**Steps:**
1. Find all SQL queries that include variables via string interpolation
2. Replace with parameterized queries using `?` placeholders
3. Pass values as a separate tuple/array
4. Remove any endpoint that accepts raw SQL from users

### Python — Before
```python
def buscar_produtos(termo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM produtos WHERE nome LIKE '%{termo}%'")
    return cursor.fetchall()
```

### Python — After
```python
def buscar_produtos(termo):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE nome LIKE ?", (f"%{termo}%",))
    return cursor.fetchall()
```

### Node.js — Before
```javascript
app.get('/api/users', (req, res) => {
    const name = req.query.name;
    db.all(`SELECT * FROM users WHERE name LIKE '%${name}%'`, (err, rows) => {
        res.json(rows);
    });
});
```

### Node.js — After
```javascript
app.get('/api/users', (req, res) => {
    const name = req.query.name;
    db.all("SELECT * FROM users WHERE name LIKE ?", [`%${name}%`], (err, rows) => {
        if (err) return next(err);
        res.json(rows);
    });
});
```

---

## 4. Fat Route → Controller Extraction

**When:** Route handlers contain business logic, DB queries, and response formatting.

**Steps:**
1. Identify the business logic within the route handler
2. Create a controller function that accepts parsed input and returns a result
3. Reduce the route handler to: parse request → call controller → send response
4. The controller should not know about HTTP (no `request`/`response` objects)

### Python — Before
```python
@app.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    nome = dados.get("nome", "")
    preco = dados.get("preco", 0)
    if not nome or preco <= 0:
        return jsonify({"erro": "Dados inválidos"}), 400
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
    db.commit()
    return jsonify({"id": cursor.lastrowid, "nome": nome, "preco": preco}), 201
```

### Python — After
```python
# routes/product_routes.py
@product_bp.route("/produtos", methods=["POST"])
def create_product():
    data = request.get_json()
    result, status = product_controller.create(data)
    return jsonify(result), status

# controllers/product_controller.py
class ProductController:
    def __init__(self, product_model):
        self.model = product_model

    def create(self, data):
        name = data.get("nome", "")
        price = data.get("preco", 0)
        if not name or price <= 0:
            return {"erro": "Dados inválidos"}, 400
        product_id = self.model.create(name, price)
        return {"id": product_id, "nome": name, "preco": price}, 201
```

### Node.js — Before
```javascript
app.post('/api/checkout', (req, res) => {
    let u = req.body.usr;
    let e = req.body.eml;
    let cid = req.body.c_id;
    let cc = req.body.card;
    // 60 lines of user lookup, payment, enrollment, audit logging...
});
```

### Node.js — After
```javascript
// routes/checkoutRoutes.js
router.post('/checkout', async (req, res, next) => {
    try {
        const result = await checkoutController.process(req.body);
        res.status(result.status).json(result.data);
    } catch (err) { next(err); }
});

// controllers/checkoutController.js
class CheckoutController {
    constructor(userModel, courseModel, paymentService) {
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.paymentService = paymentService;
    }

    async process({ userName, email, password, courseId, cardNumber }) {
        const course = await this.courseModel.findActiveById(courseId);
        if (!course) return { status: 404, data: { error: "Course not found" } };

        const user = await this.userModel.findOrCreate(userName, email, password);
        const payment = await this.paymentService.charge(cardNumber, course.price);

        if (payment.status === "DENIED") return { status: 400, data: { error: "Payment denied" } };

        await this.courseModel.enroll(user.id, courseId, payment.id);
        return { status: 201, data: { message: "Enrolled successfully", enrollmentId: payment.id } };
    }
}
```

---

## 5. Tight Coupling → Dependency Injection

**When:** Functions/classes create their own dependencies internally.

**Steps:**
1. Identify dependencies created inside functions (DB connections, services)
2. Move creation to the composition root (entry point)
3. Pass dependencies as constructor/function parameters
4. Wire everything together in `app.py` / `app.js`

### Python — Before
```python
def listar_produtos():
    db = get_db()  # hidden dependency
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    return cursor.fetchall()
```

### Python — After
```python
# models/product.py
class ProductModel:
    def __init__(self, db):
        self.db = db  # injected dependency

    def find_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos")
        return [dict(row) for row in cursor.fetchall()]

# app.py (composition root)
db = get_db()
product_model = ProductModel(db)
product_controller = ProductController(product_model)
```

### Node.js — Before
```javascript
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:');  // hardcoded
    }
}
```

### Node.js — After
```javascript
// models/user.js
class UserModel {
    constructor(db) { this.db = db; }  // injected
}

// app.js (composition root)
const db = new sqlite3.Database(config.dbPath);
const userModel = new UserModel(db);
const userController = new UserController(userModel);
```

---

## 6. N+1 Queries → Batch Query

**When:** Database queries execute inside loops.

**Steps:**
1. Identify the loop that triggers individual queries
2. Collect all needed IDs first
3. Execute a single query with `WHERE id IN (...)` or use a JOIN
4. Map results back to the parent entities

### Python — Before
```python
tasks = Task.query.all()
result = []
for task in tasks:
    user = User.query.get(task.user_id)  # N queries
    task_data = {"title": task.title, "user_name": user.name if user else None}
    result.append(task_data)
```

### Python — After
```python
tasks = Task.query.all()
user_ids = list(set(t.user_id for t in tasks if t.user_id))
users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}

result = []
for task in tasks:
    user = users.get(task.user_id)
    task_data = {"title": task.title, "user_name": user.name if user else None}
    result.append(task_data)
```

### Node.js — Before
```javascript
const orders = await db.all("SELECT * FROM orders");
for (const order of orders) {
    order.items = await db.all("SELECT * FROM items WHERE order_id = ?", [order.id]);
}
```

### Node.js — After
```javascript
const orders = await db.all("SELECT * FROM orders");
const orderIds = orders.map(o => o.id);
const items = await db.all(
    `SELECT * FROM items WHERE order_id IN (${orderIds.map(() => '?').join(',')})`,
    orderIds
);
const itemsByOrder = items.reduce((acc, item) => {
    (acc[item.order_id] = acc[item.order_id] || []).push(item);
    return acc;
}, {});
orders.forEach(order => { order.items = itemsByOrder[order.id] || []; });
```

---

## 7. Missing Validation → Input Sanitization Layer

**When:** Request data is used without any checks.

**Steps:**
1. Identify all request data access points
2. Define required fields and their types for each endpoint
3. Add validation at the route/controller boundary (before business logic)
4. Return clear error messages for invalid input

### Python — Before
```python
@app.route("/produtos", methods=["POST"])
def criar_produto():
    dados = request.get_json()
    nome = dados.get("nome")
    preco = dados.get("preco")
    # Used directly — no validation
    cursor.execute("INSERT INTO produtos (nome, preco) VALUES (?, ?)", (nome, preco))
```

### Python — After
```python
# controllers/product_controller.py
def create(self, data):
    if not data:
        return {"error": "Request body is required"}, 400

    name = data.get("nome")
    price = data.get("preco")

    errors = []
    if not name or not isinstance(name, str) or len(name.strip()) == 0:
        errors.append("'nome' is required and must be a non-empty string")
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        errors.append("'preco' must be a positive number")

    if errors:
        return {"errors": errors}, 400

    product_id = self.model.create(name.strip(), float(price))
    return {"id": product_id, "nome": name.strip(), "preco": price}, 201
```

### Node.js — Before
```javascript
app.post('/api/checkout', (req, res) => {
    let u = req.body.usr;
    let cid = req.body.c_id;
    let cc = req.body.card;
    if (!u || !cid || !cc) return res.status(400).send("Bad Request");
    // Minimal check, no type validation
});
```

### Node.js — After
```javascript
// controllers/checkoutController.js
validate(body) {
    const errors = [];
    if (!body.userName || typeof body.userName !== 'string')
        errors.push("'userName' is required");
    if (!body.email || !body.email.includes('@'))
        errors.push("'email' must be a valid email");
    if (!body.courseId || !Number.isInteger(body.courseId))
        errors.push("'courseId' must be an integer");
    if (!body.cardNumber || typeof body.cardNumber !== 'string' || body.cardNumber.length < 13)
        errors.push("'cardNumber' must be a valid card number");
    return errors;
}
```

---

## 8. Deprecated APIs → Modern Equivalents

**When:** Code uses obsolete APIs that have been superseded.

**Steps:**
1. Identify deprecated imports/calls based on the detected framework version
2. Replace with the modern equivalent
3. Verify functionality is preserved

### Python/Flask — Before
```python
from flask.ext.cors import CORS  # Removed in Flask 1.0
app.config["DEBUG"] = True       # Should use env var
```

### Python/Flask — After
```python
from flask_cors import CORS      # Modern import
# DEBUG controlled via environment
class Config:
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
```

### Node.js/Express — Before
```javascript
const bodyParser = require('body-parser');  // Deprecated since Express 4.16
app.use(bodyParser.json());

const buf = new Buffer(data);  // Deprecated
```

### Node.js/Express — After
```javascript
app.use(express.json());  // Built-in since Express 4.16

const buf = Buffer.from(data);  // Modern API
```

---

## 9. Unprotected Endpoints → Auth Middleware

**When:** Destructive or admin endpoints have no access control.

**Steps:**
1. Identify all destructive endpoints (DELETE, reset, raw query)
2. Remove raw SQL execution endpoints entirely (they should never exist)
3. Add authentication middleware to admin routes
4. For development-only endpoints, gate behind an environment check

### Python — Before
```python
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos")
    db.commit()
    return jsonify({"message": "Database reset"})

@app.route("/admin/query", methods=["POST"])
def execute_query():
    query = request.get_json().get("sql")
    cursor.execute(query)  # Arbitrary SQL execution!
```

### Python — After
```python
# Remove /admin/query entirely — never expose raw SQL execution

# Gate reset behind auth + environment check
@admin_bp.route("/reset-db", methods=["POST"])
@require_admin_auth
def reset_database():
    if not current_app.config["ALLOW_DB_RESET"]:
        return jsonify({"error": "Not allowed in this environment"}), 403
    # ... reset logic
```

### Node.js — Before
```javascript
app.delete('/api/users/:id', (req, res) => {
    db.run("DELETE FROM users WHERE id = ?", [req.params.id]);
    res.send("Deleted");
});
```

### Node.js — After
```javascript
// routes/userRoutes.js
router.delete('/:id', authMiddleware, adminOnly, async (req, res, next) => {
    try {
        await userController.delete(parseInt(req.params.id, 10));
        res.status(204).send();
    } catch (err) { next(err); }
});
```

---

## 10. No Error Handling → Centralized Error Middleware

**When:** Errors are unhandled or leak internal details to clients.

**Steps:**
1. Create a centralized error handler middleware
2. Wrap all route handlers in try/catch (or use async error wrapper)
3. Log full error details internally
4. Return safe, consistent error responses to clients

### Python — Before
```python
@app.route("/produtos/<int:id>")
def get_product(id):
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
    produto = cursor.fetchone()
    return jsonify(dict(produto))  # Crashes if produto is None
```

### Python — After
```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
```

### Node.js — Before
```javascript
app.get('/api/courses/:id', (req, res) => {
    db.get("SELECT * FROM courses WHERE id = ?", [req.params.id], (err, row) => {
        if (err) return res.status(500).send(err.message);  // Leaks internals
        res.json(row);  // Crashes if row is null
    });
});
```

### Node.js — After
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    console.error(`[ERROR] ${err.message}`, err.stack);
    res.status(err.status || 500).json({
        error: process.env.NODE_ENV === 'production'
            ? 'Internal server error'
            : err.message
    });
}
module.exports = errorHandler;
```

---

## Validation Checklist

After applying transformations, verify:

- [ ] Application starts without import/require errors
- [ ] All original endpoints return the same response format
- [ ] No hardcoded secrets remain in source files
- [ ] Each file has a single, clear responsibility
- [ ] Database access is only in model files
- [ ] Business logic is only in controller files
- [ ] Route handlers are under 15 lines each
- [ ] Error responses are consistent and don't leak internals
