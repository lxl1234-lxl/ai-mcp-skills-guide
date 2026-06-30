# 常见问题

## 通用

### Q1: 这个项目和官方 MCP Python SDK 是什么关系？

本项目是 **MCP 架构的教学/参考实现**，提供了简化版的 `SkillRegistry` 与 `MCPServer`，便于理解 MCP 协议的核心概念。**生产环境请使用官方 SDK**：[modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)。

本项目适合：

- 学习 MCP 架构设计
- 快速原型验证技能
- 作为自定义编排引擎的脚手架

### Q2: 为何 `MCPServer` 没有真正的 stdio 监听循环？

为了保持核心模块零依赖、可测试、易理解，`MCPServer` 仅提供同步的 `handle_request` 方法。如需对接 Claude Desktop 等 Host，请参考 `docs/architecture.md` 中关于官方 SDK 的集成示例。

### Q3: 支持 Node.js / TypeScript 吗？

当前仅提供 Python 实现。TypeScript 可参考 [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)。

## 技能开发

### Q4: 如何让 AI 准确判断何时调用我的技能？

技能的 `description` 是 AI 决策的关键。建议：

```python
# 差
description="搜索"

# 好
description="搜索 GitHub 仓库。当用户询问开源项目、查找代码示例或比较项目时调用。"
```

包含**功能 + 触发场景 + 输入输出说明**。

### Q5: 技能应该同步还是异步？

本项目 `BaseSkill.execute` 是同步接口（保持简单）。若需异步：

- 在 `execute` 内部用 `asyncio.run()` 包装
- 或使用 `Orchestrator` 编排异步任务

### Q6: 如何处理技能失败？

三种策略，按推荐度排序：

1. **返回结构化错误**（推荐）：`{"success": False, "error": "..."}`
2. **降级到缓存/默认值**：通过 `Orchestrator` 的 `fallback` 参数
3. **重试**：通过 `Task.max_retries` + 指数退避

### Q7: 技能可以调用其他技能吗？

可以。在 `execute` 内部实例化并调用其他技能即可。但推荐通过 `Orchestrator` 显式编排，便于追踪与调试。

## 编排

### Q8: `execute_sequential` 和 `execute_parallel` 该选哪个？

| 场景 | 选择 |
|------|------|
| 任务有数据依赖（前→后） | `sequential` |
| 任务独立可同时执行 | `parallel` |
| 根据中间结果动态决策 | `conditional` |
| 外部服务不稳定 | 任一 + `max_retries` + `fallback` |

### Q9: `execute_conditional` 何时停止？

当 `condition_fn` 返回空列表 `[]` 时停止。也会受 `max_iterations`（默认 3）限制，防止无限循环。

### Q10: `Task.fallback` 何时触发？

仅当所有重试都失败后触发。`fallback` 函数应返回降级数据（如缓存值）。

## 部署

### Q11: 如何在 Docker 中运行？

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
CMD ["python", "examples/mcp-integration/run_demo.py"]
```

### Q12: 如何监控技能执行？

`SkillRegistry.call_tool` 已自动注入 `_metadata.execution_time_ms`。可扩展记录到日志：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 贡献

### Q13: 如何贡献新技能？

1. 阅读 [技能开发指南](skill-development-guide.md)
2. 在 `src/ai_mcp_skills/` 新建模块
3. 在 `__init__.py` 导出
4. 在 `tests/` 添加测试
5. 在 `examples/` 添加演示
6. 提交 PR（参考 `.github/PULL_REQUEST_TEMPLATE.md`）

更多问题？[提交 Issue](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/issues)。
