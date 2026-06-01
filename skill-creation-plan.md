# Skill Creation Plan — refactor-arch

## Overview

Create a language-agnostic skill that analyzes, audits, and refactors any backend project to the MVC pattern. The skill must work across Python/Flask and Node.js/Express without modification.

---

## Skill Structure

Following skill-creator progressive disclosure guidelines:

```
.claude/skills/refactor-arch/
├── SKILL.md                          # <500 lines — orchestration + phases
├── assets/
│   └── audit-report-template.md      # Standardized output template for Phase 2
└── references/
    ├── project-analysis.md           # Heuristics for detecting stack, framework, DB, architecture
    ├── anti-patterns-catalog.md      # 8+ anti-patterns with detection signals + severity
    ├── mvc-architecture-guide.md     # Target MVC structure rules per layer
    └── refactoring-playbook.md       # 8+ transformation patterns with before/after code
```

**Why this structure:**
- SKILL.md stays concise (orchestration only) — references hold domain knowledge
- Assets hold output templates (used to produce formatted results)
- References are loaded on-demand, keeping context lean
- No domain-specific folders (e.g., `references/python/`, `references/node/`) because the skill must reason about ANY stack — the references themselves contain multi-language examples

---

## SKILL.md Design

### Frontmatter

```yaml
---
name: refactor-arch
description: Analyze, audit, and refactor any backend project to MVC architecture. Use this skill whenever the user wants to refactor a project, fix architectural problems, detect code smells, audit code quality, restructure a codebase to MVC, or mentions anti-patterns, god classes, separation of concerns, or legacy code cleanup — even if they don't explicitly say "refactor-arch".
---
```

**Why pushy description:** The skill-creator guidelines say descriptions should be aggressive about triggering. This covers the full semantic space of when a user might need architectural refactoring.

### Body Structure (imperative form, explains WHY)

1. **Phase 1 — Analysis** (~30 lines)
   - Scan project files to detect language, framework, dependencies, DB
   - Map current architecture (monolith, partial MVC, etc.)
   - Print structured summary
   - Point to `references/project-analysis.md` for detection heuristics

2. **Phase 2 — Audit** (~40 lines)
   - Cross-reference code against anti-patterns catalog
   - Generate report following template format
   - Classify findings by severity (CRITICAL → LOW)
   - Include exact file:line references
   - **STOP and ask user confirmation before proceeding**
   - Point to `references/anti-patterns-catalog.md` and `assets/audit-report-template.md`

3. **Phase 3 — Refactoring** (~40 lines)
   - Apply transformations from playbook
   - Create MVC directory structure appropriate to the detected stack
   - Validate: app boots + endpoints respond
   - Point to `references/mvc-architecture-guide.md` and `references/refactoring-playbook.md`

**Total SKILL.md estimate:** ~150-200 lines (well under 500 limit)

---

## Reference Files Design

### 1. project-analysis.md

**Purpose:** Give the skill heuristics to detect ANY stack without hardcoding.

**Contents:**
- File extension → language mapping
- Framework detection signals (e.g., `from flask import` → Flask, `require('express')` → Express)
- Dependency file detection (`requirements.txt`, `package.json`, `Cargo.toml`, etc.)
- Database detection (SQLite files, connection strings, ORM imports)
- Architecture classification criteria:
  - Monolith: all logic in ≤3 files, no directory separation
  - Partial MVC: some separation exists but incomplete
  - Full MVC: clear models/views/controllers separation
- Domain detection: scan route names, table names, model names to infer business domain

**Language-agnostic approach:** Describe detection as pattern-matching rules, not language-specific checklists. The skill reads the project and applies general heuristics.

### 2. anti-patterns-catalog.md

**Purpose:** Catalog of 8+ anti-patterns with concrete detection signals.

**Minimum entries (distributed severity):**

| # | Anti-Pattern | Severity | Detection Signal |
|---|---|---|---|
| 1 | God Class / God File | CRITICAL | Single file >300 lines handling multiple domains |
| 2 | Hardcoded Credentials | CRITICAL | Strings matching `secret`, `password`, `key` assigned as literals |
| 3 | SQL Injection | CRITICAL | String concatenation/f-strings in SQL queries |
| 4 | Business Logic in Routes | HIGH | Route handlers >30 lines with DB queries + validation |
| 5 | Tight Coupling / No DI | HIGH | Direct instantiation of dependencies, global mutable state |
| 6 | N+1 Queries | MEDIUM | DB queries inside loops |
| 7 | Missing Input Validation | MEDIUM | Route params used directly without sanitization |
| 8 | Deprecated API Usage | MEDIUM | Use of obsolete APIs (e.g., `flask.ext.*`, `bodyParser` in Express 4.16+) |
| 9 | Magic Numbers/Strings | LOW | Unexplained numeric literals or repeated string constants |
| 10 | Poor Naming | LOW | Single-letter variables, ambiguous function names |

**Each entry includes:**
- Name and severity
- Detection signals (language-agnostic patterns + language-specific examples)
- Impact explanation (WHY it matters)
- Recommendation (what to do about it)

**Language-agnostic approach:** Each anti-pattern describes the CONCEPT first, then gives detection examples in multiple languages. The skill matches the concept to whatever code it finds.

