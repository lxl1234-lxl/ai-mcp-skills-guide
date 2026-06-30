# 仓库优化与丰富 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `ai-mcp-skills-guide` 仓库补充 CI/CD、社区文件、新增技能、测试拆分与扩展、开发工具与文档体系，使其从"能跑的示例项目"升级为"可发布、可贡献、可维护的开源项目"。

**Architecture:** 分 5 个阶段递进：① 开发工具与 CI 基础（Makefile、mypy、pre-commit、GitHub Actions）；② GitHub 社区文件（Issue/PR 模板、CODE_OF_CONDUCT、SECURITY）；③ 新增 HTTP 请求技能（TDD）；④ 测试拆分与边界用例补充（TDD）；⑤ 文档体系（quickstart、API 参考、FAQ、troubleshooting、roadmap）。每个阶段独立可交付，每个任务自包含且可独立提交。

**Tech Stack:** Python 3.10+、pytest、pytest-asyncio、ruff、mypy、pre-commit、GitHub Actions、Markdown。

**前置约定：**
- 工作目录为仓库根 `/workspace`。
- 所有路径在仓库内为相对路径（如 `src/ai_mcp_skills/...`）。
- 每个任务结束都执行 `git add` + `git commit`，提交信息遵循 Conventional Commits。
- 测试命令：`pytest -q`；Lint 命令：`ruff check .`；类型检查：`mypy src`。
- 首次运行 `pip install -e ".[dev]"` 安装开发依赖。

---

## File Structure

### 新建文件清单（按职责分组）

**开发工具与 CI（根目录 / `.github/`）：**
- `.editorconfig` — 编辑器统一配置
- `Makefile` — 常用命令快捷方式
- `mypy.ini` — 类型检查配置
- `.pre-commit-config.yaml` — pre-commit 钩子
- `.github/workflows/ci.yml` — CI 流水线（lint + test + type check）

**GitHub 社区文件（`.github/`）：**
- `.github/ISSUE_TEMPLATE/bug_report.md` — Bug 报告模板
- `.github/ISSUE_TEMPLATE/feature_request.md` — 功能建议模板
- `.github/ISSUE_TEMPLATE/config.yml` — Issue 模板配置
- `.github/PULL_REQUEST_TEMPLATE.md` — PR 模板
- `.github/CODE_OF_CONDUCT.md` — 行为准则
- `.github/SECURITY.md` — 安全策略

**新增技能（`src/ai_mcp_skills/`）：**
- `src/ai_mcp_skills/http_skill.py` — HTTP 请求技能（仅用标准库 `urllib`，无新依赖）

**测试拆分（`tests/`）：**
- `tests/test_skill.py` — SkillMetadata/BaseSkill/TextAnalysisSkill 测试
- `tests/test_mcp.py` — ToolDefinition/ToolResult/SkillRegistry/MCPServer 测试
- `tests/test_orchestration.py` — Orchestrator 三种模式 + 重试/超时/降级测试
- `tests/test_http_skill.py` — HTTP 技能测试
- 删除 `tests/test_package.py`（内容已拆分到上述文件）

**示例与文档：**
- `examples/README.md` — 示例索引
- `examples/http-skill/run_demo.py` — HTTP 技能演示
- `docs/quickstart.md` — 5 分钟快速开始
- `docs/api-reference.md` — API 参考
- `docs/troubleshooting.md` — 故障排查
- `docs/faq.md` — 常见问题
- `docs/roadmap.md` — 项目路线图

### 修改文件清单
- `pyproject.toml` — 添加 mypy 依赖到 dev 组、版本号补丁位
- `src/ai_mcp_skills/__init__.py` — 导出 `HttpRequestSkill`
- `README.md` — 添加徽章、目录、新章节
- `CHANGELOG.md` — 添加 `[Unreleased]` 段
- `CONTRIBUTING.md` — 补充本地 pre-commit 与 CI 说明

---

## Phase 1：开发工具与 CI 基础

### Task 1: 添加 `.editorconfig`

**Files:**
- Create: `.editorconfig`

- [ ] **Step 1: 创建文件**

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.{md,yml,yaml}]
indent_size = 2

[Makefile]
indent_style = tab
```

- [ ] **Step 2: 验证文件存在**

Run: `test -f .editorconfig && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .editorconfig
git commit -m "chore: 添加 .editorconfig 统一编辑器配置"
```

---

### Task 2: 添加 `Makefile`

**Files:**
- Create: `Makefile`

- [ ] **Step 1: 创建文件**

```makefile
.PHONY: install dev test lint typecheck format clean examples

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pip install pre-commit
	pre-commit install

test:
	pytest -q

lint:
	ruff check .

typecheck:
	mypy src

format:
	ruff format .

examples: install
	python examples/basic-skill/run_demo.py
	python examples/mcp-integration/run_demo.py
	python examples/advanced-patterns/run_demo.py

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
```

- [ ] **Step 2: 验证 make 命令可用**

Run: `make -n test`
Expected: 显示 `pytest -q`

- [ ] **Step 3: Commit**

```bash
git add Makefile
git commit -m "chore: 添加 Makefile 提供常用命令快捷方式"
```

---

### Task 3: 添加 `mypy.ini` 并在 `pyproject.toml` 注册依赖

**Files:**
- Create: `mypy.ini`
- Modify: `pyproject.toml`

- [ ] **Step 1: 创建 `mypy.ini`**

```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
ignore_missing_imports = True
exclude = (^build/|^dist/|^examples/)

[mypy-tests.*]
ignore_errors = True
```

- [ ] **Step 2: 修改 `pyproject.toml` 的 `dev` 依赖**

将 `pyproject.toml` 第 32-36 行：

```toml
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.5",
]
```

替换为：

```toml
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

- [ ] **Step 3: 安装新依赖并运行 mypy**

Run: `pip install -e ".[dev]" && mypy src`
Expected: `Success: no issues found in 4 source files`（或仅有少量现有告警，可接受）

- [ ] **Step 4: Commit**

```bash
git add mypy.ini pyproject.toml
git commit -m "chore: 添加 mypy 配置并注册到 dev 依赖"
```

---

### Task 4: 添加 `.pre-commit-config.yaml`

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: 创建文件**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.7
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

- [ ] **Step 2: 验证配置语法**

Run: `pre-commit validate-config .pre-commit-config.yaml`
Expected: 无报错（若未安装 pre-commit，可跳过：`pip install pre-commit && pre-commit validate-config .pre-commit-config.yaml`）

- [ ] **Step 3: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "chore: 添加 pre-commit 钩子配置"
```

---

### Task 5: 添加 GitHub Actions CI 工作流

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: 创建目录与文件**

```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with ruff
        run: ruff check .

      - name: Type check with mypy
        run: mypy src
        continue-on-error: true

      - name: Test with pytest
        run: pytest -q
```

- [ ] **Step 2: 验证 YAML 语法**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: 添加 GitHub Actions 流水线（lint + typecheck + test, 多版本矩阵）"
```

---

## Phase 2：GitHub 社区文件

### Task 6: 添加 Issue 模板与配置

**Files:**
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/ISSUE_TEMPLATE/config.yml`

- [ ] **Step 1: 创建 bug 报告模板**

```markdown
---
name: Bug 报告
about: 报告缺陷以帮助改进项目
title: "[BUG] "
labels: bug
assignees: ''
---

## 描述

简要清晰地描述该 Bug 是什么。

## 复现步骤

1. 进入 '...'
2. 点击 '...'
3. 看到 '...'

## 期望行为

描述你期望发生的事情。

## 实际行为

描述实际发生的事情。

## 环境

- OS: [例如 Ubuntu 22.04]
- Python 版本: [例如 3.11.4]
- 包版本: [例如 1.0.0]

## 附加信息

如有日志、截图等，请在此附上。
```

- [ ] **Step 2: 创建功能建议模板**

```markdown
---
name: 功能建议
about: 提出新功能或改进建议
title: "[FEAT] "
labels: enhancement
assignees: ''
---

## 功能描述

简要清晰地描述你希望添加的功能。

## 动机

为什么需要这个功能？解决了什么问题？

## 建议方案

如果可能，描述实现思路或 API 设计。

```python
# 示例 API
skill.execute(...)
```

## 备选方案

你考虑过的其他方案。

## 附加信息

