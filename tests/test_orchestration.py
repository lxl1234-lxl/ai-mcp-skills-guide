"""Orchestrator 模块测试 - 串行/并行/条件 + 重试/超时/降级"""

import asyncio

import pytest

from ai_mcp_skills import Orchestrator, Task, TaskResult, TaskStatus

# ---------------------------------------------------------------------------
# 串行
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sequential_basic():
    orch = Orchestrator()

    async def step1():
        return {"step": 1}

    async def step2(_previous_result=None):
        return {"step": 2, "prev": _previous_result}

    results = await orch.execute_sequential(
        [
            Task(name="s1", coroutine=step1),
            Task(name="s2", coroutine=step2, depends_on=["s1"]),
        ]
    )
    assert results["s1"].status == TaskStatus.SUCCESS
    assert results["s2"].status == TaskStatus.SUCCESS
    assert results["s2"].data["prev"]["step"] == 1


@pytest.mark.asyncio
async def test_sequential_skip_on_failure():
    orch = Orchestrator()

    async def fail_step():
        raise RuntimeError("fail")

    async def next_step():
        return {"ok": True}

    results = await orch.execute_sequential(
        [
            Task(name="bad", coroutine=fail_step),
            Task(name="next", coroutine=next_step, skip_on_failure=True),
        ]
    )
    assert results["bad"].status == TaskStatus.FAILED
    assert results["next"].status == TaskStatus.SKIPPED


@pytest.mark.asyncio
async def test_sequential_stops_on_failure_without_skip():
    """不设置 skip_on_failure 时，前置失败应终止后续任务"""
    orch = Orchestrator()
    executed = []

    async def fail_step():
        raise RuntimeError("fail")

    async def next_step():
        executed.append("next")
        return {"ok": True}

    results = await orch.execute_sequential(
        [
            Task(name="bad", coroutine=fail_step),
            Task(name="next", coroutine=next_step),
        ]
    )
    assert results["bad"].status == TaskStatus.FAILED
    assert "next" not in results  # 终止，未加入结果
    assert executed == []  # 未执行


# ---------------------------------------------------------------------------
# 并行
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_parallel_basic():
    orch = Orchestrator()

    async def a():
        return {"name": "a"}

    async def b():
        return {"name": "b"}

    results = await orch.execute_parallel(
        [
            Task(name="a", coroutine=a),
            Task(name="b", coroutine=b),
        ]
    )
    assert results["a"].status == TaskStatus.SUCCESS
    assert results["b"].status == TaskStatus.SUCCESS


@pytest.mark.asyncio
async def test_parallel_exception_isolated():
    """一个任务失败不影响其他任务"""
    orch = Orchestrator()

    async def ok():
        return {"ok": True}

    async def boom():
        raise RuntimeError("boom")

    results = await orch.execute_parallel(
        [
            Task(name="ok", coroutine=ok),
            Task(name="boom", coroutine=boom),
        ]
    )
    assert results["ok"].status == TaskStatus.SUCCESS
    assert results["boom"].status == TaskStatus.FAILED


# ---------------------------------------------------------------------------
# 条件
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_conditional_branches_when_low_score():
    orch = Orchestrator()

    async def analyze():
        return {"score": 70}  # 低于阈值

    async def optimize():
        return {"optimized": True}

    def decide(results: dict[str, TaskResult]) -> list[Task]:
        r = results.get("analyze")
        if r and r.status == TaskStatus.SUCCESS and r.data.get("score", 100) < 85:
            return [Task(name="optimize", coroutine=optimize)]
        return []

    results = await orch.execute_conditional(
        [Task(name="analyze", coroutine=analyze)],
        decide,
    )
    assert "optimize" in results
    assert results["optimize"].status == TaskStatus.SUCCESS


@pytest.mark.asyncio
async def test_conditional_no_branch_when_high_score():
    orch = Orchestrator()

    async def analyze():
        return {"score": 95}

    def decide(results):
        return []  # 高分不分支

    results = await orch.execute_conditional(
        [Task(name="analyze", coroutine=analyze)],
        decide,
    )
    assert "analyze" in results
    assert len(results) == 1  # 仅初始任务


