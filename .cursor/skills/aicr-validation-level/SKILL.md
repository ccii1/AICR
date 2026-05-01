---
name: aicr-validation-level
description: Normalize and enforce validation intensity using p0, p1, or p2 with deterministic output expectations. Use when user asks for strictness level, review depth, or validation policy.
disable-model-invocation: true
---
# AICR Validation Level

## Instructions

1. Normalize input level to lowercase.
2. Accept only `p0`, `p1`, `p2`; fallback to `p1` if invalid.
3. Apply policy:
   - `p0`: highest strictness, uncertain risk treated as high.
   - `p1`: standard strictness, balance quality and delivery.
   - `p2`: fast path, prioritize critical path risks only.
4. Always include required evidence fields in output.

## Output Template

```text
validation_level: <p0|p1|p2>
required_output:
- evidence
- impact
- fix
- tests
policy_note: <single line>
```
