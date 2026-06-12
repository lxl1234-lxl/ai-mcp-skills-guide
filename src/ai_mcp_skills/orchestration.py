"""
编排引擎模块 - 多模式技能编排

提供三种编排模式:
1. 串行流水线 (Sequential): 按序执行，前驱输出作为后继输入
2. 并行执行 (Parallel): 无依赖任务并发执行
3. 条件分支 (Conditional): 根据中间结果动态决策

以及:
- 重试机制（指数退避）
- 超时控制
- 降级策略
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine


class TaskStatus(Enum):
    """任务执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    FALLBACK = "fallback"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


@dataclass
class TaskResult:
    """单个任务的执行结果

    Attributes:
        task_name: 任务名称
        status: 执行状态
        data: 结果数据
        error: 错误信息
        duration_ms: 耗时（毫秒）
        retries: 重试次数
    """
    task_name: str
    status: TaskStatus
    data: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    retries: int = 0


@dataclass
class Task:
    """编排任务定义

    Attributes:
        name: 任务名称
        coroutine: 异步执行函数
        args: 位置参数
        kwargs: 关键字参数
        depends_on: 依赖的前置任务名列表
        max_retries: 最大重试次数（默认 0 不重试）
        timeout_seconds: 超时时间
        fallback: 降级处理函数
        skip_on_failure: 前置依赖失败时是否跳过
    """
    name: str
    coroutine: Callable[..., Coroutine]
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    max_retries: int = 0
    timeout_seconds: float = 30.0
    fallback: Callable | None = None
    skip_on_failure: bool = False


class Orchestrator:
    """技能编排引擎

    支持串行、并行、条件三种编排模式。

    Usage:
        orchestrator = Orchestrator()
        results = await orchestrator.execute_sequential([task1, task2])
        results = await orchestrator.execute_parallel([task1, task2, task3])
        results = await orchestrator.execute_conditional([task1], decide_next_fn)
    """

    def __init__(self):
        self.results: dict[str, TaskResult] = {}

    async def execute_sequential(self, tasks: list[Task]) -> dict[str, TaskResult]:
        """串行流水线：按序执行，上一个输出注入下一个输入

        Args:
            tasks: 按执行顺序排列的任务列表

        Returns:
            {task_name: TaskResult} 字典
        """
        self.results.clear()
        previous = None

        for task in tasks:
            if previous and previous.status == TaskStatus.SUCCESS:
                task.kwargs["_previous_result"] = previous.data

            should_skip = any(
                dep in self.results and self.results[dep].status == TaskStatus.FAILED
                for dep in task.depends_on
            ) and task.skip_on_failure

            if should_skip:
                self.results[task.name] = TaskResult(
                    task_name=task.name, status=TaskStatus.SKIPPED,
                    error="前置任务失败，已跳过",
                )
                continue

            result = await self._execute_with_retry(task)
            self.results[task.name] = result
            previous = result

            if result.status == TaskStatus.FAILED:
                break

        return self.results

    async def execute_parallel(self, tasks: list[Task]) -> dict[str, TaskResult]:
        """并行执行：所有无依赖任务并发运行

        Args:
            tasks: 可并行执行的任务列表

        Returns:
            {task_name: TaskResult} 字典
        """
        self.results.clear()
        coroutines = [self._execute_with_retry(t) for t in tasks]
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        for task, result in zip(tasks, results):
            if isinstance(result, Exception):
                self.results[task.name] = TaskResult(
                    task_name=task.name, status=TaskStatus.FAILED, error=str(result),
                )
            else:
                self.results[task.name] = result

        return self.results

    async def execute_conditional(
        self, tasks: list[Task],
        condition_fn: Callable[[dict[str, TaskResult]], list[Task]],
        max_iterations: int = 3,
    ) -> dict[str, TaskResult]:
        """条件分支：根据结果动态决定后续任务

        Args:
            tasks: 初始任务列表
            condition_fn: 接收当前全部结果，返回下一步任务列表
            max_iterations: 最大迭代次数（防止无限循环）

        Returns:
            {task_name: TaskResult} 字典
        """
        self.results.clear()
        current = tasks
        iteration = 0

        while current and iteration < max_iterations:
            iteration += 1
            for task in current:
                result = await self._execute_with_retry(task)
                self.results[task.name] = result
            current = condition_fn(self.results)

        return self.results

    async def _execute_with_retry(self, task: Task) -> TaskResult:
        """执行单个任务，含重试、超时、降级"""
        last_error = None
        retries = 0

        for attempt in range(task.max_retries + 1):
            try:
                start = time.time()
                data = await asyncio.wait_for(
                    task.coroutine(*task.args, **task.kwargs),
                    timeout=task.timeout_seconds,
                )
                elapsed = (time.time() - start) * 1000
                return TaskResult(
                    task_name=task.name, status=TaskStatus.SUCCESS,
                    data=data, duration_ms=round(elapsed, 1), retries=retries,
                )
            except asyncio.TimeoutError:
                last_error = f"超时 ({task.timeout_seconds}s)"
                retries = attempt + 1
            except Exception as e:
                last_error = str(e)
                retries = attempt + 1
                if attempt < task.max_retries:
                    await asyncio.sleep(0.5 * (2 ** attempt))

        # 降级处理
        if task.fallback:
            try:
                fallback_data = await task.fallback()
                return TaskResult(
                    task_name=task.name, status=TaskStatus.FALLBACK,
                    data=fallback_data, error=last_error, retries=retries,
                )
            except Exception as e:
                last_error = f"降级也失败: {str(e)}"

        return TaskResult(
            task_name=task.name, status=TaskStatus.FAILED,
            error=last_error, retries=retries,
        )
