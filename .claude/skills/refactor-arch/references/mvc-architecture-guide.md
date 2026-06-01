# MVC Architecture Guide

This document defines the target architecture for refactored projects. The skill adapts the directory structure to the detected stack while maintaining the same layer responsibilities.

---

## Layer Responsibilities

### Models
- Represent data entities and their relationships
- Encapsulate database access (queries, inserts, updates, deletes)
- Define validation rules for data integrity
- One model file per domain entity

**Models should NOT:** handle HTTP requests, format API responses, or contain business orchestration logic.

### Controllers
- Orchestrate business logic flows
- Coordinate between multiple models when needed
- Apply business rules (pricing, permissions, status transitions)
- Return structured results (not HTTP responses)

**Controllers should NOT:** access `request`/`response` objects directly, format HTTP responses, or execute raw SQL.

### Views / Routes
- Define HTTP endpoints and methods
- Parse incoming requests (body, params, query)
- Call the appropriate controller method
- Format and send HTTP responses
- Apply route-level middleware (auth, validation)

**Routes should NOT:** contain business logic, execute database queries, or exceed ~10 lines per handler.

### Config
- Load environment variables
- Define application settings (port, debug mode, DB path)
- Provide defaults for development
- Never contain actual secrets — only references to env vars

### Middlewares
- Error handling (catch all unhandled errors, return safe responses)
- Authentication / Authorization
- Request logging
- CORS configuration
- Input sanitization

### Utils / Helpers
- Pure utility functions (formatting, hashing, date manipulation)
- Shared across layers but with no dependencies on models/controllers/routes
- Stateless — no side effects

---

## Target Directory Structures

### Python / Flask

```
src/
├── app.py                    # Composition root — creates app, registers blueprints
├── config/
│   └── settings.py           # Loads env vars, defines Config class
├── models/
│   ├── __init__.py
│   ├── product.py            # Product model + DB access
│   └── user.py              # User model + DB access
├── controllers/
│   ├── __init__.py
│   ├── product_controller.py # Product business logic
│   └── user_controller.py   # User business logic
├── routes/
│   ├── __init__.py
│   ├── product_routes.py    # Product HTTP endpoints (Blueprint)
│   └── user_routes.py       # User HTTP endpoints (Blueprint)
├── middlewares/
│   └── error_handler.py     # Global error handling
└── utils/
    └── helpers.py           # Shared utilities
```

**Flask-specific patterns:**
- Use Blueprints for route organization
- Register blueprints in `app.py`
- Use `app.config.from_object()` for configuration
- Error handlers registered via `@app.errorhandler()`

### Node.js / Express

```
src/
├── app.js                    # Composition root — creates app, mounts routers
├── config/
│   └── settings.js           # Loads env vars, exports config object
├── models/
│   ├── product.js            # Product model + DB access
│   └── user.js              # User model + DB access
├── controllers/
│   ├── productController.js  # Product business logic
│   └── userController.js    # User business logic
├── routes/
│   ├── productRoutes.js     # Product HTTP endpoints (Router)
│   └── userRoutes.js        # User HTTP endpoints (Router)
├── middlewares/
│   └── errorHandler.js      # Global error handling
└── utils/
    └── helpers.js           # Shared utilities
```

**Express-specific patterns:**
- Use `express.Router()` for route organization
- Mount routers with `app.use('/api/products', productRoutes)`
- Error middleware has signature `(err, req, res, next)`
- Use `express.json()` instead of body-parser (built-in since 4.16)

### Generic Template (other stacks)

```
src/
├── main.{ext}               # Entry point / composition root
├── config/
│   └── settings.{ext}
├── models/
│   └── {entity}.{ext}
├── controllers/
│   └── {entity}_controller.{ext}
├── routes/
│   └── {entity}_routes.{ext}
├── middlewares/
│   └── error_handler.{ext}
└── utils/
    └── helpers.{ext}
```

---

## Composition Root Pattern

The entry point file (`app.py` / `app.js`) should ONLY:

1. Import configuration
2. Create the application instance
3. Initialize the database connection
4. Register middlewares
5. Register routes/blueprints
6. Start the server (if `__main__` / direct execution)

It should NOT contain route handlers, business logic, or database queries.

**Python example:**
```python
from flask import Flask
from config.settings import Config
from routes.product_routes import product_bp
from routes.user_routes import user_bp
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(product_bp)
    app.register_blueprint(user_bp)

    # Register error handlers
    register_error_handlers(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=app.config["HOST"], port=app.config["PORT"])
```

**Node.js example:**
```javascript
const express = require('express');
const config = require('./config/settings');
const productRoutes = require('./routes/productRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();

app.use(express.json());
app.use('/api/products', productRoutes);
app.use('/api/users', userRoutes);
app.use(errorHandler);

app.listen(config.port, () => {
    console.log(`Server running on port ${config.port}`);
});
```

---

## Adaptation Rules

When refactoring, adapt the structure to what already exists:

- **Monolith → Full MVC:** Create all directories from scratch, extract everything
- **Partial MVC → Full MVC:** Keep what's already well-separated, fix only the leaking layers
- **Preserve existing routes:** All original URL paths must continue working after refactoring. Do not change the API contract.
- **Preserve database schema:** Do not modify table structures. Only change how they're accessed (raw SQL → model methods).
