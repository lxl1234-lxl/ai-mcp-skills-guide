# Changelog

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
