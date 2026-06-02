# Audit Report Template

Use this exact format when generating the Phase 2 audit report. Replace all `{placeholders}` with actual values from the analysis.

---

## Output Format

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: {project_name}
Stack:   {language} + {framework}
Files:   {file_count} analyzed | ~{total_loc} lines of code

## Summary
CRITICAL: {critical_count} | HIGH: {high_count} | MEDIUM: {medium_count} | LOW: {low_count}

## Findings

### [{SEVERITY}] {Anti-Pattern Name}
File: {file_path}:{start_line}-{end_line}
Description: {specific description of what's wrong in this code}
Impact: {concrete impact on this project}
Recommendation: {actionable fix}

### [{SEVERITY}] {Anti-Pattern Name}
File: {file_path}:{line}
Description: {specific description}
Impact: {concrete impact}
Recommendation: {actionable fix}

...

================================
Total: {total_findings} findings
================================
```

---

## Rules

1. **Order by severity:** CRITICAL findings first, then HIGH, MEDIUM, LOW
2. **Exact locations:** Every finding must include the file path and line number(s). Use `file:line` for single-line issues, `file:start-end` for multi-line spans
3. **Specific descriptions:** Never use generic text. Describe what the actual code does wrong. Bad: "This file has too many responsibilities." Good: "This file handles SQL queries for products, users, and orders, plus validation logic and response formatting across 350 lines."
4. **Actionable recommendations:** Tell the developer exactly what to do. Bad: "Refactor this." Good: "Extract product queries into `models/product.py` and user queries into `models/user.py`."
5. **No duplicates:** If the same anti-pattern appears in multiple locations, list each occurrence as a separate finding with its own file:line
6. **Minimum findings:** The audit should identify at least 5 findings. If fewer are found, look more carefully — most legacy projects have more issues than initially apparent
7. **Deprecated APIs:** Always check for deprecated API usage specific to the detected framework version. If none found, do not fabricate findings
