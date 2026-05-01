---
name: aicr-release-readiness
description: Run a focused pre-release pass for AICR changes and report blockers clearly. Use when Codex needs to judge whether a branch is ready to ship, summarize release risk, check tests and startup paths, verify docs/config drift, or produce a concise go/no-go recommendation.
---

# AICR Release Readiness

Use this skill for the last review before shipping a change set.

## Workflow

1. Read [references/release-checklist.md](references/release-checklist.md).
2. Inspect the git diff and identify changed runtime surfaces.
3. Run the smallest set of commands that proves those surfaces still work.
4. Report blockers first, then residual risk, then what was verified.

## Review Rules

- Favor concrete ship blockers over style comments.
- Call out missing tests when behavior changed in runtime paths.
- Distinguish "not tested" from "tested and failed".
- If release confidence depends on manual environment checks, say so explicitly.

## Expected Outputs

When using this skill, produce:

- release decision: go, needs attention, or blocked
- blockers with file references when possible
- commands run for verification
- residual risk and test gaps
