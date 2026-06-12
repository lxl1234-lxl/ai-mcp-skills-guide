"""
基础技能示例：文本分析技能

演示如何创建一个简单的、自包含的 MCP 技能。
该技能提供文本分析功能：单词计数、情感分析、关键词提取。

运行方式:
    python examples/basic-skill/skill.py
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


# ============================================================================
# 技能元数据定义
# ============================================================================

@dataclass
class SkillMetadata:
    """技能元数据 - 定义技能的基本信息"""
    name: str                              # 技能唯一标识
    description: str                       # 功能描述（AI 用于判断何时调用）
    version: str = "1.0.0"                # 语义化版本号
    author: str = ""                       # 作者
    tags: list[str] = field(default_factory=list)  # 分类标签


# ============================================================================
# 基础技能类
# ============================================================================

class BaseSkill:
    """所有技能的抽象基类

    定义了技能的标准生命周期：
        initialize() → execute() → cleanup()
    """

    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata
        self._initialized = False

    def initialize(self) -> None:
        """初始化技能资源

        在首次调用 execute() 前执行，用于建立数据库连接、
        加载配置、预热缓存等操作。
        """
        self._initialized = True
        print(f"[技能] {self.metadata.name} 初始化完成")

    def execute(self, **kwargs) -> dict[str, Any]:
        """执行技能核心逻辑

        Args:
            **kwargs: 技能所需的输入参数

        Returns:
            包含执行结果的字典，结构为:
            {
                "success": bool,
                "data": Any | None,
                "error": str | None,
                "metadata": dict
            }

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现 execute 方法")

    def cleanup(self) -> None:
        """释放技能占用的资源

        在技能不再需要时调用，用于关闭连接、释放内存等。
        """
        self._initialized = False
        print(f"[技能] {self.metadata.name} 已清理")

    def get_tool_definition(self) -> dict:
        """生成 MCP 工具定义

        返回标准的 MCP Tool 对象定义，包含名称、描述和输入 schema。
        AI 根据这些信息决定何时以及如何调用此技能。

        Returns:
            MCP 工具定义字典
        """
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "tags": self.metadata.tags,
            "inputSchema": self.get_input_schema(),
        }

    def get_input_schema(self) -> dict:
        """返回技能的输入参数 JSON Schema

        子类应覆盖此方法以定义具体的参数约束。
        """
        return {"type": "object", "properties": {}}


# ============================================================================
# 具体技能实现
# ============================================================================

