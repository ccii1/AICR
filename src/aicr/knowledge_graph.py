from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Triple:
    subject: str
    predicate: str
    obj: str


class KnowledgeGraph:
    def __init__(self, triples: List[Triple]) -> None:
        self.triples = triples

    def query(self, keyword: str) -> List[Triple]:
        key = keyword.lower()
        return [
            t
            for t in self.triples
            if key in t.subject.lower() or key in t.predicate.lower() or key in t.obj.lower()
        ]
