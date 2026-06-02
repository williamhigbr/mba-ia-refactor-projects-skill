# MVC Architecture Guide

This document defines the **target architecture** for refactored projects in language-agnostic terms. The skill maps these responsibilities to the idiomatic structure of the detected stack — not the other way around.

The core insight: **MVC is a *responsibility shape*, not a directory layout.** Forcing a literal `models/`, `controllers/`, `routes/` tree into a Rails app or a Spring Boot project is harmful. The skill must respect the destination ecosystem's conventions while enforcing the same separation of concerns.

---

## Layer Responsibilities (language-agnostic)

These responsibilities are universal. Every refactored project must have a clear, single home for each.

### Models

- Represent domain entities and their relationships.
- Encapsulate persistence: queries, inserts, updates, deletes.
- Define data validation rules tied to entity invariants (not transport-level validation).
- Typically one source unit per aggregate / domain entity.

**Models do NOT:** handle HTTP requests, format API responses, or contain business orchestration that crosses entity boundaries.

### Controllers (also called Services in some ecosystems)

- Orchestrate business workflows that span one or more models.
- Apply business rules: pricing, status transitions, permission decisions, side effects.
- Return structured results (data + status), not HTTP responses.
- Are HTTP-agnostic — testable without an HTTP runtime.

**Controllers do NOT:** access request/response objects directly, format HTTP responses, or execute raw queries that bypass the model layer.

### Views / Routes (the HTTP boundary)

- Define HTTP endpoints, methods, and paths.
- Parse incoming requests (body, query, headers, route params).
- Delegate to a controller.
- Format the response (status code, body, headers).
- Apply route-scoped middleware (auth, validation).

**Routes do NOT:** contain business logic, query the database directly, or exceed ~10 LOC per handler.

### Configuration

- Loads environment variables.
- Provides typed access to settings (port, debug flag, DB URL, secret keys).
- Provides safe defaults for development; never embeds production values.
- Single source of truth for "what is configurable".

### Middlewares (also called Filters / Interceptors)

- Cross-cutting concerns: error handling, authentication, authorization, request logging, CORS, rate limiting.
- Composable; one responsibility per middleware.
- Have access to the request/response pipeline.

### Utilities / Helpers

- Pure stateless functions: formatting, hashing, date math, ID generation.
- Have no dependencies on models, controllers, or routes.
- Trivially testable; trivially reusable.

---

## Target Directory Structures by Stack

The skill picks the right structure based on Phase 1's framework detection. When a stack is **not** in this table, fall back to the **Abstract Layout Template** below it.

### Python / Flask

```
src/
├── app.py                       # composition root (create_app factory)
├── config/
│   └── settings.py
├── models/
│   ├── __init__.py
│   ├── product.py
│   └── user.py
├── controllers/
│   ├── product_controller.py
│   └── user_controller.py
├── routes/
│   ├── product_routes.py        # Blueprint
│   └── user_routes.py
├── middlewares/
│   └── error_handler.py
└── utils/
    └── helpers.py
```

Conventions: Blueprints for route grouping; `app.config.from_object(Config)`; `@app.errorhandler` for centralized errors; `create_app()` factory pattern.

### Python / FastAPI

```
src/
├── main.py                      # composition root with FastAPI() instance
├── config/settings.py           # pydantic Settings class
├── models/                      # SQLAlchemy/SQLModel entity classes
├── schemas/                     # pydantic request/response DTOs
├── controllers/                 # service classes (HTTP-agnostic)
├── routes/                      # APIRouter instances (one per resource)
├── middlewares/                 # ASGI middleware
├── deps/                        # FastAPI dependency providers
└── utils/
```

Conventions: `APIRouter` per resource; pydantic settings via `BaseSettings`; dependency injection via `Depends(...)`; lifespan context for startup/shutdown.

### Node.js / Express

```
src/
├── app.js                       # composition root
├── config/settings.js
├── models/userModel.js
├── controllers/userController.js
├── routes/userRoutes.js         # express.Router()
├── middlewares/errorHandler.js
└── utils/helpers.js
```

Conventions: `express.Router()` per resource; `express.json()` (built-in since 4.16, do NOT use body-parser); error middleware signature `(err, req, res, next)`.

### Node.js / NestJS

```
src/
├── main.ts                      # bootstrap
├── app.module.ts
├── config/                      # @nestjs/config module
├── modules/                     # one folder per domain module
│   └── users/
│       ├── users.module.ts
│       ├── users.controller.ts  # @Controller decorator
│       ├── users.service.ts     # @Injectable
│       ├── users.repository.ts  # or use TypeORM repository
│       ├── dto/
│       │   ├── create-user.dto.ts
│       │   └── update-user.dto.ts
│       └── entities/user.entity.ts
└── common/                      # shared filters, guards, interceptors
    ├── filters/all-exceptions.filter.ts
    └── guards/auth.guard.ts
```

