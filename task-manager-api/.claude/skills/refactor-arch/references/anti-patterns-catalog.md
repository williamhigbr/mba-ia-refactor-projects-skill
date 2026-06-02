# Anti-Patterns Catalog

This catalog defines anti-patterns as **language-agnostic concepts**. Each entry has:

- **Concept** — what the anti-pattern is, in terms applicable to any language.
- **Abstract detection signals** — patterns to look for that don't depend on a specific syntax.
- **Cross-reference** — points to the matching row in `cross-language-signals.md` for syntax-level signals across 8+ ecosystems.
- **Impact** — why it matters.
- **Recommendation** — what to do; cross-references the matching pattern in `refactoring-playbook.md`.

When auditing an unfamiliar stack, rely on the **Concept** and **Abstract detection signals**. Use the cross-reference grid only as supporting evidence when the stack is documented there.

---

## 1. God Class / God File

**Severity:** CRITICAL

**Concept:** A single source unit (file, class, module, package) that owns multiple unrelated responsibilities — data access, business rules, validation, formatting, transport — for two or more domains. Concretizes as a "junk drawer" where everything lives because there is no clear home for anything.

**Abstract detection signals:**

- A single source file exceeds **300 LOC** and references entities from **3+ domains** (e.g., users + products + orders).
- A single class exposes **10+ public methods** spanning unrelated concerns.
- A single source unit accounts for **> 30% of the project's total source LOC**.
- The same unit imports/uses both a database driver/ORM and an HTTP framework directly.
- Function/method clusters within the file have **no shared state** — a sign they belong in different modules.

**Cross-reference:** `cross-language-signals.md` §1.

**Impact:** Cannot test domains in isolation. Any change risks breaking unrelated functionality. Merge conflicts in team development. Hides circular reasoning in code review.

**Recommendation:** Split into one source unit per domain entity, with one layer per responsibility. See `refactoring-playbook.md` §1.

---

## 2. Hardcoded Credentials / Secrets

**Severity:** CRITICAL

**Concept:** Sensitive values — API keys, passwords, signing secrets, database credentials, payment-gateway keys — embedded as literal values in source code instead of injected from the environment. Once committed, the secret is permanently leaked even if removed in a later commit.

**Abstract detection signals:**

- String literals assigned to identifiers matching `secret`, `key`, `password`, `passwd`, `pwd`, `token`, `api[_-]?key`, `auth`, `private`.
- Database connection strings containing real credentials (`user:password@host`).
- Configuration variables in source files holding values that look like high-entropy random strings or recognizable key formats (e.g., `sk_live_...`, `pk_live_...`, `xoxb-...`, `ghp_...`, AWS access keys).
- Long alphanumeric strings (≥ 16 chars) assigned to a config-shaped name without environment indirection.
- Default fallback values that are functional secrets (e.g., `os.getenv("KEY") or "actual-secret-value"`).

**Cross-reference:** `cross-language-signals.md` §2.

**Impact:** Anyone with repository access compromises the system. Committed secrets cannot be revoked retroactively from git history without rewriting it. Audit logs and CI artifacts may also leak the value.

**Recommendation:** Move to environment variables; provide a `.env.example` with placeholders; ensure `.env` is gitignored. See `refactoring-playbook.md` §2.

---

## 3. SQL Injection / Query Injection

**Severity:** CRITICAL

**Concept:** Any control flow that interpolates user-controlled input into a structured query language (SQL, NoSQL query DSL, GraphQL, LDAP, XPath) without parameter binding. Attackers manipulate the query structure, not just its data.

**Abstract detection signals:**

- Any string-construction operator (concatenation, interpolation, format-string, template literal, `printf`-style formatter) building a query that includes a value reachable from request input.
- Calls to `execute(...)` / `query(...)` / equivalent where the argument is a built-up string rather than a query template + parameters tuple.
- Endpoints that accept raw query text in the request body and pass it to the database.
- ORM "raw" or "unsafe" escape hatches (e.g., `raw()`, `query()`, `exec()`) used with user input.
- Search/filter endpoints that build `WHERE` clauses dynamically from request fields without an allow-list.

**Cross-reference:** `cross-language-signals.md` §3.

**Impact:** Full database read/write/delete by any unauthenticated network client. May lead to RCE depending on the database engine and configuration.

**Recommendation:** Use parameterized queries (placeholders) or ORM methods that bind values. Remove any endpoint that accepts raw queries. See `refactoring-playbook.md` §3.

---

## 4. Business Logic in Routes / Handlers (Fat Handler)

**Severity:** HIGH

