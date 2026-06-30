# 示例代码

本目录包含 `ai_mcp_skills` 包的可运行示例。所有示例都假定已执行：

```bash
pip install -e .
```

## 示例清单

| 目录 | 说明 | 运行命令 |
|------|------|---------|
| [basic-skill](basic-skill/run_demo.py) | 文本分析技能的基础使用 | `python examples/basic-skill/run_demo.py` |
| [mcp-integration](mcp-integration/run_demo.py) | MCP 服务器多工具注册与调用 | `python examples/mcp-integration/run_demo.py` |
| [advanced-patterns](advanced-patterns/run_demo.py) | 编排引擎四种模式演示 | `python examples/advanced-patterns/run_demo.py` |
| [http-skill](http-skill/run_demo.py) | HTTP 请求技能与错误处理 | `python examples/http-skill/run_demo.py` |

## 推荐学习顺序

1. **basic-skill** — 理解 `BaseSkill` 生命周期与工具定义
2. **mcp-integration** — 理解 `SkillRegistry` 与 `MCPServer` 的 JSON-RPC 交互
3. **http-skill** — 学习真实网络技能的错误处理模式
4. **advanced-patterns** — 掌握 `Orchestrator` 的串行/并行/条件/降级编排

## 示例特点

- 所有示例**无外部网络依赖**（除 http-skill 演示真实请求外）
- 每个示例独立可运行，输出清晰的进度信息
- 示例代码可直接复制作为新技能的脚手架
