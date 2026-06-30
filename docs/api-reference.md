# API 参考

> 版本: 1.0.0
> 入口: `from ai_mcp_skills import ...`

## Skill 模块

### `SkillMetadata`

技能元数据 dataclass。

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | `str` | — | 技能唯一标识 |
| `description` | `str` | — | 功能描述（AI 据此判断何时调用） |
| `version` | `str` | `"1.0.0"` | 语义化版本 |
| `author` | `str` | `""` | 作者 |
| `tags` | `list[str]` | `[]` | 分类标签 |

```python
from ai_mcp_skills import SkillMetadata
m = SkillMetadata(name="my", description="desc", tags=["a"])
```

### `BaseSkill`

所有技能的抽象基类。

| 方法 | 说明 |
|------|------|
| `initialize() -> None` | 初始化资源（连接、配置） |
| `execute(**kwargs) -> dict` | 子类必须实现，返回 `{"success", "data", "error"}` |
| `cleanup() -> None` | 释放资源 |
| `get_tool_definition() -> dict` | 生成 MCP 工具定义 |
| `get_input_schema() -> dict` | 返回输入 JSON Schema（子类覆盖） |

### `TextAnalysisSkill`

文本分析技能，继承 `BaseSkill`。

```python
from ai_mcp_skills import TextAnalysisSkill
skill = TextAnalysisSkill()
result = skill.execute(
    text="...",
    top_n_keywords=10,        # 可选，1-50
    include_readability=True,  # 可选
)
# result["data"] = {"statistics": {...}, "keywords": [...], "readability": {...}}
```

**返回结构：**

```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_chars": 100,
      "chinese_words": 20,
      "english_words": 15,
      "total_words": 35,
      "sentences": 5
    },
    "keywords": [{"word": "MCP", "frequency": 3}],
    "readability": {
      "level": "中等",
      "description": "适合有阅读习惯的读者",
      "avg_sentence_length": 7.0,
      "avg_word_length": 4.2
    }
  },
  "error": null,
  "metadata": {"text_length": 100, "version": "1.0.0"}
}
```

### `HttpRequestSkill`

HTTP 请求技能，继承 `BaseSkill`，基于标准库 `urllib`。

```python
from ai_mcp_skills import HttpRequestSkill
skill = HttpRequestSkill()
result = skill.execute(
    url="https://api.example.com/data",
    method="GET",            # 可选: GET/POST/PUT/DELETE
    headers={"X-Token": "..."},  # 可选
    body='{"k": "v"}',       # 可选, POST/PUT 使用
    timeout=30,              # 可选, 0.1-60
)
# result["data"] = {"url", "method", "status_code", "headers", "body", "body_length"}
```

## MCP 模块

### `ToolDefinition`

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | `str` | — | 工具名 |
| `description` | `str` | — | 描述 |
| `inputSchema` | `dict` | `{}` | JSON Schema |

### `ToolResult`

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `content` | `list[dict]` | — | 内容列表 |
| `isError` | `bool` | `False` | 是否错误 |

### `SkillRegistry`

技能注册中心。

| 方法 | 说明 |
|------|------|
| `register(name, description, input_schema, handler)` | 注册工具，重复抛 `ValueError` |
| `list_tools() -> list[ToolDefinition]` | 列出所有工具 |
| `call_tool(name, arguments) -> ToolResult` | 调用工具 |

### `MCPServer`

简化的 JSON-RPC MCP 服务器。

| 方法 | 说明 |
|------|------|
| `__init__(name, version)` | 创建实例 |
| `handle_request(request: dict) -> dict` | 处理 JSON-RPC 请求 |

**支持的方法：**

- `initialize` — 握手与能力协商
- `tools/list` — 列出工具
- `tools/call` — 调用工具

## Orchestration 模块

### `TaskStatus` (Enum)

`PENDING` / `RUNNING` / `SUCCESS` / `FAILED` / `FALLBACK` / `TIMEOUT` / `SKIPPED`

### `TaskResult`

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_name` | `str` | 任务名 |
| `status` | `TaskStatus` | 终态 |
| `data` | `Any` | 结果数据 |
| `error` | `str \| None` | 错误信息 |
| `duration_ms` | `float` | 耗时 |
| `retries` | `int` | 重试次数 |

### `Task`

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | `str` | — | 任务名 |
| `coroutine` | `Callable` | — | 异步函数 |
| `args` / `kwargs` | `tuple` / `dict` | `()` / `{}` | 参数 |
| `depends_on` | `list[str]` | `[]` | 依赖任务 |
| `max_retries` | `int` | `0` | 重试次数 |
| `timeout_seconds` | `float` | `30.0` | 超时 |
| `fallback` | `Callable \| None` | `None` | 降级函数 |
| `skip_on_failure` | `bool` | `False` | 前置失败是否跳过 |

### `Orchestrator`

| 方法 | 说明 |
|------|------|
| `execute_sequential(tasks) -> dict[str, TaskResult]` | 串行流水线 |
| `execute_parallel(tasks) -> dict[str, TaskResult]` | 并行执行 |
| `execute_conditional(tasks, condition_fn, max_iterations=3)` | 条件分支 |

## 模块导出清单

```python
__all__ = [
    "__version__",
    "SkillMetadata", "BaseSkill", "TextAnalysisSkill", "HttpRequestSkill",
    "ToolDefinition", "ToolResult", "SkillRegistry", "MCPServer",
    "TaskStatus", "TaskResult", "Task", "Orchestrator",
]
```