Conventions: feature modules; constructor DI; class-validator on DTOs; exception filters for centralized error handling.

### Java / Spring Boot

```
src/main/java/com/example/app/
├── Application.java             # @SpringBootApplication (composition root)
├── config/                      # @Configuration classes
├── domain/                      # entities (@Entity)
│   └── User.java
├── repository/                  # interfaces extending JpaRepository
│   └── UserRepository.java
├── service/                     # @Service classes (business logic)
│   └── UserService.java
├── controller/                  # @RestController classes
│   └── UserController.java
├── dto/
│   └── UserDto.java
├── exception/                   # custom exceptions + @RestControllerAdvice
│   └── GlobalExceptionHandler.java
└── security/                    # SecurityConfig, JWT filters
src/main/resources/
├── application.yml              # configuration
└── application-dev.yml          # profile-specific overrides
```

Conventions: constructor injection; Spring profiles for env-specific config; `@RestControllerAdvice` for centralized exceptions; bean validation via `@Valid` + `@NotNull`/`@Email`/etc.

### Go / Gin (or Echo / Chi)

```
.
├── main.go                      # composition root
├── go.mod
├── internal/
│   ├── config/config.go         # env-driven Config struct
│   ├── handler/                 # HTTP handlers (one file per resource)
│   │   ├── user_handler.go
│   │   └── product_handler.go
│   ├── service/                 # business logic
│   │   ├── user_service.go
│   │   └── product_service.go
│   ├── repository/              # data access
│   │   ├── user_repo.go
│   │   └── product_repo.go
│   ├── domain/                  # entities + interfaces
│   │   ├── user.go
│   │   └── product.go
│   ├── middleware/
│   │   ├── auth.go
│   │   └── error.go
│   └── server/server.go         # router setup, graceful shutdown
└── pkg/                         # reusable libs (optional)
```

Conventions: `internal/` for non-exported packages; interfaces defined where consumed (not where implemented); dependencies passed by value/pointer to constructors.

### Ruby / Rails

Rails already imposes a layout — **do not fight it.** Enforce responsibility separation within the Rails idiom:

```
app/
├── controllers/
│   └── users_controller.rb      # thin, delegates to services
├── models/
│   └── user.rb                  # ActiveRecord
├── services/                    # PORO business logic (NOT a Rails default; create the dir)
│   └── checkout_service.rb
├── policies/                    # if using Pundit
├── serializers/                 # if using ActiveModel::Serializer / Jbuilder
└── views/                       # for HTML responses; APIs may have none
config/
├── application.rb
├── database.yml
├── routes.rb
└── credentials.yml.enc          # encrypted secrets
```

Conventions: strong parameters in controllers; `before_action` for auth; `rescue_from` in `ApplicationController` for centralized errors; service objects in `app/services/` to keep controllers and models thin (Rails ≥ 5 autoloads this).

### Ruby / Sinatra

```
.
├── app.rb                       # composition root + route registration
├── config.ru
├── config/settings.rb
├── controllers/                 # Sinatra modular apps OR plain Ruby classes
│   └── users_controller.rb
├── models/
│   └── user.rb                  # ActiveRecord/Sequel
├── routes/
│   └── users_routes.rb          # Sinatra::Base subclasses (one per resource)
├── middlewares/
│   └── error_handler.rb         # Rack middleware
└── helpers/
    └── auth_helpers.rb
```

Conventions: modular Sinatra (subclass `Sinatra::Base`) instead of classic style for non-trivial apps; Rack middleware for cross-cutting concerns.

### PHP / Laravel

```
app/
├── Http/
│   ├── Controllers/             # thin controllers
│   ├── Middleware/
│   ├── Requests/                # FormRequest validation classes
│   └── Resources/               # API resources (response shaping)
├── Models/                      # Eloquent models
├── Services/                    # business logic (not a Laravel default; create it)
├── Providers/                   # service providers (DI bindings)
└── Exceptions/Handler.php       # central exception handler
config/                          # config files (env-driven)
routes/api.php                   # API route definitions
.env, .env.example
```

Conventions: FormRequest classes for validation; Service classes for business logic; service providers for DI; Eloquent for models; `Handler::render` for centralized errors.

### C# / .NET (ASP.NET Core)

