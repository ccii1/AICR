from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

# Make "src" importable when running from repository root.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aicr.agent_orchestrator import AICRAgent
from aicr.knowledge_graph import KnowledgeGraph, Triple
from aicr.mcp_bridge import MCPBridge
from aicr.rag_pipeline import Document, SimpleRAG
from aicr.skills import SkillRegistry


def build_agent() -> AICRAgent:
    docs = [
        Document("RAG 可以降低幻觉并提升企业知识回答准确率。"),
        Document("知识图谱适合建模部门、系统、预算、策略之间的关系。"),
        Document("MCP 可统一连接内部 API、知识库和审批系统。"),
        Document("Skill 可封装 token 预算评估、审计检查等复用能力。"),
    ]
    rag = SimpleRAG(docs)
    kg = KnowledgeGraph(
        [
            Triple("TokenPlan", "depends_on", "RAG"),
            Triple("TokenPlan", "depends_on", "KnowledgeGraph"),
            Triple("TokenPlan", "depends_on", "Agent"),
            Triple("TokenPlan", "depends_on", "MCP"),
            Triple("TokenPlan", "depends_on", "Skill"),
        ]
    )
    mcp = MCPBridge()
    mcp.register_tool("policy_checker", lambda q: f"策略检查通过: {q}")
    skills = SkillRegistry()
    skills.register("budget_estimator", lambda q: f"预算估算: 请求 `{q}` 建议 900k token/天")
    return AICRAgent(rag=rag, kg=kg, mcp=mcp, skills=skills)


def extract_review_files(payload: dict[str, Any]) -> list[str]:
    review_files: list[str] = []
    commits = payload.get("commits", [])
    for commit in commits:
        for key in ("added", "modified", "removed"):
            for file_path in commit.get(key, []):
                if file_path not in review_files:
                    review_files.append(file_path)
    return review_files


class GitLabWebhookHandler(BaseHTTPRequestHandler):
    agent = build_agent()
    webhook_secret = os.getenv("GITLAB_WEBHOOK_SECRET", "")
    validation_level = os.getenv("AICR_VALIDATION_LEVEL", "p1")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/webhook/gitlab":
            self._json_response(404, {"ok": False, "error": "not found"})
            return

        if self.webhook_secret:
            token = self.headers.get("X-Gitlab-Token", "")
            if token != self.webhook_secret:
                self._json_response(401, {"ok": False, "error": "invalid token"})
                return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._json_response(400, {"ok": False, "error": "invalid json"})
            return

        object_kind = payload.get("object_kind", "unknown")
        if object_kind not in {"push", "merge_request"}:
            self._json_response(
                200,
                {"ok": True, "ignored": True, "reason": f"unsupported object_kind={object_kind}"},
            )
            return

        review_files = extract_review_files(payload)
        query = f"GitLab webhook review for {object_kind}"
        result = self.agent.run(
            user_query=query,
            review_files=review_files,
            validation_level=self.validation_level,
        )

        self._json_response(
            200,
            {
                "ok": True,
                "event": object_kind,
                "review_files_count": len(review_files),
                "review_files": review_files,
                "result": result,
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        # Keep output concise for webhook server logs.
        print(f"[webhook] {self.address_string()} - {format % args}")

    def _json_response(self, status_code: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    host = os.getenv("AICR_WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("AICR_WEBHOOK_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), GitLabWebhookHandler)
    print(f"AICR GitLab webhook listener started at http://{host}:{port}/webhook/gitlab")
    server.serve_forever()


if __name__ == "__main__":
    main()