@pytest.mark.asyncio
async def test_conditional_max_iterations():
    """条件函数持续返回任务时应受 max_iterations 限制"""
    orch = Orchestrator()
    counter = {"n": 0}

    async def loop_task():
        counter["n"] += 1
        return {"n": counter["n"]}

    def decide(results):
        # 始终返回新任务，制造无限循环场景
        return [Task(name=f"t{counter['n']}", coroutine=loop_task)]

    results = await orch.execute_conditional(
        [Task(name="t0", coroutine=loop_task)],
        decide,
        max_iterations=2,
    )
    # 初始 + 2 次迭代
    assert len(results) <= 3


# ---------------------------------------------------------------------------
# 重试
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_succeeds_after_failures():
    orch = Orchestrator()
    attempts = {"n": 0}

    async def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient")
        return {"ok": True}

    results = await orch.execute_parallel(
        [
            Task(name="flaky", coroutine=flaky, max_retries=3, timeout_seconds=2),
        ]
    )
    assert results["flaky"].status == TaskStatus.SUCCESS
    assert results["flaky"].retries == 2  # 失败 2 次后第 3 次成功


@pytest.mark.asyncio
async def test_retry_exhausted_then_fallback():
    orch = Orchestrator()

    async def always_fail():
        raise RuntimeError("boom")

    async def fallback():
        return {"cached": True}

    results = await orch.execute_parallel(
        [
            Task(name="api", coroutine=always_fail, max_retries=1, fallback=fallback),
        ]
    )
    assert results["api"].status == TaskStatus.FALLBACK
    assert results["api"].data["cached"] is True


@pytest.mark.asyncio
async def test_timeout_handling():
    orch = Orchestrator()

    async def slow():
        await asyncio.sleep(2)
        return {"done": True}

    results = await orch.execute_parallel(
        [
            Task(name="slow", coroutine=slow, timeout_seconds=0.1, max_retries=0),
        ]
    )
    assert results["slow"].status == TaskStatus.FAILED
    assert "超时" in results["slow"].error


@pytest.mark.asyncio
async def test_no_fallback_returns_failed():
    orch = Orchestrator()

    async def boom():
        raise RuntimeError("no fallback")

    results = await orch.execute_parallel(
        [
            Task(name="x", coroutine=boom, max_retries=0),
        ]
    )
    assert results["x"].status == TaskStatus.FAILED
    assert results["x"].error == "no fallback"


# ---------------------------------------------------------------------------
# TaskResult / Task 数据结构
# ---------------------------------------------------------------------------


def test_task_result_defaults():
    tr = TaskResult(task_name="t", status=TaskStatus.PENDING)
    assert tr.data is None
    assert tr.error is None
    assert tr.duration_ms == 0.0
    assert tr.retries == 0


def test_task_result_full():
    tr = TaskResult(
        task_name="test",
        status=TaskStatus.SUCCESS,
        data={"x": 1},
        duration_ms=12.5,
        retries=2,
    )
    assert tr.task_name == "test"
    assert tr.status == TaskStatus.SUCCESS
    assert tr.data == {"x": 1}
    assert tr.duration_ms == 12.5
    assert tr.retries == 2


def test_task_defaults():
    async def f():
        return None

    t = Task(name="t", coroutine=f)
    assert t.args == ()
    assert t.kwargs == {}
    assert t.depends_on == []
    assert t.max_retries == 0
    assert t.timeout_seconds == 30.0
    assert t.fallback is None
    assert t.skip_on_failure is False


def test_task_status_enum_values():
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.SUCCESS.value == "success"
    assert TaskStatus.FAILED.value == "failed"
    assert TaskStatus.FALLBACK.value == "fallback"
    assert TaskStatus.TIMEOUT.value == "timeout"
    assert TaskStatus.SKIPPED.value == "skipped"
