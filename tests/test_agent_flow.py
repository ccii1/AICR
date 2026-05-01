from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from aicr.bootstrap import build_agent
from aicr.config import AICRConfig


class AgentFlowTests(unittest.TestCase):
    def test_agent_uses_requested_validation_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("review guidance for local vector store", encoding="utf-8")

            config = AICRConfig(
                data_dir=root / ".aicr_data",
                vector_db_path=root / ".aicr_data" / "vector.sqlite3",
                corpus_paths=(root / "README.md",),
            )
            agent = build_agent(config, root=root)

            result = agent.run(
                "please review password handling",
                review_files=["src/app.py"],
                validation_level="p0",
            )

            self.assertIn("策略检查未通过", result)
            self.assertIn("p0", result)


if __name__ == "__main__":
    unittest.main()