```
src/MyApp/
├── Program.cs                   # composition root (Minimal API or builder)
├── Controllers/                 # [ApiController] classes
│   └── UsersController.cs
├── Models/                      # entities
│   └── User.cs
├── DTOs/                        # request/response shapes
├── Services/                    # business logic (interfaces + impls)
│   ├── IUserService.cs
│   └── UserService.cs
├── Repositories/                # data access (or use EF Core directly)
├── Data/AppDbContext.cs
├── Middleware/
│   └── ExceptionMiddleware.cs
└── appsettings.json + appsettings.Development.json
```

Conventions: built-in DI registered in `Program.cs`; `[Authorize]` for auth; `IConfiguration` for env-driven config; `app.UseExceptionHandler` for centralized errors; user-secrets/Azure Key Vault for production secrets.

### Rust / Axum

```
.
├── Cargo.toml
└── src/
    ├── main.rs                  # composition root
    ├── config.rs                # env via dotenvy + serde
    ├── state.rs                 # AppState struct
    ├── error.rs                 # custom error enum + IntoResponse impl
    ├── routes.rs                # Router builder
    ├── handlers/
    │   ├── mod.rs
    │   ├── user.rs
    │   └── product.rs
    ├── services/
    │   ├── mod.rs
    │   └── user_service.rs
    ├── repository/
    │   ├── mod.rs
    │   └── user_repo.rs
    ├── domain/
    │   ├── mod.rs
    │   └── user.rs
    └── middleware/
        ├── mod.rs
        └── auth.rs
```

Conventions: `AppState` shared via `Arc`; tower middleware via `.layer(...)`; sqlx for compile-checked queries; `thiserror` for error types implementing `IntoResponse`.

---

## Abstract Layout Template (for stacks not listed above)

When the detected stack is not in the table, apply this responsibility-first layout. The **directory names** can change to match the language's conventions; the **responsibilities** stay the same.

```
<project_root>/
├── <entrypoint>                 # composition root: wires everything, no logic
├── config/                      # env-driven settings
├── models|domain/               # data shape + persistence access
├── controllers|services/        # business orchestration (HTTP-agnostic)
├── routes|views|handlers/       # HTTP boundary (request parsing + response shaping)
├── middlewares|filters|interceptors/  # cross-cutting concerns
└── utils|helpers|common/        # pure stateless helpers
```

Rules for naming:

- Use the term the host language's standard library or dominant framework uses. Examples:
  - Spring uses `service` (not `controller` for business logic).
  - Rails uses `app/services` (a community convention layered on top of MVC).
  - NestJS uses feature modules instead of a flat `controllers/` directory.
- Keep the names **plural** for collections of similar things (`controllers/` not `controller/`) **unless** the language's convention is singular (Go, Rust often prefer singular package names).
- Do NOT invent novel names. Use what readers of the language expect.

---

## Composition Root Pattern (language-agnostic recipe)

The composition root is the single place where the dependency graph is wired. It is **always** the entry point file.

The recipe, regardless of language:

1. Load configuration from environment.
2. Initialize cross-cutting infrastructure (logger, database connection, cache, message broker).
3. Construct repositories / models, injecting infrastructure.
4. Construct services / controllers, injecting repositories.
5. Construct route/handler bindings, injecting services.
6. Register middlewares / filters / interceptors.
7. Register the route bindings on the HTTP framework.
8. Start the server.

The composition root **never**: contains business logic, executes database queries, or has more than the orchestration above.

### Example A — Python / Flask

```python
# src/app.py
from flask import Flask
from src.config.settings import Config
from src.models.database import get_db
from src.models.product import ProductModel
from src.controllers.product_controller import ProductController
from src.routes.product_routes import product_bp, init_product_routes
from src.middlewares.error_handler import register_error_handlers

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db = get_db(Config.DB_PATH)                     # 2
    product_model = ProductModel(db)                # 3
    product_controller = ProductController(product_model)  # 4
    init_product_routes(product_controller)         # 5
    register_error_handlers(app)                    # 6
    app.register_blueprint(product_bp)              # 7
    return app

if __name__ == "__main__":
    create_app().run(host=Config.HOST, port=Config.PORT)  # 8
```

### Example B — Node.js / Express

```javascript
// src/app.js
const express = require('express');
const config = require('./config/settings');
const { createDatabase } = require('./config/database');
const ProductModel = require('./models/productModel');
const ProductController = require('./controllers/productController');
const productRoutes = require('./routes/productRoutes');
const errorHandler = require('./middlewares/errorHandler');

const db = createDatabase(config.dbPath);                   // 2
const productModel = new ProductModel(db);                  // 3
const productController = new ProductController(productModel); // 4

const app = express();
app.use(express.json());
app.use('/api/products', productRoutes(productController)); // 5,7
app.use(errorHandler);                                      // 6

app.listen(config.port);                                    // 8
```

