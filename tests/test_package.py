"""ai_mcp_skills 包测试"""

import asyncio
import pytest
from ai_mcp_skills import (
    SkillMetadata,
    BaseSkill,
    TextAnalysisSkill,
    ToolDefinition,
    SkillRegistry,
    MCPServer,
    Orchestrator,
    Task,
    TaskStatus,
    TaskResult,
    __version__,
)


# ---------------------------------------------------------------------------
# 版本
# ---------------------------------------------------------------------------

def test_version():
    assert __version__ == "1.0.0"


# ---------------------------------------------------------------------------
# SkillMetadata
# ---------------------------------------------------------------------------

def test_skill_metadata_defaults():
    m = SkillMetadata(name="test", description="desc")
    assert m.name == "test"
    assert m.description == "desc"
    assert m.version == "1.0.0"
    assert m.author == ""
    assert m.tags == []


def test_skill_metadata_full():
    m = SkillMetadata(
        name="my-skill", description="my desc",
        version="2.0.0", author="me", tags=["a", "b"],
    )
    assert m.name == "my-skill"
    assert m.version == "2.0.0"
    assert m.author == "me"
    assert m.tags == ["a", "b"]


# ---------------------------------------------------------------------------
# BaseSkill
# ---------------------------------------------------------------------------

def test_base_skill_tool_definition():
    m = SkillMetadata(name="my-skill", description="my desc", tags=["tag1"])
    skill = BaseSkill(m)
    d = skill.get_tool_definition()
    assert d["name"] == "my-skill"
    assert d["description"] == "my desc"
    assert d["version"] == "1.0.0"
    assert "tag1" in d["tags"]
    assert "inputSchema" in d

    # 未实现 execute 的基类调用应报错
    with pytest.raises(NotImplementedError):
        skill.execute()


# ---------------------------------------------------------------------------
# TextAnalysisSkill
# ---------------------------------------------------------------------------

def test_text_analysis_empty():
    skill = TextAnalysisSkill()
    r = skill.execute(text="")
    assert r["success"] is False
    assert r["error"]


def test_text_analysis_basic():
    skill = TextAnalysisSkill()
    r = skill.execute(text="Hello world! 你好世界！")
    assert r["success"] is True
    assert r["data"]["statistics"]["total_chars"] > 0
    assert len(r["data"]["keywords"]) > 0
    assert r["data"]["readability"] is not None


def test_text_analysis_no_readability():
    skill = TextAnalysisSkill()
    r = skill.execute(text="Hello world!", include_readability=False)
    assert r["data"]["readability"] is None


# ---------------------------------------------------------------------------
# SkillRegistry
# ---------------------------------------------------------------------------

def test_registry_register_and_list():
    reg = SkillRegistry()

    def handler(**kwargs):
        return {"ok": True}

    reg.register("tool1", "desc1", {"type": "object"}, handler)
    reg.register("tool2", "desc2", {"type": "object"}, handler)

    tools = reg.list_tools()
    assert len(tools) == 2
    assert tools[0].name == "tool1"
    assert tools[1].name == "tool2"


def test_registry_duplicate():
    reg = SkillRegistry()
    reg.register("t", "d", {}, lambda **kw: {})

    with pytest.raises(ValueError):
        reg.register("t", "d", {}, lambda **kw: {})


def test_registry_call_unknown():
    reg = SkillRegistry()
    r = reg.call_tool("unknown", {})
    assert r.isError is True


def test_registry_call_success():
    reg = SkillRegistry()
    reg.register("greet", "greet", {},
                 lambda **kw: {"message": f"Hello {kw.get('name', 'World')}"})
    r = reg.call_tool("greet", {"name": "MCP"})
    assert r.isError is False


# ---------------------------------------------------------------------------
# MCPServer
# ---------------------------------------------------------------------------

def test_mcp_server_initialize():
    srv = MCPServer("test-srv", "1.2.3")
    r = srv.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "c", "version": "1"}},
    })
    assert r["jsonrpc"] == "2.0"
    assert r["id"] == 1
    info = r["result"]["serverInfo"]
    assert info["name"] == "test-srv"
    assert info["version"] == "1.2.3"
    assert "tools" in r["result"]["capabilities"]


def test_mcp_server_unknown_method():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1, "method": "unknown"})
    assert "error" in r
    assert r["error"]["code"] == -32601


# ---------------------------------------------------------------------------
# Orchestrator - 串行
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_orchestrator_sequential():
    orch = Orchestrator()

    async def step1():
        return {"step": 1}

    async def step2(_previous_result=None):
        return {"step": 2, "prev": _previous_result}

    results = await orch.execute_sequential([
        Task(name="s1", coroutine=step1),
        Task(name="s2", coroutine=step2, depends_on=["s1"]),
    ])

    assert results["s1"].status == TaskStatus.SUCCESS
    assert results["s2"].status == TaskStatus.SUCCESS
    assert results["s2"].data["prev"]["step"] == 1


@pytest.mark.asyncio
async def test_orchestrator_sequential_skip():
    orch = Orchestrator()

    async def fail_step():
        raise RuntimeError("fail")

    async def next_step():
        return {"ok": True}

    results = await orch.execute_sequential([
        Task(name="bad", coroutine=fail_step),
        Task(name="next", coroutine=next_step, skip_on_failure=True),
    ])

    assert results["bad"].status == TaskStatus.FAILED
    assert results["next"].status == TaskStatus.SKIPPED


# ---------------------------------------------------------------------------
# Orchestrator - 并行
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_orchestrator_parallel():
    orch = Orchestrator()

    async def a(): return {"name": "a"}
    async def b(): return {"name": "b"}

    results = await orch.execute_parallel([
        Task(name="a", coroutine=a),
        Task(name="b", coroutine=b),
    ])

    assert results["a"].status == TaskStatus.SUCCESS
    assert results["b"].status == TaskStatus.SUCCESS


# ---------------------------------------------------------------------------
# Orchestrator - 降级
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_orchestrator_fallback():
    orch = Orchestrator()

    async def always_fail():
        raise RuntimeError("boom")

    async def fallback():
        return {"cached": True}

    results = await orch.execute_parallel([
        Task(name="api", coroutine=always_fail,
             fallback=fallback),
    ])

    assert results["api"].status == TaskStatus.FALLBACK
    assert results["api"].data["cached"] is True


# ---------------------------------------------------------------------------
# ToolDefinition / TaskResult
# ---------------------------------------------------------------------------

def test_tool_definition():
    td = ToolDefinition(name="t", description="d",
                        inputSchema={"type": "object"})
    assert td.name == "t"
    assert td.description == "d"
    assert td.inputSchema == {"type": "object"}


def test_task_result():
    tr = TaskResult(task_name="test", status=TaskStatus.SUCCESS,
                    data={"x": 1}, duration_ms=12.5)
    assert tr.task_name == "test"
    assert tr.status == TaskStatus.SUCCESS
    assert tr.data == {"x": 1}
    assert tr.duration_ms == 12.5
