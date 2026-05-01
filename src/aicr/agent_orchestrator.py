from __future__ import annotations

from aicr.knowledge_graph import KnowledgeGraph
from aicr.mcp_bridge import MCPBridge
from aicr.rag_pipeline import SimpleRAG
from aicr.skills import SkillRegistry


class AICRAgent:
    def __init__(
        self,
        rag: SimpleRAG,
        kg: KnowledgeGraph,
        mcp: MCPBridge,
        skills: SkillRegistry,
    ) -> None:
        self.rag = rag
        self.kg = kg
        self.mcp = mcp
        self.skills = skills

    def run(self, user_query: str) -> str:
        rag_answer = self.rag.answer(user_query)
        graph_facts = self.kg.query("token")
        graph_text = "\n".join(
            f"- ({t.subject}) -[{t.predicate}]-> ({t.obj})" for t in graph_facts
        ) or "- 无图谱命中"

        skill_text = self.skills.run("budget_estimator", user_query)
        mcp_text = self.mcp.call("policy_checker", user_query)

        return (
            "=== AICR Agent Result ===\n"
            f"[RAG]\n{rag_answer}\n\n"
            f"[Knowledge Graph]\n{graph_text}\n\n"
            f"[Skill]\n{skill_text}\n\n"
            f"[MCP]\n{mcp_text}\n"
        )
