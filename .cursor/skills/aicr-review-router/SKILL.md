---
name: aicr-review-router
description: Route code review scopes by file extensions and output language-specific focus points for cpp, py, go, and java. Use when user provides review file lists or asks to infer review scopes.
disable-model-invocation: true
---
# AICR Review Router

## Instructions

1. Read `review_files` and map extensions:
   - `.cpp` -> `cpp`
   - `.py` -> `py`
   - `.go` -> `go`
   - `.java` -> `java`
2. Deduplicate scopes and keep original appearance order.
3. If no supported extension is found, default to `py`.
4. Return concise review focus points per scope.

## Output Template

```text
scopes: <comma-separated-scopes>
focus:
- <scope>: <focus-1>, <focus-2>, <focus-3>
```

## Scope Focus

- cpp: memory safety, lifetime, race conditions, exception safety, RAII
- py: type stability, exception handling, dependency safety, testability, performance hotspots
- go: goroutine leaks, context propagation, error handling, interface boundaries, data races
- java: thread safety, nullability, transaction boundaries, resource lifecycle, API compatibility
