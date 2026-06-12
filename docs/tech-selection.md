# 技术选型说明

## 选型原则

1. **标准化优先**：优先选择已形成标准的协议和工具
2. **社区活跃度**：选择有活跃社区和维护者的技术
3. **学习成本**：考虑团队的学习曲线和上手难度
4. **性能需求**：根据实际场景选择合适性能的方案
5. **扩展性**：为未来增长预留扩展空间

## 协议层选型

### MCP (Model Context Protocol) — 推荐

| 维度 | 评估 |
|------|------|
| 标准化程度 | 由 Anthropic 推动的开放标准 |
| 生态支持 | Claude Desktop、VS Code、LangChain 等多平台支持 |
| 协议特性 | JSON-RPC 2.0、双向通信、能力协商 |
| 版本 | 最新稳定版 2024-11-05 |

**选型理由**：MCP 是当前唯一专门为 AI 智能体与工具交互设计的标准协议，拥有最广泛的生态支持。

### 对比方案

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **MCP** | 标准化、生态好、开箱即用 | 相对年轻、迭代快 | AI 工具集成首选 |
| **OpenAPI/Function Calling** | 成熟、广泛支持 | 缺少资源/提示原语 | 简单 API 调用 |
| **自研 gRPC** | 高性能、类型安全 | 缺少 AI 语义、开发成本高 | 内部高性能场景 |

## 传输层选型

### stdio — 推荐用于本地开发

- **优势**：零配置、低延迟、安全（进程内通信）
- **劣势**：无法跨网络、单进程限制
- **适用**：本地 IDE 插件、CLI 工具

### HTTP + SSE — 推荐用于生产环境

- **优势**：跨网络、负载均衡、水平扩展
- **劣势**：需要网络配置、略高延迟
- **适用**：云端部署、多租户服务

### 选型决策矩阵

| 场景 | stdio | HTTP+SSE | WebSocket |
|------|-------|----------|-----------|
| 本地开发 | 推荐 | 可用 | 过重 |
| 远程服务 | 不可用 | 推荐 | 可用 |
| 流式响应 | 支持 | 支持(SSE) | 推荐 |
| 负载均衡 | 不支持 | 支持 | 复杂 |

## 技能框架选型

### Python MCP SDK — 推荐

```python
# 官方 SDK，功能完整
from mcp.server import Server
from mcp.server.stdio import stdio_server
```

| 维度 | 评分 | 说明 |
|------|------|------|
| 完整性 | 5/5 | 官方维护，功能最全 |
| 文档 | 4/5 | 文档逐渐完善 |
| 社区 | 4/5 | GitHub 活跃 |
| 类型安全 | 5/5 | 基于 Pydantic，类型完整 |

### FastMCP (Python)

```python
# 高级封装，开发效率更高
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

| 维度 | 评分 | 说明 |
|------|------|------|
| 开发效率 | 5/5 | 装饰器风格，简洁优雅 |
| 社区 | 3/5 | 较新，社区在成长 |
| 适用场景 | 快速原型开发 | — |

### TypeScript MCP SDK

| 维度 | 评分 | 说明 |
|------|------|------|
| 生态 | 5/5 | npm 生态丰富 |
| 类型安全 | 5/5 | TypeScript 原生支持 |
| 适用场景 | Node.js 项目 | — |

## 编排层选型

### LangChain — 推荐用于复杂工作流

```python
from langchain.agents import create_agent
from langchain_mcp import MCPToolkit

# 将 MCP 工具集成到 LangChain 智能体
toolkit = MCPToolkit(server_params)
agent = create_agent(llm, toolkit.get_tools())
```

| 维度 | 评分 |
|------|------|
| 工作流编排 | 5/5 |
| 工具集成 | 5/5 |
| 学习成本 | 3/5（较陡） |

### 自定义编排器 — 推荐用于简单场景

```python
class SimpleOrchestrator:
    """轻量级编排器，无外部依赖"""

    async def execute_plan(self, plan: list[Task]) -> list[Result]:
        results = []
        for task in plan:
            result = await task.skill.execute(**task.params)
            results.append(result)
        return results
```

### 选型建议

| 场景 | 推荐方案 |
|------|---------|
| 快速原型 / 简单流程 | 自定义编排器 |
| 复杂多步骤工作流 | LangChain |
| 企业级任务调度 | Temporal / Prefect |

## 存储层选型

| 组件 | 推荐 | 备选 |
|------|------|------|
| 技能配置 | YAML/JSON 文件 | etcd |
| 执行日志 | SQLite（本地）/ PostgreSQL（生产） | Elasticsearch |
| 会话状态 | 内存（短期）/ Redis（长期） | PostgreSQL |
| 技能缓存 | LRU 内存缓存 | Redis |

## 技术栈总览

```
┌────────────────────────────────────────────┐
│  协议层: MCP (JSON-RPC 2.0)               │
├────────────────────────────────────────────┤
│  传输层: stdio / HTTP+SSE                  │
├────────────────────────────────────────────┤
│  服务层: Python 3.10+ (FastMCP / MCP SDK)  │
├────────────────────────────────────────────┤
│  编排层: LangChain / 自定义编排器           │
├────────────────────────────────────────────┤
│  存储层: SQLite → PostgreSQL               │
├────────────────────────────────────────────┤
│  监控: structlog + Prometheus              │
└────────────────────────────────────────────┘
```
