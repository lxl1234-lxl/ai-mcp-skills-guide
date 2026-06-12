"""
MCP 服务器演示：多工具注册与调用

演示如何使用 ai_mcp_skills 包的 MCPServer 和 SkillRegistry。

运行方式:
    pip install -e .
    python examples/mcp-integration/run_demo.py
"""

import json

from ai_mcp_skills import MCPServer


def make_tools() -> dict:
    """定义工具函数"""

    def weather_query(**kwargs) -> dict:
        """天气查询（模拟）"""
        import random
        city = kwargs.get("city", "")
        if not city:
            return {"success": False, "error": "城市名称不能为空"}
        random.seed(hash(city) % (2 ** 31))
        conditions = ["晴天", "多云", "阴天", "小雨", "中雨", "阵雨"]
        return {
            "success": True,
            "data": {
                "city": city,
                "temperature": round(25 + random.uniform(-5, 5), 1),
                "unit": "°C",
                "humidity": random.randint(40, 90),
                "condition": random.choice(conditions),
            },
        }

    def math_calc(**kwargs) -> dict:
        """数学计算"""
        expression = kwargs.get("expression", "")
        if not expression:
            return {"success": False, "error": "表达式不能为空"}
        try:
            safe_builtins = {
                "abs": abs, "round": round, "min": min, "max": max,
                "pow": pow, "sqrt": lambda x: x ** 0.5,
            }
            result = eval(expression, {"__builtins__": {}}, safe_builtins)
            return {
                "success": True,
                "data": {"expression": expression, "result": result},
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def file_read(**kwargs) -> dict:
        """文件读取"""
        path = kwargs.get("path", "")
        if not path:
            return {"success": False, "error": "路径不能为空"}
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(5000)
            return {"success": True, "data": {"path": path, "content": content}}
        except FileNotFoundError:
            return {"success": False, "error": f"文件不存在: {path}"}

    return {
        "weather_query": (weather_query, {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "城市名称"}},
            "required": ["city"],
        }),
        "math_calculate": (math_calc, {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "数学表达式"}},
            "required": ["expression"],
        }),
        "filesystem_read": (file_read, {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "文件路径"}},
            "required": ["path"],
        }),
    }


def main():
    """启动 MCP 服务器演示"""
    print("=" * 55)
    print("AI MCP Skills Server - 演示模式")
    print("=" * 55)

    # 1. 创建服务器并注册工具
    server = MCPServer(name="ai-skills-demo", version="1.0.0")
    tools = make_tools()
    for name, (handler, schema) in tools.items():
        server.registry.register(
            name=name,
            description=f"工具: {name}",
            input_schema=schema,
            handler=handler,
        )

    # 2. 初始化握手
    r = server.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05",
                    "clientInfo": {"name": "demo", "version": "1.0"}},
    })
    info = r["result"]["serverInfo"]
    print(f"服务器: {info['name']} v{info['version']} 已就绪")

    # 3. 列出工具
    r = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    print(f"\n已注册 {len(r['result']['tools'])} 个工具:")
    for t in r["result"]["tools"]:
        print(f"  - {t['name']}")

    # 4. 调用工具
    print("\n>>> 调用 math_calculate")
    r = server.handle_request({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "math_calculate",
                    "arguments": {"expression": "2 ** 10 + sqrt(144)"}},
    })
    data = json.loads(r["result"]["content"][0]["text"])
    print(f"  结果: {data['data']['result']}")

    print("\n>>> 调用 weather_query")
    r = server.handle_request({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "weather_query", "arguments": {"city": "北京"}},
    })
    w = json.loads(r["result"]["content"][0]["text"])["data"]
    print(f"  {w['city']}: {w['temperature']}{w['unit']}, {w['condition']}")

    print(f"\n{'=' * 55}")
    print("演示完成！服务器支持 3 个工具，通过 MCP 协议通信。")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    main()
