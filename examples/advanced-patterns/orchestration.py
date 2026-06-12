"""
高级编排模式示例

演示多技能编排的三种核心模式：
1. 串行流水线 - Sequential Pipeline
2. 并行执行   - Parallel Execution
3. 条件分支   - Conditional Branching

以及：
- 重试与降级策略
- 执行结果追踪
- 超时控制

运行方式:
    python examples/advanced-patterns/orchestration.py
"""

import asyncio
import time
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine


# ============================================================================
# 基础定义
# ============================================================================

class TaskStatus(Enum):
    """任务执行状态"""
    PENDING = "pending"        # 等待执行
    RUNNING = "running"        # 执行中
    SUCCESS = "success"        # 执行成功
    FAILED = "failed"          # 执行失败
    FALLBACK = "fallback"      # 已降级处理
    TIMEOUT = "timeout"        # 执行超时
    SKIPPED = "skipped"        # 已跳过


@dataclass
class TaskResult:
    """单个任务的执行结果"""
    task_name: str                     # 任务名称
    status: TaskStatus                 # 执行状态
    data: Any = None                   # 结果数据
    error: str | None = None           # 错误信息
    duration_ms: float = 0.0           # 执行耗时（毫秒）
    retries: int = 0                   # 重试次数


@dataclass
class Task:
    """编排任务定义"""
    name: str                                      # 任务名称
    coroutine: Callable[..., Coroutine]            # 异步执行函数
    args: tuple = ()                               # 位置参数
    kwargs: dict = field(default_factory=dict)     # 关键字参数
    depends_on: list[str] = field(default_factory=list)  # 依赖的前置任务名
    max_retries: int = 0                           # 最大重试次数
    timeout_seconds: float = 30.0                  # 超时时间
    fallback: Callable | None = None               # 降级处理函数
    skip_on_failure: bool = False                  # 前置失败时是否跳过


# ============================================================================
# 模拟技能函数（模拟耗时的外部调用）
# ============================================================================

async def search_repositories(query: str) -> dict:
    """模拟：搜索 GitHub 仓库"""
    await asyncio.sleep(0.3 + random.random() * 0.2)
    return {
        "query": query,
        "repos": [
            {"name": "awesome-mcp", "stars": 1200, "lang": "Python"},
            {"name": "mcp-server", "stars": 800, "lang": "TypeScript"},
            {"name": "fastmcp", "stars": 450, "lang": "Python"},
        ],
        "total_count": 3,
    }


async def read_repo_readme(owner: str, repo: str) -> dict:
    """模拟：读取仓库 README"""
    await asyncio.sleep(0.2)
    return {
        "repo": f"{owner}/{repo}",
        "content": f"# {repo}\n\nAn awesome MCP project.",
        "size": 128,
    }


async def analyze_code_quality(code: str) -> dict:
    """模拟：代码质量分析"""
    await asyncio.sleep(0.5)
    score = random.randint(65, 98)
    return {
        "score": score,
        "grade": "A" if score >= 90 else "B" if score >= 80 else "C",
        "issues": [
            "缺少类型注解" if score < 80 else None,
            "建议添加单元测试" if score < 90 else None,
        ],
    }


