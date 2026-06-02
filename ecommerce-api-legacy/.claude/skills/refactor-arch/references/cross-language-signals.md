# Cross-Language Signal Grid

Each section below corresponds to an entry in `anti-patterns-catalog.md` (same numbering). Use this file when auditing a project whose stack is documented here. For undocumented stacks, fall back to the abstract signals in the catalog.

Columns:

- **Bad signal** — concrete example of code that triggers this anti-pattern.
- **Good signal** — concrete example of the corrected pattern (what to look for to confirm it's *not* this anti-pattern).

Languages covered (consistent across all sections):

1. Python — Flask / FastAPI / Django / SQLAlchemy / psycopg2 / sqlite3
2. JS/TS (Node.js) — Express / Koa / NestJS / Sequelize / Prisma / sqlite3 / pg
3. Java / Kotlin — Spring Boot / JPA / JDBC
4. Go — Gin / Echo / net/http / database/sql / GORM
5. Ruby — Rails / Sinatra / ActiveRecord / Sequel
6. PHP — Laravel / Symfony / PDO / Eloquent
7. C# / .NET — ASP.NET Core / EF Core / Dapper
8. Rust — Axum / Actix-web / sqlx / Diesel

---

## §1 — God Class / God File

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `models.py` (300+ LOC) with `class Everything:` mixing user, product, order CRUD + business rules | One file per domain in `models/`, plus separate `controllers/` and `routes/` |
| JS/TS | `AppManager.js` class with route registration + DB calls + payment logic + audit | Domain-specific files: `models/userModel.js`, `controllers/checkoutController.js`, `routes/checkoutRoutes.js` |
| Java | One `@Service` or `@Controller` class with 20+ public methods spanning multiple aggregates | Per-aggregate `@Service` and `@RestController` classes; thin controllers |
| Go | `main.go` containing `http.HandleFunc` calls + SQL queries + business logic + struct definitions | Packages per domain (`internal/user`, `internal/order`), each with its own handler/service/repo files |
| Ruby | A single `app.rb` (Sinatra) doing routing + ActiveRecord CRUD + view rendering for many resources | Rails: per-resource controller in `app/controllers/`; Sinatra: extract modular apps under `lib/` |
| PHP | `App.php` with all controllers as static methods, plus DB connection management | Per-resource controllers in `app/Http/Controllers/`; service classes for business logic |
| C# / .NET | `HomeController.cs` with 30+ actions for multiple domains and direct DbContext use | Per-aggregate `*Controller` and `*Service` classes; repositories abstract DB access |
| Rust | `main.rs` with all routes, handlers, and database calls inline in one file | Module split: `mod handlers; mod services; mod models;` with submodules per domain |

---

## §2 — Hardcoded Credentials / Secrets

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `app.config["SECRET_KEY"] = "literal-value"` / `password = "abc123"` | `os.environ["SECRET_KEY"]` / `os.getenv("SECRET_KEY", "change-me")` reading from `.env` |
| JS/TS | `const apiKey = "sk_live_..."` / `process.env.X || "actual-secret"` | `process.env.API_KEY` with fail-fast if absent; `.env.example` committed |
| Java | `@Value("static-secret")` literal / hardcoded JDBC URL with credentials | `@Value("${app.secret}")` resolved from `application-{env}.yml` and env vars; Spring profiles |
| Go | `const SecretKey = "abc"` / `dsn := "user:pass@/db"` | `os.Getenv("SECRET_KEY")`; `viper` or `envconfig` reading from env |
| Ruby | `SECRET = "abc"` in `config/initializers/` / `database.yml` with literal password | `ENV.fetch("SECRET_KEY_BASE")`; Rails encrypted credentials (`config/credentials.yml.enc`) |
| PHP | `define("API_KEY", "abc")` / DB password in `config.php` | `getenv("API_KEY")` / `env("API_KEY")` (Laravel) reading from `.env` |
| C# / .NET | `appsettings.json` committed with real production secrets | `appsettings.Development.json` for placeholders; user-secrets / Azure Key Vault for real values; `IConfiguration` indirection |
| Rust | `const KEY: &str = "abc"` / hardcoded in `lazy_static!` | `std::env::var("KEY")` or `dotenvy` crate reading from `.env` |

---

## §3 — SQL Injection / Query Injection

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `cursor.execute(f"SELECT * FROM t WHERE id={x}")` / `"… %s" % x` / `"…" + x` | `cursor.execute("SELECT … WHERE id = ?", (x,))` / `cursor.execute("… %s", (x,))` (psycopg2 binds when passed as tuple) |
| JS/TS | `` db.query(`SELECT … WHERE id = ${x}`) `` / `db.run("… " + x)` | `db.query("SELECT … WHERE id = ?", [x])` / `db.query("… $1 …", [x])` (pg) / Prisma `where: { id: x }` |
| Java | `Statement.executeQuery("… " + x)` | `PreparedStatement.setString(1, x)` and `?` placeholders; JPA Criteria API; `@Query` with named params |
| Go | `db.Exec(fmt.Sprintf("…%s…", x))` | `db.Exec("… ? …", x)` / `db.Query("… $1 …", x)` (pq/pgx) / `gorm.Where("id = ?", x)` |
| Ruby | `User.where("name = '#{params[:name]}'")` / `find_by_sql("… #{x}")` | `User.where("name = ?", params[:name])` / `User.where(name: params[:name])` |
| PHP | `mysqli_query($db, "SELECT * FROM t WHERE id=$id")` / `$pdo->query("… $x")` | `$stmt = $pdo->prepare("… ?"); $stmt->execute([$x]);` / Eloquent `Model::where('id', $x)` |
| C# / .NET | `cmd.CommandText = $"SELECT … {x}"` / Dapper `Query($"… {x}")` | `cmd.Parameters.AddWithValue("@id", x)` / Dapper `Query("…@id…", new { id = x })` / EF Core LINQ |
| Rust | `format!("SELECT … {}", x)` passed to `sqlx::query` | `sqlx::query!("SELECT … WHERE id = $1", x)` / `diesel::dsl::sql_query(...).bind(...)` |

---

## §4 — Business Logic in Routes / Handlers

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | Flask: `@app.route(...)` body of 50+ LOC with `cursor.execute` + branching | Route calls `controller.create(data)`; controller returns `(payload, status)`; route returns `jsonify(payload), status` |
| JS/TS | Express: `app.post('/x', (req, res) => { /* 60 LOC */ })` | `router.post('/x', async (req,res,next) => { try { const r = await ctrl.do(req.body); res.json(r); } catch(e){next(e)} })` |
| Java | `@PostMapping` method 80+ LOC with `entityManager.persist` + business rules | `@PostMapping` delegates to a `@Service` that owns the logic; controller is 5–10 LOC |
| Go | `func handler(c *gin.Context) { /* 100 LOC */ }` | Handler reads input via `c.Bind(...)`, calls `service.Do(ctx, in)`, writes `c.JSON(...)` |
| Ruby | Rails: `def create; ... 40 LOC of business logic ...; end` in controller | `def create; result = UseCase.call(params); render json: result; end` — logic in `app/services/` |
| PHP | Laravel: controller method with `DB::table(...)` + business decisions inline | Service classes injected into controller via constructor; controller delegates |
| C# / .NET | Action method with EF Core queries, branching, response shaping in 60+ LOC | Action calls a `MediatR` handler / service; action is 3–5 LOC |
| Rust | Axum handler closure 80+ LOC with sqlx queries and conditional logic | Handler calls `service::do_thing(state, input).await?` and serializes the result |

---

## §5 — Tight Coupling / No Dependency Injection

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | Functions that call `get_db()` / `connect()` internally with no parameter | Class accepts `db` in `__init__`; FastAPI uses `Depends(...)`; composition root wires everything |
| JS/TS | Class constructor: `this.db = new sqlite3.Database(':memory:')` | Constructor takes `db` parameter; `new UserModel(db)` from composition root; NestJS `@Injectable()` |
| Java | `new ProductService()` (no Spring) / `Class.forName(...)` for JDBC inside service | `@Service` with constructor injection; `@Autowired` removed in favor of constructor params |
| Go | Package-level `var db *sql.DB` initialized in `init()` and used everywhere | Pass `*sql.DB` (or repository interface) into handler/service constructors |
| Ruby | Singleton service that lazy-instantiates dependencies (`@@cache ||= ...`) | Pass collaborators in initializer; in Rails, use Plain Old Ruby Objects with explicit deps |
| PHP | `new \PDO(...)` inside controller methods | Constructor injection via Laravel container / Symfony service container |
| C# / .NET | `new DbContext()` inside controllers / services | Constructor injection via built-in DI; register in `Program.cs` |
| Rust | Hardcoded DB connection in `main`; handlers reach into static globals | Pass `Arc<AppState>` via Axum's `State<...>`; build state at startup |

---

## §6 — N+1 Query Problem

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | SQLAlchemy: `for t in tasks: t.user.name` triggers per-iteration query | `tasks = session.query(Task).options(joinedload(Task.user)).all()` |
| JS/TS | Sequelize: `tasks.forEach(t => User.findByPk(t.user_id))` | `Task.findAll({ include: [User] })` / single `WHERE id IN (?)` query |
| Java | JPA: lazy `task.getUser()` inside a loop | `@EntityGraph` on the repository method; `JOIN FETCH` in JPQL; `findAllWithUsers()` |
| Go | `for _, t := range tasks { db.Get(&u, "… WHERE id = ?", t.UserID) }` | `db.Select(&users, "… WHERE id IN (?)", userIDs)` / GORM `.Preload("User")` |
| Ruby | `Task.all.map { |t| t.user.name }` (lazy ActiveRecord association) | `Task.includes(:user).all` / `.preload(:user)` |
| PHP | Eloquent: iterating tasks and accessing `$task->user` per row | `Task::with('user')->get()` (eager loading) |
| C# / .NET | EF Core: `tasks.ToList()` then `t.User.Name` triggers per-row query | `_db.Tasks.Include(t => t.User).ToList()` |
| Rust | sqlx: loop calling `query_as!("…", task.user_id)` per task | Single `query_as!("… WHERE id = ANY($1)", &user_ids)` |

---

## §7 — Missing Input Validation

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `data = request.get_json(); name = data["name"]` then DB insert with no checks | Pydantic / marshmallow schema validates incoming dict; FastAPI uses typed body params |
| JS/TS | `const x = req.body.x; await Model.create({ x })` | `zod` / `joi` / `class-validator` (NestJS) schema validates before processing |
| Java | `@RequestBody UserDto u` without bean validation annotations | DTO fields annotated `@NotNull`, `@Email`, `@Size`; `@Valid` on the parameter |
| Go | `c.BindJSON(&in)` then use without checks | `c.ShouldBindJSON(&in)` followed by `validate.Struct(in)` (`go-playground/validator`) |
| Ruby | `params[:user][:email]` used directly in queries | Strong parameters in Rails: `params.require(:user).permit(:email)` plus model validations |
| PHP | `$request->input('email')` used directly | Laravel `FormRequest` with `rules()` method; Symfony validators on DTOs |
| C# / .NET | `[FromBody] Dto d` used without DataAnnotations | `[Required]`, `[EmailAddress]`, `[StringLength]` on DTO + `ModelState.IsValid` check |
| Rust | Axum: `Json(payload): Json<T>` without validation | `validator` crate via `#[derive(Validate)]`; call `payload.validate()?` |

---

## §8 — Deprecated API Usage

| Stack | Concrete deprecations to flag |
|---|---|
| Python / Flask | `from flask.ext.*` (gone since Flask 1.0); `flask.json.dumps` patterns superseded by `flask.json.provider`; `app.before_first_request` deprecated in Flask 2.3 |
| Python / Django | `django.utils.encoding.smart_text` (use `smart_str`); `django.conf.urls.url` (use `re_path`/`path`) |
| Python / FastAPI | `Depends` patterns using deprecated `Body(...)` shortcuts; `event handlers` (use lifespan context) |
| JS/TS / Express | `body-parser` package (built-in since 4.16: `express.json()`); `req.connection` (use `req.socket`) |
| JS/TS / Node | `new Buffer(x)` (use `Buffer.from(x)`); `url.parse` (use `URL` constructor); `crypto.createCipher` (use `createCipheriv`) |
| JS/TS / NestJS | `HttpException` constructors with positional args (use object form) |
| Java / Spring | `WebSecurityConfigurerAdapter` (deprecated in Spring Security 5.7+); `@RequestMapping` without explicit method (prefer `@GetMapping`/etc.) |
| Java / general | `java.util.Date` (prefer `java.time.*`); `Class.newInstance()` (use `Class.getDeclaredConstructor().newInstance()`); MD5/SHA-1 for security |
| Go | `ioutil.ReadFile` (use `os.ReadFile` since Go 1.16); `ioutil.ReadAll` (use `io.ReadAll`); `rand.Seed` (use `rand.New(rand.NewSource(...))`) |
| Ruby / Rails | `update_attributes` (use `update`); `before_filter` (use `before_action` since Rails 5); `attr_accessible` (replaced by strong params) |
| PHP / Laravel | `Input::get()` (use `request()->input()`); `mcrypt_*` (replaced by `openssl` / `sodium`); `array_*` patterns superseded by `Arr::*` helpers |
| C# / .NET | `WebHost.CreateDefaultBuilder` (use `WebApplication.CreateBuilder`); `Newtonsoft.Json` defaulting (use `System.Text.Json`); sync `Stream` methods in async code |
| Rust | `std::mem::uninitialized` (use `MaybeUninit`); `try!` macro (use `?` operator); `tokio::macros::main` v0 patterns |
| Cross-language | MD5/SHA-1 for password hashing (use bcrypt/argon2/PBKDF2); DES/3DES (use AES-GCM/ChaCha20-Poly1305); ECB mode (use GCM/CBC+HMAC); `eval()` for parsing structured data |

---

## §9 — Magic Numbers and Strings

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `if amount > 10000: discount = amount * 0.1` | `if amount > DISCOUNT_TIER_1: discount = amount * DISCOUNT_RATE_1` (constants module) |
| JS/TS | `setTimeout(retry, 3000)` / `if (status === "PAID")` | `setTimeout(retry, RETRY_DELAY_MS)` / `if (status === PaymentStatus.Paid)` |
| Java | `if (status.equals("ACTIVE"))` repeated in many files | `enum Status { ACTIVE, INACTIVE }` plus `Status.ACTIVE` references |
| Go | `time.Sleep(3 * time.Second)` with no explanation | `const RetryDelay = 3 * time.Second` |
| Ruby | `if user.role == "admin"` repeated | `class Role; ADMIN = 'admin'.freeze; end` or enum gem |
| PHP | `if ($order->status === "paid")` everywhere | `class OrderStatus { const PAID = 'paid'; }` |
| C# / .NET | `if (statusCode == 200)` | `if (statusCode == StatusCodes.Status200OK)` |
| Rust | `if amount > 10000.0` | `const DISCOUNT_THRESHOLD: f64 = 10_000.0;` |

---

## §10 — Poor Naming Conventions

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `def proc(d):` / `u = req.json["u"]` | `def process_order(order):` / `user = request.json["user"]`; PEP 8 snake_case |
| JS/TS | `let u = req.body.u;` / `function fn1(x)` | `const userName = req.body.userName;` / `function calculateTotalPrice(order)` |
| Java | `class Mgr` / `void do1(Object o)` | `class OrderManager` / `void processOrder(Order order)`; PascalCase for classes |
| Go | `func H(w, r)` / variables `a, b, c` outside math contexts | `func handleCheckout(w http.ResponseWriter, r *http.Request)`; idiomatic short names only inside small scopes |
| Ruby | `def do_stuff(d)` / `attr :a` | `def calculate_invoice_total(order)` / `attr_reader :line_items` |
| PHP | `function fn1($x)` / `$a = ...` / mixed snake/camel | `function calculateTotal($order)` / PSR-12 conventions |
| C# / .NET | `void Mtd1(object o)` / camelCase fields without prefix | `void CalculateTotal(Order order)` / `private readonly IRepository _repo;` |
| Rust | `fn do1(x: i32)` / `let r = ...` | `fn process_payment(amount: i64)` / Rust idiomatic snake_case |

---

## §11 — Unprotected Destructive Endpoints

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `@app.route("/admin/reset-db", methods=["POST"])` with no `@login_required` / no env gate | Decorator chain with `@require_admin`; reads `os.getenv("ALLOW_DB_RESET")` |
| JS/TS | `app.delete('/users/:id', handler)` with no auth middleware | `router.delete('/:id', authMiddleware, adminOnly, handler)` |
| Java | `@DeleteMapping("/users/{id}")` without `@PreAuthorize("hasRole('ADMIN')")` | Method or class annotated `@PreAuthorize("hasRole('ADMIN')")`; security configuration enforces |
| Go | `r.DELETE("/users/:id", h)` without auth middleware | `admin := r.Group("/admin"); admin.Use(authMiddleware); admin.DELETE(...)` |
| Ruby | Rails: `def destroy ... end` action without `before_action :authenticate_admin!` | Controller has `before_action :authenticate_admin!, only: [:destroy]` |
| PHP | Laravel: route declared without `->middleware('auth:admin')` | `Route::middleware(['auth:admin'])->group(function () { ... });` |
| C# / .NET | `[HttpDelete]` action without `[Authorize(Roles = "Admin")]` | `[Authorize(Roles = "Admin")]` on controller or action |
| Rust | Axum: `Router::new().route("/admin/reset", post(handler))` with no auth layer | `.layer(middleware::from_fn(require_admin))` on the admin router branch |
| All | Endpoint accepting raw SQL/query text from request body and executing it | **Remove the endpoint entirely.** Raw query execution endpoints have no safe form. |

---

## §12 — No Error Handling / Bare Exceptions

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `except: pass` / `except Exception as e: return str(e)` | Centralized `@app.errorhandler(Exception)` returning safe JSON; specific exception classes caught at boundaries |
| JS/TS | `try {...} catch(e) { res.status(500).send(e.message); }` repeated everywhere | `app.use(errorHandler)` last; handlers `next(err)` to it; production-vs-dev message gating |
| Java | Spring: `@ExceptionHandler` only inside one controller; inconsistent error shapes | `@RestControllerAdvice` class with `@ExceptionHandler` per concrete error type; uniform `ProblemDetail` responses |
| Go | `if err != nil { return err }` propagating raw DB errors to client | Wrap with context (`fmt.Errorf("operation: %w", err)`); central middleware translates to 4xx/5xx |
| Ruby | Rails: rescuing `Exception` (catches process signals); leaking `e.message` | `rescue_from StandardError do |e|`; structured error renderer; specific rescues for known errors |
| PHP | Laravel: blank `catch (\Exception $e) { return $e->getMessage(); }` | Override `App\Exceptions\Handler::render()`; specific handlers per exception type |
| C# / .NET | Try-catch in every action returning `BadRequest(ex.Message)` | `app.UseExceptionHandler(...)` middleware; `ProblemDetails`-based responses; specific exception filters |
| Rust | `Result` propagation without any boundary translation; `unwrap()` in handlers | Custom error enum implementing `IntoResponse`; central error mapping; no `unwrap()` in request paths |

---

## §13 — Synchronous I/O in Asynchronous Context

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | `time.sleep` / `requests.get` / `psycopg2` calls inside `async def` handlers | `asyncio.sleep`, `httpx.AsyncClient`, `asyncpg`, or `await asyncio.to_thread(blocking_fn)` |
| JS/TS | `fs.readFileSync` in async route handler; `JSON.parse` of huge payload blocking | `await fs.promises.readFile(...)`; offload heavy CPU work to `worker_threads` |
| Java | `Thread.sleep(...)` in reactive Webflux handler; blocking JDBC in WebFlux | `Mono.delay(...)`; R2DBC for reactive DB access; or `.subscribeOn(Schedulers.boundedElastic())` for unavoidable blocking |
| Go | (Go has no event loop, but) panics caused by long unyielding loops in single-handler goroutines | Spawn goroutines for parallelizable work; use channels with timeouts; respect `ctx.Done()` |
| Ruby | Sync HTTP client (`Net::HTTP`) inside Sinatra handler under EventMachine reactor | `async-http` gem or `Async::HTTP`; reactor-aware drivers |
| PHP | (PHP request model is synchronous per request; not typically applicable except in Swoole/ReactPHP) | In Swoole, use `Swoole\Coroutine\` namespace; avoid blocking PHP funcs inside coroutines |
| C# / .NET | `.Result` / `.Wait()` on async tasks in async actions; sync `File.ReadAllText` in async pipeline | `await ReadAllTextAsync(...)`; never `.Result`/`.Wait()` in request paths |
| Rust | Calling `std::thread::sleep` or `std::fs::read` inside Tokio handler | `tokio::time::sleep`; `tokio::fs::read`; `tokio::task::spawn_blocking(|| ...)` for CPU-bound work |

---

## §14 — Mutable Shared State Without Synchronization

| Stack | Bad signal | Good signal |
|---|---|---|
| Python | Module-level `counters = {}` mutated from handlers under multi-process WSGI/ASGI | Per-request scope; `threading.Lock` for in-memory state; Redis for cross-process state |
| JS/TS | `let totalRequests = 0` at module scope incremented from handlers | Atomics where applicable; cluster-aware metrics (Prometheus client); per-process counters reconciled at scrape time |
| Java | `@Component` singleton with mutable `Map` field accessed by multiple threads without sync | `ConcurrentHashMap`; `@Volatile` for flags; explicit locks; or stateless service |
| Go | Package-level `var cache = map[string]X{}` accessed concurrently | `sync.Map` or `map` + `sync.RWMutex`; channels for ownership transfer |
| Ruby | Class variable `@@cache` updated from request handlers under multi-thread Puma | `Concurrent::Map` (concurrent-ruby gem); per-request memoization; Redis cache |
| PHP | (Less applicable: shared-nothing model) but `static` properties in long-running workers (Swoole, RoadRunner) | Reset state per request in Swoole; APCu / Redis for shared state |
| C# / .NET | Static field mutated from controller actions | `ConcurrentDictionary<TKey,TValue>`; `Interlocked.*`; scoped DI for per-request data |
| Rust | `static mut` (rejected by linter) / `lazy_static!` with non-`Sync` type | `Arc<RwLock<...>>`, `Arc<Mutex<...>>`, `dashmap::DashMap` for concurrent maps |

---

## How to use this grid

1. After Phase 1 detects the language, locate the matching column for each pattern when auditing source files.
2. Use **Bad signal** examples as positive matches (this is the anti-pattern).
3. Use **Good signal** examples as negative matches (this code is fine; keep moving).
4. The grid is illustrative, not exhaustive — patterns that resemble the bad signal but use different syntax should still be flagged. Defer to the abstract concept and signals in `anti-patterns-catalog.md` when in doubt.
5. Adding a new language is a single column per table; adding a new pattern is a new section. Keep both formats consistent for future maintainers.
