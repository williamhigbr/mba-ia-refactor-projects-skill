# Project Analysis — Detection Heuristics

## Language Detection

Identify the primary language by file extensions present in the project:

| Extension | Language |
|---|---|
| `.py` | Python |
| `.js`, `.mjs`, `.cjs` | JavaScript (Node.js) |
| `.ts`, `.mts` | TypeScript |
| `.rb` | Ruby |
| `.java` | Java |
| `.go` | Go |
| `.php` | PHP |

If multiple languages are present, the primary language is the one with the most source files (excluding config/build files).

## Framework Detection

Scan import statements and dependency files for framework signals:

### Python
| Signal | Framework |
|---|---|
| `from flask import` or `import flask` | Flask |
| `from django` or `import django` | Django |
| `from fastapi import` or `import fastapi` | FastAPI |

### JavaScript/TypeScript
| Signal | Framework |
|---|---|
| `require('express')` or `from 'express'` | Express |
| `require('koa')` or `from 'koa'` | Koa |
| `require('fastify')` or `from 'fastify'` | Fastify |
| `require('hapi')` or `from '@hapi/hapi'` | Hapi |

### Version Detection
- Python: check `requirements.txt`, `Pipfile`, `pyproject.toml` for pinned versions
- Node.js: check `package.json` `dependencies` field for version ranges

## Dependency File Detection

| File | Ecosystem |
|---|---|
| `requirements.txt`, `Pipfile`, `pyproject.toml` | Python |
| `package.json`, `package-lock.json` | Node.js |
| `Gemfile` | Ruby |
| `pom.xml`, `build.gradle` | Java |
| `go.mod` | Go |
| `composer.json` | PHP |

## Database Detection

Look for these signals in order of priority:

1. **ORM imports:** `from sqlalchemy`, `from peewee`, `require('sequelize')`, `require('mongoose')`
2. **Raw DB drivers:** `import sqlite3`, `require('sqlite3')`, `require('pg')`, `require('mysql2')`
3. **DB files:** `*.db`, `*.sqlite`, `*.sqlite3` in project root
4. **Connection strings:** patterns like `sqlite:///`, `postgres://`, `mongodb://`
5. **Table creation:** `CREATE TABLE` statements in source code

### Table Name Extraction
- From `CREATE TABLE {name}` statements
- From ORM model class names (usually plural of the class)
- From migration files if present

## Architecture Classification

Classify the current architecture based on these criteria:

### Monolith (no separation)
- All logic in ≤4 files
- No directory structure for separation of concerns
- Route handlers contain DB queries, business logic, and response formatting
- Single entry point file does everything or delegates to one "god" module

### Partial MVC
- Some directory separation exists (e.g., `models/`, `routes/`)
- But responsibilities leak across layers (business logic in routes, DB in controllers)
- Missing one or more key layers (no controllers, no proper models)

### Layered / Full MVC
- Clear `models/`, `controllers/`, `routes/` (or equivalent) directories
- Each layer has a single responsibility
- Entry point only wires things together

## Domain Detection

Infer the application domain by examining:

1. **Route paths:** `/products`, `/users`, `/orders` → E-commerce; `/tasks`, `/projects` → Task management
2. **Table/model names:** `courses`, `enrollments` → LMS/Education; `payments` → Financial
3. **README or package description:** Often states the domain directly
4. **Variable naming patterns:** Domain-specific terminology in function/variable names

Describe the domain concisely, e.g.: "E-commerce API (products, orders, users)" or "Task Manager (tasks, categories, users)"
