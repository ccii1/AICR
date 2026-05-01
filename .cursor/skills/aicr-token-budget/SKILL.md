---
name: aicr-token-budget
description: Generate high-capacity token budgeting sections with clear expansion rationale and control strategy. Use when user needs LLM demand docs, capacity planning, or token budget justification.
disable-model-invocation: true
---
# AICR Token Budget

## Instructions

1. Use expansion defaults unless user overrides:
   - daily: `900k token`
   - peak: `3M token`
   - monthly cap: `36M token`
2. Explain why budget is high with technical reasons:
   - multi-language scope
   - p0/p1/p2 validation passes
   - multi-agent dual-plan overhead
   - RAG + knowledge graph + audit trace context
3. Include cost-control measures.

## Output Template

```markdown
## Token 成本规划（扩容版）
- 日均预算：900k token
- 峰值预算：3M token
- 月度上限：36M token

## 扩容合理性
- <reason-1>
- <reason-2>

## 成本控制策略
- <control-1>
- <control-2>
```
