"""AI MCP Skills - AI 系统中 MCP 架构的技能开发框架

提供:
- 技能定义基类和元数据
- MCP 服务端实现（工具注册、调用路由）
- 多模式编排引擎（串行/并行/条件/重试降级）
"""

__version__ = "1.0.0"

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
