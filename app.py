from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

# Make "src" importable when running from repository root.
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aicr.bootstrap import build_agent
from aicr.config import AICRConfig


CONFIG = AICRConfig.from_env(ROOT)


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
    agent = build_agent(CONFIG, root=ROOT)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/webhook/gitlab":
            self._json_response(404, {"ok": False, "error": "not found"})
            return

        if CONFIG.webhook_secret:
            token = self.headers.get("X-Gitlab-Token", "")
            if token != CONFIG.webhook_secret:
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
            validation_level=CONFIG.validation_level,
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
        print(f"[webhook] {self.address_string()} - {format % args}")

    def _json_response(self, status_code: int, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    server = ThreadingHTTPServer((CONFIG.webhook_host, CONFIG.webhook_port), GitLabWebhookHandler)
    print(
        "AICR GitLab webhook listener started at "
        f"http://{CONFIG.webhook_host}:{CONFIG.webhook_port}/webhook/gitlab"
    )
    print(GitLabWebhookHandler.agent.rag.health_summary())
    server.serve_forever()


if __name__ == "__main__":
    main()