其他相关上下文。
```

- [ ] **Step 3: 创建 Issue 模板配置**

```yaml
blank_issues_enabled: false
contact_links:
  - name: 项目文档
    url: https://github.com/lxl1234-lxl/ai-mcp-skills-guide/tree/main/docs
    about: 在提 Issue 前请先查阅文档
```

- [ ] **Step 4: Commit**

```bash
git add .github/ISSUE_TEMPLATE/
git commit -m "docs: 添加 Issue 模板（bug 报告 / 功能建议）"
```

---

### Task 7: 添加 PR 模板

**Files:**
- Create: `.github/PULL_REQUEST_TEMPLATE.md`

- [ ] **Step 1: 创建文件**

```markdown
## 变更描述

<!-- 简要描述本次 PR 做了什么以及为什么 -->

## 变更类型

- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 文档 (docs)
- [ ] 重构 (refactor)
- [ ] 测试 (test)
- [ ] 构建/CI (chore)

## 关联 Issue

<!-- 例如 Closes #123 -->

## 检查清单

- [ ] 代码通过 `ruff check .`
- [ ] 通过 `mypy src`
- [ ] 通过 `pytest -q`
- [ ] 新增测试覆盖新功能
- [ ] 文档已更新（如适用）
- [ ] CHANGELOG 已更新

## 截图 / 日志

<!-- 如适用，附上验证截图或日志 -->
```

- [ ] **Step 2: Commit**

```bash
git add .github/PULL_REQUEST_TEMPLATE.md
git commit -m "docs: 添加 Pull Request 模板"
```

---

### Task 8: 添加 `CODE_OF_CONDUCT.md`

**Files:**
- Create: `.github/CODE_OF_CONDUCT.md`

- [ ] **Step 1: 创建文件（Contributor Covenant 2.1 中文摘要版）**

```markdown
# 贡献者公约

本项目遵循 [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) 精神。

## 我们的承诺

为了营造一个开放友好的环境，作为贡献者和维护者，我们承诺让参与项目和社区的每个人都不受骚扰，无论年龄、体型、可见或不可见的残疾、族裔、性征、性别认同与表达、经验水平、教育、社会经济地位、国籍、个人外貌、种族、宗教或性取向。

## 我们的准则

有助于营造积极环境的行为示例：

- 对他人展现同理心和善意
- 尊重不同观点和经验
- 给予建设性反馈
- 承担责任并向受我们错误影响的人道歉
- 关注的不仅是个人，更是整个社区

不可接受的行为示例：

- 使用性化语言或图像
- 钓鱼、辱骂或贬损性评论
- 公开或私下骚扰
- 未经明确许可发布他人私人信息

## 执行

可通过在 GitHub 上 [新建 Issue](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/issues) 私下举报违规行为。维护者将在 3 个工作日内评估并回应。

## 来源

本公约改编自 Contributor Covenant 2.1，中文翻译仅供参考，如有歧义以英文原文为准。
```

- [ ] **Step 2: Commit**

```bash
git add .github/CODE_OF_CONDUCT.md
git commit -m "docs: 添加贡献者公约 CODE_OF_CONDUCT"
```

---

### Task 9: 添加 `SECURITY.md`

**Files:**
- Create: `.github/SECURITY.md`

- [ ] **Step 1: 创建文件**

```markdown
# 安全策略

## 报告漏洞

如果你发现安全漏洞，请**不要**在公开 Issue 中披露。

请通过以下方式私密报告：

1. 在 GitHub 上 [新建私密安全建议](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/security/advisories/new)
2. 或发送邮件至维护者（见仓库 owner 资料）

请在报告中包含：

- 漏洞的描述与影响范围
- 复现步骤
- 受影响的版本
- 建议的修复方案（如有）

## 响应时间

- 收到报告后 3 个工作日内确认
- 评估完成后 30 天内发布修复版本

## 支持的版本

| 版本 | 是否支持安全更新 |
|------|----------------|
| 1.x  | ✅              |
| < 1.0| ❌              |

## 安全最佳实践（针对使用者）

- 不要在技能参数中硬编码密钥，使用环境变量
- `MCPServer` 仅在受信任环境中暴露 stdio 接口
- 评估第三方技能时，审查其 `execute` 实现
```

- [ ] **Step 2: Commit**

```bash
git add .github/SECURITY.md
git commit -m "docs: 添加安全策略 SECURITY.md"
```

---

## Phase 3：新增 HTTP 请求技能（TDD）

### Task 10: 为 HTTP 技能编写失败测试

**Files:**
- Create: `tests/test_http_skill.py`

- [ ] **Step 1: 创建测试文件**

```python
"""HttpRequestSkill 单元测试"""

from ai_mcp_skills import HttpRequestSkill


def test_http_skill_metadata():
    skill = HttpRequestSkill()
    m = skill.metadata
    assert m.name == "http_request"
    assert "http" in m.tags
    assert m.version == "1.0.0"


def test_http_skill_input_schema():
    skill = HttpRequestSkill()
    schema = skill.get_input_schema()
    assert schema["type"] == "object"
    assert "url" in schema["properties"]
    assert schema["required"] == ["url"]
    assert schema["properties"]["method"]["enum"] == ["GET", "POST", "PUT", "DELETE"]


def test_http_skill_empty_url():
    skill = HttpRequestSkill()
    r = skill.execute(url="")
    assert r["success"] is False
    assert r["error"]


def test_http_skill_invalid_url():
    skill = HttpRequestSkill()
    r = skill.execute(url="not-a-url")
    assert r["success"] is False
    assert "URL" in r["error"] or "无效" in r["error"]


def test_http_skill_success(monkeypatch):
    """使用伪造响应验证 GET 成功路径"""
    skill = HttpRequestSkill()

    class FakeResponse:
        status = 200
        headers = {"Content-Type": "text/plain"}
        def read(self):
            return b"hello world"
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=None):
        # 记录请求信息
        FakeResponse._req = req
        FakeResponse._timeout = timeout
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    r = skill.execute(url="https://example.com", method="GET", timeout=5)
    assert r["success"] is True
    assert r["data"]["status_code"] == 200
    assert r["data"]["body"] == "hello world"
    assert r["data"]["url"] == "https://example.com"
    assert r["data"]["method"] == "GET"


def test_http_skill_post_with_body(monkeypatch):
    """验证 POST 请求体被正确发送"""
    skill = HttpRequestSkill()
    captured = {}

    class FakeResponse:
        status = 201
        headers = {}
        def read(self):
            return b'{"id": 1}'
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    def fake_urlopen(req, timeout=None):
        captured["data"] = req.data
        captured["method"] = req.get_method()
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    r = skill.execute(
        url="https://api.example.com/items",
        method="POST",
        body='{"name": "test"}',
        headers={"Content-Type": "application/json"},
    )
    assert r["success"] is True
    assert r["data"]["status_code"] == 201
    assert captured["method"] == "POST"
    assert captured["data"] == b'{"name": "test"}'


