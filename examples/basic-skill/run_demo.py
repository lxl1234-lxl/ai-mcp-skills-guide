"""
基础技能示例：文本分析技能

演示如何使用 ai_mcp_skills 包创建和运行技能。
运行前需安装包: pip install -e .

运行方式:
    python examples/basic-skill/run_demo.py
"""

from ai_mcp_skills import TextAnalysisSkill


def main():
    """演示技能的完整使用流程"""
    # 1. 创建技能实例
    skill = TextAnalysisSkill()

    # 2. 初始化
    skill.initialize()

    # 3. 查看工具定义（AI 可见的接口描述）
    print("=" * 50)
    tool_def = skill.get_tool_definition()
    print(f"工具名称: {tool_def['name']}")
    print(f"工具描述: {tool_def['description']}")
    print(f"标签:     {tool_def['tags']}")

    # 4. 执行分析
    print("\n" + "=" * 50)
    print("执行文本分析...\n")

    sample_text = """
    人工智能技术正在深刻改变软件开发的方式。
    MCP 协议让 AI 智能体能够安全地与外部工具交互。
    通过技能（Skill）模块化设计，开发者可以轻松扩展 AI 的能力边界。
    The MCP protocol enables AI agents to interact with external tools securely.
    Skill-based modular design makes AI extensibility straightforward.
    """

    result = skill.execute(text=sample_text, top_n_keywords=5, include_readability=True)

    if result["success"]:
        data = result["data"]
        stats = data["statistics"]
        print(f"文本统计:")
        print(f"  总字符数: {stats['total_chars']}")
        print(f"  中文词数: {stats['chinese_words']}")
        print(f"  英文词数: {stats['english_words']}")
        print(f"  总词数:   {stats['total_words']}")
        print(f"  句子数:   {stats['sentences']}")

        print(f"\n关键词 (Top-5):")
        for kw in data["keywords"]:
            bar = "█" * kw["frequency"]
            print(f"  {kw['word']:<12} {bar} ({kw['frequency']})")

        if data["readability"]:
            r = data["readability"]
            print(f"\n可读性评估:")
            print(f"  等级:     {r['level']}")
            print(f"  说明:     {r['description']}")
            print(f"  平均句长: {r['avg_sentence_length']} 词/句")
            print(f"  平均词长: {r['avg_word_length']} 字符/词")
    else:
        print(f"分析失败: {result['error']}")

    # 5. 清理
    skill.cleanup()
    print(f"\n{'=' * 50}")
    print("演示完成！")


if __name__ == "__main__":
    main()