**Concept:** The HTTP transport layer (route handlers, controller actions, lambda functions) contains business rules, persistence calls, and response formatting in addition to its proper responsibility (request parsing and response shaping). The unit is impossible to test without an HTTP runtime, and the business logic is impossible to reuse from other transports (CLI, message queue, scheduled job).

**Abstract detection signals:**

- A route/handler function exceeds **30 LOC** of body (excluding signature and braces).
- A route/handler contains direct calls to a database driver, ORM, or repository.
- A route/handler implements branching business rules (pricing, status transitions, permission checks not delegated to middleware).
- The handler signature accepts request/response objects but the body contains pure-domain logic that doesn't touch them for most of its length.
- The same business decision appears in two or more route handlers (copy-pasted because there's no shared controller).

**Cross-reference:** `cross-language-signals.md` §4.

**Impact:** Business logic cannot be unit-tested without HTTP scaffolding. Cannot be reused from non-HTTP entry points. Routes become unreadable. Onboarding cost grows linearly with handler size.

**Recommendation:** Extract business logic to a controller/service layer that knows nothing about HTTP. Routes shrink to: parse → call → respond. See `refactoring-playbook.md` §4.

---

## 5. Tight Coupling / No Dependency Injection

**Severity:** HIGH

**Concept:** Modules construct or import their concrete dependencies internally rather than receiving them as parameters. The dependency graph is implicit and rigid; swapping implementations or substituting test doubles requires changing source code.

**Abstract detection signals:**

- Database connections, HTTP clients, or external-service clients instantiated **inside** functions/methods that should be configurable.
- Top-level (module-scoped) mutable singletons providing cross-cutting services (DB, cache, logger).
- A class constructor with **zero parameters** despite the class needing collaborators (constructor secretly imports and wires its own deps).
- Hardcoded paths or URLs to external services baked into business logic.
- No discernible "composition root" — no single file that wires the dependency graph.

**Cross-reference:** `cross-language-signals.md` §5.

**Impact:** Cannot test without real infrastructure. Cannot swap implementations (e.g., production DB → test DB → in-memory DB). Hidden coupling causes spooky-action-at-a-distance bugs. Forces integration tests where unit tests would suffice.

**Recommendation:** Pass collaborators as constructor or function parameters. Build the dependency graph in the composition root. See `refactoring-playbook.md` §5.

---

## 6. N+1 Query Problem

**Severity:** MEDIUM

**Concept:** Code retrieves a collection of N items, then issues an additional query per item to fetch related data. The result is **1 + N** (or worse, **1 + N×M**) round-trips when a single batch query (JOIN, `WHERE id IN (...)`, eager-loading) would suffice.

**Abstract detection signals:**

- Any database call appearing inside a `for`/`while`/`forEach`/`map` loop body.
- Lazy-loading attribute access on ORM relationships inside an iteration.
- Two or more database calls separated only by a loop construct over a previously-fetched collection.
- Pattern: `parents = db.fetch(...) ; for parent in parents: child = db.fetch_by_id(parent.child_id, ...)`.

**Cross-reference:** `cross-language-signals.md` §6.

**Impact:** Performance degrades linearly (or worse) with data size. Acceptable in tests with 10 rows; catastrophic with 100,000.

**Recommendation:** Replace with a single JOIN, a batch `WHERE id IN (...)` query, or the ORM's eager-loading mechanism. See `refactoring-playbook.md` §6.

---

## 7. Missing Input Validation

**Severity:** MEDIUM

**Concept:** Request data is consumed by business logic or persistence without checking for presence, type, format, range, or length. Trust placed in unauthenticated network input is the root of countless vulnerabilities and crashes.

**Abstract detection signals:**

- Any access to request body / query string / route parameter that flows to a database call, file system call, or business decision **without** an intermediate type check, length check, or format check.
- Use of language-specific "loose" type coercions on request input (`Number(...)`, `int(...)`, `parseInt(...)`) without bounds checking.
- Lack of a validation library or hand-rolled validation function in the project.
- Field names in handlers that don't match documented API contract field names (often signals undocumented, unvalidated inputs).

**Cross-reference:** `cross-language-signals.md` §7.

**Impact:** Crashes on malformed input. Storage of garbage data. Vector for downstream injection attacks. Inconsistent error responses confuse API consumers.

**Recommendation:** Validate at the boundary between transport and business layers. Reject early with structured error responses. Use a validation library when available. See `refactoring-playbook.md` §7.

---

## 8. Deprecated API Usage

**Severity:** MEDIUM

**Concept:** Code uses APIs the platform owner has marked deprecated, scheduled for removal, or superseded by a safer/faster alternative. The project still works today but accumulates technical debt and may break on the next major version upgrade.

**Abstract detection signals (cross-language):**

- Imports / uses of symbols documented as deprecated in the framework's official changelog or release notes.
- Use of polyfill libraries no longer needed because the host language adopted the feature (e.g., body-parser in Node, six in Python 3).
- Symbols annotated `@Deprecated` (Java), `@deprecated` (JSDoc / PHP), `[Obsolete]` (.NET), `#[deprecated]` (Rust), `Deprecation` warnings emitted at runtime.
- Synchronous variants where async equivalents exist (`fs.readFileSync` in async contexts; blocking calls inside Tokio tasks).
- Cryptographic primitives now considered weak: MD5 or SHA-1 for password hashing; DES/3DES for encryption; ECB cipher mode; static IVs.
- `eval` / dynamic `exec` for parsing structured data when a parser is available.
- HTTP/1.0 idioms in HTTP/2-aware frameworks; `XMLHttpRequest` patterns when `fetch` is canonical.

**Cross-reference:** `cross-language-signals.md` §8 (per-framework deprecation lists).

**Impact:** Silent breakage on the next major upgrade. Known-weak cryptography puts users at risk today. Code reviews waste time on outdated patterns.

**Recommendation:** Replace each deprecated symbol with its current equivalent. When migration is non-trivial, document the change inline. See `refactoring-playbook.md` §8.

---

## 9. Magic Numbers and Strings

**Severity:** LOW

**Concept:** Numeric literals or repeated string constants appear in business logic with no name explaining their meaning. The intent lives in the author's head, not in the code.

**Abstract detection signals:**

- Numeric literals other than `0`, `1`, `-1` appearing inside conditions, calculations, retry counts, timeouts, or thresholds.
- The same string literal (`"pending"`, `"PAID"`, `"admin"`) appearing in three or more places without a shared constant.
- Tier/threshold values (`> 1000`, `>= 0.05`) embedded in pricing or scoring logic.
- HTTP status codes used as raw integers rather than named constants.

**Cross-reference:** `cross-language-signals.md` §9.

**Impact:** Difficult to understand intent; easy to introduce inconsistencies when values change in one place but not another.

**Recommendation:** Extract to named constants or configuration entries; group by domain (pricing rules, retry policy, status enumerations). See `refactoring-playbook.md` §9.

---

## 10. Poor Naming Conventions

**Severity:** LOW

**Concept:** Identifiers (variables, functions, types, files) have names that fail to communicate their purpose. Cognitive load shifts from reading to deciphering.

**Abstract detection signals:**

- Single-letter variable names outside loop counters (`i`, `j`, `k` are fine; `u`, `e`, `p` for "user, email, password" are not).
- Cryptic abbreviations not part of the host language's standard vocabulary (`usr`, `eml`, `pwd`, `cid`).
- Generic placeholder names in production code: `data`, `result`, `temp`, `info`, `obj`, `manager`, `handler`, `helper`, `util` (when overly broad).
- Inconsistent naming style mixing within a single file (e.g., camelCase and snake_case alternating).
- Mixed natural language for domain terms (e.g., Portuguese function names alongside English ones).

**Cross-reference:** `cross-language-signals.md` §10.

**Impact:** Slows code review and onboarding. Reduces searchability across the codebase. Encourages copy-paste rather than reuse.

**Recommendation:** Rename to descriptive, intent-revealing names following the language's idiomatic style guide. See `refactoring-playbook.md` §10.

---

## 11. Unprotected Destructive Endpoints

**Severity:** HIGH

**Concept:** Administrative or destructive operations — `DELETE`, database reset, raw query execution, bulk update — are exposed over the network without authentication, authorization, or environment gating.

**Abstract detection signals:**

- Route paths matching `/admin`, `/debug`, `/dev`, `/reset`, `/wipe`, `/raw[_-]?query`, `/console`.
- HTTP `DELETE` handlers without a discernible auth check, role check, or middleware.
- Any endpoint that accepts and executes free-form SQL/NoSQL queries from the request.
- Endpoints that drop, truncate, or recreate tables without environment guards (e.g., enabled only in production-equivalent configurations).
- Migration endpoints exposed at runtime in production builds.

**Cross-reference:** `cross-language-signals.md` §11.

**Impact:** Any unauthenticated network client can destroy data or own the database. Discovery is automated by widely-distributed scanners.

**Recommendation:** Remove raw-query endpoints entirely. Gate destructive operations behind authentication, role checks, and environment flags (e.g., `ALLOW_DB_RESET=true` only in dev). See `refactoring-playbook.md` §9 / §11.

---

## 12. No Error Handling / Bare Exceptions

**Severity:** MEDIUM

**Concept:** Errors are either silently swallowed (bare `catch`/`except` with no action), allowed to crash the process unhandled, or returned to clients with raw internal details that leak architecture and aid attackers. There is no centralized error pipeline.

**Abstract detection signals:**

- `catch`/`except` blocks with empty bodies or just a `return` / `pass` / `continue`.
- Error responses that include stack traces, raw exception messages, or SQL error text.
- No global error-handling middleware/filter registered with the HTTP framework.
- Inconsistent error response shapes across endpoints (some return JSON, some return plain text, some return HTML).
- Logging of errors without preserving the original context (e.g., `logger.error("failed")` discarding `err`).

**Cross-reference:** `cross-language-signals.md` §12.

**Impact:** Bugs become silent; debugging becomes archaeology. Error-detail leakage helps attackers map internals. Inconsistent shapes confuse API consumers.

**Recommendation:** Register a centralized error handler. Catch specific error types when meaningful. Log full details internally; return safe, structured messages to clients. See `refactoring-playbook.md` §10.

---

## 13. Synchronous I/O in Asynchronous Context

**Severity:** MEDIUM

**Concept:** A blocking I/O call (file read, network call, sleep, CPU-bound loop) executes inside an event-loop or coroutine-based runtime that expects all operations to yield control. The blocking call freezes every concurrent task on the same loop.

**Abstract detection signals:**

- A sync I/O primitive (`fs.readFileSync`, `time.sleep`, `Thread.sleep`, blocking `recv`) inside an `async`/`await` function or a Promise/Task chain.
- Long-running CPU loops in handlers without yielding (`for` loops over millions of items inline).
- Use of synchronous DB drivers from within async handlers (e.g., `psycopg2` in `asyncio` code; `sqlite3` Node module's sync API in an async route).
- Mixing async-first frameworks (FastAPI, Tornado, Tokio, Vert.x) with non-async libraries that block on `await`.
- Lack of `async`/`await` annotation on functions performing obvious I/O when the framework supports it.

**Cross-reference:** `cross-language-signals.md` §13.

**Impact:** One slow call freezes the entire process for all concurrent users. Apparent performance is acceptable under low load, then collapses non-linearly under contention. Misdiagnosed as "the framework is slow" when the real cause is one blocking call.

**Recommendation:** Replace sync calls with their async equivalents. Run unavoidably blocking work on a worker thread/pool (`asyncio.to_thread`, `tokio::spawn_blocking`, `Promise.resolve().then(...)` is **not** sufficient). See `refactoring-playbook.md` §13.

---

## 14. Mutable Shared State Without Synchronization

**Severity:** HIGH

**Concept:** Multiple concurrent execution units (threads, goroutines, async tasks, processes) read and write the same in-memory state without locks, atomic operations, channels, or other synchronization. Generalizes the "global mutable state" issue from single-threaded code to a correctness bug under any real concurrency.

**Abstract detection signals:**

- Module-level / static / package-scoped mutable variables touched from multiple handlers, goroutines, threads, or async tasks.
- Singleton caches/maps/lists with no associated mutex, RWLock, or atomic compare-and-swap.
- Global counters (`totalRevenue++`, `requestCount += 1`) accessed from concurrent handlers.
- Mutable instance fields on a singleton service registered as a long-lived component (e.g., `@Component`/`@Service` in Spring, `app.locals` in Express).
- "Working memory" maps that accumulate per-request data with no eviction policy.

**Cross-reference:** `cross-language-signals.md` §14.

**Impact:** Race conditions cause sporadic data corruption, lost updates, and stale reads. Bugs are intermittent, hard to reproduce, and disappear under a debugger. Memory-leak risk as caches grow unbounded.

**Recommendation:** Eliminate the shared state when possible (compute from the database). When state is truly needed, protect with the language's standard concurrency primitive (mutex, atomic, channel, immutable snapshot). For caches, use a proper cache library with eviction. See `refactoring-playbook.md` §14.

---

## How to use this catalog

1. For every source file in the project, walk through the catalog and check each abstract signal against the code.
2. When the detected stack is in `cross-language-signals.md`, use that file's row as supporting syntax-level evidence.
3. When the stack is **not** documented, rely solely on the abstract signals — they are designed to apply to any language.
4. Record one finding per **distinct location**: if the same anti-pattern appears in five files, that's five findings.
5. Severity is fixed per pattern except when context modifies it: deprecated APIs in cryptographic code escalate to HIGH or CRITICAL; sync I/O on a request-critical path can escalate to HIGH if it visibly impacts users.
