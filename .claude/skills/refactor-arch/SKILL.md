---
name: refactor-arch
description: Analyze, audit, and refactor any backend project to MVC architecture. Use this skill whenever the user wants to refactor a project, fix architectural problems, detect code smells, audit code quality, restructure a codebase to MVC, or mentions anti-patterns, god classes, separation of concerns, or legacy code cleanup — even if they don't explicitly say "refactor-arch".
---

# Architectural Refactoring Skill

Analyze any backend project, audit it for anti-patterns, and refactor it to a clean MVC architecture. This skill is language-agnostic — it detects the stack first, then adapts all analysis and transformations accordingly.

Execute the three phases sequentially. Never skip a phase or reorder them.

---

## Phase 1 — Project Analysis

**Goal:** Understand what you're working with before making any judgments.

Read `references/project-analysis.md` for detection heuristics.

1. Scan all source files in the project directory
2. Detect language, framework, and dependencies from file extensions and imports
3. Identify the database layer (ORM, raw SQL, in-memory, file-based)
4. Map the current architecture (monolith, partial MVC, layered, etc.)
5. Identify the application domain by examining route names, model names, and table names
6. Count source files and estimate lines of code

Print the analysis summary in this exact format:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      {detected language}
Framework:     {detected framework + version}
Dependencies:  {key dependencies}
Domain:        {business domain description}
Architecture:  {current architecture classification}
Source files:  {count} files analyzed
DB tables:     {table names if detectable}
================================
```

Proceed immediately to Phase 2.

---

## Phase 2 — Architecture Audit

**Goal:** Identify every anti-pattern and code smell, with exact locations and severity.

Read `references/anti-patterns-catalog.md` for the full catalog of detectable anti-patterns.
Read `assets/audit-report-template.md` for the exact output format.

1. For each source file, check against every anti-pattern in the catalog
2. Record the exact file path and line numbers for each finding
3. Classify each finding by severity (CRITICAL, HIGH, MEDIUM, LOW)
4. Write a description specific to the actual code found — never use generic descriptions
5. Check for deprecated API usage specific to the detected framework version
6. Generate the full audit report following the template format exactly
7. Order findings by severity (CRITICAL first, LOW last)

**IMPORTANT:** After printing the report, STOP and ask the user for confirmation before proceeding to Phase 3. Do not modify any files until the user explicitly confirms. Say:

> "Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]"

---

## Phase 3 — Refactoring

**Goal:** Restructure the project to clean MVC, eliminating all findings from Phase 2.

Read `references/mvc-architecture-guide.md` for the target architecture.
Read `references/refactoring-playbook.md` for transformation patterns.

1. Create the MVC directory structure appropriate for the detected stack
2. Apply transformations from the playbook for each finding identified in Phase 2
3. Extract configuration to a dedicated config module (no hardcoded credentials or magic values)
4. Separate concerns: Models handle data, Controllers handle business logic, Views/Routes handle HTTP
5. Add centralized error handling middleware
6. Create a clear entry point (composition root) that wires everything together
7. Ensure all original endpoints remain functional with the same request/response contracts

### Validation

After refactoring is complete:

1. Attempt to start the application using the appropriate command for the stack
2. Verify each original endpoint responds without errors
3. Confirm no CRITICAL or HIGH anti-patterns remain

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
