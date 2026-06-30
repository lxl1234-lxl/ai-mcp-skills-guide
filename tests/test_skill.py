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
        name="my-skill",
        description="my desc",
        version="2.0.0",
        author="me",
        tags=["a", "b"],
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
