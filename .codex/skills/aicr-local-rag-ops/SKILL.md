---
name: aicr-local-rag-ops
description: Maintain, inspect, and improve the local AICR RAG index backed by SQLite. Use when Codex needs to ingest local corpus files, debug retrieval quality, refresh `.aicr_data/vector_store.sqlite3`, validate corpus paths, or explain why local RAG results are weak or stale.
---

# AICR Local RAG Ops

Use this skill to operate the repository's local RAG pipeline without introducing remote vector services.

## Workflow

1. Read [references/rag-ops-checklist.md](references/rag-ops-checklist.md).
2. Inspect `src/aicr/config.py`, `src/aicr/rag_pipeline.py`, and `src/aicr/local_vector_store.py`.
3. Confirm which corpus paths are active through `AICRConfig.from_env()` and `AICR_RAG_PATHS`.
4. Rebuild or extend the index only with local files already available in the workspace.
5. Verify with `python scripts/demo.py` or focused tests after changing ingestion or retrieval behavior.

## Operating Rules

- Keep storage local. Prefer SQLite and on-disk assets already in the repository.
- Preserve deterministic startup. If ingestion happens at boot, keep it idempotent.
- Do not delete the vector DB unless the user asked for a rebuild or the repair requires it.
- When retrieval quality is poor, inspect chunking, corpus selection, and query matching before adding new abstractions.
- If a stronger local embedding model is introduced later, wire it behind the same `SimpleRAG` surface.

## Expected Outputs

When using this skill, produce:

- the corpus paths in play
- the vector DB path
- whether reindexing was necessary
- the validation command you ran
- any retrieval-quality caveats that remain
