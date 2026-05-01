# Hardening Checklist

## Runtime Safety

- Validate environment-derived config.
- Avoid silent fallback that hides bad production settings.
- Keep startup idempotent and predictable.

## Storage

- Ensure the local SQLite path is explicit.
- Avoid destructive rebuilds unless requested.
- Document rebuild behavior and recovery steps.

## Service Behavior

- Return explicit status codes for malformed or unauthorized requests.
- Keep logs concise but useful.
- Add health or status output where operators need it.

## Verification

- `python -m compileall src app.py scripts\demo.py tests`
- `$env:PYTHONPATH='src'; python -m unittest discover -s tests -v`
- a focused runtime command if service logic changed
