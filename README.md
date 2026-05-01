# AICR

AICR is a production-oriented local review assistant skeleton for code and policy workflows.
It combines:

- local RAG backed by an on-disk SQLite vector store
- a lightweight knowledge graph for relationship lookup
- a ReAct-style evidence collection loop
- policy and skill registries
- GitLab webhook ingestion for automated review triggers

## What changed

The project is no longer a memory-only demo:

- RAG now persists chunks and embeddings to `./.aicr_data/vector_store.sqlite3`
- the vector store is fully local and does not depend on remote services
- app and demo now share the same bootstrap path
- prompt templates and review text were cleaned up
- the demo entrypoint runs without manual `PYTHONPATH` setup inside the script

## Project layout

```text
AICR/
  app.py
  scripts/
    demo.py
  docs/
    prompts/
      p0.md
      p1.md
      p2.md
  src/aicr/
    agent_orchestrator.py
    bootstrap.py
    config.py
    knowledge_graph.py
    local_vector_store.py
    mcp_bridge.py
    multi_agent.py
    prompt_rules.py
    rag_pipeline.py
    react_agent.py
    review.py
    skills.py
    workflow.py
  tests/
    test_agent_flow.py
    test_rag_pipeline.py
```

## Local vector store

The local RAG pipeline:

1. reads local text/code files from configured paths
2. chunks content with overlap
3. generates local hashed embeddings
4. persists chunks and embeddings into SQLite
5. retrieves the top matching chunks for each review query

Default corpus paths:

- `README.md`
- `docs/`
- `src/`

You can override them with `AICR_RAG_PATHS`.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python scripts/demo.py
```

## Webhook service

```bash
set AICR_WEBHOOK_PORT=8000
set AICR_VALIDATION_LEVEL=p1
set GITLAB_WEBHOOK_SECRET=your_secret
python app.py
```

Webhook endpoint:

```text
http://<your-host>:8000/webhook/gitlab
```

Supported GitLab events:

- `push`
- `merge_request`

## Environment variables

- `AICR_DATA_DIR`
- `AICR_VECTOR_DB_PATH`
- `AICR_RAG_PATHS`
- `AICR_RAG_COLLECTION`
- `AICR_RAG_TOP_K`
- `AICR_RAG_CHUNK_SIZE`
- `AICR_RAG_CHUNK_OVERLAP`
- `AICR_EMBEDDING_DIMENSIONS`
- `AICR_WEBHOOK_HOST`
- `AICR_WEBHOOK_PORT`
- `AICR_VALIDATION_LEVEL`
- `GITLAB_WEBHOOK_SECRET`

## Test

```bash
set PYTHONPATH=src
python -m unittest discover -s tests -v
```

## Production notes

This repository is now much closer to a deployable local service, but "production-grade"
still depends on your environment and requirements. Before real deployment, you should add:

- structured logging
- metrics and health endpoints
- request authentication beyond shared-secret webhook validation
- backup/rotation strategy for the SQLite store
- a stronger local embedding model if you need semantic quality beyond hashed embeddings
- CI automation for tests and packaging