### Example C — Go / Gin

```go
// main.go
package main

import (
    "log"
    "github.com/gin-gonic/gin"
    "example.com/app/internal/config"
    "example.com/app/internal/handler"
    "example.com/app/internal/middleware"
    "example.com/app/internal/repository"
    "example.com/app/internal/service"
)

func main() {
    cfg := config.Load()                                    // 1
    db := repository.NewDB(cfg.DSN)                         // 2
    productRepo := repository.NewProductRepo(db)            // 3
    productSvc := service.NewProductService(productRepo)    // 4
    productHandler := handler.NewProductHandler(productSvc) // 5

    r := gin.New()
    r.Use(middleware.Recovery(), middleware.ErrorHandler()) // 6
    productHandler.Register(r.Group("/api/products"))       // 7

    if err := r.Run(cfg.Addr); err != nil {                 // 8
        log.Fatal(err)
    }
}
```

The structure is identical across the three languages. Only the syntax differs.

---

## Mapping to Non-MVC-Native Architectures

Some ecosystems ship an opinionated architecture that already enforces separation. Refactoring **toward MVC** there is wrong; refactor **within** the existing architecture instead.

### Hexagonal / Ports-and-Adapters

Found in: many DDD-influenced Java/Kotlin projects, some Go and Rust projects.

Equivalence:

| MVC layer | Hexagonal equivalent |
|---|---|
| Models | Domain (entities, aggregates, value objects) |
| Controllers | Application services / Use cases |
| Routes | Inbound adapters (HTTP, CLI, message-broker consumers) |
| Persistence inside Models | Outbound adapters (repository implementations) |
| Configuration | Composition root + adapters configuration |

The skill should preserve the existing `domain/`, `application/`, `infrastructure/` directories and only fix anti-patterns *within* them. Do not collapse the structure into `models/controllers/routes/`.

### Clean Architecture

Found in: some larger Java, .NET, and TypeScript codebases.

Equivalence:

| MVC layer | Clean Architecture equivalent |
|---|---|
| Models | Entities + Use Case input/output models |
| Controllers | Use Cases / Interactors |
| Routes | Interface Adapters (Controllers in Clean's vocabulary) |
| Configuration | Frameworks & Drivers layer |
| Middlewares | Cross-cutting in the outermost layer |

Preserve the dependency direction (outer depends on inner, never reverse) when refactoring.

### CQRS / Event-Sourced

Found in: high-throughput systems, some .NET and Scala codebases.

Equivalence:

| MVC layer | CQRS equivalent |
|---|---|
| Controllers | Command handlers and query handlers (separate) |
| Models | Aggregates (write side) + read models (query side) |
| Routes | Endpoint that dispatches to command bus or query bus |

Keep the read/write split. Do not merge command and query handlers into a single controller.

### Modular Monolith / Feature-Sliced

Found in: NestJS, larger Spring Boot, Domain-driven Go projects.

Each feature directory contains its own MVC subset:

```
src/modules/users/
  ├── users.controller.ts
  ├── users.service.ts
  ├── users.repository.ts
  └── users.entity.ts
src/modules/orders/
  └── ...
```

Refactoring should preserve the feature boundaries. A finding within `users/` is fixed inside `users/`; do not extract into a top-level shared layer unless the duplication is genuine.

### Microservices in Monorepo

Found in: large polyglot monorepos.

Each service is independent. Refactor each service as if it were a standalone project. Do not enforce a shared layout across services unless the team has explicitly chosen one (e.g., a shared `internal/` toolkit).

---

## Adaptation Rules

When applying the target structure to an actual project:

1. **Detection drives layout.** Phase 1 picks which target structure to apply. Default to the abstract template if no match.
2. **Existing structure is data.** If the project already has, say, `app/services/` (Rails-style), keep it. Don't relocate to `controllers/` just to match a generic template.
3. **Preserve the API contract.** Original URL paths must continue working after refactoring. Original request/response shapes must be byte-equivalent unless a finding explicitly required a fix.
4. **Preserve the database schema.** Do not change table structures. Only change *how* they are accessed.
5. **One concern per file.** A file that grew to host two concerns gets split. A file with a single concern stays put even if it's small.
6. **Composition root last.** Wire dependencies after all other refactors complete; the composition root reflects the final shape, not an interim one.
