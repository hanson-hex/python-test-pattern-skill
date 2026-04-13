# HTTP Mock 测试模式

## 模式概述

测试需要调用外部 HTTP API 的代码时使用此模式。

## 按 HTTP 库分类的 Mock 模式

不同 HTTP 库需要不同的 mock 类：

### 1. aiohttp

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class MockAiohttpResponse:
    """Mock aiohttp ClientResponse."""

    def __init__(self, status=200, json_data=None, text="", content=b""):
        self.status = status
        self._json = json_data or {}
        self._text = text
        self._content = content

    async def json(self):
        return self._json

    async def text(self):
        return self._text

    async def read(self):
        return self._content

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class MockAiohttpSession:
    """Mock aiohttp ClientSession."""

    def __init__(self):
        self._responses = {}
        self._calls = []

    def add_response(self, url_pattern, response):
        self._responses[url_pattern] = response

    def get(self, url, **kwargs):
        self._calls.append({"method": "GET", "url": url})
        for pattern, resp in self._responses.items():
            if pattern in url:
                return resp
        return MockAiohttpResponse(status=404)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass
```

### 2. httpx

```python
class MockHttpxResponse:
    """Mock httpx Response."""

    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self._text = text

    def json(self):
        return self._json

    def read(self):
        return self._text.encode()


class MockHttpxClient:
    """Mock httpx AsyncClient."""

    def __init__(self):
        self._expectations = []

    def expect_post(self, url=None, response_status=200, response_json=None):
        self._expectations.append({
            "method": "POST",
            "url": url,
            "response": MockHttpxResponse(
                status_code=response_status,
                json_data=response_json
            ),
        })

    async def post(self, url, **kwargs):
        for exp in self._expectations:
            if exp["method"] == "POST" and (exp["url"] is None or exp["url"] in url):
                return exp["response"]
        return MockHttpxResponse(status_code=404)
```

### 3. requests（同步 HTTP）

```python
class MockRequestsResponse:
    """Mock requests Response."""

    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json


# Usage with patch
from unittest.mock import patch

def test_sync_api_call():
    mock_resp = MockRequestsResponse(status_code=200, json_data={"success": True})
    with patch("requests.get", return_value=mock_resp):
        result = fetch_data_sync()
    assert result is True
```

## 基本 HTTP Mock（通用）

使用技能提供的通用 fixtures：

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
class Test{class_name}HTTP:
    """测试 HTTP 调用"""

    async def test_{api_call}_success(
        self,
        instance,
        mock_http_response,  # 来自 skill fixtures
    ):
        """测试 API 调用成功"""
        # 创建 mock 响应
        mock_resp = mock_http_response(
            status=200,
            json_data={"success": True, "data": "result"},
        )

        # 创建 mock session
        mock_session = MagicMock()
        mock_session.post = AsyncMock(return_value=mock_resp)

        # 注入 mock
        instance._http = mock_session

        # 执行测试
        result = await instance.{method}()

        # 验证结果
        assert result is True
        mock_session.post.assert_called_once()
```

## 多个顺序请求

```python
async def test_{method}_multiple_requests(self, instance, mock_http_response):
    """测试多个顺序 HTTP 请求"""

    # 创建多个 mock 响应
    token_response = mock_http_response(
        status=200,
        json_data={"token": "abc123"},
    )
    api_response = mock_http_response(
        status=200,
        json_data={"result": "success"},
    )

    # 配置 mock session 按顺序返回
    mock_session = MagicMock()
    mock_session.post = AsyncMock(side_effect=[token_response, api_response])

    instance._http = mock_session
    result = await instance.{method}()

    assert result is True
    assert mock_session.post.call_count == 2
```

## 错误响应处理

```python
async def test_{method}_handles_api_error(self, instance, mock_http_response):
    """测试处理 API 错误响应"""

    # 模拟 API 返回错误（HTTP 200 但业务错误）
    error_response = mock_http_response(
        status=200,
        json_data={"errcode": 40001, "errmsg": "invalid"},
    )

    mock_session = MagicMock()
    mock_session.post = AsyncMock(return_value=error_response)
    instance._http = mock_session

    result = await instance.{method}()

    # 验证错误处理
    assert result is False  # 或断言抛出异常


async def test_{method}_handles_http_error(self, instance, mock_http_response):
    """测试处理 HTTP 5xx 错误"""

    error_response = mock_http_response(
        status=500,
        text_data="Internal Server Error",
    )

    mock_session = MagicMock()
    mock_session.post = AsyncMock(return_value=error_response)
    instance._http = mock_session

    result = await instance.{method}()

    assert result is False
```

## 验证请求参数

```python
async def test_{method}_with_correct_params(self, instance, mock_http_response):
    """测试使用正确的参数调用 API"""

    mock_resp = mock_http_response(status=200, json_data={})
    mock_session = MagicMock()
    mock_session.post = AsyncMock(return_value=mock_resp)
    instance._http = mock_session

    await instance.send_message("user123", "Hello")

    # 验证调用参数
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "https://api.example.com/send"
    assert "user123" in str(call_args)
```

## 高级 HTTP Mock

如果你的项目需要更复杂的 HTTP mock（如请求/响应匹配、自动验证等），
建议在你的项目中创建自己的 MockHttpSession：

```python
# 在你的项目中: tests/fixtures/http_mock.py

class MockHttpResponse:
    """Mock HTTP response matching your HTTP client interface."""

    def __init__(self, status=200, json_data=None, text=""):
        self.status = status
        self._json = json_data or {}
        self._text = text

    async def json(self):
        return self._json

    async def text(self):
        return self._text


class MockHttpSession:
    """
    Advanced HTTP mock with request/response matching.
    Customize based on your HTTP client (aiohttp, requests, httpx).
    """

    def __init__(self):
        self._expectations = []
        self._calls = []

    def expect_post(self, url=None, response_status=200, response_json=None):
        """Expect a POST request."""
        self._expectations.append({
            "method": "POST",
            "url": url,
            "response": MockHttpResponse(status=response_status, json_data=response_json),
        })

    async def post(self, url, **kwargs):
        self._calls.append({"method": "POST", "url": url})
        return self._find_response("POST", url)

    def _find_response(self, method, url):
        for exp in self._expectations:
            if exp["method"] == method:
                if exp["url"] is None or exp["url"] in url:
                    return exp["response"]
        return MockHttpResponse(status=404)

    @property
    def call_count(self):
        return len(self._calls)
```

参考 `patterns/project_specific_fixtures.md` 获取更多指导。
