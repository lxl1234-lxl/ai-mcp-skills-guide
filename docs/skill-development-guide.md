# AI 技能开发指南

## 技能（Skill）是什么

在 MCP 架构中，**Skill** 是封装了特定领域能力的可复用模块。每个 Skill 通过 MCP 协议向 AI 智能体暴露工具接口，使 AI 能够调用外部能力完成复杂任务。

## 技能生命周期

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  定义    │───>│  注册    │───>│  执行    │───>│  卸载    │
│ Define   │    │ Register │    │ Execute  │    │ Dispose  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │                                                   │
     └────────────── 更新 (Update) ──────────────────────┘
```

### 1. 定义阶段

定义 Skill 的元数据、参数和执行逻辑。

### 2. 注册阶段

将 Skill 注册到 MCP Server 的工具列表中，使其可被发现和调用。

### 3. 执行阶段

AI 智能体通过 MCP 协议调用 Skill，Skill 执行业务逻辑并返回结果。

### 4. 更新阶段

在不中断服务的情况下更新 Skill 的实现或配置。

### 5. 卸载阶段

从注册中心移除 Skill，释放相关资源。

## 技能设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **单一职责** | 每个 Skill 只做一件事 | `github_search` 只负责搜索，不管创建 |
| **明确输入输出** | 使用类型注解清晰定义参数和返回值 | `def search(query: str) -> list[Repo]` |
| **幂等性** | 相同输入多次调用产生相同结果 | 读操作天然幂等，写操作需设计 |
| **错误可恢复** | 提供清晰的错误信息和降级方案 | 网络失败时返回缓存数据 |
| **可观测性** | 记录执行日志和性能指标 | 记录每次调用的耗时和结果 |

## 开发一个技能

### 第一步：定义技能元数据

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class SkillMetadata:
    """技能元数据定义"""
    name: str                          # 技能唯一标识
    description: str                   # 技能功能描述（AI 用于判断何时调用）
    version: str = "1.0.0"            # 语义化版本号
    author: str = ""                   # 作者信息
    tags: list[str] = field(default_factory=list)  # 分类标签
```

### 第二步：实现技能基类

```python
from abc import ABC, abstractmethod

class BaseSkill(ABC):
    """所有技能的抽象基类"""

    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata
        self._initialized = False

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """执行技能核心逻辑，子类必须实现"""
        ...

    @abstractmethod
    def get_input_schema(self) -> dict:
        """返回技能的输入参数 JSON Schema"""
        ...

    async def initialize(self) -> None:
        """初始化技能所需的资源（数据库连接、API 客户端等）""""
        self._initialized = True

    async def cleanup(self) -> None:
        """释放技能占用的资源""""
        self._initialized = False
```

### 第三步：实现具体技能

```python
class GitHubSearchSkill(BaseSkill):
    """GitHub 仓库搜索技能"""

    def __init__(self):
        super().__init__(SkillMetadata(
            name="github_search",
            description="搜索 GitHub 上的仓库、代码和 Issue",
            version="1.0.0",
            tags=["github", "search", "code"],
        ))

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "search_type": {
                    "type": "string",
                    "enum": ["repositories", "code", "issues"],
                    "default": "repositories",
                    "description": "搜索类型"
                },
                "per_page": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 10,
                    "description": "每页结果数量"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, search_type: str = "repositories",
                      per_page: int = 10) -> dict:
        """执行 GitHub 搜索"""
        # 实际实现中调用 GitHub API
        results = await self._call_github_api(query, search_type, per_page)

        return {
            "success": True,
            "total_count": len(results),
            "results": results,
        }

    async def _call_github_api(self, query: str, search_type: str,
                                per_page: int) -> list:
        """内部方法：调用 GitHub API"""
        # 实现 API 调用逻辑
        ...
```

### 第四步：注册到 MCP Server

```python
from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent

# 创建 MCP 服务器
server = Server("ai-skills-server")

# 注册技能
github_skill = GitHubSearchSkill()

@server.list_tools()
async def list_tools() -> list[Tool]:
    """向 AI 暴露可用的工具列表"""
    return [
        Tool(
            name=github_skill.metadata.name,
            description=github_skill.metadata.description,
            inputSchema=github_skill.get_input_schema(),
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理 AI 的工具调用请求"""
    if name == "github_search":
        result = await github_skill.execute(**arguments)
        return [TextContent(type="text", text=json.dumps(result))]
    raise ValueError(f"Unknown tool: {name}")

# 启动服务
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
```

## 技能最佳实践

### 1. 清晰的描述

技能描述是 AI 判断何时调用的关键依据，应包含：

- 功能说明
- 适用场景
- 输入输出说明

```python
# 好的描述
description="搜索 GitHub 仓库。当你需要查找开源项目、代码示例或 Issue 时调用此工具。"

# 不好的描述
description="搜索"
```

### 2. 细粒度工具

将大功能拆分为多个细粒度工具，提高 AI 的选择精度：

```python
# 推荐：拆分
github_search_repos()   # 搜索仓库
github_search_code()    # 搜索代码
github_get_file()       # 读取文件

# 不推荐：一个工具做所有事
github_do_everything()  # 做所有事
```

### 3. 结构化返回值

始终返回结构化数据，便于 AI 理解和后续处理：

```python
return {
    "success": True,
    "data": {"name": "repo-name", "stars": 100},
    "error": None,
    "metadata": {"execution_time_ms": 150},
}
```

### 4. 错误处理策略

```python
async def execute(self, **kwargs) -> dict:
    try:
        result = await self._do_work(**kwargs)
        return {"success": True, "data": result, "error": None}
    except NetworkError as e:
        # 网络错误：尝试使用缓存
        cached = self._get_cached_result(**kwargs)
        if cached:
            return {"success": True, "data": cached,
                    "warning": "使用缓存数据，可能不是最新的"}
        return {"success": False, "data": None,
                "error": f"网络不可用: {str(e)}"}
    except Exception as e:
        # 未知错误：返回明确错误信息
        return {"success": False, "data": None,
                "error": f"执行失败: {str(e)}"}
```

### 5. 测试技能

```python
import pytest

@pytest.mark.asyncio
async def test_github_search():
    skill = GitHubSearchSkill()
    result = await skill.execute(query="mcp server", per_page=5)
    assert result["success"] is True
    assert len(result["results"]) <= 5
```

## 技能编排模式

### 顺序编排

多个技能按顺序执行，前一个的输出作为后一个的输入。

```
搜索仓库 → 读取 README → 分析内容 → 生成报告
```

### 并行编排

多个独立技能同时执行，提高效率。

```
          ┌─→ 搜索 GitHub
分析请求 ─┼─→ 搜索文档
          └─→ 搜索 Stack Overflow
```

### 条件编排

根据中间结果动态决定后续调用。

```
搜索 → 找到结果？ → 是 → 读取详情
                 → 否 → 扩大搜索范围
```

## 下一步

- 查看 [基础技能示例](../examples/basic-skill/skill.py) 的完整代码
- 了解 [高级编排模式](../examples/advanced-patterns/orchestration.py)
- 参考 [使用案例分析](use-cases.md) 了解最佳实践
