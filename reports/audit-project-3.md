================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   11 analyzed | ~750 lines of code

## Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Hardcoded Credentials
File: services/notification_service.py:8-9
Description: SMTP email credentials hardcoded directly in class constructor: `self.email_user = 'taskmanager@gmail.com'` and `self.email_password = 'senha123'`. These secrets are committed to source control.
Impact: Exposed credentials in repository history; anyone with repo access can impersonate the service email account.
Recommendation: Move to environment variables (`os.environ["SMTP_USER"]`, `os.environ["SMTP_PASSWORD"]`) and load via python-dotenv from a `.env` file excluded from version control.

### [CRITICAL] Insecure Password Hashing (MD5)
File: models/user.py:26-30
Description: User passwords are hashed using `hashlib.md5()` which is cryptographically broken for password storage — no salt, trivially reversible via rainbow tables.
Impact: All user passwords are vulnerable to mass compromise if the database is leaked. MD5 is a deprecated cryptographic hash for security purposes.
Recommendation: Replace with `werkzeug.security.generate_password_hash` / `check_password_hash` (bcrypt-based, already available via Flask) or use the `bcrypt` package directly.

### [HIGH] Business Logic in Route Handlers
File: routes/task_routes.py:12-60
Description: The `get_tasks()` route handler contains 50+ lines of inline logic: manual dict construction, overdue calculation, N+1 user/category lookups, and error handling — all in the route body.
Impact: Routes are untestable without HTTP context; logic is duplicated across handlers (same overdue calculation appears in 4 places); changes to business rules require modifying route files.
Recommendation: Extract task business logic into a `controllers/task_controller.py` that receives data and returns results; keep route handlers thin (parse → call → respond).

### [HIGH] N+1 Query Problem
File: routes/task_routes.py:40-52
Description: Inside the `get_tasks()` loop, each task triggers separate queries: `User.query.get(t.user_id)` and `Category.query.get(t.category_id)` — one per task, resulting in 2N+1 queries for N tasks.
Impact: Linear database query growth; a list of 100 tasks fires 201 queries. Severe performance degradation at scale.
Recommendation: Use SQLAlchemy eager loading: `Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()` to resolve all relationships in a single query.

### [HIGH] Hardcoded SECRET_KEY in App Config
File: app.py:13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` — the Flask secret key is hardcoded as a literal string. Despite `python-dotenv` being listed as a dependency, it is not used.
Impact: Session/cookie signing key is exposed in source; anyone can forge sessions. The key is the same across all environments.
Recommendation: Load from environment: `app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-change-me')` with fail-fast in production.

### [MEDIUM] Password Exposed in User Serialization
File: models/user.py:16-17
Description: `to_dict()` includes the password hash in its output: `'password': self.password`. This is returned in API responses (e.g., login endpoint returns full `user.to_dict()`).
Impact: Password hashes leak to any API consumer, facilitating offline cracking attacks.
Recommendation: Exclude `password` from `to_dict()` output; create a separate internal serialization if the hash is needed server-side.

### [MEDIUM] Duplicated Overdue Calculation Logic
File: routes/task_routes.py:26-36, routes/task_routes.py:71-79, routes/task_routes.py:215-221, routes/user_routes.py:131-139
Description: The same overdue-checking logic (`if t.due_date < datetime.utcnow() and status not in [done, cancelled]`) is copy-pasted in at least 4 locations across route files, plus a `is_overdue()` method on the Task model that is never used.
Impact: Any change to overdue rules requires finding and updating all copies; high risk of inconsistency.
Recommendation: Use the existing `Task.is_overdue()` method consistently, or move it to a controller/service that all routes call.

### [MEDIUM] Bare `except:` Clauses Swallowing All Errors
File: routes/task_routes.py:57, routes/task_routes.py:152, routes/task_routes.py:197
Description: Multiple handlers use bare `except:` without specifying exception type, catching and hiding all errors including `SystemExit` and `KeyboardInterrupt`. Error responses are generic strings with no logging.
Impact: Bugs are silently swallowed; debugging production issues becomes extremely difficult; no centralized error handling exists.
Recommendation: Catch specific exceptions (`except SQLAlchemyError`), add a centralized Flask `@app.errorhandler(Exception)` that logs errors and returns structured JSON.

### [LOW] Unused Imports
File: routes/task_routes.py:7
Description: `import json, os, sys, time` — none of these modules are used in the file.
Impact: Code noise; misleads readers about dependencies.
Recommendation: Remove unused imports.

### [LOW] Magic Strings for Status and Priority
File: routes/task_routes.py:94, routes/user_routes.py:62
Description: Status values (`'pending'`, `'in_progress'`, `'done'`, `'cancelled'`) and role values (`'user'`, `'admin'`, `'manager'`) are repeated as inline strings across multiple files, despite `utils/helpers.py` defining `VALID_STATUSES` and `VALID_ROLES` constants that are never imported.
Impact: Typos in status strings cause silent bugs; adding a new status requires finding all occurrences.
Recommendation: Import and use `VALID_STATUSES`/`VALID_ROLES` from `utils/helpers.py` consistently, or define an enum.

================================
Total: 10 findings
================================