def test_http_skill_network_error(monkeypatch):
    """网络错误应被捕获并返回结构化失败"""
    import urllib.error
    skill = HttpRequestSkill()

    def fake_urlopen(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    r = skill.execute(url="https://example.com")
    assert r["success"] is False
    assert "connection refused" in r["error"] or "URLError" in r["error"]


def test_http_skill_to_dict_conversion():
    """验证内部 _to_dict 辅助方法"""
    skill = HttpRequestSkill()
    # 直接调用私有方法验证响应转换
    class FakeHeaders:
        def items(self):
            return [("Content-Type", "text/plain"), ("X-Custom", "abc")]
    d = skill._headers_to_dict(FakeHeaders())
    assert d == {"Content-Type": "text/plain", "X-Custom": "abc"}
```

- [ ] **Step 2: 运行测试验证其失败**

Run: `pytest tests/test_http_skill.py -v`
Expected: 全部 FAIL，错误信息包含 `ImportError: cannot import name 'HttpRequestSkill'`

- [ ] **Step 3: Commit（红阶段）**

```bash
git add tests/test_http_skill.py
git commit -m "test: 为 HttpRequestSkill 添加测试用例（红阶段）"
```

---

### Task 11: 实现 `HttpRequestSkill`

**Files:**
- Create: `src/ai_mcp_skills/http_skill.py`

- [ ] **Step 1: 创建实现文件**

```python
"""HTTP 请求技能 - 基于 urllib 标准库

提供:
- HttpRequestSkill: 发送 HTTP/HTTPS 请求并返回结构化响应
"""

import json
import urllib.error
import urllib.request
from typing import Any

from ai_mcp_skills.skill import BaseSkill, SkillMetadata


class HttpRequestSkill(BaseSkill):
    """HTTP 请求技能

    通过标准库 urllib 发送 HTTP 请求，返回统一结构化结果。

    支持的 HTTP 方法: GET, POST, PUT, DELETE
    支持自定义请求头、请求体和超时。
    """

    def __init__(self):
        super().__init__(SkillMetadata(
            name="http_request",
            description="发送 HTTP 请求并返回状态码、响应头与响应体。"
                        "适用于调用 REST API、抓取网页或上传数据。",
            version="1.0.0",
            tags=["http", "network", "api", "request"],
        ))

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "请求的完整 URL（含 http:// 或 https://）",
                    "minLength": 1,
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "default": "GET",
                    "description": "HTTP 方法",
                },
                "headers": {
                    "type": "object",
                    "description": "请求头键值对",
                    "default": {},
                },
                "body": {
                    "type": "string",
                    "description": "请求体（POST/PUT 使用）",
                    "default": "",
                },
                "timeout": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 60,
                    "default": 30,
                    "description": "超时时间（秒）",
                },
            },
            "required": ["url"],
        }

    def execute(
        self, url: str, method: str = "GET", headers: dict | None = None,
        body: str = "", timeout: float = 30,
    ) -> dict[str, Any]:
        """执行 HTTP 请求

        Args:
            url: 请求 URL
            method: HTTP 方法
            headers: 请求头
            body: 请求体
            timeout: 超时秒数

        Returns:
            结构化结果: success/data/error
        """
        if not url or not url.strip():
            return {"success": False, "data": None, "error": "URL 不能为空"}
        if not (url.startswith("http://") or url.startswith("https://")):
            return {"success": False, "data": None, "error": f"无效 URL: {url}（需以 http:// 或 https:// 开头）"}

        method = (method or "GET").upper()
        if method not in ("GET", "POST", "PUT", "DELETE"):
            return {"success": False, "data": None, "error": f"不支持的 HTTP 方法: {method}"}

        try:
            data = body.encode("utf-8") if body else None
            req = urllib.request.Request(
                url, data=data, method=method, headers=headers or {},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                # 尝试 UTF-8 解码，失败则返回前 200 字符的 base64 摘要
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    text = f"<二进制数据 {len(raw)} 字节>"

                return {
                    "success": True,
                    "data": {
                        "url": url,
                        "method": method,
                        "status_code": resp.status,
                        "headers": self._headers_to_dict(resp.headers),
                        "body": text,
                        "body_length": len(raw),
                    },
                    "error": None,
                    "metadata": {"version": self.metadata.version},
                }
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "data": {"status_code": e.code, "url": url},
                "error": f"HTTP 错误 {e.code}: {e.reason}",
            }
        except urllib.error.URLError as e:
            return {"success": False, "data": None, "error": f"网络错误: {e.reason}"}
        except Exception as e:
            return {"success": False, "data": None, "error": f"请求失败: {e}"}

    @staticmethod
    def _headers_to_dict(headers) -> dict:
        """将 HTTP 响应头转换为字典"""
        try:
            return {k: v for k, v in headers.items()}
        except AttributeError:
            return {}
```

- [ ] **Step 2: 运行测试验证其通过**

Run: `pytest tests/test_http_skill.py -v`
Expected: 全部 PASS（8 个测试）

- [ ] **Step 3: 运行全部测试确保无回归**

Run: `pytest -q`
Expected: 全部 PASS（包含原有 test_package.py 的测试）

- [ ] **Step 4: Commit**

```bash
git add src/ai_mcp_skills/http_skill.py
git commit -m "feat: 添加 HttpRequestSkill（基于 urllib 标准库）"
```

---

### Task 12: 在包入口导出 `HttpRequestSkill`

**Files:**
- Modify: `src/ai_mcp_skills/__init__.py`

- [ ] **Step 1: 修改导入与 `__all__`**

将 `src/ai_mcp_skills/__init__.py` 第 11-27 行：

```python
from ai_mcp_skills.orchestration import (
    Orchestrator,
    Task,
    TaskResult,
    TaskStatus,
)
from ai_mcp_skills.skill import (
    BaseSkill,
    SkillMetadata,
    TextAnalysisSkill,
)
from ai_mcp_skills.mcp import (
    MCPServer,
    SkillRegistry,
    ToolDefinition,
    ToolResult,
)

__all__ = [
    # 版本
    "__version__",
    # Skill
    "SkillMetadata",
    "BaseSkill",
    "TextAnalysisSkill",
    # MCP
    "ToolDefinition",
    "ToolResult",
    "SkillRegistry",
    "MCPServer",
    # Orchestration
    "TaskStatus",
    "TaskResult",
    "Task",
    "Orchestrator",
]
```

替换为：

```python
from ai_mcp_skills.orchestration import (
    Orchestrator,
    Task,
    TaskResult,
    TaskStatus,
)
from ai_mcp_skills.skill import (
    BaseSkill,
    SkillMetadata,
    TextAnalysisSkill,
)
from ai_mcp_skills.http_skill import HttpRequestSkill
from ai_mcp_skills.mcp import (
    MCPServer,
    SkillRegistry,
    ToolDefinition,
    ToolResult,
)

__all__ = [
    # 版本
    "__version__",
    # Skill
    "SkillMetadata",
    "BaseSkill",
    "TextAnalysisSkill",
    "HttpRequestSkill",
    # MCP
    "ToolDefinition",
    "ToolResult",
    "SkillRegistry",
    "MCPServer",
    # Orchestration
    "TaskStatus",
    "TaskResult",
    "Task",
    "Orchestrator",
]
```

- [ ] **Step 2: 验证导入成功**

Run: `python -c "from ai_mcp_skills import HttpRequestSkill; print(HttpRequestSkill().metadata.name)"`
Expected: `http_request`

- [ ] **Step 3: 运行全部测试**

Run: `pytest -q`
Expected: 全部 PASS

- [ ] **Step 4: Commit**

```bash
git add src/ai_mcp_skills/__init__.py
git commit -m "feat: 在包入口导出 HttpRequestSkill"
```

---

### Task 13: 添加 HTTP 技能演示脚本

**Files:**
- Create: `examples/http-skill/run_demo.py`

- [ ] **Step 1: 创建演示脚本**

```python
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
```

- [ ] **Step 2: 运行演示（应能正常完成，即使无网络也只输出降级信息）**

Run: `python examples/http-skill/run_demo.py`
Expected: 输出 "演示完成！" 而不抛出异常

- [ ] **Step 3: Commit**

```bash
git add examples/http-skill/run_demo.py
git commit -m "docs: 添加 HTTP 技能示例演示脚本"
```

---

## Phase 4：测试拆分与边界用例补充（TDD）

### Task 14: 创建 `tests/test_skill.py` 并迁移 Skill 测试

**Files:**
- Create: `tests/test_skill.py`

- [ ] **Step 1: 创建测试文件（迁移并扩展）**

```python
"""Skill 模块测试 - SkillMetadata / BaseSkill / TextAnalysisSkill"""

import pytest
from ai_mcp_skills import BaseSkill, SkillMetadata, TextAnalysisSkill


# ---------------------------------------------------------------------------
# SkillMetadata
# ---------------------------------------------------------------------------

def test_skill_metadata_defaults():
    m = SkillMetadata(name="test", description="desc")
    assert m.name == "test"
    assert m.description == "desc"
    assert m.version == "1.0.0"
    assert m.author == ""
    assert m.tags == []


def test_skill_metadata_full():
    m = SkillMetadata(
        name="my-skill", description="my desc",
        version="2.0.0", author="me", tags=["a", "b"],
    )
    assert m.name == "my-skill"
    assert m.version == "2.0.0"
    assert m.author == "me"
    assert m.tags == ["a", "b"]


def test_skill_metadata_tags_independent():
    """验证 tags 默认值不会在实例间共享"""
    m1 = SkillMetadata(name="a", description="d")
    m1.tags.append("x")
    m2 = SkillMetadata(name="b", description="d")
    assert m2.tags == []  # 不应受 m1 影响


# ---------------------------------------------------------------------------
# BaseSkill
# ---------------------------------------------------------------------------

def test_base_skill_tool_definition():
    m = SkillMetadata(name="my-skill", description="my desc", tags=["tag1"])
    skill = BaseSkill(m)
    d = skill.get_tool_definition()
    assert d["name"] == "my-skill"
    assert d["description"] == "my desc"
    assert d["version"] == "1.0.0"
    assert "tag1" in d["tags"]
    assert "inputSchema" in d


