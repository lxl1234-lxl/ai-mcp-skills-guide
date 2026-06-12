# AI MCP Skills Guide

AI 系统中的 **MCP（Management Control Plane）** 架构设计、技能（Skill）开发指南与代码实现示例。

## 项目目的

本项目旨在为 AI 系统开发者提供一套完整的 MCP 架构实践指南，涵盖：

- **架构设计**：MCP 在 AI 系统中的分层设计、组件交互与数据流
- **技能开发**：如何为 AI 智能体设计、实现和管理可复用的技能模块
- **代码示例**：从基础技能到高级编排的完整实现示例
- **案例分析**：真实场景下的 MCP 应用案例与技术决策

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 协议层 | MCP (Model Context Protocol) | AI 智能体与工具服务之间的标准通信协议 |
| 服务层 | Python 3.10+ / Node.js 18+ | 技能服务器运行时 |
| 传输层 | stdio / HTTP+SSE | 本地与远程通信方式 |
| 编排层 | LangChain / Custom Orchestrator | 多技能编排与工作流管理 |
| 存储层 | SQLite / PostgreSQL | 状态持久化与配置管理 |

## 仓库结构

```
ai-mcp-skills-guide/
├── README.md                           # 项目概述
├── LICENSE                             # 开源许可证
├── CONTRIBUTING.md                     # 贡献指南
├── .gitignore                          # Git 忽略规则
├── docs/
│   ├── architecture.md                 # MCP 架构设计文档
│   ├── skill-development-guide.md      # AI 技能开发指南
│   ├── use-cases.md                    # 使用案例分析
│   └── tech-selection.md              # 技术选型说明
└── examples/
    ├── basic-skill/                    # 基础技能示例
    │   └── skill.py
    ├── mcp-integration/                # MCP 集成示例
    │   └── mcp_server.py
    └── advanced-patterns/              # 高级编排模式
        └── orchestration.py
```

## 快速开始

### 环境要求

- Python 3.10+
- pip 或 uv（推荐）

### 安装

```bash
# 克隆仓库
git clone https://github.com/lxl1234-lxl/ai-mcp-skills-guide.git
cd ai-mcp-skills-guide

# 安装依赖
pip install mcp langchain-core pydantic

# 运行基础技能示例
python examples/basic-skill/skill.py
```

### 运行 MCP 服务器示例

```bash
# 启动 MCP 集成服务器（stdio 模式）
