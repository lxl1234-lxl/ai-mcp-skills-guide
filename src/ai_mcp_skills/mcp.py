"""
MCP 服务端模块 - 工具定义、技能注册中心与 MCP 服务器实现

提供:
- ToolDefinition: MCP 工具定义
- ToolResult: 工具调用结果
- SkillRegistry: 技能注册中心（工具注册/发现/调用）
- MCPServer: 简化的 MCP 协议服务器（JSON-RPC 处理）
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """MCP 协议工具定义

    Attributes:
        name: 工具唯一名称
        description: 功能描述（AI 据此判断何时调用）
        inputSchema: 输入参数 JSON Schema
    """

    name: str
    description: str
    inputSchema: dict = field(default_factory=dict)


@dataclass
class ToolResult:
    """MCP 工具调用结果

    Attributes:
        content: 结果内容列表（支持多部分）
        isError: 是否为错误结果
    """

    content: list[dict]
    isError: bool = False


class SkillRegistry:
    """技能注册中心

    管理所有已注册的 MCP 工具:
    - 工具的注册与注销
    - 根据名称查找和调用
    - 生成工具列表供 AI 发现
    """

    def __init__(self):
        self._tools: dict[str, tuple[ToolDefinition, Callable]] = {}

    def register(
        self, name: str, description: str,
        input_schema: dict, handler: Callable,
    ) -> None:
        """注册一个新工具到注册中心

        Args:
            name: 工具唯一标识
            description: 功能描述
            input_schema: 输入参数 JSON Schema
            handler: 工具执行函数 (async kwargs -> dict)

        Raises:
            ValueError: 工具名重复时抛出
        """
        if name in self._tools:
            raise ValueError(f"工具 '{name}' 已存在")
        self._tools[name] = (
            ToolDefinition(name, description, input_schema),
            handler,
        )

    def list_tools(self) -> list[ToolDefinition]:
        """获取所有已注册的工具定义（对应 MCP tools/list）"""
        return [td for td, _ in self._tools.values()]

    def call_tool(self, name: str, arguments: dict) -> ToolResult:
        """调用指定工具（对应 MCP tools/call）

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            ToolResult 包含执行结果或错误信息
        """
        if name not in self._tools:
            return ToolResult(
                content=[{"type": "text", "text": f"错误: 未知工具 '{name}'"}],
                isError=True,
            )

        _, handler = self._tools[name]
        try:
            start = time.time()
            result = handler(**arguments)
            elapsed = (time.time() - start) * 1000

            if isinstance(result, dict):
                result.setdefault("_metadata", {})
                result["_metadata"]["execution_time_ms"] = round(elapsed, 2)

            return ToolResult(
                content=[{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                isError=False,
            )
        except Exception as e:
            return ToolResult(
                content=[{"type": "text", "text": f"工具执行错误: {str(e)}"}],
                isError=True,
            )


class MCPServer:
    """简化的 MCP 协议服务器

    通过 stdio 与 AI Host 通信，支持:
    - initialize: 握手与能力协商
    - tools/list: 返回可用工具列表
    - tools/call: 执行工具调用

    Usage:
        server = MCPServer("my-server", "1.0.0")
        server.register_builtin_tools()
        response = server.handle_request(request_dict)
    """

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.registry = SkillRegistry()

    def handle_request(self, request: dict) -> dict:
        """处理 JSON-RPC 请求并返回响应

        Args:
            request: JSON-RPC 请求 {"jsonrpc": "2.0", "id": N, "method": "...", "params": {...}}

        Returns:
            JSON-RPC 响应字典
        """
        method = request.get("method", "")
        req_id = request.get("id")

        try:
            if method == "initialize":
                return self._handle_initialize(req_id)
            elif method == "tools/list":
                return self._handle_list_tools(req_id)
            elif method == "tools/call":
                return self._handle_call_tool(req_id, request.get("params", {}))
            else:
                return self._error(req_id, -32601, f"未知方法: {method}")
        except Exception as e:
            return self._error(req_id, -32603, str(e))

    def _handle_initialize(self, req_id) -> dict:
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": self.name, "version": self.version},
                "capabilities": {"tools": {}},
            },
        }

    def _handle_list_tools(self, req_id) -> dict:
        tools = self.registry.list_tools()
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "tools": [
                    {"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
                    for t in tools
                ]
            },
        }

    def _handle_call_tool(self, req_id, params: dict) -> dict:
        result = self.registry.call_tool(
            params.get("name", ""),
            params.get("arguments", {}),
        )
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"content": result.content, "isError": result.isError},
        }

    @staticmethod
    def _error(req_id, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
