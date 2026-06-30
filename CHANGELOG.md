# Changelog

## [Unreleased]

## [1.1.0] - 2026-06-30

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
- PyPI 自动发布 workflow（基于 Trusted Publishers，tag 推送触发）

### Changed
- 测试文件拆分为 `test_skill.py` / `test_mcp.py` / `test_orchestration.py` / `test_http_skill.py`
- `README.md` 添加徽章、目录、内置技能与开发章节
- `CONTRIBUTING.md` 补充 pre-commit 与 CI 说明

### Removed
- `tests/test_package.py`（内容已拆分到分模块测试文件）

## [1.0.0] - 2026-06-12

### Added
- `ai_mcp_skills` Python 包，支持 `pip install` 安装
- `SkillMetadata` 和 `BaseSkill` 技能基类
- `TextAnalysisSkill` 文本分析技能（含关键词提取、可读性评估）
- `ToolDefinition` 和 `ToolResult` MCP 协议数据结构
- `SkillRegistry` 技能注册中心（工具注册/发现/调用）
- `MCPServer` 简化 MCP 协议服务器（JSON-RPC 处理）
- `Orchestrator` 编排引擎，支持串行/并行/条件三种模式
- 重试机制（指数退避）、超时控制、降级策略
- 3 个可运行的示例程序 (`run_demo.py`)
- 完整的文档体系（架构/开发指南/案例/技术选型）
