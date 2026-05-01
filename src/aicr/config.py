from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AICRConfig:
    app_name: str = "AICR"
    data_dir: Path = field(default_factory=lambda: Path(".aicr_data"))
    vector_db_path: Path = field(default_factory=lambda: Path(".aicr_data") / "vector_store.sqlite3")
    rag_collection: str = "default"
    rag_top_k: int = 4
    chunk_size: int = 800
    chunk_overlap: int = 120
    embedding_dimensions: int = 256
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8000
    validation_level: str = "p1"
    webhook_secret: str = ""
    corpus_paths: tuple[Path, ...] = field(default_factory=tuple)

    @classmethod
    def from_env(cls, root: Path | None = None) -> "AICRConfig":
        root = root or Path.cwd()
        data_dir = root / os.getenv("AICR_DATA_DIR", ".aicr_data")
        vector_db_path = root / os.getenv(
            "AICR_VECTOR_DB_PATH",
            str(Path(".aicr_data") / "vector_store.sqlite3"),
        )

        configured_paths = os.getenv("AICR_RAG_PATHS", "")
        if configured_paths.strip():
            corpus_paths = tuple(
                (root / item.strip()).resolve()
                for item in configured_paths.split(os.pathsep)
                if item.strip()
            )
        else:
            corpus_paths = (
                (root / "README.md").resolve(),
                (root / "docs").resolve(),
                (root / "src").resolve(),
            )

        return cls(
            data_dir=data_dir.resolve(),
            vector_db_path=vector_db_path.resolve(),
            rag_collection=os.getenv("AICR_RAG_COLLECTION", "default"),
            rag_top_k=int(os.getenv("AICR_RAG_TOP_K", "4")),
            chunk_size=int(os.getenv("AICR_RAG_CHUNK_SIZE", "800")),
            chunk_overlap=int(os.getenv("AICR_RAG_CHUNK_OVERLAP", "120")),
            embedding_dimensions=int(os.getenv("AICR_EMBEDDING_DIMENSIONS", "256")),
            webhook_host=os.getenv("AICR_WEBHOOK_HOST", "0.0.0.0"),
            webhook_port=int(os.getenv("AICR_WEBHOOK_PORT", "8000")),
            validation_level=os.getenv("AICR_VALIDATION_LEVEL", "p1"),
            webhook_secret=os.getenv("GITLAB_WEBHOOK_SECRET", ""),
            corpus_paths=corpus_paths,
        )
