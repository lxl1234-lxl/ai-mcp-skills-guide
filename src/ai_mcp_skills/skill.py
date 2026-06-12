"""
技能核心模块 - 技能元数据定义与基础技能类

提供:
- SkillMetadata: 技能元数据（名称、描述、版本、标签）
- BaseSkill: 所有技能的抽象基类
- TextAnalysisSkill: 文本分析技能（示例实现）
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillMetadata:
    """技能元数据 - 定义技能的基本信息

    Attributes:
        name: 技能唯一标识，用于 MCP 工具发现和调用
        description: 功能描述，AI 据此判断何时调用此技能
        version: 语义化版本号 (SemVer)
        author: 作者信息
        tags: 分类标签，便于技能发现和分组
    """

    name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    tags: list[str] = field(default_factory=list)


class BaseSkill:
    """所有技能的抽象基类

    定义技能的标准生命周期:
        initialize() -> execute() -> cleanup()

    子类必须实现 execute() 方法。
    """

    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata
        self._initialized = False

    def initialize(self) -> None:
        """初始化技能资源

        在首次调用 execute() 前执行。
        可用于建立数据库连接、加载配置、预热缓存等。
        """
        self._initialized = True

    def execute(self, **kwargs) -> dict[str, Any]:
        """执行技能核心逻辑

        Args:
            **kwargs: 技能所需的输入参数

        Returns:
            结构化结果字典: {"success": bool, "data": Any, "error": str|None}

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现 execute 方法")

    def cleanup(self) -> None:
        """释放技能占用的资源（连接、内存等）"""
        self._initialized = False

    def get_tool_definition(self) -> dict:
        """生成 MCP 协议的工具定义

        返回标准格式，包含名称、描述、输入 schema，
        供 AI 智能体发现和调用。

        Returns:
            MCP Tool 定义字典
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

        子类应覆盖此方法以定义具体参数约束。
        """
        return {"type": "object", "properties": {}}


class TextAnalysisSkill(BaseSkill):
    """文本分析技能

    对输入文本执行多维分析:
    - 基础统计：字符数、单词数、句子数
    - 关键词提取：基于词频过滤停用词的 Top-N 关键词
    - 可读性评估：基于平均句长和词长的可读性评分
    """

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
            description="分析文本内容，返回字数统计、关键词提取和可读性评分",
            version="1.0.0",
            tags=["text", "analysis", "nlp"],
        ))

    def get_input_schema(self) -> dict:
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
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10,
                    "description": "返回的关键词数量",
                },
                "include_readability": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否计算可读性评分",
                },
            },
            "required": ["text"],
        }

    def execute(
        self, text: str, top_n_keywords: int = 10,
        include_readability: bool = True,
    ) -> dict[str, Any]:
        """执行文本分析

        Args:
            text: 输入文本
            top_n_keywords: 返回关键词数量 (1-50)
            include_readability: 是否包含可读性分析

        Returns:
            包含统计、关键词和可读性评估的结果字典
        """
        if not text or not text.strip():
            return {"success": False, "data": None, "error": "输入文本不能为空"}

        try:
            stats = self._calculate_stats(text)
            keywords = self._extract_keywords(text, top_n_keywords)
            readability = self._assess_readability(text, stats) if include_readability else None

            return {
                "success": True,
                "data": {
                    "statistics": stats,
                    "keywords": keywords,
                    "readability": readability,
                },
                "error": None,
                "metadata": {
                    "text_length": len(text),
                    "version": self.metadata.version,
                },
            }
        except Exception as e:
            return {"success": False, "data": None, "error": f"分析失败: {str(e)}"}

    def _calculate_stats(self, text: str) -> dict:
        clean = text.strip()
        words_cn = len(re.findall(r'[\u4e00-\u9fff]', clean))
        words_en = len(re.findall(r'[a-zA-Z]+', clean))
        sentences = max(len(re.findall(r'[。！？.!?\n]+', clean)), 1)
        return {
            "total_chars": len(clean),
            "chars_no_spaces": len(clean.replace(" ", "").replace("\n", "")),
            "chinese_words": words_cn,
            "english_words": words_en,
            "total_words": words_cn + words_en,
            "sentences": sentences,
            "paragraphs": len([p for p in clean.split("\n") if p.strip()]),
        }

    def _extract_keywords(self, text: str, top_n: int) -> list[dict]:
        cn_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        en_words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        all_words = [w for w in cn_words + en_words
                     if w.lower() not in self.STOP_WORDS]
        word_freq = Counter(all_words)
        return [
            {"word": word, "frequency": freq}
            for word, freq in word_freq.most_common(top_n)
        ]

    def _assess_readability(self, text: str, stats: dict) -> dict:
        tw = stats["total_words"]
        if tw == 0:
            return {"score": 0, "level": "N/A", "description": "无文本内容"}
        avg_sl = tw / stats["sentences"]
        en_words = re.findall(r'[a-zA-Z]+', text)
        avg_wl = sum(len(w) for w in en_words) / len(en_words) if en_words else 0

        if avg_sl < 10:
            level, desc = "非常简单", "适合儿童阅读"
        elif avg_sl < 20:
            level, desc = "简单", "适合普通读者"
        elif avg_sl < 30:
            level, desc = "中等", "适合有阅读习惯的读者"
        else:
            level, desc = "复杂", "适合专业读者"

        return {
            "level": level,
            "description": desc,
            "avg_sentence_length": round(avg_sl, 1),
            "avg_word_length": round(avg_wl, 1),
        }
