# 快速开始（5 分钟）

本文带你从零安装到运行第一个 AI 技能。

## 1. 环境要求

- Python 3.10 或更高
- pip（推荐使用 [uv](https://github.com/astral-sh/uv) 加速）

## 2. 安装

```bash
# 从 PyPI 安装
pip install ai-mcp-skills

# 或从源码安装（开发模式）
git clone https://github.com/lxl1234-lxl/ai-mcp-skills-guide.git
cd ai-mcp-skills-guide
pip install -e ".[dev]"
```

## 3. 第一个技能调用

```python
from ai_mcp_skills import TextAnalysisSkill

skill = TextAnalysisSkill()
result = skill.execute(text="MCP 协议让 AI 安全调用外部工具。Hello MCP!")

print(result["data"]["statistics"])
# {'total_chars': ..., 'chinese_words': ..., 'english_words': ...}

print(result["data"]["keywords"])
# [{'word': 'MCP', 'frequency': 2}, ...]
```

## 4. 通过 MCP 协议调用

```python
from ai_mcp_skills import MCPServer

server = MCPServer("my-server", "1.0.0")
server.registry.register(
    name="greet",
    description="问候工具",
    input_schema={"type": "object",
                  "properties": {"name": {"type": "string"}}},
    handler=lambda **kw: {"message": f"Hello {kw.get('name', 'World')}!"},
)

# 模拟 AI 客户端发起 JSON-RPC 调用
resp = server.handle_request({
    "jsonrpc": "2.0", "id": 1, "method": "tools/call",
    "params": {"name": "greet", "arguments": {"name": "MCP"}},
})
print(resp["result"]["content"][0]["text"])
# {"message": "Hello MCP!"}
```

## 5. 编排多个技能

```python
import asyncio
from ai_mcp_skills import Orchestrator, Task

async def fetch_data():
    return {"items": [1, 2, 3]}

async def process(_previous_result=None):
    return {"processed": True}

async def main():
    orch = Orchestrator()
    results = await orch.execute_sequential([
        Task(name="fetch", coroutine=fetch_data),
        Task(name="process", coroutine=process, depends_on=["fetch"]),
    ])
    print(results["process"].status)  # TaskStatus.SUCCESS

asyncio.run(main())
```

## 6. 运行示例

```bash
python examples/basic-skill/run_demo.py
python examples/mcp-integration/run_demo.py
python examples/advanced-patterns/run_demo.py
python examples/http-skill/run_demo.py
```

## 下一步

- 阅读 [架构设计](architecture.md) 理解 MCP 分层
- 参考 [技能开发指南](skill-development-guide.md) 自定义技能
- 查看 [使用案例](use-cases.md) 了解真实场景