### 3. audit-report-template.md (assets/)

**Purpose:** Standardized output template so reports are consistent across projects.

**Template structure:**
```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: {project_name}
Stack:   {language} + {framework}
Files:   {count} analyzed | ~{loc} lines of code

## Summary
CRITICAL: {n} | HIGH: {n} | MEDIUM: {n} | LOW: {n}

## Findings

### [{SEVERITY}] {Anti-Pattern Name}
File: {file}:{start_line}-{end_line}
Description: {what's wrong}
Impact: {why it matters}
Recommendation: {what to do}

...

================================
Total: {total} findings
================================
```

**Rules:**
- Findings ordered by severity (CRITICAL first)
- Each finding must have exact file:line
- Description must be specific to the actual code found (not generic)

### 4. mvc-architecture-guide.md

**Purpose:** Define the target MVC structure the skill refactors toward.

**Contents:**
- Layer responsibilities:
  - **Models:** Data representation, DB access, validation rules
  - **Views/Routes:** HTTP handling, request parsing, response formatting
  - **Controllers:** Business logic orchestration, coordination between models
- Supporting layers:
  - **Config:** Environment variables, settings (no hardcoded values)
  - **Middlewares:** Cross-cutting concerns (error handling, auth, logging)
  - **Utils/Helpers:** Pure utility functions
- Target directory structures per ecosystem:
  - Python/Flask example
  - Node.js/Express example
  - Generic template for other stacks
- Composition root pattern (single entry point that wires everything)

**Language-agnostic approach:** Define responsibilities abstractly, then show concrete directory examples per ecosystem. The skill picks the appropriate structure based on Phase 1 detection.

### 5. refactoring-playbook.md

**Purpose:** Concrete transformation patterns with before/after code.

**Minimum 8 patterns:**

1. **God Class → Domain Separation** — Split by responsibility into separate modules
2. **Hardcoded Credentials → Config Module** — Extract to env vars / config file
3. **SQL Injection → Parameterized Queries** — Replace string interpolation with params
4. **Fat Route → Controller Extraction** — Move business logic to controller layer
5. **Tight Coupling → Dependency Injection** — Pass dependencies as parameters
6. **N+1 → Batch Query** — Replace loop queries with JOINs or batch fetches
7. **Missing Validation → Input Sanitization** — Add validation layer at route entry
8. **Deprecated APIs → Modern Equivalents** — Replace with current API versions

**Each pattern includes:**
- Before code (Python AND Node.js examples)
- After code (Python AND Node.js examples)
- Step-by-step transformation instructions
- Validation criteria (how to confirm it worked)

**Language-agnostic approach:** Show the same transformation in multiple languages. The skill recognizes the pattern regardless of syntax and applies the appropriate language's solution.

---

## Language-Agnostic Strategy

The skill achieves technology independence through three mechanisms:

1. **Detection-first:** Phase 1 identifies the stack BEFORE any analysis. All subsequent phases adapt behavior based on detected language/framework.

2. **Pattern-based reasoning:** Anti-patterns are described as abstract concepts with language-specific detection signals. The skill matches concepts, not syntax.

3. **Multi-language examples in references:** Every transformation pattern shows both Python and Node.js versions. For unknown stacks, the skill extrapolates from the abstract pattern description.

**What the SKILL.md should NOT do:**
- Hardcode file paths or project structures
- Assume a specific package manager
- Reference language-specific tools without detecting first
- Use language-specific terminology in phase instructions

---

## Validation Strategy

For Phase 3 validation, the skill should:

1. **Boot test:** Run the appropriate start command (`python app.py`, `node src/app.js`, etc.)
2. **Endpoint test:** Hit each discovered endpoint and verify non-error responses
3. **Zero anti-patterns check:** Re-run Phase 2 logic on refactored code to confirm findings are resolved

---

## Implementation Order

1. Write `SKILL.md` (orchestration, phases, pointers to references)
2. Write `references/project-analysis.md`
3. Write `references/anti-patterns-catalog.md`
4. Write `assets/audit-report-template.md`
5. Write `references/mvc-architecture-guide.md`
6. Write `references/refactoring-playbook.md`
7. Test on `code-smells-project/` (Python/Flask monolith — hardest case)
8. Test on `ecommerce-api-legacy/` (Node.js/Express — proves language agnosticism)
9. Test on `task-manager-api/` (Python/Flask partial — proves adaptability)
10. Iterate based on results (expect 2-4 iterations)

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Single references/ folder (no per-language subfolders) | The skill must reason about any language — splitting by language would make it rigid |
| Multi-language examples in playbook | Teaches the pattern abstractly while giving concrete syntax for known stacks |
| Phase 2 mandatory pause | README requirement + prevents destructive changes without human review |
| Detection heuristics over hardcoded lists | New frameworks can be handled by pattern matching, not catalog updates |
| SKILL.md under 200 lines | Keeps orchestration lean; domain knowledge lives in references |
| Imperative form throughout | Skill-creator guideline — direct instructions perform better |
| Explain WHY in anti-patterns | Skill-creator guideline — models reason better when they understand purpose |
