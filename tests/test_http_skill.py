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
    """验证内部 _headers_to_dict 辅助方法"""
    skill = HttpRequestSkill()
    # 直接调用私有方法验证响应转换
    class FakeHeaders:
        def items(self):
            return [("Content-Type", "text/plain"), ("X-Custom", "abc")]
    d = skill._headers_to_dict(FakeHeaders())
    assert d == {"Content-Type": "text/plain", "X-Custom": "abc"}
