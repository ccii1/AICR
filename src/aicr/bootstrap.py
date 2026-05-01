from __future__ import annotations

import re
from pathlib import Path

from aicr.agent_orchestrator import AICRAgent
from aicr.config import AICRConfig
from aicr.knowledge_graph import KnowledgeGraph, Triple
from aicr.mcp_bridge import MCPBridge
from aicr.rag_pipeline import SimpleRAG
from aicr.skills import SkillRegistry


def build_agent(config: AICRConfig, root: Path | None = None) -> AICRAgent:
    root = root or Path.cwd()
    rag = SimpleRAG.from_config(config, root=root)

    graph = KnowledgeGraph(
        [
            Triple("RAG", "uses", "LocalVectorStore"),
            Triple("RAG", "stores_in", str(config.vector_db_path)),
            Triple("AICR", "orchestrates", "Workflow"),
            Triple("AICR", "orchestrates", "ReAct"),
            Triple("AICR", "orchestrates", "MultiAgentPlans"),
            Triple("ReviewPolicy", "supports", "p0"),
            Triple("ReviewPolicy", "supports", "p1"),
            Triple("ReviewPolicy", "supports", "p2"),
        ]
    )

    mcp = MCPBridge()
    mcp.register_tool("policy_checker", _policy_check)
    mcp.register_tool("vector_store_status", lambda _: rag.health_summary())

    skills = SkillRegistry()
    skills.register("budget_estimator", _budget_estimator)
    skills.register("rag_status", lambda _: rag.health_summary())

    return AICRAgent(rag=rag, kg=graph, mcp=mcp, skills=skills)


def _policy_check(query: str) -> str:
    matched = re.search(r"\[validation_level=(p[0-2])\]", query, flags=re.IGNORECASE)
    validation_level = matched.group(1).lower() if matched else "p1"
    text = query.lower()
    if any(flag in text for flag in ("password", "secret", "token leak", "权限绕过")):
        return f"策略检查未通过: 检测到敏感风险关键词，建议按 {validation_level} 阻断处理。"
    return f"策略检查通过: 当前请求符合 {validation_level} 级别默认审查策略。"


def _budget_estimator(query: str) -> str:
    base_tokens = max(1200, len(query) * 18)
    if "review" in query.lower() or "审查" in query:
        base_tokens += 1800
    return f"预算估算: 当前请求建议预留约 {base_tokens} tokens 的单次执行预算。"
