"""
高级编排模式演示

演示 ai_mcp_skills.Orchestrator 的三种编排模式:
1. 串行流水线 2. 并行执行 3. 条件分支 4. 重试与降级

运行方式:
    pip install -e .
    python examples/advanced-patterns/run_demo.py
"""

import asyncio
import random
import time

from ai_mcp_skills import Orchestrator, Task, TaskResult, TaskStatus

# ---------------------------------------------------------------------------
# 模拟技能函数
# ---------------------------------------------------------------------------


async def search_repos(query: str) -> dict:
    await asyncio.sleep(0.3 + random.random() * 0.2)
    return {"query": query, "repos": ["awesome-mcp", "mcp-server", "fastmcp"], "total": 3}


async def read_readme(owner: str, repo: str) -> dict:
    await asyncio.sleep(0.2)
    return {"repo": f"{owner}/{repo}", "content": f"# {repo}"}


async def analyze_code(code: str) -> dict:
    await asyncio.sleep(0.5)
    score = random.randint(65, 98)
    return {"score": score, "grade": "A" if score >= 90 else "B" if score >= 80 else "C"}


async def generate_report(data: dict) -> dict:
    await asyncio.sleep(0.3)
    return {"title": "分析报告", "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")}


async def unstable_api(url: str) -> dict:
    await asyncio.sleep(0.2)
    if random.random() < 0.7:
        raise ConnectionError(f"连接失败: {url}")
    return {"status": 200, "data": f"响应来自 {url}"}


async def fallback_cache(url: str = "") -> dict:
    await asyncio.sleep(0.05)
    return {"status": 200, "data": "缓存数据", "_cached": True}


# ---------------------------------------------------------------------------
# 演示函数
# ---------------------------------------------------------------------------


async def demo_sequential():
    print("\n" + "=" * 50)
    print("1. 串行流水线 模式")
    print("=" * 50)
    orch = Orchestrator()
    results = await orch.execute_sequential(
        [
            Task(name="搜索仓库", coroutine=search_repos, kwargs={"query": "mcp"}),
            Task(
                name="读取README",
                coroutine=read_readme,
                kwargs={"owner": "x", "repo": "y"},
                depends_on=["搜索仓库"],
            ),
            Task(
                name="代码分析",
                coroutine=analyze_code,
                kwargs={"code": "..."},
                depends_on=["读取README"],
            ),
            Task(
                name="生成报告",
                coroutine=generate_report,
                kwargs={"data": {}},
                depends_on=["搜索仓库", "代码分析"],
            ),
        ]
    )
    _print_summary(results)


async def demo_parallel():
    print("\n" + "=" * 50)
    print("2. 并行执行 模式")
    print("=" * 50)
    orch = Orchestrator()
    results = await orch.execute_parallel(
        [
            Task(name="搜索GitHub", coroutine=search_repos, kwargs={"query": "mcp"}),
            Task(name="搜索GitLab", coroutine=search_repos, kwargs={"query": "agent"}),
            Task(
                name="搜索文档", coroutine=unstable_api, kwargs={"url": "https://docs.example.com"}
            ),
        ]
    )
    _print_summary(results)


async def demo_conditional():
    print("\n" + "=" * 50)
    print("3. 条件分支 模式")
    print("=" * 50)

    def decide(results: dict[str, TaskResult]) -> list[Task]:
        r = results.get("代码质量分析")
        if r and r.status == TaskStatus.SUCCESS and r.data.get("score", 0) < 85:
            print("  → 评分 < 85，触发优化建议")
            return [
                Task(name="优化建议", coroutine=unstable_api, kwargs={"url": "optimizer/analyze"})
            ]
        return []

    orch = Orchestrator()
    results = await orch.execute_conditional(
        [Task(name="代码质量分析", coroutine=analyze_code, kwargs={"code": "sample"})],
        decide,
    )
    _print_summary(results)


async def demo_retry_fallback():
    print("\n" + "=" * 50)
    print("4. 重试与降级 模式")
    print("=" * 50)
    orch = Orchestrator()
    results = await orch.execute_parallel(
        [
            Task(
                name="不稳定API",
                coroutine=unstable_api,
                kwargs={"url": "https://unstable.example.com"},
                max_retries=2,
                timeout_seconds=1.0,
                fallback=lambda: fallback_cache(),
            ),
        ]
    )
    _print_summary(results)


def _print_summary(results: dict[str, TaskResult]):
    print("─" * 40)
    for name, r in results.items():
        icon = {
            TaskStatus.SUCCESS: "OK",
            TaskStatus.FAILED: "FAIL",
            TaskStatus.FALLBACK: "降级",
            TaskStatus.TIMEOUT: "超时",
            TaskStatus.SKIPPED: "跳过",
        }.get(r.status, "?")
        info = f"重试{r.retries}次" if r.retries else ""
        print(f"  {icon:<6} {name:<16} {r.duration_ms:>6.0f}ms  {info}")
        if r.data:
            d = str(r.data)[:70]
            print(f"         数据: {d}")
        if r.error:
            print(f"         错误: {r.error}")


async def main():
    print("AI 技能编排引擎 - 四种模式演示")
    await demo_sequential()
    await demo_parallel()
    await demo_conditional()
    await demo_retry_fallback()
    print(f"\n{'=' * 50}")
    print("全部演示完成！")


if __name__ == "__main__":
    asyncio.run(main())
