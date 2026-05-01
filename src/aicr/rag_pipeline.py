from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Document:
    text: str


class SimpleRAG:
    def __init__(self, documents: List[Document]) -> None:
        self.documents = documents

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        scored = []
        query_terms = set(query.lower().split())
        for doc in self.documents:
            terms = set(doc.text.lower().split())
            score = len(query_terms.intersection(terms))
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]

    def answer(self, query: str, top_k: int = 3) -> str:
        hits = self.retrieve(query, top_k=top_k)
        context = "\n".join(f"- {d.text}" for d in hits if d.text)
        if not context:
            return "未检索到有效上下文。"
        return f"基于检索结果回答：\n{context}"
