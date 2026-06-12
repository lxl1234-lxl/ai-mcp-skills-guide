# MCP 架构设计文档

## 概述

MCP（Management Control Plane）在 AI 系统中充当智能体与外部能力之间的**控制面**，负责能力发现、协议协商、执行调度和状态管理。本文档定义了 MCP 在 AI 系统中的架构分层、组件职责和交互模式。

## 架构分层

```
┌─────────────────────────────────────────────────┐
│                  AI Host Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │  LLM     │  │  Agent   │  │  Orchestrator│  │
│  │  Engine  │  │  Runtime │  │  (LangChain) │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
├─────────────────────────────────────────────────┤
│               MCP Client Layer                   │
│  ┌──────────────────────────────────────────┐   │
│  │     MCP Client (协议客户端)               │   │
│  │  - 能力发现 (Capability Discovery)        │   │
│  │  - 协议协商 (Protocol Negotiation)        │   │
│  │  - 请求路由 (Request Routing)             │   │
│  │  - 连接管理 (Connection Management)       │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│              Transport Layer                     │
│  ┌─────────────────┐  ┌────────────────────┐    │
│  │  stdio Transport │  │  HTTP+SSE Transport│    │
│  └─────────────────┘  └────────────────────┘    │
├─────────────────────────────────────────────────┤
│               MCP Server Layer                   │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐   │
│  │ Tool     │ │ Resource │ │ Prompt         │   │
│  │ Provider │ │ Provider │ │ Provider      │   │
│  └──────────┘ └──────────┘ └───────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │         Skill Registry (技能注册中心)     │   │
│  └──────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│              External Services                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │
│  │ GitHub │ │Database│ │  API   │ │  File  │  │
│  │  API   │ │        │ │Gateway │ │ System │  │
│  └────────┘ └────────┘ └────────┘ └────────┘  │
└─────────────────────────────────────────────────┘
```

## 核心组件

### 1. AI Host Layer（宿主层）

宿主层是 AI 模型的运行环境，负责推理和决策。

- **LLM Engine**：大语言模型推理引擎
- **Agent Runtime**：智能体运行时，管理对话上下文和工具调用循环
- **Orchestrator**：编排器，管理多步骤工作流和技能调用顺序

### 2. MCP Client Layer（客户端层）

MCP 客户端是 Host 与 Server 之间的桥梁。

```python
# MCP 客户端的核心抽象
class MCPClient:
    """MCP 协议客户端，管理与服务器的生命周期"""

    def __init__(self, transport: Transport):
        self._transport = transport           # 传输层实现
        self._capabilities: dict = {}         # 服务器能力缓存
        self._tools: list[ToolDef] = []       # 可用工具列表
        self._resources: list[ResourceDef] = []  # 可用资源列表

    async def initialize(self) -> None:
        """与服务器握手，交换能力信息""""
        ...

    async def call_tool(self, name: str, arguments: dict) -> ToolResult:
        """调用服务器提供的工具""""
        ...

    async def read_resource(self, uri: str) -> ResourceContent:
        """读取服务器提供的资源""""
        ...
```

### 3. Transport Layer（传输层）

支持两种传输模式：

| 模式 | 适用场景 | 特点 |
|------|---------|------|
| **stdio** | 本地进程通信 | 低延迟、无需网络配置、适合开发 |
| **HTTP+SSE** | 远程服务通信 | 支持分布式部署、跨网络访问 |

### 4. MCP Server Layer（服务端层）

服务端提供三种核心原语：

- **Tool（工具）**：可被 AI 调用的函数，接收参数并返回结果
- **Resource（资源）**：可被 AI 读取的只读数据源（文件、数据库记录等）
- **Prompt（提示模板）**：预定义的提示模板，帮助 AI 构建上下文

### 5. Skill Registry（技能注册中心）

技能注册中心管理所有已注册的技能模块：

```python
class SkillRegistry:
    """技能注册中心 - 管理所有可用技能的发现和生命周期"""

    def __init__(self):
        self._skills: dict[str, BaseSkill] = {}  # 技能实例映射

    def register(self, skill: BaseSkill) -> None:
        """注册一个新技能到系统中""""
        ...

    def discover(self, capability: str) -> list[BaseSkill]:
        """根据能力描述发现匹配的技能""""
        ...

    def get_tool_definitions(self) -> list[ToolDef]:
        """获取所有技能的 MCP 工具定义""""
        ...
```

## 数据流

### 工具调用流程

```
┌──────┐    ┌───────┐    ┌────────┐    ┌─────────┐    ┌──────────┐
│ Host │───>│Client │───>│Transport│───>│ Server  │───>│  Skill   │
│(LLM) │    │       │    │        │    │         │    │ Executor │
└──────┘    └───────┘    └────────┘    └─────────┘    └──────────┘
    │                                                        │
    │  1. LLM 决定调用工具                                   │
    │  2. Client 封装请求（JSON-RPC）                        │
    │  3. Transport 发送请求                                 │
    │  4. Server 路由到对应 Skill                           │
    │  5. Skill 执行并返回结果                              │
    │<─────────── 6. 结果沿原路径返回 ────────────────────── │
```

## 设计原则

1. **关注点分离**：协议层、传输层、业务逻辑层严格解耦
2. **能力即接口**：Server 通过能力声明对外暴露功能，Client 按需发现
3. **松耦合通信**：基于 JSON-RPC 的无状态请求-响应模式
4. **渐进增强**：从简单 stdio 本地模式起步，逐步扩展到 HTTP+SSE 分布式模式
5. **容错设计**：每个 Skill 独立运行，单个 Skill 故障不影响整体系统

## 扩展性考虑

- **水平扩展**：Server 可部署多实例，通过负载均衡分发请求
- **技能热加载**：支持运行时动态注册和卸载技能
- **多协议适配**：预留 gRPC、WebSocket 等传输层扩展点
- **监控与可观测性**：集成日志、指标和追踪能力
