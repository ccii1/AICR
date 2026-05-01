# AICR - AI Capability & Compliance Review

AICR 是一个面向企业级 LLM 需求落地的参考项目，展示以下前沿能力如何协同：

- RAG：企业知识检索增强生成
- 知识图谱：实体与关系建模，支持可追溯答案
- Agent：多步骤任务规划与执行
- MCP：统一连接外部工具和数据源
- Skill：可复用技能模块，沉淀业务能力

## 目标场景

用于支持企业内部 LLM 能力建设需求：

1. 构建企业知识底座与可审计问答流程
2. 明确 token 消耗来源与优化手段
3. 提供可演示、可扩展、可提交的 GitHub 项目模板

## 项目结构

```text
AICR/
  docs/
    llm-demand.md
  scripts/
    demo.py
  src/aicr/
    agent_orchestrator.py
    config.py
    knowledge_graph.py
    mcp_bridge.py
    rag_pipeline.py
    skills.py
```

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python scripts/demo.py
```

## GitLab Webhook 监听

```bash
set PYTHONPATH=src
set AICR_WEBHOOK_PORT=8000
set AICR_VALIDATION_LEVEL=p1
set GITLAB_WEBHOOK_SECRET=your_secret
python app.py
```

- Webhook URL: `http://<your-host>:8000/webhook/gitlab`
- Header: `X-Gitlab-Token: your_secret`
- 支持事件：`push`、`merge_request`

## 模块说明

- `rag_pipeline.py`: 文本切分、向量化、检索与回答生成
- `knowledge_graph.py`: 基于三元组的知识图谱查询
- `workflow.py`: 轻量工作流引擎，支持分步执行与状态记录
- `react_agent.py`: ReAct 思维链执行器，产出可审计轨迹
- `multi_agent.py`: 多 Agent 协作器，支持两套 plan 并行评估
- `prompt_rules.py`: 多套提示词规则引擎，按审查文件扩展名触发（cpp/py/go/java）
- `docs/prompts/p0.md|p1.md|p2.md`: 按验证强度定义的提示词模板（已抽离）
- `review.py`: 结构化评审结果（优势、风险、建议）
- `agent_orchestrator.py`: 将 Workflow + ReAct + RAG + KG + Skill + MCP 串联
- `mcp_bridge.py`: MCP 工具注册与调用
- `skills.py`: 业务技能注册（预算评估、风险检查等）

## 产出价值

- 提供了 LLM 能力建设与成本规划所需的技术可行性证明
- 具备后续接入真实向量库、图数据库、MCP Server 的扩展点
- 支持快速演示与汇报
