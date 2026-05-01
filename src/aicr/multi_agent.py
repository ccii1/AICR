from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from aicr.prompt_rules import PromptRuleEngine


@dataclass
class AgentResult:
    agent_name: str
    focus: str
    output: str


@dataclass
class PlanResult:
    plan_name: str
    strategy: str
    scopes: List[str]
    validation_level: str
    prompt_text: str
    results: List[AgentResult]
    conclusion: str

    def render(self) -> str:
        lines = [
            f"Plan: {self.plan_name}",
            f"Strategy: {self.strategy}",
            f"Scopes: {', '.join(self.scopes)}",
            f"Validation: {self.validation_level}",
            f"Prompt: {self.prompt_text}",
            "Agents:",
        ]
        for item in self.results:
            lines.append(
                f"- {item.agent_name} ({item.focus}): {item.output}"
            )
        lines.append(f"Conclusion: {self.conclusion}")
        return "\n".join(lines)


class MultiAgentCoordinator:
    def __init__(self, tools: Dict[str, Callable[[str], str]]) -> None:
        self.tools = tools
        self.prompt_engine = PromptRuleEngine()

    def run_two_plans(
        self,
        query: str,
        review_files: List[str],
        validation_level: str = "p1",
    ) -> List[PlanResult]:
        return [
            self._run_plan_a(query, review_files, validation_level),
            self._run_plan_b(query, review_files, validation_level),
        ]

    def _run_plan_a(
        self,
        query: str,
        review_files: List[str],
        validation_level: str,
    ) -> PlanResult:
        # Plan A: 审核稳健优先，先规则后预算再补知识证据。
        prompt = self.prompt_engine.build_prompt("Plan-A", review_files, validation_level)
        prompt_query = self._compose_prompt_query(query, prompt.prompt_text)
        results = [
            self._exec("compliance-agent", "策略合规", "policy_checker", prompt_query),
            self._exec("cost-agent", "成本预算", "budget_estimator", prompt_query),
            self._exec("knowledge-agent", "知识检索", "rag_answer", prompt_query),
            self._exec("graph-agent", "关系校验", "graph_lookup", prompt_query),
        ]
        conclusion = "适合正式审批流程，强调可追溯和低风险。"
        return PlanResult(
            plan_name="Plan-A",
            strategy="risk-first",
            scopes=prompt.scopes,
            validation_level=prompt.validation_level,
            prompt_text=prompt.prompt_text,
            results=results,
            conclusion=conclusion,
        )

    def _run_plan_b(
        self,
        query: str,
        review_files: List[str],
        validation_level: str,
    ) -> PlanResult:
        # Plan B: 效率优先，先拿知识与预算，最后做策略兜底。
        prompt = self.prompt_engine.build_prompt("Plan-B", review_files, validation_level)
        prompt_query = self._compose_prompt_query(query, prompt.prompt_text)
        results = [
            self._exec("knowledge-agent", "快速检索", "rag_answer", prompt_query),
            self._exec("graph-agent", "关系补全", "graph_lookup", prompt_query),
            self._exec("cost-agent", "预算估算", "budget_estimator", prompt_query),
            self._exec("compliance-agent", "最终合规", "policy_checker", prompt_query),
        ]
        conclusion = "适合预研和快速迭代，强调交付速度。"
        return PlanResult(
            plan_name="Plan-B",
            strategy="speed-first",
            scopes=prompt.scopes,
            validation_level=prompt.validation_level,
            prompt_text=prompt.prompt_text,
            results=results,
            conclusion=conclusion,
        )

    def _compose_prompt_query(self, query: str, prompt_text: str) -> str:
        return f"[SYSTEM_PROMPT]\n{prompt_text}\n[USER_QUERY]\n{query}"

    def _exec(self, agent_name: str, focus: str, tool_name: str, query: str) -> AgentResult:
        tool = self.tools.get(tool_name)
        if not tool:
            return AgentResult(
                agent_name=agent_name,
                focus=focus,
                output=f"工具不存在: {tool_name}",
            )
        return AgentResult(agent_name=agent_name, focus=focus, output=tool(query))
