---
name: aicr-gitlab-webhook-review
description: Run and troubleshoot AICR review flows driven by GitLab webhook payloads. Use when Codex needs to inspect `app.py`, validate `push` or `merge_request` payload handling, simulate webhook requests, trace extracted review files, or debug why GitLab-triggered reviews behave differently from the demo path.
---

# AICR GitLab Webhook Review

Use this skill to reason about the webhook execution path from HTTP payload to review result.

## Workflow

1. Read [references/webhook-flow.md](references/webhook-flow.md).
2. Inspect `app.py` and the agent bootstrap path it uses.
3. Verify event type, secret handling, JSON decoding, and extracted review files.
4. If needed, simulate a local webhook request with a small payload fixture.
5. Validate that the reported `validation_level` and review file list match the request context.

## Operating Rules

- Treat `push` and `merge_request` as the only supported event kinds unless the user asks to extend support.
- Keep webhook validation behavior explicit. Secret mismatch should fail closed.
- Prefer small, reproducible payloads when debugging.
- If behavior differs from `scripts/demo.py`, compare input shaping rather than assuming orchestration is broken.

## Expected Outputs

When using this skill, produce:

- the event kind
- the extracted review file list
- the validation level in effect
- the failing or passing branch of webhook logic
- the command or request used to verify behavior
