"""MCP 模块测试 - ToolDefinition / ToolResult / SkillRegistry / MCPServer"""

import json
import pytest
from ai_mcp_skills import MCPServer, SkillRegistry, ToolDefinition, ToolResult


# ---------------------------------------------------------------------------
# ToolDefinition / ToolResult
# ---------------------------------------------------------------------------

def test_tool_definition():
    td = ToolDefinition(name="t", description="d", inputSchema={"type": "object"})
    assert td.name == "t"
    assert td.description == "d"
    assert td.inputSchema == {"type": "object"}


def test_tool_definition_default_schema():
    td = ToolDefinition(name="t", description="d")
    assert td.inputSchema == {}


def test_tool_result_defaults():
    tr = ToolResult(content=[])
    assert tr.content == []
    assert tr.isError is False


def test_tool_result_with_error():
    tr = ToolResult(content=[{"type": "text", "text": "err"}], isError=True)
    assert tr.isError is True
    assert len(tr.content) == 1


# ---------------------------------------------------------------------------
# SkillRegistry
# ---------------------------------------------------------------------------

def test_registry_register_and_list():
    reg = SkillRegistry()
    reg.register("tool1", "desc1", {"type": "object"}, lambda **kw: {})
    reg.register("tool2", "desc2", {"type": "object"}, lambda **kw: {})
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
    assert "未知工具" in r.content[0]["text"]


def test_registry_call_success():
    reg = SkillRegistry()
    reg.register("greet", "greet", {},
                 lambda **kw: {"message": f"Hello {kw.get('name', 'World')}"})
    r = reg.call_tool("greet", {"name": "MCP"})
    assert r.isError is False
    data = json.loads(r.content[0]["text"])
    assert data["message"] == "Hello MCP"


def test_registry_call_includes_metadata():
    """成功调用应附带 _metadata.execution_time_ms"""
    reg = SkillRegistry()
    reg.register("echo", "e", {}, lambda **kw: {"ok": True})
    r = reg.call_tool("echo", {})
    data = json.loads(r.content[0]["text"])
    assert "_metadata" in data
    assert "execution_time_ms" in data["_metadata"]


def test_registry_call_handler_raises():
    """handler 抛异常时返回 isError=True"""
    def boom(**kw):
        raise RuntimeError("boom")
    reg = SkillRegistry()
    reg.register("boom", "b", {}, boom)
    r = reg.call_tool("boom", {})
    assert r.isError is True
    assert "boom" in r.content[0]["text"]


def test_registry_list_tools_returns_definitions_only():
    """list_tools 应只返回 ToolDefinition，不含 handler"""
    reg = SkillRegistry()
    reg.register("t", "d", {"type": "object"}, lambda **kw: {})
    tools = reg.list_tools()
    assert all(isinstance(t, ToolDefinition) for t in tools)


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


def test_mcp_server_list_tools_empty():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert r["result"]["tools"] == []


def test_mcp_server_list_tools_after_register():
    srv = MCPServer("s", "1")
    srv.registry.register("t", "desc", {"type": "object"}, lambda **kw: {})
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert len(r["result"]["tools"]) == 1
    assert r["result"]["tools"][0]["name"] == "t"


def test_mcp_server_call_tool():
    srv = MCPServer("s", "1")
    srv.registry.register("add", "加法",
                          {"type": "object"},
                          lambda **kw: {"sum": kw.get("a", 0) + kw.get("b", 0)})
    r = srv.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "add", "arguments": {"a": 2, "b": 3}},
    })
    assert r["result"]["isError"] is False
    data = json.loads(r["result"]["content"][0]["text"])
    assert data["sum"] == 5


def test_mcp_server_call_unknown_tool():
    srv = MCPServer("s", "1")
    r = srv.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "missing", "arguments": {}},
    })
    assert r["result"]["isError"] is True


def test_mcp_server_no_method_field():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1})
    assert "error" in r
    assert r["error"]["code"] == -32601


def test_mcp_server_response_id_preserved():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 42, "method": "tools/list"})
    assert r["id"] == 42