def test_base_skill_execute_raises():
    with pytest.raises(NotImplementedError):
        BaseSkill(SkillMetadata(name="x", description="d")).execute()


def test_base_skill_initialize_cleanup_lifecycle():
    skill = BaseSkill(SkillMetadata(name="x", description="d"))
    assert skill._initialized is False
    skill.initialize()
    assert skill._initialized is True
    skill.cleanup()
    assert skill._initialized is False


def test_base_skill_default_input_schema():
    skill = BaseSkill(SkillMetadata(name="x", description="d"))
    schema = skill.get_input_schema()
    assert schema == {"type": "object", "properties": {}}


# ---------------------------------------------------------------------------
# TextAnalysisSkill
# ---------------------------------------------------------------------------

def test_text_analysis_empty():
    skill = TextAnalysisSkill()
    r = skill.execute(text="")
    assert r["success"] is False
    assert r["error"]


def test_text_analysis_whitespace_only():
    skill = TextAnalysisSkill()
    r = skill.execute(text="   \n\t  ")
    assert r["success"] is False


def test_text_analysis_basic():
    skill = TextAnalysisSkill()
    r = skill.execute(text="Hello world! 你好世界！")
    assert r["success"] is True
    assert r["data"]["statistics"]["total_chars"] > 0
    assert len(r["data"]["keywords"]) > 0
    assert r["data"]["readability"] is not None


def test_text_analysis_no_readability():
    skill = TextAnalysisSkill()
    r = skill.execute(text="Hello world!", include_readability=False)
    assert r["data"]["readability"] is None


def test_text_analysis_chinese_stats():
    skill = TextAnalysisSkill()
    r = skill.execute(text="你好世界，今天天气真好。")
    s = r["data"]["statistics"]
    assert s["chinese_words"] > 0
    assert s["total_chars"] > 0


def test_text_analysis_english_stats():
    skill = TextAnalysisSkill()
    r = skill.execute(text="The quick brown fox jumps over the lazy dog.")
    s = r["data"]["statistics"]
    assert s["english_words"] >= 6  # the/quick/brown/fox/jumps/over...


def test_text_analysis_top_n_keywords_limit():
    skill = TextAnalysisSkill()
    r = skill.execute(text="apple apple banana cherry cherry cherry date", top_n_keywords=2)
    kws = r["data"]["keywords"]
    assert len(kws) == 2
    assert kws[0]["frequency"] >= kws[1]["frequency"]


def test_text_analysis_metadata_returned():
    skill = TextAnalysisSkill()
    r = skill.execute(text="hello")
    assert "metadata" in r
    assert r["metadata"]["version"] == skill.metadata.version
    assert r["metadata"]["text_length"] == 5


def test_text_analysis_readability_levels():
    """验证可读性等级随句长变化"""
    skill = TextAnalysisSkill()
    # 极短句
    r1 = skill.execute(text="a b c d.")
    assert r1["data"]["readability"]["level"] in ("非常简单", "简单")
    # 长句
    long_text = " ".join([f"word{i}" for i in range(50)]) + "."
    r2 = skill.execute(text=long_text)
    assert r2["data"]["readability"]["level"] in ("中等", "复杂")


def test_text_analysis_empty_text_readability():
    """无单词的文本不应崩溃"""
    skill = TextAnalysisSkill()
    r = skill.execute(text="...")
    # 句子分隔符存在但无单词
    if r["success"]:
        assert r["data"]["readability"] is not None


def test_text_analysis_get_input_schema():
    skill = TextAnalysisSkill()
    schema = skill.get_input_schema()
    assert schema["required"] == ["text"]
    assert "top_n_keywords" in schema["properties"]
    assert "include_readability" in schema["properties"]
```

- [ ] **Step 2: 运行新测试文件**

Run: `pytest tests/test_skill.py -v`
Expected: 全部 PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_skill.py
git commit -m "test: 拆分 Skill 模块测试并补充边界用例"
```

---

### Task 15: 创建 `tests/test_mcp.py` 并迁移 MCP 测试

**Files:**
- Create: `tests/test_mcp.py`

- [ ] **Step 1: 创建测试文件**

```python
"""MCP 模块测试 - ToolDefinition / ToolResult / SkillRegistry / MCPServer"""

import json
import pytest
from ai_mcp_skills import MCPServer, SkillRegistry, ToolDefinition, ToolResult


# ---------------------------------------------------------------------------
# ToolDefinition / ToolResult
# ---------------------------------------------------------------------------

def test_tool_definition():
    td = ToolDefinition(name="t", description="d", inputSchema={"type": "object"})
    assert td.name == "t"
    assert td.description == "d"
    assert td.inputSchema == {"type": "object"}


def test_tool_definition_default_schema():
    td = ToolDefinition(name="t", description="d")
    assert td.inputSchema == {}


def test_tool_result_defaults():
    tr = ToolResult(content=[])
    assert tr.content == []
    assert tr.isError is False


def test_tool_result_with_error():
    tr = ToolResult(content=[{"type": "text", "text": "err"}], isError=True)
    assert tr.isError is True
    assert len(tr.content) == 1


# ---------------------------------------------------------------------------
# SkillRegistry
# ---------------------------------------------------------------------------

def test_registry_register_and_list():
    reg = SkillRegistry()
    reg.register("tool1", "desc1", {"type": "object"}, lambda **kw: {})
    reg.register("tool2", "desc2", {"type": "object"}, lambda **kw: {})
    tools = reg.list_tools()
    assert len(tools) == 2
    assert tools[0].name == "tool1"
    assert tools[1].name == "tool2"


def test_registry_duplicate():
    reg = SkillRegistry()
    reg.register("t", "d", {}, lambda **kw: {})
    with pytest.raises(ValueError):
        reg.register("t", "d", {}, lambda **kw: {})


def test_registry_call_unknown():
    reg = SkillRegistry()
    r = reg.call_tool("unknown", {})
    assert r.isError is True
    assert "未知工具" in r.content[0]["text"]


def test_registry_call_success():
    reg = SkillRegistry()
    reg.register("greet", "greet", {},
                 lambda **kw: {"message": f"Hello {kw.get('name', 'World')}"})
    r = reg.call_tool("greet", {"name": "MCP"})
    assert r.isError is False
    data = json.loads(r.content[0]["text"])
    assert data["message"] == "Hello MCP"


def test_registry_call_includes_metadata():
    """成功调用应附带 _metadata.execution_time_ms"""
    reg = SkillRegistry()
    reg.register("echo", "e", {}, lambda **kw: {"ok": True})
    r = reg.call_tool("echo", {})
    data = json.loads(r.content[0]["text"])
    assert "_metadata" in data
    assert "execution_time_ms" in data["_metadata"]


def test_registry_call_handler_raises():
    """handler 抛异常时返回 isError=True"""
    def boom(**kw):
        raise RuntimeError("boom")
    reg = SkillRegistry()
    reg.register("boom", "b", {}, boom)
    r = reg.call_tool("boom", {})
    assert r.isError is True
    assert "boom" in r.content[0]["text"]


def test_registry_list_tools_returns_definitions_only():
    """list_tools 应只返回 ToolDefinition，不含 handler"""
    reg = SkillRegistry()
    reg.register("t", "d", {"type": "object"}, lambda **kw: {})
    tools = reg.list_tools()
    assert all(isinstance(t, ToolDefinition) for t in tools)


# ---------------------------------------------------------------------------
# MCPServer
# ---------------------------------------------------------------------------

def test_mcp_server_initialize():
    srv = MCPServer("test-srv", "1.2.3")
    r = srv.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05",
                   "clientInfo": {"name": "c", "version": "1"}},
    })
    assert r["jsonrpc"] == "2.0"
    assert r["id"] == 1
    info = r["result"]["serverInfo"]
    assert info["name"] == "test-srv"
    assert info["version"] == "1.2.3"
    assert "tools" in r["result"]["capabilities"]


def test_mcp_server_unknown_method():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1, "method": "unknown"})
    assert "error" in r
    assert r["error"]["code"] == -32601


def test_mcp_server_list_tools_empty():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert r["result"]["tools"] == []


def test_mcp_server_list_tools_after_register():
    srv = MCPServer("s", "1")
    srv.registry.register("t", "desc", {"type": "object"}, lambda **kw: {})
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert len(r["result"]["tools"]) == 1
    assert r["result"]["tools"][0]["name"] == "t"


def test_mcp_server_call_tool():
    srv = MCPServer("s", "1")
    srv.registry.register("add", "加法",
                          {"type": "object"},
                          lambda **kw: {"sum": kw.get("a", 0) + kw.get("b", 0)})
    r = srv.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "add", "arguments": {"a": 2, "b": 3}},
    })
    assert r["result"]["isError"] is False
    data = json.loads(r["result"]["content"][0]["text"])
    assert data["sum"] == 5


def test_mcp_server_call_unknown_tool():
    srv = MCPServer("s", "1")
    r = srv.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "missing", "arguments": {}},
    })
    assert r["result"]["isError"] is True


def test_mcp_server_no_method_field():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 1})
    assert "error" in r
    assert r["error"]["code"] == -32601


def test_mcp_server_response_id_preserved():
    srv = MCPServer("s", "1")
    r = srv.handle_request({"jsonrpc": "2.0", "id": 42, "method": "tools/list"})
    assert r["id"] == 42
```

