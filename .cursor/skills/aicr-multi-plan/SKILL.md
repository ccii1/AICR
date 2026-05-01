---
name: aicr-multi-plan
description: Produce two comparable multi-agent execution plans (Plan-A risk-first and Plan-B speed-first) with consistent structure. Use when user asks for dual strategies or plan comparison.
disable-model-invocation: true
---
# AICR Multi Plan

## Instructions

1. Always generate both plans.
2. Keep stable order:
   - Plan-A (`risk-first`): compliance -> cost -> knowledge -> graph
   - Plan-B (`speed-first`): knowledge -> graph -> cost -> compliance
3. Include `scopes` and `validation_level`.
4. End each plan with one-line conclusion.

## Output Template

```text
Plan: Plan-A
Strategy: risk-first
Scopes: <...>
Validation: <p0|p1|p2>
Conclusion: 适合正式流程，强调可追溯与低风险。

Plan: Plan-B
Strategy: speed-first
Scopes: <...>
Validation: <p0|p1|p2>
Conclusion: 适合预研迭代，强调交付速度。
```
