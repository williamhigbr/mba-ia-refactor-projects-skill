# Project Analysis — Detection Heuristics

This file gives the skill a deterministic procedure to identify the language, framework, persistence layer, architecture, and domain of any backend project — even one whose stack is not explicitly documented here.

The detection flow is:

1. **Language** — from file extensions, weighted by source-file count.
2. **Framework** — from the registry below; fall back to import/include heuristics.
3. **Dependency manifest** — confirms the ecosystem and yields version data.
4. **Database layer** — from ORM imports, raw drivers, schema files, or connection strings.
5. **Architecture** — from abstract criteria (file count, LOC distribution, layer leakage), not from language-specific rules.
6. **Domain** — from route names, model/table names, README, and identifier vocabulary.

If the framework is not in the registry, follow the **Unknown stack — fallback procedure** at the end of this file. Never abort.

---

## 1. Language Detection

Identify the primary language by file extensions present in the project, excluding files in `node_modules/`, `vendor/`, `.venv/`, `target/`, `build/`, `dist/`, `.git/`.

| Extension | Language |
|---|---|
| `.py`, `.pyi` | Python |
| `.js`, `.mjs`, `.cjs` | JavaScript (Node.js) |
| `.ts`, `.mts`, `.tsx` | TypeScript |
| `.rb`, `.rake` | Ruby |
| `.java` | Java |
| `.kt`, `.kts` | Kotlin |
| `.go` | Go |
| `.rs` | Rust |
| `.php` | PHP |
| `.cs` | C# / .NET |
| `.fs`, `.fsx` | F# / .NET |
| `.ex`, `.exs` | Elixir |
| `.erl` | Erlang |
| `.scala`, `.sc` | Scala |
| `.swift` | Swift |
| `.clj`, `.cljs` | Clojure |

The primary language is the one with the most source files. If two languages are tied or close (e.g., a TypeScript project that compiles to JavaScript), prefer the higher-level one (TypeScript over JavaScript, Kotlin over Java) when source files in both exist.

---

## 2. Framework Registry

This registry pairs each known framework with detection signals. Match in this order: **dependency manifest → import statements → idiomatic file names**.

If multiple frameworks match, use the one with the strongest signal in the dependency manifest.

### Python

| Framework | Manifest signal | Import signal | Idiomatic file |
|---|---|---|---|
| Flask | `flask` in `requirements.txt` / `pyproject.toml` | `from flask import` | `app.py` with `Flask(__name__)` |
| Django | `Django>=` in manifest | `from django` | `manage.py`, `settings.py`, `wsgi.py` |
| FastAPI | `fastapi` in manifest | `from fastapi import FastAPI` | `main.py` with `FastAPI()` |
| Pyramid | `pyramid` in manifest | `from pyramid.config` | `wsgi.py` |
| Tornado | `tornado` in manifest | `import tornado.web` | — |

### JavaScript / TypeScript (Node.js)

| Framework | Manifest signal | Import signal | Idiomatic file |
|---|---|---|---|
| Express | `"express"` in `package.json` | `require('express')` / `from 'express'` | `app.js` / `server.js` |
| Koa | `"koa"` in `package.json` | `require('koa')` | — |
| Fastify | `"fastify"` in `package.json` | `require('fastify')` | — |
| Hapi | `"@hapi/hapi"` in `package.json` | `require('@hapi/hapi')` | — |
| NestJS | `"@nestjs/core"` in `package.json` | `from '@nestjs/common'` | `main.ts`, `*.module.ts`, `*.controller.ts` |
| Next.js (API routes) | `"next"` in `package.json` | `from 'next'` | `pages/api/` or `app/api/` |

### Java / Kotlin (JVM)

| Framework | Manifest signal | Import signal | Idiomatic file |
|---|---|---|---|
| Spring Boot | `org.springframework.boot` in `pom.xml` / `build.gradle` | `import org.springframework.` | `*Application.java` with `@SpringBootApplication` |
| Quarkus | `io.quarkus` in manifest | `import io.quarkus.` / `import jakarta.ws.rs.` | — |
| Micronaut | `io.micronaut` in manifest | `import io.micronaut.` | — |
| Ktor (Kotlin) | `io.ktor` in manifest | `import io.ktor.` | — |
| Jakarta EE / Java EE | `jakarta.ws.rs` or `javax.ws.rs` | `@Path`, `@GET`, `@Produces` | — |

### Go

