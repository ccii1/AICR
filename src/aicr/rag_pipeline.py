from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from aicr.config import AICRConfig
from aicr.local_vector_store import LocalEmbeddingModel, LocalVectorStore, SearchHit, VectorDocument


TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".go",
    ".h",
    ".hpp",
    ".java",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass
class Document:
    text: str
    source: str = "memory"
    title: str = ""
    metadata: dict[str, str] = field(default_factory=dict)


class SimpleRAG:
    def __init__(
        self,
        *,
        vector_store: LocalVectorStore,
        embedding_model: LocalEmbeddingModel,
        collection: str,
        top_k: int = 4,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.collection = collection
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @classmethod
    def from_config(cls, config: AICRConfig, root: Path | None = None) -> "SimpleRAG":
        root = root or Path.cwd()
        rag = cls(
            vector_store=LocalVectorStore(config.vector_db_path),
            embedding_model=LocalEmbeddingModel(config.embedding_dimensions),
            collection=config.rag_collection,
            top_k=config.rag_top_k,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )
        rag.bootstrap(config.corpus_paths, root=root)
        return rag

    def bootstrap(self, corpus_paths: Sequence[Path], root: Path | None = None) -> int:
        root = root or Path.cwd()
        resolved_paths = []
        for path in corpus_paths:
            candidate = path if path.is_absolute() else (root / path)
            if candidate.exists():
                resolved_paths.append(candidate)
        return self.ingest_paths(resolved_paths)

    def ingest_documents(self, documents: Sequence[Document]) -> int:
        chunks: list[VectorDocument] = []
        for document in documents:
            for idx, chunk in enumerate(self._chunk_text(document.text)):
                chunks.append(
                    VectorDocument(
                        doc_id=f"{document.source}#{idx}",
                        source=document.source,
                        title=document.title or Path(document.source).name,
                        text=chunk,
                        metadata={**document.metadata, "chunk_index": str(idx)},
                    )
                )
        return self.vector_store.upsert_documents(self.collection, chunks, self.embedding_model)

    def ingest_paths(self, paths: Sequence[Path]) -> int:
        documents: list[Document] = []
        for path in paths:
            documents.extend(self._load_path(path))
        if not documents:
            return 0
        return self.ingest_documents(documents)

    def retrieve(self, query: str, top_k: int | None = None) -> list[SearchHit]:
        query_embedding = self.embedding_model.embed(query)
        return self.vector_store.search(
            self.collection,
            query_embedding,
            top_k=top_k or self.top_k,
        )

    def answer(self, query: str, top_k: int | None = None) -> str:
        hits = self.retrieve(query, top_k=top_k)
        if not hits:
            return "未检索到本地知识，请补充语料或检查索引。"

        lines = ["基于本地知识库检索结果："]
        for idx, hit in enumerate(hits, start=1):
            excerpt = self._summarize(hit.document.text)
            source = hit.document.source
            lines.append(f"{idx}. [{source}] score={hit.score:.3f} {excerpt}")
        return "\n".join(lines)

    def health_summary(self) -> str:
        count = self.vector_store.count_documents(self.collection)
        return (
            f"本地向量库状态: collection={self.collection}, "
            f"documents={count}, db={self.vector_store.db_path}"
        )

    def _load_path(self, path: Path) -> list[Document]:
        if path.is_dir():
            documents: list[Document] = []
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix.lower() in TEXT_EXTENSIONS:
                    documents.extend(self._load_path(child))
            return documents

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            return []

        text = self._read_text(path)
        if not text.strip():
            return []
        return [Document(text=text, source=str(path), title=path.name)]

    def _read_text(self, path: Path) -> str:
        for encoding in ("utf-8", "utf-8-sig", "gb18030"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return path.read_text(encoding="utf-8", errors="ignore")

    def _chunk_text(self, text: str) -> Iterable[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []
        if len(normalized) <= self.chunk_size:
            return [normalized]

        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(start + self.chunk_size, len(normalized))
            chunks.append(normalized[start:end])
            if end >= len(normalized):
                break
            start = max(end - self.chunk_overlap, start + 1)
        return chunks

    def _summarize(self, text: str, limit: int = 160) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3] + "..."
