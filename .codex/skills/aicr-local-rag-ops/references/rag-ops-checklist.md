# RAG Ops Checklist

## Read First

- `src/aicr/config.py`
- `src/aicr/rag_pipeline.py`
- `src/aicr/local_vector_store.py`
- `src/aicr/bootstrap.py`

## Typical Commands

```powershell
$env:PYTHONPATH='src'; python scripts\demo.py
$env:PYTHONPATH='src'; python -m unittest discover -s tests -v
```

## Investigation Sequence

1. Confirm the configured corpus roots.
2. Confirm the SQLite DB path exists or will be created.
3. Check document count via `rag.health_summary()`.
4. Reproduce the weak retrieval with a concrete query.
5. Inspect chunk size, overlap, and which files were actually ingested.
6. Only then patch ingestion, chunking, or retrieval ranking.

## Common Failure Modes

- Corpus path points to an empty or wrong directory.
- Files are not in supported text extensions.
- Query terms do not overlap well with the local hashed embedding scheme.
- Index exists but is stale relative to recent source changes.
