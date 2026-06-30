# 贡献指南

感谢你对 AI MCP Skills Guide 的关注！我们欢迎各种形式的贡献。

## 行为准则

- 尊重所有贡献者，保持专业和友善的交流
- 对事不对人，聚焦技术讨论
- 接受建设性批评，积极回应反馈

## 如何贡献

### 报告 Bug

1. 在 [Issues](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/issues) 中搜索是否已有相似问题
2. 如无，创建新 Issue，使用 Bug 报告模板
3. 提供详细的复现步骤、预期行为和实际行为

### 提出功能建议

1. 在 Issues 中搜索是否已有类似建议
2. 清楚描述功能的使用场景和价值
3. 如果可能，提供初步的 API 设计方案

### 提交代码

#### 1. Fork 并克隆

```bash
# Fork 仓库到你的账户
# 然后克隆到本地
git clone https://github.com/YOUR_USERNAME/ai-mcp-skills-guide.git
cd ai-mcp-skills-guide
```

#### 2. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

#### 3. 开发和测试

```bash
# 安装开发依赖与 pre-commit 钩子
make dev          # 等价于 pip install -e ".[dev]" && pre-commit install

# 运行测试
make test         # 等价于 pytest -q

# 运行代码检查
make lint         # 等价于 ruff check .

# 类型检查
make typecheck    # 等价于 mypy src
```

提交前 `pre-commit` 会自动运行 ruff 与格式化。如需手动运行：

```bash
pre-commit run --all-files
```

CI（GitHub Actions）会在 PR 上自动运行相同的检查（Python 3.10/3.11/3.12 矩阵）。

#### 4. 提交代码

```bash
git add .
git commit -m "feat: 添加 XXX 功能"
```

提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

| 前缀 | 说明 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | Bug 修复 |
| `docs:` | 文档更新 |
| `refactor:` | 代码重构 |
| `test:` | 测试相关 |
| `chore:` | 构建/工具变动 |

#### 5. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 代码规范

### Python

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 风格
- 使用类型注解
- 函数和类必须有文档字符串

```python
def calculate_kpi(data: list[float], method: str = "mean") -> dict[str, float]:
    """
    计算关键绩效指标。

    Args:
        data: 输入数据列表
        method: 计算方法 ("mean", "median", "max", "min")

    Returns:
        包含各 KPI 指标值的字典

    Raises:
        ValueError: 当 data 为空或 method 不支持时
    """
    ...
```

### 文档

- 使用清晰的中文编写文档
- 代码示例必须包含注释
- 架构图使用 ASCII art 或 Mermaid

## 审查流程

1. 提交 PR 后，自动化检查（lint、test）会运行
2. 维护者会在 3 个工作日内进行代码审查
3. 审查意见需要全部解决后才能合并
4. 合并策略：Squash and Merge

## 目录规范

新增内容时请遵循现有目录结构：

```
docs/        → 文档类内容
examples/    → 可运行的代码示例
```

## 获取帮助

- 在 Issue 中 @ 维护者
- 在 PR 中直接讨论技术细节

---

再次感谢你的贡献！
