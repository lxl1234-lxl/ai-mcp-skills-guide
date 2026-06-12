"""
MCP 集成示例：多技能服务器

演示如何创建一个完整的 MCP Server，注册多个技能工具并处理调用请求。
该服务器提供三个工具：文件系统操作、数学计算、天气查询（模拟）。

注意：此示例不依赖外部 MCP 库，展示了 MCP 协议的核心通信逻辑。
如需生产使用，建议使用官方的 `mcp` Python SDK。

运行方式:
    python examples/mcp-integration/mcp_server.py
"""

import json
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable


# ============================================================================
# MCP 协议基础定义（简化版）
# ============================================================================

@dataclass
class ToolDefinition:
    """MCP 工具定义"""
    name: str                              # 工具名称
    description: str                       # 工具描述
    inputSchema: dict = field(default_factory=dict)  # 输入参数 JSON Schema


@dataclass
class ToolResult:
    """MCP 工具调用结果"""
    content: list[dict]                    # 结果内容（支持多部分）
    isError: bool = False                  # 是否为错误结果


# ============================================================================
# 技能注册中心
# ============================================================================

class SkillRegistry:
    """技能注册中心 - 管理所有已注册的技能工具

    负责:
    - 工具的注册和注销
    - 根据工具名称查找和调用
    - 生成工具列表供 AI 发现
    """

    def __init__(self):
        # 工具名 → (ToolDefinition, 执行函数) 的映射
        self._tools: dict[str, tuple[ToolDefinition, Callable]] = {}
        self._tool_count: int = 0

    def register(
        self,
        name: str,
        description: str,
        input_schema: dict,
        handler: Callable,
    ) -> None:
        """注册一个新工具

        Args:
            name: 工具唯一标识
            description: 工具功能描述（AI 据此判断何时调用）
            input_schema: 输入参数 JSON Schema
            handler: 工具执行函数，接收 kwargs，返回 dict
        """
        if name in self._tools:
            raise ValueError(f"工具 '{name}' 已存在，请使用不同名称")

        tool_def = ToolDefinition(
            name=name,
            description=description,
            inputSchema=input_schema,
        )
        self._tools[name] = (tool_def, handler)
        self._tool_count += 1
        print(f"[注册] 工具 '{name}' 已注册")

    def list_tools(self) -> list[ToolDefinition]:
        """获取所有已注册的工具定义

        这是 MCP 协议中 tools/list 请求的响应内容。
        AI 通过此接口发现可用的工具。
        """
        return [tool_def for tool_def, _ in self._tools.values()]

    def call_tool(self, name: str, arguments: dict) -> ToolResult:
        """调用指定的工具

        Args:
            name: 工具名称
            arguments: 工具参数

        Returns:
            ToolResult: 工具执行结果
        """
        if name not in self._tools:
            return ToolResult(
                content=[{"type": "text", "text": f"错误: 未知工具 '{name}'"}],
                isError=True,
            )

        _, handler = self._tools[name]
        try:
            start_time = time.time()
            result = handler(**arguments)
            elapsed = (time.time() - start_time) * 1000

            # 附加执行元数据
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


# ============================================================================
# 具体工具实现
# ============================================================================

def tool_filesystem_read(**kwargs) -> dict:
    """文件系统读取工具

    模拟读取文件内容。生产环境中应接入真实文件系统。

    Args:
        path: 文件路径
        encoding: 字符编码

    Returns:
        文件内容和元数据
    """
    path = kwargs.get("path", "")
    encoding = kwargs.get("encoding", "utf-8")

    # 参数验证
    if not path:
        return {"success": False, "error": "文件路径不能为空"}

    # 模拟文件读取（生产环境使用 open()）
    try:
        with open(path, "r", encoding=encoding) as f:
            content = f.read()

        return {
            "success": True,
            "data": {
                "path": path,
                "content": content[:5000],  # 限制返回长度
                "size_bytes": len(content.encode(encoding)),
                "encoding": encoding,
                "truncated": len(content) > 5000,
            },
        }
    except FileNotFoundError:
        return {"success": False, "error": f"文件不存在: {path}"}
    except Exception as e:
        return {"success": False, "error": f"读取失败: {str(e)}"}


