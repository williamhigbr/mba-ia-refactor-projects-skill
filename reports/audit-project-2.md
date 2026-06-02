================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] God Class / God File
File: src/AppManager.js:1-120
Description: Single class `AppManager` owns database initialization, route registration, all business logic (checkout flow, financial reporting, user deletion), and audit logging. Spans 120 LOC across 4 different domains (users, courses, enrollments, payments).
Impact: Impossible to test any single domain in isolation; any change risks breaking unrelated functionality. No reuse possible.
Recommendation: Extract into `models/` (User, Course, Enrollment, Payment), `controllers/` (checkoutController, reportController, userController), and `routes/` for HTTP binding.

### [CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:1-6
Description: Production credentials hardcoded as plain literals: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser`, `dbUser`. These are committed to source control.
Impact: Anyone with repository access has full production database and payment gateway credentials. Credential rotation requires code change and redeploy.
Recommendation: Move all secrets to environment variables (`process.env.DB_PASS`, etc.) with a `.env` file for local dev (gitignored) and fail-fast if required vars are missing.

### [CRITICAL] Insecure Cryptography (badCrypto)
File: src/utils.js:14-19
Description: Password "hashing" function `badCrypto` repeatedly Base64-encodes the password 10000 times and truncates to 10 chars. This is not a hash — it's trivially reversible and provides zero security.
Impact: All user passwords stored in the database are effectively plaintext. A database breach exposes every user's password immediately.
Recommendation: Replace with `bcrypt` (`bcrypt.hashSync(pwd, 10)`) or `argon2`. Store proper hashes and use `bcrypt.compare` for verification.

### [HIGH] Business Logic in Routes / Handlers
File: src/AppManager.js:26-72
Description: The `/api/checkout` route handler contains 47 lines of deeply nested business logic: user lookup/creation, payment processing, enrollment creation, audit logging, and response formatting — all in a single callback chain.
Impact: Cannot unit-test checkout logic without spinning up Express and a database. Business rules are entangled with HTTP concerns.
Recommendation: Extract checkout logic into a `CheckoutController.execute(data)` method that receives plain objects and returns results. Route handler should only parse request and call controller.

### [HIGH] Unprotected Destructive Endpoint
File: src/AppManager.js:109-115
Description: `DELETE /api/users/:id` has no authentication or authorization middleware. Any unauthenticated client can delete any user. Additionally, it does not cascade-delete related enrollments/payments, leaving orphaned records.
Impact: Data integrity violation and security breach — any anonymous request can destroy user accounts.
Recommendation: Add auth middleware to destructive routes. Implement cascade deletion or soft-delete pattern.

### [MEDIUM] N+1 Query Problem
File: src/AppManager.js:76-107
Description: The `/api/admin/financial-report` endpoint iterates courses, then for each course iterates enrollments, then for each enrollment makes 2 individual queries (user + payment). For C courses with E enrollments each, this executes 1 + C + C*E*2 queries.
Impact: Report endpoint becomes extremely slow as data grows. With 10 courses and 100 enrollments each, this is 2001 queries for a single request.
Recommendation: Use JOINs or batch queries: `SELECT enrollments.*, users.name, payments.amount, payments.status FROM enrollments JOIN users... JOIN payments... WHERE course_id IN (...)`.

### [MEDIUM] Missing Input Validation
File: src/AppManager.js:28-32
Description: Checkout endpoint only checks presence of fields (`!u || !e || !cid || !cc`). No email format validation, no card number format/length check, no course_id type validation. The password field (`pwd`) isn't even checked for presence.
Impact: Invalid data stored in database; potential for unexpected behavior with malformed inputs. Empty passwords default to "123456".
Recommendation: Add input validation with a library like `joi` or `zod` to validate email format, card number format (Luhn check), and require all fields with proper types.

### [MEDIUM] Deprecated API Usage (body-parser pattern)
File: package.json + src/app.js:6
Description: While `express.json()` is correctly used (good), the project does NOT use the deprecated `body-parser` standalone package. However, `new Buffer(pwd)` is used in `src/utils.js:16` via `Buffer.from(pwd)` — this is the modern form. No deprecated APIs detected in this specific project.
Impact: N/A — No deprecated API usage found. This finding is reclassified below.

### [MEDIUM] Mutable Shared State Without Synchronization
File: src/utils.js:8-9
Description: `globalCache` object and `totalRevenue` variable are module-level mutable state shared across all requests. Under Node.js clustering or concurrent requests, cache writes from one request can interleave with reads from another.
Impact: Stale or corrupted cache data under concurrent load; revenue counter may lose updates. Behavior is unpredictable.
Recommendation: Use Redis or a proper cache layer for cross-request state. Remove mutable module-level variables.

### [LOW] Poor Naming Conventions
File: src/AppManager.js:28-32
Description: Request body fields use cryptic abbreviated names: `usr`, `eml`, `pwd`, `c_id`, `cc`. Internal variables follow same pattern: `u`, `e`, `p`, `cid`, `cc`. The callback parameter `self` is used to work around `this` binding issues.
Impact: Code is difficult to read and maintain. New developers must trace through code to understand what `u` or `cc` represent.
Recommendation: Use descriptive names: `userName`, `email`, `password`, `courseId`, `cardNumber`. Use arrow functions or `.bind()` to avoid `self` pattern.

### [LOW] Magic Numbers and Strings
File: src/AppManager.js:41
Description: Payment validation uses magic string check `cc.startsWith("4")` to determine if payment is "PAID" or "DENIED". The status strings "PAID" and "DENIED" are repeated as literals throughout the codebase.
Impact: Business rules are implicit and scattered. Changing payment logic requires finding all magic string occurrences.
Recommendation: Extract payment statuses to constants (`PAYMENT_STATUS.PAID`, `PAYMENT_STATUS.DENIED`). Move card validation logic to a dedicated payment service.

================================
Total: 10 findings
================================

> Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y (auto-approved)