| Framework | Manifest signal (`go.mod`) | Import signal | Idiomatic file |
|---|---|---|---|
| Gin | `github.com/gin-gonic/gin` | `"github.com/gin-gonic/gin"` | `main.go` |
| Echo | `github.com/labstack/echo` | `"github.com/labstack/echo/v4"` | — |
| Fiber | `github.com/gofiber/fiber` | `"github.com/gofiber/fiber/v2"` | — |
| Chi | `github.com/go-chi/chi` | `"github.com/go-chi/chi/v5"` | — |
| net/http (stdlib) | (no third-party) | `"net/http"` with `http.HandleFunc` | — |

### Ruby

| Framework | Manifest signal (`Gemfile`) | Idiomatic file |
|---|---|---|
| Rails | `gem 'rails'` | `config/application.rb`, `app/controllers/` |
| Sinatra | `gem 'sinatra'` | `app.rb` with `require 'sinatra'` |
| Hanami | `gem 'hanami'` | `config/app.rb` |
| Roda | `gem 'roda'` | `config.ru` |
| Grape | `gem 'grape'` | `mounted under Rack` |

### Rust

| Framework | Manifest signal (`Cargo.toml`) | Import signal |
|---|---|---|
| Axum | `axum =` | `use axum::` |
| Actix-web | `actix-web =` | `use actix_web::` |
| Rocket | `rocket =` | `use rocket::` |
| Warp | `warp =` | `use warp::` |
| Tower / Hyper | `hyper =` / `tower =` | `use hyper::` |

### PHP

| Framework | Manifest signal (`composer.json`) | Idiomatic file |
|---|---|---|
| Laravel | `"laravel/framework"` | `artisan`, `app/Http/Controllers/` |
| Symfony | `"symfony/framework-bundle"` | `bin/console`, `config/services.yaml` |
| Slim | `"slim/slim"` | `public/index.php` with `Slim\App` |
| CodeIgniter | `"codeigniter4/framework"` | — |

### C# / .NET

| Framework | Manifest signal (`*.csproj`) | Idiomatic file |
|---|---|---|
| ASP.NET Core (MVC) | `Microsoft.AspNetCore.Mvc` | `Program.cs`, `Controllers/*.cs` |
| ASP.NET Core (Minimal API) | `Microsoft.AspNetCore.App` | `Program.cs` with `app.MapGet(...)` |
| ServiceStack | `ServiceStack` | — |

### Elixir

| Framework | Manifest signal (`mix.exs`) | Idiomatic file |
|---|---|---|
| Phoenix | `{:phoenix, ...}` | `lib/<app>_web.ex`, `lib/<app>_web/router.ex` |
| Plug (raw) | `{:plug, ...}` | — |

### Other ecosystems

| Framework | Language | Manifest |
|---|---|---|
| Spring (Scala) / Akka HTTP | Scala | `build.sbt` with `akka-http` |
| Vapor | Swift | `Package.swift` with `vapor` |
| Compojure / Pedestal | Clojure | `project.clj` / `deps.edn` |

### Version detection

Always extract the framework version when detectable. Sources:

- Python — pinned line in `requirements.txt` (`flask==3.1.1`), `[tool.poetry.dependencies]` in `pyproject.toml`, `Pipfile.lock`.
- Node.js — `dependencies.<name>` in `package.json`; the resolved version in `package-lock.json` or `yarn.lock`.
- Java / Kotlin — `<version>` in `pom.xml` or `id 'org.springframework.boot' version '...'` in `build.gradle`.
- Go — version line in `go.mod` (`require github.com/gin-gonic/gin v1.9.1`).
- Ruby — pinned line in `Gemfile` (`gem 'rails', '7.1'`) or `Gemfile.lock`.
- Rust — version in `Cargo.toml` and `Cargo.lock`.
- PHP — `require` block in `composer.json` and `composer.lock`.
- .NET — `<PackageReference Include="..." Version="..." />` in `*.csproj`.
- Elixir — `deps` function in `mix.exs` and `mix.lock`.

Report the version even if it's a range (`^4.18.2`, `>=3.0,<4.0`).

---

## 3. Dependency Manifest Detection

| File | Ecosystem |
|---|---|
| `requirements.txt`, `Pipfile`, `Pipfile.lock`, `pyproject.toml`, `setup.py`, `setup.cfg` | Python |
| `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` | Node.js |
| `Gemfile`, `Gemfile.lock`, `*.gemspec` | Ruby |
| `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle` | Java/Kotlin |
| `go.mod`, `go.sum` | Go |
| `Cargo.toml`, `Cargo.lock` | Rust |
| `composer.json`, `composer.lock` | PHP |
| `*.csproj`, `*.fsproj`, `*.sln`, `packages.config` | C#/.NET |
| `mix.exs`, `mix.lock` | Elixir |
| `Package.swift` | Swift |
| `build.sbt`, `project.scala` | Scala |
| `project.clj`, `deps.edn`, `shadow-cljs.edn` | Clojure |