async def generate_report(data: dict) -> dict:
    """模拟：生成分析报告"""
    await asyncio.sleep(0.3)
    return {
        "title": "MCP 项目分析报告",
        "summary": f"分析了 {len(data.get('repos', []))} 个仓库",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


async def call_external_api(url: str, fail_probability: float = 0.3) -> dict:
    """模拟：调用外部 API（有一定失败概率）"""
    await asyncio.sleep(0.2)
    if random.random() < fail_probability:
        raise ConnectionError(f"无法连接到 {url}")
    return {"status": 200, "data": f"来自 {url} 的响应"}


async def fallback_api_call(url: str) -> dict:
    """降级处理：使用缓存数据替代 API 调用"""
    await asyncio.sleep(0.05)
    return {"status": 200, "data": f"来自缓存的 {url} 数据",
            "_cached": True}


# ============================================================================
# 编排引擎
# ============================================================================

class Orchestrator:
    """技能编排引擎

    支持多种编排模式，负责:
    - 任务依赖解析
    - 并行/串行执行调度
    - 重试与超时控制
    - 降级策略执行
    """

    def __init__(self):
        self.results: dict[str, TaskResult] = {}

    async def execute_sequential(self, tasks: list[Task]) -> dict[str, TaskResult]:
        """串行流水线模式

        按顺序逐个执行任务，前一个成功后才执行下一个。
        适合步骤之间有数据依赖的场景。

        Args:
            tasks: 按执行顺序排列的任务列表

        Returns:
            所有任务的执行结果
        """
        print("\n>>> 串行流水线模式 <<<")
        self.results.clear()
        previous_result = None

        for task in tasks:
            print(f"  → 执行: {task.name}")

            # 将前一个任务的结果注入到当前任务的参数中
            if previous_result and previous_result.status == TaskStatus.SUCCESS:
                task.kwargs["_previous_result"] = previous_result.data

            # 检查前置依赖是否失败
            should_skip = False
            for dep in task.depends_on:
                if dep in self.results and self.results[dep].status == TaskStatus.FAILED:
                    if task.skip_on_failure:
                        should_skip = True
                        break

            if should_skip:
                self.results[task.name] = TaskResult(
                    task_name=task.name,
                    status=TaskStatus.SKIPPED,
                    error="前置任务失败，已跳过",
                )
                continue

            result = await self._execute_with_retry(task)
            self.results[task.name] = result
            previous_result = result

            if result.status == TaskStatus.FAILED:
                print(f"    ✗ 失败: {result.error}")
                break

        return self.results

    async def execute_parallel(self, tasks: list[Task]) -> dict[str, TaskResult]:
        """并行执行模式

        同时执行所有独立任务，最大化利用并发能力。
        适合步骤之间无依赖关系的场景。

        Args:
            tasks: 可并行执行的任务列表

        Returns:
            所有任务的执行结果
        """
        print("\n>>> 并行执行模式 <<<")
        self.results.clear()

        print(f"  → 并行启动 {len(tasks)} 个任务")

        # 并发执行所有任务
        coroutines = [self._execute_with_retry(task) for task in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                self.results[task.name] = TaskResult(
                    task_name=task.name,
                    status=TaskStatus.FAILED,
                    error=str(result),
                )
                print(f"    ✗ {task.name}: 异常 - {result}")
            else:
                self.results[task.name] = result
                status_icon = "✓" if result.status == TaskStatus.SUCCESS else "✗"
                print(f"    {status_icon} {task.name}: {result.status.value}")

        return self.results

    async def execute_conditional(
        self,
        tasks: list[Task],
        condition_fn: Callable[[dict[str, TaskResult]], list[Task]],
        max_iterations: int = 3,
    ) -> dict[str, TaskResult]:
        """条件分支模式

        根据当前结果动态决定下一步执行什么。
        适合需要根据中间结果做决策的场景。

        Args:
            tasks: 初始任务列表
            condition_fn: 条件判断函数，接收当前结果，返回下一步任务列表
            max_iterations: 最大迭代次数，防止无限循环

        Returns:
            所有任务的执行结果
        """
        print("\n>>> 条件分支模式 <<<")
        self.results.clear()

        iteration = 0
        current_tasks = tasks

        while current_tasks and iteration < max_iterations:
            iteration += 1
            print(f"  迭代 {iteration}: 执行 {len(current_tasks)} 个任务")

            for task in current_tasks:
                result = await self._execute_with_retry(task)
                self.results[task.name] = result
                status_icon = "✓" if result.status == TaskStatus.SUCCESS else "✗"
                print(f"    {status_icon} {task.name}")

            # 根据当前结果决定下一步
            current_tasks = condition_fn(self.results)
            if current_tasks:
                print(f"  → 条件触发，继续执行 {len(current_tasks)} 个任务")

        if iteration >= max_iterations and current_tasks:
            print(f"  ⚠ 达到最大迭代次数 ({max_iterations})，停止")

        return self.results

    async def _execute_with_retry(self, task: Task) -> TaskResult:
        """执行单个任务，支持重试和超时

        Args:
            task: 要执行的任务

        Returns:
            任务执行结果
        """
        last_error = None
        retries = 0

        for attempt in range(task.max_retries + 1):
            try:
                start = time.time()

                # 带超时的执行
                result_data = await asyncio.wait_for(
                    task.coroutine(*task.args, **task.kwargs),
                    timeout=task.timeout_seconds,
                )

                elapsed = (time.time() - start) * 1000
                return TaskResult(
                    task_name=task.name,
                    status=TaskStatus.SUCCESS,
                    data=result_data,
                    duration_ms=round(elapsed, 1),
                    retries=retries,
                )

            except asyncio.TimeoutError:
                last_error = f"执行超时 ({task.timeout_seconds}s)"
                retries = attempt + 1

            except Exception as e:
                last_error = str(e)
                retries = attempt + 1
                if attempt < task.max_retries:
                    # 指数退避重试
                    wait_time = 0.5 * (2 ** attempt)
                    print(f"    ⚠ 重试 {retries}/{task.max_retries}: "
                          f"等待 {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)

        # 所有重试都失败，尝试降级处理
        if task.fallback:
            try:
                print(f"    ⟳ 执行降级处理: {task.name}")
                fallback_data = await task.fallback()
                return TaskResult(
                    task_name=task.name,
                    status=TaskStatus.FALLBACK,
                    data=fallback_data,
                    error=last_error,
                    retries=retries,
                )
            except Exception as e:
                last_error = f"降级处理也失败: {str(e)}"

        return TaskResult(
            task_name=task.name,
            status=TaskStatus.FAILED if last_error else TaskStatus.TIMEOUT,
            error=last_error,
            retries=retries,
        )


# ============================================================================
# 演示运行
# ============================================================================

async def demo_sequential():
    """演示：串行流水线"""
    orchestrator = Orchestrator()
    tasks = [
        Task(
            name="搜索仓库",
            coroutine=search_repositories,
            kwargs={"query": "mcp server python"},
        ),
        Task(
            name="读取README",
            coroutine=read_repo_readme,
            kwargs={"owner": "modelcontextprotocol", "repo": "python-sdk"},
            depends_on=["搜索仓库"],
        ),
        Task(
            name="代码分析",
            coroutine=analyze_code_quality,
            kwargs={"code": "# sample code"},
            depends_on=["读取README"],
        ),
        Task(
            name="生成报告",
            coroutine=generate_report,
            kwargs={"data": {}},
            depends_on=["搜索仓库", "代码分析"],
        ),
    ]
    results = await orchestrator.execute_sequential(tasks)
    print_summary(results)


async def demo_parallel():
    """演示：并行执行"""
    orchestrator = Orchestrator()
    tasks = [
        Task(name="搜索 GitHub", coroutine=search_repositories,
             kwargs={"query": "mcp"}),
        Task(name="搜索 GitLab", coroutine=search_repositories,
             kwargs={"query": "agent"}),
        Task(name="搜索文档", coroutine=call_external_api,
             kwargs={"url": "https://docs.example.com/search?q=mcp"}),
    ]
    results = await orchestrator.execute_parallel(tasks)
    print_summary(results)


async def demo_conditional():
    """演示：条件分支"""
    orchestrator = Orchestrator()

    def decide_next(results: dict[str, TaskResult]) -> list[Task]:
        """根据质量分析结果决定后续操作"""
        quality_result = results.get("代码质量分析")
        if quality_result and quality_result.status == TaskStatus.SUCCESS:
            score = quality_result.data.get("score", 0)
            if score < 85:
                print(f"  → 质量评分 {score} < 85，触发优化建议")
                return [
                    Task(name="生成优化建议", coroutine=call_external_api,
                         kwargs={"url": "optimizer/analyze"}),
                ]
        return []

    tasks = [
        Task(name="代码质量分析", coroutine=analyze_code_quality,
             kwargs={"code": "sample code"}),
    ]
    results = await orchestrator.execute_conditional(tasks, decide_next)
    print_summary(results)


async def demo_retry_fallback():
    """演示：重试与降级"""
    orchestrator = Orchestrator()

    # 模拟会失败的 API 调用，配置了重试和降级
    tasks = [
        Task(
            name="不稳定API调用",
            coroutine=call_external_api,
            kwargs={"url": "https://unstable-api.example.com", "fail_probability": 0.8},
            max_retries=2,              # 最多重试 2 次
            timeout_seconds=1.0,        # 1 秒超时
            fallback=lambda: fallback_api_call("https://unstable-api.example.com"),
        ),
    ]

    print("\n>>> 重试与降级模式 <<<")
    results = await orchestrator.execute_parallel(tasks)
    print_summary(results)


def print_summary(results: dict[str, TaskResult]):
    """打印执行摘要"""
    print("\n  执行摘要:")
    for name, result in results.items():
        icon = {
            TaskStatus.SUCCESS: "✓",
            TaskStatus.FAILED: "✗",
            TaskStatus.FALLBACK: "⟳",
            TaskStatus.TIMEOUT: "⏱",
            TaskStatus.SKIPPED: "→",
        }.get(result.status, "?")

        status_text = result.status.value
        if result.retries > 0:
            status_text += f" (重试{result.retries}次)"

        print(f"    {icon} {name}: {status_text} "
              f"({result.duration_ms:.0f}ms)")

        if result.data:
            # 截断显示数据
            data_str = str(result.data)[:80]
            if len(str(result.data)) > 80:
                data_str += "..."
            print(f"      数据: {data_str}")
        if result.error:
            print(f"      错误: {result.error}")


async def main():
    """运行所有编排模式演示"""
    print("=" * 60)
    print("AI 技能编排引擎 - 高级模式演示")
    print("=" * 60)

    await demo_sequential()
    await demo_parallel()
    await demo_conditional()
    await demo_retry_fallback()

    print("\n" + "=" * 60)
    print("所有编排模式演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