class TextAnalysisSkill(BaseSkill):
    """文本分析技能

    对输入文本执行多维度的分析：
    - 基础统计：字符数、单词数、句子数
    - 关键词提取：基于词频的 Top-N 关键词
    - 可读性评估：基于平均句长和词长
    """

    # 常见停用词列表，在关键词提取时过滤
    STOP_WORDS = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
        "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
        "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "它",
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "can", "shall",
        "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "and", "or", "but", "not", "so", "if", "as", "than", "that",
    }

    def __init__(self):
        super().__init__(SkillMetadata(
            name="text_analysis",
            description=(
                "分析文本内容，返回字数统计、关键词提取和可读性评分。"
                "适用于需要评估文本质量、提取关键信息的场景。"
            ),
            version="1.0.0",
            tags=["text", "analysis", "nlp"],
        ))

    def get_input_schema(self) -> dict:
        """定义文本分析技能的输入参数约束"""
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "需要分析的文本内容，支持中英文",
                    "minLength": 1,
                },
                "top_n_keywords": {
                    "type": "integer",
                    "description": "返回的关键词数量",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                },
                "include_readability": {
                    "type": "boolean",
                    "description": "是否计算可读性评分",
                    "default": True,
                },
            },
            "required": ["text"],
        }

    def execute(
        self,
        text: str,
        top_n_keywords: int = 10,
        include_readability: bool = True,
    ) -> dict[str, Any]:
        """执行文本分析

        Args:
            text: 输入文本
            top_n_keywords: 返回关键词数量
            include_readability: 是否包含可读性分析

        Returns:
            分析结果字典
        """
        try:
            # 输入验证
            if not text or not text.strip():
                return {
                    "success": False,
                    "data": None,
                    "error": "输入文本不能为空",
                }

            # 1. 基础统计
            stats = self._calculate_stats(text)

            # 2. 关键词提取
            keywords = self._extract_keywords(text, top_n_keywords)

            # 3. 可读性评估（可选）
            readability = None
            if include_readability:
                readability = self._assess_readability(text, stats)

            result = {
                "success": True,
                "data": {
                    "statistics": stats,
                    "keywords": keywords,
                    "readability": readability,
                },
                "error": None,
                "metadata": {
                    "text_length": len(text),
                    "analysis_version": self.metadata.version,
                },
            }
            return result

        except Exception as e:
            # 统一的错误处理
            return {
                "success": False,
                "data": None,
                "error": f"文本分析失败: {str(e)}",
            }

    def _calculate_stats(self, text: str) -> dict:
        """计算文本基础统计指标

        Args:
            text: 输入文本

        Returns:
            统计指标字典
        """
        # 清理文本
        clean_text = text.strip()

        # 字符数（不含空格）
        chars_no_spaces = len(clean_text.replace(" ", "").replace("\n", ""))

        # 单词数（英文按空格，中文按字符）
        words_cn = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
        words_en = len(re.findall(r'[a-zA-Z]+', clean_text))

        # 句子数（基于标点符号分割）
        sentences = len(re.findall(r'[。！？.!?\n]+', clean_text))
        if sentences == 0:
            sentences = 1  # 至少算一个句子

        return {
            "total_chars": len(clean_text),
            "chars_no_spaces": chars_no_spaces,
            "chinese_words": words_cn,
            "english_words": words_en,
            "total_words": words_cn + words_en,
            "sentences": sentences,
            "paragraphs": len([p for p in clean_text.split("\n") if p.strip()]),
        }

    def _extract_keywords(self, text: str, top_n: int) -> list[dict]:
        """提取文本关键词

        使用词频统计方法，过滤停用词后提取高频词。

        Args:
            text: 输入文本
            top_n: 返回数量

        Returns:
            关键词列表，每项包含词语和频率
        """
        # 提取中文词语（2-4字组合）
        cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)

        # 提取英文单词
        en_words = re.findall(r'[a-zA-Z]{3,}', text.lower())

        # 合并并过滤停用词
        all_words = [w for w in cn_words + en_words
                     if w.lower() not in self.STOP_WORDS]

        # 统计词频
        word_freq = Counter(all_words)

        # 返回 Top-N
        return [
            {"word": word, "frequency": freq}
            for word, freq in word_freq.most_common(top_n)
        ]

    def _assess_readability(self, text: str, stats: dict) -> dict:
        """评估文本可读性

        基于平均句长和平均词长计算可读性评分。

        Args:
            text: 输入文本
            stats: 已计算的统计指标

        Returns:
            可读性评估结果
        """
        total_words = stats["total_words"]
        sentences = stats["sentences"]

        if total_words == 0:
            return {"score": 0, "level": "N/A", "description": "无文本内容"}

        # 平均句长
        avg_sentence_length = total_words / sentences

        # 平均词长（仅英文）
        en_words = re.findall(r'[a-zA-Z]+', text)
        avg_word_length = (
            sum(len(w) for w in en_words) / len(en_words)
            if en_words else 0
        )

        # 可读性等级判定
        if avg_sentence_length < 10:
            level = "非常简单"
            description = "适合儿童阅读"
        elif avg_sentence_length < 20:
            level = "简单"
            description = "适合普通读者"
        elif avg_sentence_length < 30:
            level = "中等"
            description = "适合有阅读习惯的读者"
        else:
            level = "复杂"
            description = "适合专业读者"

        return {
            "level": level,
            "description": description,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_word_length": round(avg_word_length, 1),
        }


# ============================================================================
# 演示运行
# ============================================================================

def main():
    """演示技能的完整使用流程"""
    # 1. 创建技能实例
    skill = TextAnalysisSkill()

    # 2. 初始化技能
    skill.initialize()

    # 3. 查看工具定义（AI 可见的接口描述）
    print("\n=== 工具定义（供 AI 发现） ===")
    tool_def = skill.get_tool_definition()
    print(f"名称: {tool_def['name']}")
    print(f"描述: {tool_def['description']}")
    print(f"标签: {tool_def['tags']}")

    # 4. 执行技能
    print("\n=== 执行文本分析 ===")
    sample_text = """
    人工智能技术正在深刻改变软件开发的方式。
    MCP 协议让 AI 智能体能够安全地与外部工具交互。
    通过技能（Skill）模块化设计，开发者可以轻松扩展 AI 的能力边界。
    The MCP protocol enables AI agents to interact with external tools securely.
    Skill-based modular design makes AI extensibility straightforward.
    """

    result = skill.execute(
        text=sample_text,
        top_n_keywords=5,
        include_readability=True,
    )

    # 5. 输出结果
    if result["success"]:
        data = result["data"]
        stats = data["statistics"]
        print(f"\n文本统计:")
        print(f"  总字符数: {stats['total_chars']}")
        print(f"  中文词数: {stats['chinese_words']}")
        print(f"  英文词数: {stats['english_words']}")
        print(f"  句子数:   {stats['sentences']}")

        print(f"\n关键词 (Top-5):")
        for kw in data["keywords"]:
            print(f"  {kw['word']}: {kw['frequency']}次")

        if data["readability"]:
            r = data["readability"]
            print(f"\n可读性评估:")
            print(f"  等级: {r['level']} ({r['description']})")
            print(f"  平均句长: {r['avg_sentence_length']}词/句")
    else:
        print(f"分析失败: {result['error']}")

    # 6. 清理资源
    skill.cleanup()


if __name__ == "__main__":
    main()
