# 使用案例分析

## 案例一：GitHub 智能助手

### 背景

开发者需要频繁在 GitHub 上搜索代码、管理 Issue 和审查 PR。通过 MCP 技能集成，AI 可以直接操作 GitHub，实现端到端的开发辅助。

### 架构

```
AI IDE (Host)
    │
    ├── github_search_skill ───→ GitHub Search API
    ├── github_issue_skill  ───→ GitHub Issues API
    ├── github_pr_skill     ───→ GitHub Pull Requests API
    └── code_review_skill   ───→ 本地代码分析
```

### 技能组合

| 技能 | 功能 | 触发场景 |
|------|------|---------|
| `github_search` | 搜索仓库/代码/Issue | 用户询问开源项目 |
| `github_read_file` | 读取仓库文件 | 需要查看源代码 |
| `github_create_issue` | 创建 Issue | 提交 Bug 或功能请求 |
| `code_review` | 代码审查 | 审查 PR 变更 |

### 工作流示例

**场景：用户要求 "搜索 Python MCP 项目并分析其架构"**

```
1. github_search(query="mcp server lang:python")  → 获取仓库列表
2. github_read_file(owner="...", repo="...", path="README.md") → 读取项目说明
3. github_read_file(owner="...", repo="...", path="src/server.py") → 读取核心代码
4. code_review(files=[...])  → 分析代码架构
5. 生成架构分析报告 → 返回给用户
```

### 关键收益

- 减少 60% 的手动搜索和文件查阅时间
- AI 自动理解上下文，技能调用次数减少 40%
- 代码审查覆盖率达到 100%

---

## 案例二：库存管理系统仿真

### 背景

快消品行业需要仿真库存策略来优化补货决策。AI 通过 MCP 技能调用仿真引擎，根据历史数据和策略参数生成仿真报告。

### 架构

```
用户界面 (Web)
    │
    ├── inventory_sim_skill ───→ 仿真引擎
    ├── data_analysis_skill ───→ 数据分析模块
    └── report_gen_skill    ───→ 报告生成器
```

### 技能设计

```python
class InventorySimulationSkill(BaseSkill):
    """库存仿真技能"""

    async def execute(
        self,
        product_id: str,           # 产品 ID
        simulation_days: int,      # 仿真天数
        strategy: str,             # 库存策略 (sS, RQ, base-stock)
        demand_forecast: list,     # 需求预测数据
    ) -> dict:
        """执行库存仿真并返回结果"""
        # 参数验证
        self._validate_params(product_id, simulation_days, strategy)

        # 加载历史数据
        history = await self._load_history(product_id)

        # 运行仿真
        sim_result = await self._run_simulation(
            history=history,
            forecast=demand_forecast,
            days=simulation_days,
            strategy=strategy,
        )

        # 计算 KPI
        kpis = self._calculate_kpis(sim_result)

        return {
            "simulation_id": sim_result.id,
            "kpis": kpis,
            "recommendations": self._generate_recommendations(kpis),
            "charts": sim_result.chart_urls,
        }
```

### 工作流示例

**场景：用户询问 "产品 SKU-001 应该采用什么补货策略？"**

```
1. data_analysis_skill(product_id="SKU-001") → 分析历史销售数据
2. inventory_sim_skill(product_id="SKU-001", strategy="sS") → 运行 S-s 策略仿真
3. inventory_sim_skill(product_id="SKU-001", strategy="RQ") → 运行 R-Q 策略仿真
4. report_gen_skill(comparison_data=[...]) → 对比分析并生成推荐
5. 返回策略推荐报告 → 展示给用户
```

---

## 案例三：多技能编排 — 项目初始化助手

### 背景

新项目启动时需要创建仓库、设置 CI/CD、配置开发环境等。通过技能编排，AI 可以一次性完成所有初始化工作。

### 编排流程

```
用户: "创建一个新的 Python Web 项目"
    │
    ├── 1. github_create_repo(name="...", description="...")
    │       └── 返回 repo_url
    │
    ├── 2. file_write_batch(files=[
    │       "pyproject.toml", "src/main.py",
    │       "tests/test_main.py", ".github/workflows/ci.yml"
    │   ])
    │       └── 创建项目骨架
    │
    ├── 3. github_create_branch(branch="develop")
    │       └── 创建开发分支
    │
    └── 4. github_create_issue(title="项目初始化完成")
            └── 记录初始化状态
```

### 技能编排实现

```python
class ProjectInitOrchestrator:
    """项目初始化编排器"""

    def __init__(self, skills: list[BaseSkill]):
        self.skills = {s.metadata.name: s for s in skills}

    async def initialize_project(self, config: ProjectConfig) -> dict:
        """执行完整的项目初始化流程"""
        results = {}

        # 阶段 1：创建远程仓库
        repo_result = await self.skills["github_create_repo"].execute(
            name=config.name,
            description=config.description,
        )
        results["repo"] = repo_result

        # 阶段 2：并行写入所有模板文件
        file_tasks = [
            self.skills["file_write"].execute(path=p, content=c)
            for p, c in self._generate_templates(config).items()
        ]
        file_results = await asyncio.gather(*file_tasks)
        results["files"] = file_results

        # 阶段 3：创建开发分支
        branch_result = await self.skills["github_create_branch"].execute(
            repo=config.name,
            branch="develop",
        )
        results["branch"] = branch_result

        return results
```

---

## 设计模式总结

| 模式 | 适用场景 | 优点 | 注意事项 |
|------|---------|------|---------|
| **串行流水线** | 步骤有依赖关系 | 逻辑清晰、易于调试 | 总耗时为各步骤之和 |
| **并行执行** | 步骤独立无依赖 | 速度快、效率高 | 需处理部分失败 |
| **条件分支** | 根据结果动态决策 | 灵活、适应性强 | 复杂度较高 |
| **重试+降级** | 外部服务不稳定 | 提高可靠性 | 需设计合理的降级策略 |
