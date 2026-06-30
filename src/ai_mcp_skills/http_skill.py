"""HTTP 请求技能 - 基于 urllib 标准库

提供:
- HttpRequestSkill: 发送 HTTP/HTTPS 请求并返回结构化响应
"""

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
                # 尝试 UTF-8 解码，失败则返回二进制摘要
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