def tool_math_calculate(**kwargs) -> dict:
    """数学计算工具

    支持基本的数学表达式计算。

    Args:
        expression: 数学表达式字符串
        precision: 结果精度（小数位数）

    Returns:
        计算结果
    """
    expression = kwargs.get("expression", "")
    precision = kwargs.get("precision", 4)

    if not expression:
        return {"success": False, "error": "表达式不能为空"}

    # 安全白名单：只允许数字、运算符、括号和基本函数
    allowed_chars = set("0123456789.+-*/()% **, ")
    allowed_funcs = {"abs", "round", "min", "max", "pow", "sqrt"}

    # 安全检查：过滤危险字符
    safe_expr = expression
    for func in allowed_funcs:
        safe_expr = safe_expr.replace(func, "")

    unsafe = [c for c in safe_expr if c not in allowed_chars]
    if unsafe:
        return {
            "success": False,
            "error": f"表达式包含不允许的字符: {unsafe}",
        }

    try:
        # 使用 eval 计算（已通过安全检查）
        # 生产环境建议使用 numexpr 或自定义解析器
        result = eval(expression, {"__builtins__": {}}, {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
            "sqrt": lambda x: x ** 0.5,
        })
        return {
            "success": True,
            "data": {
                "expression": expression,
                "result": round(result, precision) if isinstance(result, float) else result,
                "type": type(result).__name__,
            },
        }
    except Exception as e:
        return {"success": False, "error": f"计算错误: {str(e)}"}


def tool_weather_query(**kwargs) -> dict:
    """天气查询工具（模拟）

    模拟查询指定城市的天气信息。
    实际部署时应接入真实天气 API。

    Args:
        city: 城市名称
        units: 温度单位 (metric/imperial)

    Returns:
        天气信息
    """
    city = kwargs.get("city", "")
    units = kwargs.get("units", "metric")

    if not city:
        return {"success": False, "error": "城市名称不能为空"}

    # 模拟天气数据（生产环境替换为 API 调用）
    import random
    random.seed(hash(city) % (2**31))  # 使同一城市返回一致结果

    conditions = ["晴天", "多云", "阴天", "小雨", "中雨", "阵雨"]
    temp_base = 25 if units == "metric" else 77

    return {
        "success": True,
        "data": {
            "city": city,
            "temperature": round(temp_base + random.uniform(-5, 5), 1),
            "unit": "°C" if units == "metric" else "°F",
            "humidity": random.randint(40, 90),
            "condition": random.choice(conditions),
            "wind_speed": round(random.uniform(0, 20), 1),
            "forecast": [
                {"day": "今天", "high": 28, "low": 20, "condition": "晴转多云"},
                {"day": "明天", "high": 26, "low": 19, "condition": "小雨"},
                {"day": "后天", "high": 30, "low": 22, "condition": "晴天"},
            ],
            "_note": "此为模拟数据，生产环境请接入真实天气 API",
        },
    }


# ============================================================================
# MCP Server 主程序
# ============================================================================

