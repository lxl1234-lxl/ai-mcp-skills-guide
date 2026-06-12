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
# 从 PyPI 安装（推荐）
pip install ai-mcp-skills

# 或从源码安装
git clone https://github.com/lxl1234-lxl/ai-mcp-skills-guide.git
cd ai-mcp-skills-guide
pip install -e .
```

### 运行示例

```bash
# 基础技能示例
python examples/basic-skill/run_demo.py

# MCP 服务器示例
python examples/mcp-integration/run_demo.py

# 高级编排示例
python examples/advanced-patterns/run_demo.py
```

### 快速使用

```python
from ai_mcp_skills import TextAnalysisSkill

skill = TextAnalysisSkill()
result = skill.execute(text="Hello world! 你好世界！")
print(result["data"]["keywords"])
```

## 核心概念

### MCP（Management Control Plane）

MCP 是连接 AI 智能体与外部工具、数据源和服务的标准协议。它定义了三个核心角色：

1. **Host（宿主）**：运行 AI 模型的应用（如 Claude Desktop、IDE）
2. **Client（客户端）**：在 Host 内部发起到 Server 的连接
3. **Server（服务端）**：提供工具、资源和提示模板的服务

### Skill（技能）

Skill 是封装了特定领域能力的可复用模块。每个 Skill 包含：

- **元数据**：名称、描述、版本、参数定义
- **执行逻辑**：核心业务逻辑实现
- **错误处理**：异常捕获与降级策略
- **测试用例**：单元测试与集成测试

## 使用方法

### 1. 了解架构

阅读 [架构设计文档](docs/architecture.md) 理解 MCP 在 AI 系统中的整体设计。

### 2. 学习技能开发

参考 [技能开发指南](docs/skill-development-guide.md) 学习如何创建自己的 AI 技能。

### 3. 运行示例代码

从 [examples/](examples/) 目录中选择适合你的示例运行和修改。

### 4. 参考案例

查看 [使用案例](docs/use-cases.md) 了解真实场景中的最佳实践。

## 参与贡献

我们欢迎所有形式的贡献！请阅读 [贡献指南](CONTRIBUTING.md) 了解：

- 如何提交 Issue
- 如何提交 Pull Request
- 代码规范与审查流程

## 许可证

本项目采用 [MIT License](LICENSE)。

---

**维护者**: [lxl1234-lxl](https://github.com/lxl1234-lxl)