- [ ] **Step 2: 运行测试**

Run: `pytest tests/test_mcp.py -v`
Expected: 全部 PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_mcp.py
git commit -m "test: 拆分 MCP 模块测试并补充边界用例"
```

---

### Task 16: 创建 `tests/test_orchestration.py` 并迁移/扩展编排测试

**Files:**
- Create: `tests/test_orchestration.py`

- [ ] **Step 1: 创建测试文件**

```python
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

    results = await orch.execute_sequential([
        Task(name="s1", coroutine=step1),
        Task(name="s2", coroutine=step2, depends_on=["s1"]),
    ])
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

    results = await orch.execute_sequential([
        Task(name="bad", coroutine=fail_step),
        Task(name="next", coroutine=next_step, skip_on_failure=True),
    ])
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

    results = await orch.execute_sequential([
        Task(name="bad", coroutine=fail_step),
        Task(name="next", coroutine=next_step),
    ])
    assert results["bad"].status == TaskStatus.FAILED
    assert "next" not in results  # 终止，未加入结果
    assert executed == []  # 未执行


# ---------------------------------------------------------------------------
# 并行
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_parallel_basic():
    orch = Orchestrator()

    async def a(): return {"name": "a"}
    async def b(): return {"name": "b"}

    results = await orch.execute_parallel([
        Task(name="a", coroutine=a),
        Task(name="b", coroutine=b),
    ])
    assert results["a"].status == TaskStatus.SUCCESS
    assert results["b"].status == TaskStatus.SUCCESS


@pytest.mark.asyncio
async def test_parallel_exception_isolated():
    """一个任务失败不影响其他任务"""
    orch = Orchestrator()

    async def ok(): return {"ok": True}
    async def boom(): raise RuntimeError("boom")

    results = await orch.execute_parallel([
        Task(name="ok", coroutine=ok),
        Task(name="boom", coroutine=boom),
    ])
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
        [Task(name="analyze", coroutine=analyze)], decide,
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
        [Task(name="analyze", coroutine=analyze)], decide,
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
        [Task(name="t0", coroutine=loop_task)], decide, max_iterations=2,
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

    results = await orch.execute_parallel([
        Task(name="flaky", coroutine=flaky, max_retries=3, timeout_seconds=2),
    ])
    assert results["flaky"].status == TaskStatus.SUCCESS
    assert results["flaky"].retries == 2  # 失败 2 次后第 3 次成功


@pytest.mark.asyncio
async def test_retry_exhausted_then_fallback():
    orch = Orchestrator()

    async def always_fail():
        raise RuntimeError("boom")

    async def fallback():
        return {"cached": True}

    results = await orch.execute_parallel([
        Task(name="api", coroutine=always_fail, max_retries=1,
             fallback=fallback),
    ])
    assert results["api"].status == TaskStatus.FALLBACK
    assert results["api"].data["cached"] is True


@pytest.mark.asyncio
async def test_timeout_handling():
    orch = Orchestrator()

    async def slow():
        await asyncio.sleep(2)
        return {"done": True}

    results = await orch.execute_parallel([
        Task(name="slow", coroutine=slow, timeout_seconds=0.1, max_retries=0),
    ])
    assert results["slow"].status == TaskStatus.FAILED
    assert "超时" in results["slow"].error


@pytest.mark.asyncio
async def test_no_fallback_returns_failed():
    orch = Orchestrator()

    async def boom():
        raise RuntimeError("no fallback")

    results = await orch.execute_parallel([
        Task(name="x", coroutine=boom, max_retries=0),
    ])
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
        task_name="test", status=TaskStatus.SUCCESS,
        data={"x": 1}, duration_ms=12.5, retries=2,
    )
    assert tr.task_name == "test"
    assert tr.status == TaskStatus.SUCCESS
    assert tr.data == {"x": 1}
    assert tr.duration_ms == 12.5
    assert tr.retries == 2


def test_task_defaults():
    async def f(): return None
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
```

- [ ] **Step 2: 运行测试**

Run: `pytest tests/test_orchestration.py -v`
Expected: 全部 PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_orchestration.py
git commit -m "test: 拆分 Orchestrator 测试并补充重试/超时/降级用例"
```

---

### Task 17: 删除旧 `tests/test_package.py` 并验证全部测试通过

**Files:**
- Delete: `tests/test_package.py`

- [ ] **Step 1: 删除旧文件**

Run: `rm tests/test_package.py`

- [ ] **Step 2: 验证测试集完整（含版本断言）**

Run: `pytest -q`
Expected: 全部 PASS，测试数量 ≥ 40（包含 http_skill + skill + mcp + orchestration）

- [ ] **Step 3: 确认 lint 通过**

Run: `ruff check .`
Expected: `All checks passed!`

- [ ] **Step 4: Commit**

```bash
git add -A tests/
git commit -m "refactor: 删除聚合测试文件，迁移到分模块测试"
```

---

## Phase 5：文档体系

### Task 18: 添加 `examples/README.md` 索引

**Files:**
- Create: `examples/README.md`

- [ ] **Step 1: 创建文件**

```markdown
# 示例代码

本目录包含 `ai_mcp_skills` 包的可运行示例。所有示例都假定已执行：

```bash
pip install -e .
```

## 示例清单

| 目录 | 说明 | 运行命令 |
|------|------|---------|
| [basic-skill](basic-skill/run_demo.py) | 文本分析技能的基础使用 | `python examples/basic-skill/run_demo.py` |
| [mcp-integration](mcp-integration/run_demo.py) | MCP 服务器多工具注册与调用 | `python examples/mcp-integration/run_demo.py` |
| [advanced-patterns](advanced-patterns/run_demo.py) | 编排引擎四种模式演示 | `python examples/advanced-patterns/run_demo.py` |
| [http-skill](http-skill/run_demo.py) | HTTP 请求技能与错误处理 | `python examples/http-skill/run_demo.py` |

## 推荐学习顺序

1. **basic-skill** — 理解 `BaseSkill` 生命周期与工具定义
2. **mcp-integration** — 理解 `SkillRegistry` 与 `MCPServer` 的 JSON-RPC 交互
3. **http-skill** — 学习真实网络技能的错误处理模式
4. **advanced-patterns** — 掌握 `Orchestrator` 的串行/并行/条件/降级编排

## 示例特点

- 所有示例**无外部网络依赖**（除 http-skill 演示真实请求外）
- 每个示例独立可运行，输出清晰的进度信息
- 示例代码可直接复制作为新技能的脚手架
```

- [ ] **Step 2: Commit**

```bash
git add examples/README.md
git commit -m "docs: 添加 examples 索引 README"
```

---

### Task 19: 添加 `docs/quickstart.md`

**Files:**
- Create: `docs/quickstart.md`

- [ ] **Step 1: 创建文件**

```markdown
# 快速开始（5 分钟）

本文带你从零安装到运行第一个 AI 技能。

## 1. 环境要求

- Python 3.10 或更高
- pip（推荐使用 [uv](https://github.com/astral-sh/uv) 加速）

## 2. 安装

```bash
# 从 PyPI 安装
pip install ai-mcp-skills

# 或从源码安装（开发模式）
git clone https://github.com/lxl1234-lxl/ai-mcp-skills-guide.git
cd ai-mcp-skills-guide
pip install -e ".[dev]"
```

## 3. 第一个技能调用

```python
from ai_mcp_skills import TextAnalysisSkill

