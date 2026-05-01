from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aicr.config import AICRConfig
from aicr.rag_pipeline import SimpleRAG


class RagPipelineTests(unittest.TestCase):
    def test_bootstrap_indexes_local_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            (docs_dir / "guide.md").write_text(
                "AICR uses a local vector store for retrieval and review.",
                encoding="utf-8",
            )

            config = AICRConfig(
                data_dir=root / ".aicr_data",
                vector_db_path=root / ".aicr_data" / "vector.sqlite3",
                corpus_paths=(docs_dir,),
            )
            rag = SimpleRAG.from_config(config, root=root)

            answer = rag.answer("local vector review")
            self.assertIn("本地知识库检索结果", answer)
            self.assertIn("guide.md", answer)
            self.assertGreater(rag.vector_store.count_documents(config.rag_collection), 0)


if __name__ == "__main__":
    unittest.main()