class MCPServer:
    """简化的 MCP 协议服务器

    通过 stdio 与 AI Host 通信，支持:
    - tools/list:  返回可用工具列表
    - tools/call:  执行工具调用
    - initialize:  初始化握手
    """

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.registry = SkillRegistry()

    def register_builtin_tools(self) -> None:
        """注册所有内置工具"""
        # 文件系统读取工具
        self.registry.register(
            name="filesystem_read",
            description="读取指定路径的文件内容。用于查看源代码、配置文件等文本文件。",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件的绝对路径",
                    },
                    "encoding": {
                        "type": "string",
                        "default": "utf-8",
                        "description": "文件编码",
                    },
                },
                "required": ["path"],
            },
            handler=tool_filesystem_read,
        )

        # 数学计算工具
        self.registry.register(
            name="math_calculate",
            description=(
                "计算数学表达式。支持加减乘除、幂运算、开方等。"
                "当需要进行数值计算时使用此工具。"
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '2 + 3 * 4' 或 'sqrt(16)'",
                    },
                    "precision": {
                        "type": "integer",
                        "default": 4,
                        "description": "结果小数位数",
                    },
                },
                "required": ["expression"],
            },
            handler=tool_math_calculate,
        )

        # 天气查询工具
        self.registry.register(
            name="weather_query",
            description="查询指定城市的天气信息。返回温度、湿度、天气状况和预报。",
            input_schema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如 '北京'、'Shanghai'",
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial"],
                        "default": "metric",
                        "description": "温度单位",
                    },
                },
                "required": ["city"],
            },
            handler=tool_weather_query,
        )

    def handle_request(self, request: dict) -> dict:
        """处理 JSON-RPC 请求

        Args:
            request: JSON-RPC 请求对象

        Returns:
            JSON-RPC 响应对象
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
                return self._error_response(req_id, -32601, f"未知方法: {method}")
        except Exception as e:
            return self._error_response(req_id, -32603, str(e))

    def _handle_initialize(self, req_id) -> dict:
        """处理初始化握手"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                },
                "capabilities": {
                    "tools": {},  # 声明支持工具调用
                },
            },
        }

    def _handle_list_tools(self, req_id) -> dict:
        """处理工具列表请求"""
        tools = self.registry.list_tools()
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "inputSchema": t.inputSchema,
                    }
                    for t in tools
                ]
            },
        }

    def _handle_call_tool(self, req_id, params: dict) -> dict:
        """处理工具调用请求"""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        result = self.registry.call_tool(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": result.content,
                "isError": result.isError,
            },
        }

    def _error_response(self, req_id, code: int, message: str) -> dict:
        """生成错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": code, "message": message},
        }


# ============================================================================
# 演示与交互
# ============================================================================

def main():
    """启动 MCP 服务器演示"""
    print("=" * 60)
    print("AI MCP Skills Server - 演示模式")
    print("=" * 60)

    # 1. 创建服务器并注册工具
    server = MCPServer(name="ai-skills-demo", version="1.0.0")
    server.register_builtin_tools()

    # 2. 模拟 AI Host 发起初始化握手
    print("\n>>> [1] 初始化握手")
    init_response = server.handle_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "demo-client", "version": "1.0.0"},
        },
    })
    print(f"服务器: {init_response['result']['serverInfo']['name']} "
          f"v{init_response['result']['serverInfo']['version']}")

    # 3. 模拟 AI Host 获取工具列表
    print("\n>>> [2] 获取工具列表")
    tools_response = server.handle_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
    })
    print("可用工具:")
    for tool in tools_response["result"]["tools"]:
        print(f"  - {tool['name']}: {tool['description'][:60]}...")

    # 4. 模拟 AI Host 调用各工具
    print("\n>>> [3] 调用数学计算工具")
    calc_result = server.handle_request({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "math_calculate",
            "arguments": {"expression": "2 ** 10 + sqrt(144)", "precision": 2},
        },
    })
    content = json.loads(calc_result["result"]["content"][0]["text"])
    print(f"结果: {content['data']['expression']} = {content['data']['result']}")

    print("\n>>> [4] 调用天气查询工具")
    weather_result = server.handle_request({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "weather_query",
            "arguments": {"city": "北京", "units": "metric"},
        },
    })
    weather = json.loads(weather_result["result"]["content"][0]["text"])
    wd = weather["data"]
    print(f"{wd['city']}: {wd['temperature']}{wd['unit']}, "
          f"{wd['condition']}, 湿度 {wd['humidity']}%")

    print("\n>>> [5] 调用文件读取工具")
    file_result = server.handle_request({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "filesystem_read",
            "arguments": {"path": __file__},  # 读取自身文件
        },
    })
    file_data = json.loads(file_result["result"]["content"][0]["text"])
    if file_data["success"]:
        print(f"成功读取: {file_data['data']['path']} "
              f"({file_data['data']['size_bytes']} 字节)")
    else:
        print(f"读取结果: {file_data}")

    print("\n" + "=" * 60)
    print("演示完成！服务器共注册了 3 个工具。")
    print("在 MCP 生产模式下，服务器通过 stdio 持续运行，等待 AI 调用。")
    print("=" * 60)


if __name__ == "__main__":
    main()
