# Release Checklist

## Check These First

- `git status --short`
- changed files in `src/`, `app.py`, `scripts/`, `tests/`, and docs tied to runtime behavior

## Minimum Verification

```powershell
python -m compileall src app.py scripts\demo.py tests
$env:PYTHONPATH='src'; python -m unittest discover -s tests -v
$env:PYTHONPATH='src'; python scripts\demo.py
```

## Ship Blockers

- runtime import failures
- config regressions
- startup path regressions
- webhook request handling regressions
- broken or stale docs for new required env vars
