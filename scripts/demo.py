from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aicr.bootstrap import build_agent
from aicr.config import AICRConfig


def main() -> None:
    config = AICRConfig.from_env(ROOT)
    agent = build_agent(config, root=ROOT)
    review_files = [
        "services/reviewer/main.go",
        "backend/graph/index.py",
        "core/runtime/agent.cpp",
        "platform/audit/PolicyCheck.java",
    ]
    result = agent.run(
        "申请 LLM token 使用计划并完成 review",
        review_files=review_files,
        validation_level="p0",
    )
    print(result)


if __name__ == "__main__":
    main()
