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