If a project has no manifest file, it is either a stdlib-only project (Go, Python, single-file scripts) or a non-buildable artifact. Report `Dependencies: none detected` and continue.

---

## 4. Database Layer Detection

Look for these signals in order. Stop at the first strong match, but record all signals found.

### 4.1 ORM imports / declarations

| Ecosystem | ORM signals |
|---|---|
| Python | `from sqlalchemy`, `from peewee`, `from tortoise`, `from sqlmodel`, `from django.db import models` |
| Node.js | `require('sequelize')`, `require('typeorm')`, `require('prisma')`, `require('mongoose')`, `require('knex')` |
| Java | `@Entity` (JPA/Hibernate), `extends JpaRepository`, `@Repository` |
| Go | `gorm.io/gorm`, `github.com/jmoiron/sqlx`, `database/sql` with `sqlx.DB` |
| Ruby | `ActiveRecord::Base`, `Sequel.connect`, `gem 'sequel'` |
| Rust | `sqlx::query`, `diesel::table!`, `sea_orm::EntityTrait` |
| PHP | `Eloquent` / `Model` extends, `Doctrine\ORM\EntityManager` |
| C# / .NET | `DbContext`, `DbSet<T>`, EF Core attributes (`[Key]`, `[Table]`) |
| Elixir | `use Ecto.Schema`, `Ecto.Repo` |

### 4.2 Raw driver imports

`sqlite3`, `pg`, `mysql2`, `mongodb`, `cassandra-driver`, `redis`, `pymongo`, `psycopg2`, `mysqlclient`, `pq` (Go), `tokio-postgres` (Rust), `mysqli`/`PDO` (PHP), `Microsoft.Data.SqlClient` (.NET).

### 4.3 Schema artifacts

- Migration directories: `migrations/`, `db/migrate/`, `prisma/migrations/`, `priv/repo/migrations/`, `src/main/resources/db/migration/` (Flyway), `Migrations/` (.NET).
- `CREATE TABLE` statements in any source file.
- Entity classes annotated `@Entity`, `@Table`, `@Schema`, `defrecord`, etc.

### 4.4 Connection strings

`sqlite:///`, `postgres://`, `postgresql://`, `mysql://`, `mongodb://`, `redis://`, `jdbc:`, `Server=...;Database=...;` (.NET), `ecto://`.

### 4.5 Database files

`*.db`, `*.sqlite`, `*.sqlite3`, `*.mdb`, `*.accdb` in the project root or `data/` / `db/` directories.

### 4.6 Table-name extraction

Order of preference for naming the discovered tables:

1. Explicit `CREATE TABLE <name>` in source or migrations.
2. ORM model class names (Pluralize: `User` → `users` unless overridden).
3. Migration file names (e.g., `001_create_users.sql`).
4. Repository / DAO class names (`UserRepository` → `users`).

---

## 5. Architecture Classification

Classify using the abstract criteria below, **never** using language-specific rules.

### Monolith (no separation)

Any of these is sufficient:

- **≤ 4 source files total** AND no directory separation by responsibility.
- A single source file accounts for **> 40% of the project's source LOC**.
- Route declarations, business logic, and database queries co-occur within the same file or class for ≥ 2 unrelated domains.
- The entry point file directly contains > 5 route handlers/controller actions with embedded business logic.

### Partial MVC

- Some directory separation exists (e.g., `models/`, `routes/`, `controllers/`, or framework-equivalent like `app/controllers/` in Rails) **but** at least one of:
  - Business logic leaks into route handlers (handlers > 30 LOC routinely).
  - Database access happens outside the model layer (raw queries in controllers/routes).
  - Configuration/secrets are hardcoded in source instead of loaded from environment.
  - A required layer is missing entirely (no controllers, no centralized error handling, no config module).

### Full / Clean MVC (or framework-equivalent)

- All five responsibilities have a dedicated home (config, models, controllers, routes/views, middlewares).
- Route handlers are thin (≤ ~10 LOC, parse → call → respond).
- Models exclusively own data access.
- Controllers exclusively own business orchestration.
- Configuration is environment-driven.
- Centralized error handling exists.

### Other architectures (recognize and report, do not force MVC blindly)

