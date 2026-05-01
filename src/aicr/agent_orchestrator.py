from __future__ import annotations

from aicr.knowledge_graph import KnowledgeGraph
from aicr.multi_agent import MultiAgentCoordinator
from aicr.mcp_bridge import MCPBridge
from aicr.rag_pipeline import SimpleRAG
from aicr.react_agent import ReActAgent
from aicr.review import ReviewEngine
from aicr.skills import SkillRegistry
from aicr.workflow import WorkflowContext, WorkflowEngine


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

    def run(
        self,
        user_query: str,
        review_files: list[str] | None = None,
        validation_level: str = "p1",
    ) -> str:
        review_files = review_files or []
        workflow = WorkflowEngine()
        context = WorkflowContext(user_query=user_query)
        policy_payload = f"[validation_level={validation_level}] {user_query}"

        def step_rag(ctx: WorkflowContext) -> None:
            ctx.state["rag_answer"] = self.rag.answer(ctx.user_query)

        def step_kg(ctx: WorkflowContext) -> None:
            graph_facts = self.kg.query("RAG") + self.kg.query("ReviewPolicy")
            ctx.state["graph_text"] = "\n".join(
                f"- ({t.subject}) -[{t.predicate}]-> ({t.obj})" for t in graph_facts
            ) or "- 未查询到图谱关系。"

        def step_skill(ctx: WorkflowContext) -> None:
            ctx.state["skill_text"] = self.skills.run("budget_estimator", ctx.user_query)

        def step_mcp(ctx: WorkflowContext) -> None:
            ctx.state["mcp_text"] = self.mcp.call("policy_checker", policy_payload)
            ctx.state["vector_store_text"] = self.mcp.call("vector_store_status", ctx.user_query)

        workflow.add_step("rag_retrieval", step_rag)
        workflow.add_step("graph_lookup", step_kg)
        workflow.add_step("skill_inference", step_skill)
        workflow.add_step("policy_check", step_mcp)
        context = workflow.run(context)

        react = ReActAgent(
            tools={
                "policy_checker": lambda q: self.mcp.call(
                    "policy_checker",
                    f"[validation_level={validation_level}] {q}",
                ),
                "budget_estimator": lambda q: self.skills.run("budget_estimator", q),
                "rag_answer": lambda q: self.rag.answer(q),
                "graph_lookup": lambda q: "\n".join(
                    f"- ({t.subject}) -[{t.predicate}]-> ({t.obj})" for t in self.kg.query(q)
                )
                or "- 未命中图谱关系。",
                "rag_status": lambda q: self.skills.run("rag_status", q),
            }
        )
        react_trace = react.run(user_query, max_steps=5)
        react_text = "\n".join(
            f"{idx + 1}. thought={step.thought}\n   action={step.action}\n   observation={step.observation}"
            for idx, step in enumerate(react_trace)
        )

        review = ReviewEngine().run(
            user_query,
            react_trace,
            review_files=review_files,
            validation_level=validation_level,
        )

        multi_agent = MultiAgentCoordinator(
            tools={
                "policy_checker": lambda q: self.mcp.call(
                    "policy_checker",
                    f"[validation_level={validation_level}] {q}",
                ),
                "budget_estimator": lambda q: self.skills.run("budget_estimator", q),
                "rag_answer": lambda q: self.rag.answer(q),
                "graph_lookup": lambda q: "\n".join(
                    f"- ({t.subject}) -[{t.predicate}]-> ({t.obj})" for t in self.kg.query(q)
                )
                or "- 未命中图谱关系。",
                "rag_status": lambda q: self.skills.run("rag_status", q),
            }
        )
        plans = multi_agent.run_two_plans(
            user_query,
            review_files=review_files,
            validation_level=validation_level,
        )
        plans_text = "\n\n".join(plan.render() for plan in plans)
        review_files_text = ", ".join(review_files) if review_files else "未提供文件清单。"

        return (
            "=== AICR Agent Result ===\n"
            f"[Validation Level]\n{validation_level}\n\n"
            f"[Review Files]\n{review_files_text}\n\n"
            f"[Workflow Last Step]\n{context.state.get('last_step', 'unknown')}\n\n"
            f"[RAG]\n{context.state.get('rag_answer', '')}\n\n"
            f"[Vector Store]\n{context.state.get('vector_store_text', '')}\n\n"
            f"[Knowledge Graph]\n{context.state.get('graph_text', '')}\n\n"
            f"[Skill]\n{context.state.get('skill_text', '')}\n\n"
            f"[MCP]\n{context.state.get('mcp_text', '')}\n\n"
            f"[ReAct Trace]\n{react_text}\n\n"
            f"[Multi-Agent Two Plans]\n{plans_text}\n\n"
            f"[Review]\n{review.render()}\n"
        )
