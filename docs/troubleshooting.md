# 故障排查

常见问题与解决方案。

## 安装问题

### `ModuleNotFoundError: No module named 'ai_mcp_skills'`

**原因：** 未安装或未在开发模式安装。

**解决：**

```bash
pip install -e .
# 或
pip install ai-mcp-skills
```

验证：

```bash
python -c "import ai_mcp_skills; print(ai_mcp_skills.__version__)"
```

### `pip install -e ".[dev]"` 报错：unknown extra 'dev'

**原因：** 使用了旧版本 pip（< 21）。

**解决：** 升级 pip：

```bash
pip install --upgrade pip
```

## 测试问题

### `pytest` 找不到测试

**原因：** 测试路径未配置或工作目录不对。

**解决：** 在仓库根目录运行：

```bash
pytest tests/ -v
```

`pyproject.toml` 已配置 `testpaths = ["tests"]`，因此 `pytest` 命令也应能工作。

### 异步测试 `RuntimeWarning: coroutine was never awaited`

**原因：** 未安装 `pytest-asyncio` 或未配置 `asyncio_mode`。

**解决：** 确认 `pyproject.toml` 包含：

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

并安装：`pip install pytest-asyncio`

### `test_http_skill` 因网络失败

**原因：** 测试中使用 `monkeypatch` 替换 `urllib.request.urlopen`，不依赖网络。若仍失败，检查是否有自定义 `conftest.py` 覆盖。

**解决：**

```bash
pytest tests/test_http_skill.py -v -p no:cacheprovider
```

## 运行时问题

### `MCPServer` 没有实际 stdio 监听

**说明：** 本项目 `MCPServer` 提供 `handle_request(dict) -> dict` 的同步接口，便于测试与集成。若需对接真实 AI Host（如 Claude Desktop），请使用官方 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)：

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
```

### `Orchestrator.execute_parallel` 中任务结果丢失

**检查：** 是否设置了 `depends_on`？`execute_parallel` 不使用依赖关系，所有任务并发执行。如需依赖，改用 `execute_sequential`。

### 技能 `execute` 返回 `{"success": False, "error": "..."}`

**排查清单：**

1. 检查输入参数是否符合 `get_input_schema()` 定义
2. 查看错误信息中的具体异常
3. 对网络类技能（如 `HttpRequestSkill`），检查 URL 与超时设置
4. 使用 `try/except` 包裹业务逻辑并返回结构化错误

## Lint / 类型问题

### `ruff check .` 报 `F401 imported but unused`

**解决：** 删除未使用的 import，或添加 `# noqa: F401`。

### `mypy src` 报 `Module has no attribute`

**原因：** `__init__.py` 导出的名称与模块实际定义不匹配。

**解决：** 同步更新 `src/ai_mcp_skills/__init__.py` 的导入与 `__all__`。

## 仍无法解决？

- 搜索 [已有 Issue](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/issues)
- 提交新 Issue（参考 `.github/ISSUE_TEMPLATE/`）
- 阅读 [FAQ](faq.md)