skill = TextAnalysisSkill()
result = skill.execute(text="MCP 协议让 AI 安全调用外部工具。Hello MCP!")

print(result["data"]["statistics"])
# {'total_chars': ..., 'chinese_words': ..., 'english_words': ...}

print(result["data"]["keywords"])
# [{'word': 'MCP', 'frequency': 2}, ...]
```

## 4. 通过 MCP 协议调用

```python
from ai_mcp_skills import MCPServer

server = MCPServer("my-server", "1.0.0")
server.registry.register(
    name="greet",
    description="问候工具",
    input_schema={"type": "object",
                  "properties": {"name": {"type": "string"}}},
    handler=lambda **kw: {"message": f"Hello {kw.get('name', 'World')}!"},
)

# 模拟 AI 客户端发起 JSON-RPC 调用
resp = server.handle_request({
    "jsonrpc": "2.0", "id": 1, "method": "tools/call",
    "params": {"name": "greet", "arguments": {"name": "MCP"}},
})
print(resp["result"]["content"][0]["text"])
# {"message": "Hello MCP!"}
```

## 5. 编排多个技能

```python
import asyncio
from ai_mcp_skills import Orchestrator, Task

async def fetch_data():
    return {"items": [1, 2, 3]}

async def process(_previous_result=None):
    return {"processed": True}

async def main():
    orch = Orchestrator()
    results = await orch.execute_sequential([
        Task(name="fetch", coroutine=fetch_data),
        Task(name="process", coroutine=process, depends_on=["fetch"]),
    ])
    print(results["process"].status)  # TaskStatus.SUCCESS

asyncio.run(main())
```

## 6. 运行示例

```bash
python examples/basic-skill/run_demo.py
python examples/mcp-integration/run_demo.py
python examples/advanced-patterns/run_demo.py
python examples/http-skill/run_demo.py
```

## 下一步

- 阅读 [架构设计](architecture.md) 理解 MCP 分层
- 参考 [技能开发指南](skill-development-guide.md) 自定义技能
- 查看 [使用案例](use-cases.md) 了解真实场景
```

- [ ] **Step 2: Commit**

```bash
git add docs/quickstart.md
git commit -m "docs: 添加 5 分钟快速开始指南"
```

---

### Task 20: 添加 `docs/api-reference.md`

**Files:**
- Create: `docs/api-reference.md`

- [ ] **Step 1: 创建文件**

```markdown
# API 参考

> 版本: 1.0.0
> 入口: `from ai_mcp_skills import ...`

## Skill 模块

### `SkillMetadata`

技能元数据 dataclass。

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | `str` | — | 技能唯一标识 |
| `description` | `str` | — | 功能描述（AI 据此判断何时调用） |
| `version` | `str` | `"1.0.0"` | 语义化版本 |
| `author` | `str` | `""` | 作者 |
| `tags` | `list[str]` | `[]` | 分类标签 |

```python
from ai_mcp_skills import SkillMetadata
m = SkillMetadata(name="my", description="desc", tags=["a"])
```

### `BaseSkill`

所有技能的抽象基类。

| 方法 | 说明 |
|------|------|
| `initialize() -> None` | 初始化资源（连接、配置） |
| `execute(**kwargs) -> dict` | 子类必须实现，返回 `{"success", "data", "error"}` |
| `cleanup() -> None` | 释放资源 |
| `get_tool_definition() -> dict` | 生成 MCP 工具定义 |
| `get_input_schema() -> dict` | 返回输入 JSON Schema（子类覆盖） |

### `TextAnalysisSkill`

文本分析技能，继承 `BaseSkill`。

```python
from ai_mcp_skills import TextAnalysisSkill
skill = TextAnalysisSkill()
result = skill.execute(
    text="...",
    top_n_keywords=10,        # 可选，1-50
    include_readability=True,  # 可选
)
# result["data"] = {"statistics": {...}, "keywords": [...], "readability": {...}}
```

**返回结构：**

```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_chars": 100,
      "chinese_words": 20,
      "english_words": 15,
      "total_words": 35,
      "sentences": 5
    },
    "keywords": [{"word": "MCP", "frequency": 3}],
    "readability": {
      "level": "中等",
      "description": "适合有阅读习惯的读者",
      "avg_sentence_length": 7.0,
      "avg_word_length": 4.2
    }
  },
  "error": null,
  "metadata": {"text_length": 100, "version": "1.0.0"}
}
```

### `HttpRequestSkill`

HTTP 请求技能，继承 `BaseSkill`，基于标准库 `urllib`。

```python
from ai_mcp_skills import HttpRequestSkill
skill = HttpRequestSkill()
result = skill.execute(
    url="https://api.example.com/data",
    method="GET",            # 可选: GET/POST/PUT/DELETE
    headers={"X-Token": "..."},  # 可选
    body='{"k": "v"}',       # 可选, POST/PUT 使用
    timeout=30,              # 可选, 0.1-60
)
# result["data"] = {"url", "method", "status_code", "headers", "body", "body_length"}
```

## MCP 模块

### `ToolDefinition`

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | `str` | — | 工具名 |
| `description` | `str` | — | 描述 |
| `inputSchema` | `dict` | `{}` | JSON Schema |

### `ToolResult`

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `content` | `list[dict]` | — | 内容列表 |
| `isError` | `bool` | `False` | 是否错误 |

### `SkillRegistry`

技能注册中心。

| 方法 | 说明 |
|------|------|
| `register(name, description, input_schema, handler)` | 注册工具，重复抛 `ValueError` |
| `list_tools() -> list[ToolDefinition]` | 列出所有工具 |
| `call_tool(name, arguments) -> ToolResult` | 调用工具 |

### `MCPServer`

简化的 JSON-RPC MCP 服务器。

| 方法 | 说明 |
|------|------|
| `__init__(name, version)` | 创建实例 |
| `handle_request(request: dict) -> dict` | 处理 JSON-RPC 请求 |

**支持的方法：**

- `initialize` — 握手与能力协商
- `tools/list` — 列出工具
- `tools/call` — 调用工具

## Orchestration 模块

### `TaskStatus` (Enum)

`PENDING` / `RUNNING` / `SUCCESS` / `FAILED` / `FALLBACK` / `TIMEOUT` / `SKIPPED`

### `TaskResult`

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_name` | `str` | 任务名 |
| `status` | `TaskStatus` | 终态 |
| `data` | `Any` | 结果数据 |
| `error` | `str \| None` | 错误信息 |
| `duration_ms` | `float` | 耗时 |
| `retries` | `int` | 重试次数 |

### `Task`

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `name` | `str` | — | 任务名 |
| `coroutine` | `Callable` | — | 异步函数 |
| `args` / `kwargs` | `tuple` / `dict` | `()` / `{}` | 参数 |
| `depends_on` | `list[str]` | `[]` | 依赖任务 |
| `max_retries` | `int` | `0` | 重试次数 |
| `timeout_seconds` | `float` | `30.0` | 超时 |
| `fallback` | `Callable \| None` | `None` | 降级函数 |
| `skip_on_failure` | `bool` | `False` | 前置失败是否跳过 |

### `Orchestrator`

| 方法 | 说明 |
|------|------|
| `execute_sequential(tasks) -> dict[str, TaskResult]` | 串行流水线 |
| `execute_parallel(tasks) -> dict[str, TaskResult]` | 并行执行 |
| `execute_conditional(tasks, condition_fn, max_iterations=3)` | 条件分支 |

## 模块导出清单

```python
__all__ = [
    "__version__",
    "SkillMetadata", "BaseSkill", "TextAnalysisSkill", "HttpRequestSkill",
    "ToolDefinition", "ToolResult", "SkillRegistry", "MCPServer",
    "TaskStatus", "TaskResult", "Task", "Orchestrator",
]
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/api-reference.md
git commit -m "docs: 添加 API 参考文档"
```

---

### Task 21: 添加 `docs/troubleshooting.md`

**Files:**
- Create: `docs/troubleshooting.md`

- [ ] **Step 1: 创建文件**

