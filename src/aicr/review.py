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
        validation_level: str = "p1",
    ) -> ReviewResult:
        strengths = [
            "工作流已串联检索、图谱、技能与策略检查",
            "ReAct 轨迹可审计，支持逐步回放",
        ]
        risks = []
        suggestions = []
        level = validation_level.lower()

        if "token" not in query.lower():
            risks.append("查询未显式包含 token 约束，成本评估粒度不足")
            suggestions.append("在请求模板中加入日预算、峰值预算、月上限参数")

        missing_tool = any("工具不存在" in step.observation for step in react_trace)
        if missing_tool:
            risks.append("存在未注册工具，可能导致流程中断")
            suggestions.append("在启动阶段做工具自检并阻断不完整发布")

        # 收敛规则：用固定信号映射风险等级，避免主观波动。
        if missing_tool:
            danger_level = "high"
        elif risks and level == "p0":
            danger_level = "high"
        elif risks:
            danger_level = "medium"
        elif level == "p2":
            danger_level = "low"
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
