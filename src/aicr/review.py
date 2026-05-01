from __future__ import annotations

from dataclasses import dataclass
from typing import List

from aicr.react_agent import ReActStep


@dataclass
class ReviewResult:
    status: str
    danger_level: str
    strengths: List[str]
    risks: List[str]
    suggestions: List[str]

    def render(self) -> str:
        strengths = "\n".join(f"- {item}" for item in self.strengths) or "- 无"
        risks = "\n".join(f"- {item}" for item in self.risks) or "- 无"
        suggestions = "\n".join(f"- {item}" for item in self.suggestions) or "- 无"
        return (
            f"Review Status: {self.status}\n"
            f"Danger Level: {self.danger_level}\n"
            f"[Strengths]\n{strengths}\n\n"
            f"[Risks]\n{risks}\n\n"
            f"[Suggestions]\n{suggestions}\n"
        )


class ReviewEngine:
    def run(
        self,
        query: str,
        react_trace: List[ReActStep],
        review_files: List[str] | None = None,
        validation_level: str = "p1",
    ) -> ReviewResult:
        review_files = review_files or []
        strengths = [
            "主流程已串联本地 RAG、知识图谱、技能和策略检查。",
            "ReAct 轨迹可回放，便于审计和问题定位。",
        ]
        risks: list[str] = []
        suggestions: list[str] = []
        level = validation_level.lower()
        query_lower = query.lower()

        if not review_files:
            risks.append("未提供待审查文件列表，当前结果更接近预审而不是正式发布审查。")
            suggestions.append("在接入 CI 或 webhook 时传入精确的变更文件清单。")

        if "token" not in query_lower and "审查" not in query and "review" not in query_lower:
            risks.append("请求目标不够明确，难以推断审查范围和风险边界。")
            suggestions.append("补充业务目标、风险约束和预期输出格式。")

        if any("工具不存在" in step.observation for step in react_trace):
            risks.append("ReAct 轨迹里存在缺失工具，说明运行时装配不完整。")
            suggestions.append("在服务启动阶段执行工具注册自检，并将失败直接阻断。")

        if not any("本地向量库状态" in step.observation for step in react_trace):
            risks.append("没有观测到向量库健康检查结果，RAG 可用性证据不足。")
            suggestions.append("保留向量库状态检查，并在部署时监控索引条数和更新时间。")

        if level == "p0" and risks:
            danger_level = "high"
        elif risks:
            danger_level = "medium"
        else:
            danger_level = "low"

        if danger_level == "high":
            status = "blocked"
        elif danger_level == "medium":
            status = "needs_attention"
        else:
            status = "pass"

        return ReviewResult(
            status=status,
            danger_level=danger_level,
            strengths=strengths,
            risks=risks,
            suggestions=suggestions,
        )