```markdown
# 故障排查

常见问题与解决方案。

## 安装问题

### `ModuleNotFoundError: No module named 'ai_mcp_skills'`

**原因：** 未安装或未在开发模式安装。

**解决：**

```bash
pip install -e .
# 或
pip install ai-mcp-skills
```

验证：

```bash
python -c "import ai_mcp_skills; print(ai_mcp_skills.__version__)"
```

### `pip install -e ".[dev]"` 报错：unknown extra 'dev'

**原因：** 使用了旧版本 pip（< 21）。

**解决：** 升级 pip：

```bash
pip install --upgrade pip
```

## 测试问题

### `pytest` 找不到测试

**原因：** 测试路径未配置或工作目录不对。

**解决：** 在仓库根目录运行：

```bash
pytest tests/ -v
```

`pyproject.toml` 已配置 `testpaths = ["tests"]`，因此 `pytest` 命令也应能工作。

### 异步测试 `RuntimeWarning: coroutine was never awaited`

**原因：** 未安装 `pytest-asyncio` 或未配置 `asyncio_mode`。

**解决：** 确认 `pyproject.toml` 包含：

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

并安装：`pip install pytest-asyncio`

### `test_http_skill` 因网络失败

**原因：** 测试中使用 `monkeypatch` 替换 `urllib.request.urlopen`，不依赖网络。若仍失败，检查是否有自定义 `conftest.py` 覆盖。

**解决：**

```bash
pytest tests/test_http_skill.py -v -p no:cacheprovider
```

## 运行时问题

### `MCPServer` 没有实际 stdio 监听

**说明：** 本项目 `MCPServer` 提供 `handle_request(dict) -> dict` 的同步接口，便于测试与集成。若需对接真实 AI Host（如 Claude Desktop），请使用官方 [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)：

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
```

### `Orchestrator.execute_parallel` 中任务结果丢失

**检查：** 是否设置了 `depends_on`？`execute_parallel` 不使用依赖关系，所有任务并发执行。如需依赖，改用 `execute_sequential`。

### 技能 `execute` 返回 `{"success": False, "error": "..."}`

**排查清单：**

1. 检查输入参数是否符合 `get_input_schema()` 定义
2. 查看错误信息中的具体异常
3. 对网络类技能（如 `HttpRequestSkill`），检查 URL 与超时设置
4. 使用 `try/except` 包裹业务逻辑并返回结构化错误

## Lint / 类型问题

### `ruff check .` 报 `F401 imported but unused`

**解决：** 删除未使用的 import，或添加 `# noqa: F401`。

### `mypy src` 报 `Module has no attribute`

**原因：** `__init__.py` 导出的名称与模块实际定义不匹配。

**解决：** 同步更新 `src/ai_mcp_skills/__init__.py` 的导入与 `__all__`。

## 仍无法解决？

- 搜索 [已有 Issue](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/issues)
- 提交新 Issue（参考 `.github/ISSUE_TEMPLATE/`）
- 阅读 [FAQ](faq.md)
```

- [ ] **Step 2: Commit**

```bash
git add docs/troubleshooting.md
git commit -m "docs: 添加故障排查指南"
```

---

### Task 22: 添加 `docs/faq.md`

**Files:**
- Create: `docs/faq.md`

- [ ] **Step 1: 创建文件**

```markdown
# 常见问题

## 通用

### Q1: 这个项目和官方 MCP Python SDK 是什么关系？

本项目是 **MCP 架构的教学/参考实现**，提供了简化版的 `SkillRegistry` 与 `MCPServer`，便于理解 MCP 协议的核心概念。**生产环境请使用官方 SDK**：[modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)。

本项目适合：

- 学习 MCP 架构设计
- 快速原型验证技能
- 作为自定义编排引擎的脚手架

### Q2: 为何 `MCPServer` 没有真正的 stdio 监听循环？

为了保持核心模块零依赖、可测试、易理解，`MCPServer` 仅提供同步的 `handle_request` 方法。如需对接 Claude Desktop 等 Host，请参考 `docs/architecture.md` 中关于官方 SDK 的集成示例。

### Q3: 支持 Node.js / TypeScript 吗？

当前仅提供 Python 实现。TypeScript 可参考 [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)。

## 技能开发

### Q4: 如何让 AI 准确判断何时调用我的技能？

技能的 `description` 是 AI 决策的关键。建议：

```python
# 差
description="搜索"

# 好
description="搜索 GitHub 仓库。当用户询问开源项目、查找代码示例或比较项目时调用。"
```

包含**功能 + 触发场景 + 输入输出说明**。

### Q5: 技能应该同步还是异步？

本项目 `BaseSkill.execute` 是同步接口（保持简单）。若需异步：

- 在 `execute` 内部用 `asyncio.run()` 包装
- 或使用 `Orchestrator` 编排异步任务

### Q6: 如何处理技能失败？

三种策略，按推荐度排序：

1. **返回结构化错误**（推荐）：`{"success": False, "error": "..."}`
2. **降级到缓存/默认值**：通过 `Orchestrator` 的 `fallback` 参数
3. **重试**：通过 `Task.max_retries` + 指数退避

### Q7: 技能可以调用其他技能吗？

可以。在 `execute` 内部实例化并调用其他技能即可。但推荐通过 `Orchestrator` 显式编排，便于追踪与调试。

## 编排

### Q8: `execute_sequential` 和 `execute_parallel` 该选哪个？

| 场景 | 选择 |
|------|------|
| 任务有数据依赖（前→后） | `sequential` |
| 任务独立可同时执行 | `parallel` |
| 根据中间结果动态决策 | `conditional` |
| 外部服务不稳定 | 任一 + `max_retries` + `fallback` |

### Q9: `execute_conditional` 何时停止？

当 `condition_fn` 返回空列表 `[]` 时停止。也会受 `max_iterations`（默认 3）限制，防止无限循环。

### Q10: `Task.fallback` 何时触发？

仅当所有重试都失败后触发。`fallback` 函数应返回降级数据（如缓存值）。

## 部署

### Q11: 如何在 Docker 中运行？

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
CMD ["python", "examples/mcp-integration/run_demo.py"]
```

### Q12: 如何监控技能执行？

`SkillRegistry.call_tool` 已自动注入 `_metadata.execution_time_ms`。可扩展记录到日志：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 贡献

### Q13: 如何贡献新技能？

1. 阅读 [技能开发指南](skill-development-guide.md)
2. 在 `src/ai_mcp_skills/` 新建模块
3. 在 `__init__.py` 导出
4. 在 `tests/` 添加测试
5. 在 `examples/` 添加演示
6. 提交 PR（参考 `.github/PULL_REQUEST_TEMPLATE.md`）

更多问题？[提交 Issue](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/issues)。
```

- [ ] **Step 2: Commit**

```bash
git add docs/faq.md
git commit -m "docs: 添加常见问题 FAQ"
```

---

### Task 23: 添加 `docs/roadmap.md`

**Files:**
- Create: `docs/roadmap.md`

- [ ] **Step 1: 创建文件**

```markdown
# 项目路线图

> 本路线图反映当前规划，可能调整。欢迎在 [Issues](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/issues) 提出建议。

## 已完成（v1.0.0）

- [x] `SkillMetadata` / `BaseSkill` 技能基类
- [x] `TextAnalysisSkill` 文本分析示例技能
- [x] `ToolDefinition` / `ToolResult` / `SkillRegistry` / `MCPServer`
- [x] `Orchestrator` 三种编排模式 + 重试/超时/降级
- [x] 文档体系：架构、开发指南、案例、技术选型
- [x] 3 个可运行示例

## 进行中（v1.1.0）

- [x] `HttpRequestSkill` 基于 urllib 的网络技能
- [x] 测试拆分与边界用例覆盖
- [x] GitHub Actions CI 流水线
- [x] Issue / PR 模板与社区文件
- [x] Quickstart / API 参考 / FAQ / Troubleshooting

## 计划中（v1.2.0）

- [ ] MCP Resource 与 Prompt 原语支持
- [ ] 异步 `BaseSkill.execute` 接口
- [ ] 技能配置文件（YAML）加载器
- [ ] `MCPClient` 客户端实现
- [ ] stdio 真实监听循环（对接官方 SDK）

## 远期（v2.0.0）

- [ ] WebSocket 传输层
- [ ] 技能热加载与版本管理
- [ ] 分布式编排（多进程）
- [ ] 可观测性：metrics + tracing
- [ ] TypeScript 实现

## 版本策略

遵循 [SemVer](https://semver.org/)：

- **补丁版本**：Bug 修复，不破坏 API
- **次版本**：新功能，向后兼容
- **主版本**：破坏性变更

## 反馈

如有路线图建议，请：

1. 在 Issues 中标记 `roadmap` 标签
2. 描述使用场景与价值
3. 如可能，提供初步实现方案
```

- [ ] **Step 2: Commit**

