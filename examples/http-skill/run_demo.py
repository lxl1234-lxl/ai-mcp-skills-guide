"""HTTP 请求技能示例

演示如何使用 HttpRequestSkill 调用公共 API 并处理响应。
仅使用不依赖网络的本地回环：先尝试 httpbin 镜像，失败时回退到本地说明。

运行方式:
    pip install -e .
    python examples/http-skill/run_demo.py
"""

from ai_mcp_skills import HttpRequestSkill


def main():
    skill = HttpRequestSkill()
    skill.initialize()

    print("=" * 55)
    print("HttpRequestSkill 演示")
    print("=" * 55)

    # 1. 查看工具定义
    td = skill.get_tool_definition()
    print(f"工具: {td['name']}  标签: {td['tags']}")
    print(f"输入 schema: {td['inputSchema']['required']} 必填字段")

    # 2. 演示无效 URL（不依赖网络）
    print("\n>>> 调用无效 URL（演示错误处理）")
    r = skill.execute(url="not-a-url")
    print(f"  success={r['success']}  error={r['error']}")

    # 3. 演示空 URL
    print("\n>>> 调用空 URL")
    r = skill.execute(url="")
    print(f"  success={r['success']}  error={r['error']}")

    # 4. 尝试真实网络请求（可能失败，演示降级）
    print("\n>>> 尝试访问 https://httpbin.org/get")
    r = skill.execute(url="https://httpbin.org/get", method="GET", timeout=5)
    if r["success"]:
        d = r["data"]
        print(f"  状态码: {d['status_code']}")
        print(f"  响应长度: {d['body_length']} 字节")
        print(f"  响应头 Content-Type: {d['headers'].get('Content-Type', 'N/A')}")
        # 截取前 100 字符
        print(f"  响应预览: {d['body'][:100]}...")
    else:
        print(f"  网络不可用或请求失败（演示用）: {r['error']}")
        print("  在生产中可结合 Orchestrator 的 fallback 机制降级到缓存。")

    # 5. 演示 POST 请求构造（仅打印，不实际发送）
    print("\n>>> 演示 POST 请求构造")
    r = skill.execute(
        url="https://httpbin.org/post",
        method="POST",
        body='{"name": "ai-mcp-skills", "version": "1.0.0"}',
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    if r["success"]:
        print(f"  POST 成功，状态码: {r['data']['status_code']}")
    else:
        print(f"  POST 请求未送达（演示）: {r['error']}")

    skill.cleanup()
    print(f"\n{'=' * 55}")
    print("演示完成！")


if __name__ == "__main__":
    main()