- **Hexagonal / Ports-and-Adapters** — explicit `domain/`, `application/`, `infrastructure/` directories or `port`/`adapter` naming.
- **Clean Architecture** — `entities/`, `usecases/`, `interfaces/`, `frameworks/` layering.
- **CQRS / Event-sourced** — separate `commands/`, `queries/`, `events/` directories; uses an event bus.
- **Modular monolith** — feature-sliced modules each containing their own MVC subset.
- **Microservices in monorepo** — multiple service roots, each independently deployable.

If you detect one of these, **report it** in Phase 1 and adapt Phase 3 accordingly: enforcing MVC inside an already-Hexagonal codebase is a regression. The skill should preserve the existing architectural choice and only fix anti-patterns within it. See `mvc-architecture-guide.md` for the *Mapping to non-MVC native architectures* section.

---

## 6. Domain Detection

Infer the application domain from the strongest signal available, in this order:

1. **README / package description / `pyproject.toml [project] description` / `package.json description`** — often states the domain directly.
2. **Route paths** — `/products|/orders|/users` → e-commerce; `/courses|/enrollments` → LMS; `/tasks|/projects` → task management; `/posts|/comments` → social/blog; `/transactions|/accounts` → finance.
3. **Table names** — same mapping as routes.
4. **Identifier vocabulary** — domain terminology in function names, comments, and string literals.
5. **Localized terms** — Portuguese (`produtos`, `pedidos`, `usuarios`) → likely Brazilian-Portuguese codebase; flag in domain description.

Describe the domain in one sentence: `"E-commerce API (products, orders, users)"` or `"Task Manager (tasks, categories, users)"`.

---

## 7. Unknown Stack — Fallback Procedure

When the framework is not in the registry, OR the language has no entry above, follow this procedure. **Never abort.**

### Step 1 — Confirm the language

If the dominant extension is missing from §1, search for it on `https://en.wikipedia.org/wiki/List_of_programming_languages_by_type` (skip the network call; rely on prior knowledge). If still unknown, name it by extension: `Language: unknown (.xyz dominant)`.

### Step 2 — Probe for HTTP-server idioms

Search the source for any of these regex patterns (case-insensitive):

```
\brouter?\b
\bget\s*\(\s*["'`]
\bpost\s*\(\s*["'`]
\bput\s*\(\s*["'`]
\bdelete\s*\(\s*["'`]
\bhandle\b|\bhandler\b
\bmiddleware\b|\bfilter\b|\binterceptor\b
\bserver?\.listen\b|\bapp\.run\b|\bhttp\.serve\b
@(GET|POST|PUT|DELETE|PATCH|Path|RequestMapping|Route)
\bdef\s+\w+\s*\(\s*req|request|ctx|context\b
```

Any match indicates an HTTP-handling project. Record matched files as candidate route definitions.

### Step 3 — Probe for entry point

Look for, in this order:

1. A file named `main.*`, `app.*`, `server.*`, `index.*`, `Program.*`, or matching `*Application.*`.
2. A function named `main`, `start`, `run`, `bootstrap`, or annotated `@SpringBootApplication`/equivalent.
3. A top-level execution guard: `if __name__ == "__main__":`, `func main()`, `public static void main`, `fn main()`, `defmodule App.Application do`.

Record the most likely entry point.

### Step 4 — Probe for persistence

Run §4 detection broadly. Even unknown ecosystems usually reuse standard SQL string idioms or call out to known DB drivers via FFI or shell. If no match, record `Database: undetermined`.

### Step 5 — Honest reporting

In the Phase 1 summary, output:

```
Language:      <best guess>
Framework:     undetermined (probed: <list of probes that fired>)
Dependencies:  <whatever was found in any manifest>
Domain:        <inferred from routes/tables/strings>
Architecture:  <classified by abstract criteria from §5>
Source files:  <count>
DB tables:     <if detectable, else "undetermined">
```

**Do not fabricate a framework name.** "undetermined" is a valid and acceptable answer. The audit (Phase 2) and the refactor (Phase 3) can still proceed using abstract concepts — see `anti-patterns-catalog.md` and `refactoring-playbook.md`.

### Step 6 — Adaptation

When Phase 3 needs to produce idiomatic code for an unknown stack:

1. Identify the stack's idiomatic equivalents for: HTTP route declaration, middleware, dependency wiring, error handling, configuration loading, persistence access. Use the probes from Step 2 as anchors.
2. Apply the playbook's abstract recipe using those equivalents.
3. If a needed equivalent doesn't exist in the language (e.g., the language has no concept of middleware), document the gap explicitly in the Phase 3 output. Do not force a foreign idiom.

This procedure ensures the skill degrades gracefully on stacks it has no examples for, instead of silently misclassifying them as Python or Node.