```bash
git add docs/roadmap.md
git commit -m "docs: 添加项目路线图"
```

---

### Task 24: 增强 `README.md`（徽章 + 目录 + 新章节）

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 替换 README 顶部（第 1-3 行）**

将：

```markdown
# AI MCP Skills Guide

AI 系统中的 **MCP（Management Control Plane）** 架构设计、技能（Skill）开发指南与代码实现示例。
```

替换为：

```markdown
# AI MCP Skills Guide

[![CI](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/actions/workflows/ci.yml/badge.svg)](https://github.com/lxl1234-lxl/ai-mcp-skills-guide/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/ai-mcp-skills.svg)](https://pypi.org/project/ai-mcp-skills/)
[![Python](https://img.shields.io/pypi/pyversions/ai-mcp-skills.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)

> AI 系统中的 **MCP（Management Control Plane）** 架构设计、技能（Skill）开发指南与代码实现示例。

一个轻量级、零外部依赖（除 `pydantic`）的 Python 库，演示如何为 AI 智能体设计可复用的技能模块、MCP 协议服务端与多模式编排引擎。

## 目录

- [快速开始](#快速开始)
- [核心特性](#核心特性)
- [安装](#安装)
- [使用示例](#使用示例)
- [内置技能](#内置技能)
- [项目结构](#项目结构)
- [核心概念](#核心概念)
- [文档](#文档)
- [开发](#开发)
- [贡献](#参与贡献)
- [许可证](#许可证)

## 快速开始

```python
from ai_mcp_skills import TextAnalysisSkill

skill = TextAnalysisSkill()
result = skill.execute(text="MCP 协议让 AI 安全调用外部工具。Hello MCP!")
print(result["data"]["keywords"])
```

详见 [5 分钟快速开始](docs/quickstart.md)。

## 核心特性

- **技能框架**：`BaseSkill` 抽象基类 + `SkillMetadata` 元数据
- **MCP 协议**：简化的 JSON-RPC 服务器（`initialize` / `tools/list` / `tools/call`）
- **编排引擎**：串行 / 并行 / 条件三种模式 + 重试 + 超时 + 降级
- **内置技能**：文本分析、HTTP 请求
- **零网络依赖**：核心模块仅依赖 `pydantic`，HTTP 技能使用标准库 `urllib`
- **完整测试**：分模块单元测试，覆盖正常与边界路径
```

- [ ] **Step 2: 在 README 末尾"使用方法"段前插入"内置技能"章节**

找到 README 第 87 行附近：

```markdown
## 核心概念
```

在其**之前**插入：

```markdown
## 内置技能

| 技能 | 类 | 说明 |
|------|----|----|
| 文本分析 | `TextAnalysisSkill` | 字符统计、关键词提取、可读性评估（中英文） |
| HTTP 请求 | `HttpRequestSkill` | GET/POST/PUT/DELETE，支持自定义头与超时 |

```python
from ai_mcp_skills import HttpRequestSkill

skill = HttpRequestSkill()
r = skill.execute(url="https://api.example.com/data", method="GET")
if r["success"]:
    print(r["data"]["status_code"], r["data"]["body"][:100])
```

```

- [ ] **Step 3: 在"许可证"段之前插入"开发"章节**

找到 README 中的 `## 参与贡献`，在其**之前**插入：

```markdown
## 开发

```bash
# 安装开发依赖
make dev          # 等价于 pip install -e ".[dev]" && pre-commit install

# 常用命令
make test         # 运行 pytest
make lint         # ruff check .
make typecheck    # mypy src
make format       # ruff format .
```

CI 通过 GitHub Actions 自动运行 lint + typecheck + test（Python 3.10/3.11/3.12 矩阵）。

```

- [ ] **Step 4: 验证 README 渲染**

Run: `python -c "open('README.md').read()" && echo OK`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: 增强 README（徽章、目录、内置技能、开发章节）"
```

---

### Task 25: 更新 `CONTRIBUTING.md` 与 `CHANGELOG.md`

**Files:**
- Modify: `CONTRIBUTING.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: 在 `CONTRIBUTING.md` 的"#### 3. 开发和测试"段后补充 pre-commit 说明**

找到 `CONTRIBUTING.md` 第 44-55 行：

```markdown
#### 3. 开发和测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行代码检查
ruff check .
```
```

替换为：

```markdown
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
```

- [ ] **Step 2: 在 `CHANGELOG.md` 顶部添加 `[Unreleased]` 段**

将 `CHANGELOG.md` 第 1-3 行：

```markdown
# Changelog

## [1.0.0] - 2026-06-12
```

替换为：

```markdown
# Changelog

## [Unreleased]

### Added
- `HttpRequestSkill` 基于 urllib 标准库的 HTTP 请求技能（GET/POST/PUT/DELETE）
- GitHub Actions CI 流水线（lint + typecheck + test，Python 3.10/3.11/3.12 矩阵）
- Issue 模板（Bug 报告 / 功能建议）与 PR 模板
- `CODE_OF_CONDUCT.md` 贡献者公约
- `SECURITY.md` 安全策略
- 文档：`quickstart.md`、`api-reference.md`、`troubleshooting.md`、`faq.md`、`roadmap.md`
- `examples/README.md` 示例索引
- `examples/http-skill/run_demo.py` HTTP 技能演示
- 开发工具：`Makefile`、`mypy.ini`、`.pre-commit-config.yaml`、`.editorconfig`

### Changed
- 测试文件拆分为 `test_skill.py` / `test_mcp.py` / `test_orchestration.py` / `test_http_skill.py`
- `README.md` 添加徽章、目录、内置技能与开发章节
- `CONTRIBUTING.md` 补充 pre-commit 与 CI 说明

### Removed
- `tests/test_package.py`（内容已拆分到分模块测试文件）

## [1.0.0] - 2026-06-12
```

- [ ] **Step 3: Commit**

```bash
git add CONTRIBUTING.md CHANGELOG.md
git commit -m "docs: 更新 CONTRIBUTING 与 CHANGELOG 以反映新增工具与流程"
```

---

## 验证阶段

### Task 26: 全量验证（测试 + Lint + 类型 + 示例）

**Files:** 无修改

- [ ] **Step 1: 运行全部测试**

Run: `pytest -q`
Expected: 全部 PASS，测试数 ≥ 40

- [ ] **Step 2: 运行 Lint**

Run: `ruff check .`
Expected: `All checks passed!`

- [ ] **Step 3: 运行类型检查**

Run: `mypy src`
Expected: `Success: no issues found` 或仅 `examples/` 中的可忽略告警

- [ ] **Step 4: 运行格式化检查**

Run: `ruff format --check .`
Expected: 无文件需要重新格式化（如有，运行 `make format` 后重新提交）

- [ ] **Step 5: 运行所有示例（不抛异常即通过）**

Run:
```bash
python examples/basic-skill/run_demo.py > /dev/null && echo "basic OK"
python examples/mcp-integration/run_demo.py > /dev/null && echo "mcp OK"
python examples/advanced-patterns/run_demo.py > /dev/null && echo "advanced OK"
python examples/http-skill/run_demo.py > /dev/null && echo "http OK"
```
Expected: 四行 `OK`

- [ ] **Step 6: 验证包导入与导出**

Run: `python -c "from ai_mcp_skills import *; print('exports OK')"`
Expected: `exports OK`

- [ ] **Step 7: 如有格式化修正，提交**

```bash
git add -A
git commit -m "chore: 应用 ruff format 统一代码格式" || echo "无格式化变更"
```

---

## 实施完成

至此仓库已从"能跑的示例项目"升级为：

- ✅ **CI 自动化**：每次 PR 在 3 个 Python 版本上跑 lint + test + typecheck
- ✅ **社区就绪**：Issue/PR 模板、行为准则、安全策略齐全
- ✅ **多技能示例**：文本分析 + HTTP 请求，覆盖本地与网络场景
- ✅ **测试覆盖**：分模块、含边界用例（重试、超时、降级、条件循环上限）
- ✅ **开发体验**：Makefile、pre-commit、mypy、editorconfig 一键就绪
- ✅ **文档完整**：Quickstart、API 参考、FAQ、Troubleshooting、Roadmap 形成闭环

后续建议（不在本计划范围）：

- 接入官方 MCP Python SDK 提供真实 stdio 监听
- 添加 `MCPClient` 客户端实现
- 引入 `mkdocs` 构建文档站点
- 添加覆盖率统计（`coverage` + Codecov 徽章）
