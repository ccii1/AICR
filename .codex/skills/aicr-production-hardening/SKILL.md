---
name: aicr-production-hardening
description: Harden the AICR service for deployment, reliability, and maintainability. Use when Codex needs to upgrade prototype logic into safer production behavior, add health checks, improve config handling, tighten error paths, strengthen logging and tests, or identify operational gaps before deployment.
---

# AICR Production Hardening

Use this skill when the work is about operability, reliability, and deployment safety rather than feature expansion.

## Workflow

1. Read [references/hardening-checklist.md](references/hardening-checklist.md).
2. Inspect the touched runtime path end to end: config, bootstrap, service entrypoint, storage, tests.
3. Identify the highest-risk gap first: data durability, request validation, startup safety, logging, or test coverage.
4. Make narrowly scoped changes that improve failure behavior and observability.
5. Verify with compile/test/runtime commands, not just code inspection.

## Priorities

Prefer work in this order:

1. fail-closed request validation
2. deterministic startup and storage behavior
3. useful operational visibility
4. test coverage for critical paths
5. documentation of run and recovery steps

## Expected Outputs

When using this skill, produce:

- the production risk being addressed
- the exact code path changed
- the validation run
- remaining operational gaps that still exist after the patch
