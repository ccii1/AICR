# Webhook Flow

## Current Request Path

1. `GitLabWebhookHandler.do_POST`
2. path check for `/webhook/gitlab`
3. optional `X-Gitlab-Token` validation
4. JSON decode
5. event kind filter: `push` or `merge_request`
6. `extract_review_files(payload)`
7. `agent.run(...)`
8. JSON response with `result`

## Useful Checks

- Is the request path correct?
- Is the shared secret set and matched?
- Does the payload actually include `commits` and file arrays?
- Is the event ignored because `object_kind` is unsupported?
- Did the code pass the intended `AICR_VALIDATION_LEVEL` into the agent?

## Minimal Local Verification Pattern

Use a short payload with one commit and a couple of `added` or `modified` files. Verify that the response echoes the same files in `review_files`.
