---
name: refactor-arch
description: Analyze, audit, and refactor any backend project to MVC architecture. Use this skill whenever the user wants to refactor a project, fix architectural problems, detect code smells, audit code quality, restructure a codebase to MVC, or mentions anti-patterns, god classes, separation of concerns, or legacy code cleanup — even if they don't explicitly say "refactor-arch".
---

# Architectural Refactoring Skill

Analyze any backend project, audit it for anti-patterns, and refactor it to a clean MVC architecture (or to the architecture idiomatic for the detected stack). This skill is **language-agnostic** — it detects the stack first, then adapts all analysis and transformations accordingly. It works for stacks documented in the references and degrades gracefully for unfamiliar stacks.

Execute the three phases sequentially. Never skip a phase or reorder them.

---

## Phase 1 — Project Analysis

**Goal:** Understand what you're working with before making any judgments.

Read `references/project-analysis.md` for detection heuristics, the framework registry, the database-detection grid, and the abstract architecture-classification criteria.

1. Scan all source files in the project directory (skip `node_modules/`, `vendor/`, `.venv/`, `target/`, `build/`, `dist/`, `.git/`).
2. Detect the **language** from file-extension counts.
3. Detect the **framework** by matching against the registry in `project-analysis.md` §2 (manifest signal → import signal → idiomatic file signal). If no entry matches, follow the **Unknown stack — fallback procedure** in `project-analysis.md` §7. Never abort.
4. Identify the **persistence layer** (ORM, raw driver, schema artifacts, connection strings, DB files) per `project-analysis.md` §4.
5. Classify the **architecture** using the abstract criteria in `project-analysis.md` §5. Recognize and report non-MVC native architectures (Hexagonal, Clean, CQRS, Modular Monolith, Microservices) — do not force-label them as monolith.
6. Identify the **application domain** by examining route names, model names, and table names (§6).
7. Count source files and estimate total LOC.

Print the analysis summary in this exact format:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      {detected language}
Framework:     {detected framework + version, OR "undetermined (probed: …)" if unknown}
Dependencies:  {key dependencies}
Domain:        {business domain description}
Architecture:  {current architecture classification}
Source files:  {count} files analyzed
DB tables:     {table names if detectable, else "undetermined"}
================================
```

Proceed immediately to Phase 2.

---

## Phase 2 — Architecture Audit

**Goal:** Identify every anti-pattern and code smell, with exact locations and severity.

Read in this order:

- `references/anti-patterns-catalog.md` — concept-first descriptions of all 14 detectable anti-patterns with abstract detection signals.
- `references/cross-language-signals.md` — syntax-level Bad/Good signal grid covering 8 ecosystems for every catalog entry. Use this when the detected stack matches one of the columns.
- `assets/audit-report-template.md` — the exact output format.

1. For each source file, walk through the catalog and check each abstract signal against the code.
2. When the detected stack appears in `cross-language-signals.md`, use that file's row as supporting syntax-level evidence. When it does **not** appear, rely solely on the abstract signals from the catalog — they are designed to apply to any language.
3. Record the exact file path and line numbers for each finding.
4. Classify each finding by severity (CRITICAL, HIGH, MEDIUM, LOW). Severity is fixed per pattern except where context modifies it (deprecated cryptography → HIGH/CRITICAL; sync I/O on a request-critical path → HIGH).
5. Write a description **specific to the actual code found**. Never use generic descriptions copied from the catalog.
6. Check for deprecated API usage specific to the detected framework version. Use `cross-language-signals.md` §8 for the per-ecosystem deprecation list.
7. Generate the full audit report following `assets/audit-report-template.md` exactly.
8. Order findings by severity (CRITICAL first, LOW last).

**Minimum bar:** the report must contain ≥ 5 findings, including ≥ 1 CRITICAL or HIGH. If the project genuinely has fewer issues, look harder — most legacy projects have more than initially apparent.

**IMPORTANT:** After printing the report, STOP and ask the user for confirmation before proceeding to Phase 3. Do not modify any files until the user explicitly confirms. Say:

> "Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]"

---

## Phase 3 — Refactoring

**Goal:** Restructure the project to clean MVC (or to the architecture idiomatic for the detected stack), eliminating all findings from Phase 2.

Read in this order:

- `references/mvc-architecture-guide.md` — target architectures per stack, abstract layout template, composition-root recipe, and the **Mapping to Non-MVC-Native Architectures** section (Hexagonal, Clean, CQRS, Modular Monolith, Microservices).
- `references/refactoring-playbook.md` — abstract recipes plus three-language examples for every transformation pattern, the **Pattern X on an Unknown Stack** procedure for undocumented stacks, and the whole-project validation checklist.

1. **Choose the target structure.** If the detected framework appears in `mvc-architecture-guide.md`'s stack-specific section, use that structure. Otherwise, apply the **Abstract Layout Template** in the same file. If the project already uses a non-MVC-native architecture (Hexagonal, Clean, CQRS, Modular Monolith), preserve it and apply Playbook **Pattern 14 — Layer-Violation Untangling**.
2. **Apply transformations** from the playbook for each finding identified in Phase 2. Each playbook entry has an Abstract Recipe — apply it verbatim, substituting framework equivalents per the **Pattern X on an Unknown Stack** procedure when needed.
3. **Extract configuration** to a dedicated config module (no hardcoded credentials or magic values). See Playbook §2.
4. **Separate concerns:** Models handle data and persistence, Controllers/Services handle business logic (HTTP-agnostic), Views/Routes handle the HTTP boundary.
5. **Add centralized error handling** middleware/filter/advice appropriate to the stack. See Playbook §11.
6. **Create a clear composition root** that wires the dependency graph. See `mvc-architecture-guide.md`'s *Composition Root Pattern* section.
7. **Preserve the API contract.** All original endpoints must remain functional with the same request/response shapes. Do not change URL paths or response keys unless a finding explicitly required a fix.
8. **Preserve the database schema.** Do not modify table structures; only change *how* they are accessed.

### Validation

After refactoring is complete:

1. Attempt to start the application using the appropriate command for the stack (e.g., `python -m src.app`, `node src/app.js`, `go run ./cmd/server`, `bundle exec rackup`, `cargo run`).
2. Verify each original endpoint still responds without 5xx errors. (4xx responses to test inputs are acceptable for protected/validation endpoints.)
3. Re-apply Phase 2 logic to confirm no CRITICAL or HIGH anti-patterns remain.
4. Run the **whole-project validation checklist** at the bottom of `references/refactoring-playbook.md`.

Print the final summary:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
{tree of new directory structure}

## Validation
  ✓/✗ Application boots without errors
  ✓/✗ All endpoints respond correctly
  ✓/✗ Zero CRITICAL/HIGH anti-patterns remaining
================================
```

If the boot fails or endpoints regress, debug and iterate up to 3 times before reporting failure. The skill must produce working code, not just a refactored shape.
