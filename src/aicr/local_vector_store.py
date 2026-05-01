from __future__ import annotations

import json
import math
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Sequence


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+", re.UNICODE)
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]+", re.UNICODE)


@dataclass
class VectorDocument:
    text: str
    source: str
    title: str = ""
    doc_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    document: VectorDocument
    score: float


class LocalEmbeddingModel:
    def __init__(self, dimensions: int = 256) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = list(self._iter_features(text))
        if not tokens:
            return vector

        for token in tokens:
            index = int(sha256(token.encode("utf-8")).hexdigest(), 16) % self.dimensions
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0.0:
            return vector
        return [value / norm for value in vector]

    def _iter_features(self, text: str) -> Iterable[str]:
        lowered = text.lower()
        for token in TOKEN_PATTERN.findall(lowered):
            yield f"w:{token}"
            if len(token) > 3:
                for idx in range(len(token) - 2):
                    yield f"g:{token[idx:idx + 3]}"

        for block in CJK_PATTERN.findall(text):
            for char in block:
                yield f"c:{char}"
            if len(block) > 1:
                for idx in range(len(block) - 1):
                    yield f"b:{block[idx:idx + 2]}"


class LocalVectorStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def upsert_documents(
        self,
        collection: str,
        documents: Sequence[VectorDocument],
        embedding_model: LocalEmbeddingModel,
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        upserted = 0

        with sqlite3.connect(self.db_path) as conn:
            for index, document in enumerate(documents):
                doc_id = document.doc_id or self._stable_doc_id(collection, document, index)
                checksum = sha256(document.text.encode("utf-8")).hexdigest()
                current = conn.execute(
                    "SELECT checksum FROM rag_documents WHERE collection = ? AND doc_id = ?",
                    (collection, doc_id),
                ).fetchone()
                if current and current[0] == checksum:
                    continue

                embedding = embedding_model.embed(document.text)
                conn.execute(
                    """
                    INSERT INTO rag_documents (
                        collection, doc_id, source, title, text, metadata_json,
                        embedding_json, checksum, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(collection, doc_id) DO UPDATE SET
                        source = excluded.source,
                        title = excluded.title,
                        text = excluded.text,
                        metadata_json = excluded.metadata_json,
                        embedding_json = excluded.embedding_json,
                        checksum = excluded.checksum,
                        updated_at = excluded.updated_at
                    """,
                    (
                        collection,
                        doc_id,
                        document.source,
                        document.title,
                        document.text,
                        json.dumps(document.metadata, ensure_ascii=False, sort_keys=True),
                        json.dumps(embedding),
                        checksum,
                        now,
                    ),
                )
                upserted += 1
            conn.commit()
        return upserted

    def search(
        self,
        collection: str,
        query_embedding: Sequence[float],
        top_k: int = 4,
        source_filters: Sequence[str] | None = None,
    ) -> list[SearchHit]:
        sql = """
            SELECT doc_id, source, title, text, metadata_json, embedding_json
            FROM rag_documents
            WHERE collection = ?
        """
        params: list[Any] = [collection]

        if source_filters:
            placeholders = ",".join("?" for _ in source_filters)
            sql += f" AND source IN ({placeholders})"
            params.extend(source_filters)

        hits: list[SearchHit] = []
        with sqlite3.connect(self.db_path) as conn:
            for row in conn.execute(sql, params):
                embedding = json.loads(row[5])
                score = self._cosine_similarity(query_embedding, embedding)
                metadata = json.loads(row[4]) if row[4] else {}
                hits.append(
                    SearchHit(
                        document=VectorDocument(
                            doc_id=row[0],
                            source=row[1],
                            title=row[2],
                            text=row[3],
                            metadata=metadata,
                        ),
                        score=score,
                    )
                )

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]

    def count_documents(self, collection: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM rag_documents WHERE collection = ?",
                (collection,),
            ).fetchone()
        return int(row[0]) if row else 0

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_documents (
                    collection TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (collection, doc_id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_rag_documents_collection_source "
                "ON rag_documents(collection, source)"
            )
            conn.commit()

    def _stable_doc_id(self, collection: str, document: VectorDocument, index: int) -> str:
        key = f"{collection}|{document.source}|{document.title}|{index}|{document.text[:120]}"
        return sha256(key.encode("utf-8")).hexdigest()

    def _cosine_similarity(self, left: Sequence[float], right: Sequence[float]) -> float:
        return float(sum(a * b for a, b in zip(left, right)))
