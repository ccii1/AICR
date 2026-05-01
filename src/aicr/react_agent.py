from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class ReActStep:
    thought: str
    action: str
    observation: str


class ReActAgent:
    def __init__(self, tools: Dict[str, Callable[[str], str]]) -> None:
        self.tools = tools

    def run(self, query: str, max_steps: int = 3) -> List[ReActStep]:
        trace: List[ReActStep] = []
        tool_order = self._plan_tools(query)

        for idx, tool_name in enumerate(tool_order[:max_steps]):
            thought = f"第 {idx + 1} 步：调用 `{tool_name}` 补充审查证据。"
            tool = self.tools.get(tool_name)
            if not tool:
                trace.append(
                    ReActStep(
                        thought=thought,
                        action=f"call:{tool_name}",
                        observation=f"工具不存在: {tool_name}",
                    )
                )
                continue
            observation = tool(query)
            trace.append(
                ReActStep(
                    thought=thought,
                    action=f"call:{tool_name}",
                    observation=observation,
                )
            )
        return trace

    def _plan_tools(self, query: str) -> List[str]:
        lowered = query.lower()
        tools: List[str] = []
        if "review" in lowered or "审查" in query or "审核" in query:
            tools.append("policy_checker")
        if "token" in lowered or "预算" in query or "成本" in query:
            tools.append("budget_estimator")
        tools.extend(["rag_answer", "graph_lookup", "rag_status"])

        seen = set()
        ordered = []
        for item in tools:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered
