from aicr.agent_orchestrator import AICRAgent
from aicr.knowledge_graph import KnowledgeGraph, Triple
from aicr.mcp_bridge import MCPBridge
from aicr.rag_pipeline import Document, SimpleRAG
from aicr.skills import SkillRegistry


def main() -> None:
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
    skills.register("budget_estimator", lambda q: f"预算估算: 请求 `{q}` 建议 150k token/天")

    agent = AICRAgent(rag=rag, kg=kg, mcp=mcp, skills=skills)
    review_files = [
        "services/reviewer/main.go",
        "backend/graph/index.py",
        "core/runtime/agent.cpp",
        "platform/audit/PolicyCheck.java",
    ]
    result = agent.run(
        "申请 LLM token 使用计划并完成review",
        review_files=review_files,
        validation_level="p0",
    )
    print(result)


if __name__ == "__main__":
    main()
