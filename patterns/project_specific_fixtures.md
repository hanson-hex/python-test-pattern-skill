# 项目特定 Fixtures 扩展指南

本 skill 提供通用的 Python 测试 fixtures (`fixtures/generic_fixtures.py`)。

**建议**：将项目特定的 fixtures 放在您项目的 `tests/conftest.py` 或 `tests/fixtures/` 目录中。

## 如何扩展

### 方法 1：直接引用通用 fixtures

```python
# tests/conftest.py
import pytest
from fixtures.generic_fixtures import (
    mock_async_context_manager,
    mock_http_response,
    call_counter,
)

# 直接使用或 alias
@pytest.fixture
def http_response(mock_http_response):
    """Alias for mock_http_response."""
    return mock_http_response
```

### 方法 2：创建项目特定的 fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock

# 为项目特定类创建的 fixtures
@pytest.fixture
def mock_process():
    """
    Mock process handler for YOUR_PROJECT.

    Adjust this to match your process handler signature.
    """
    async def _mock_handler(*args, **kwargs):
        mock_event = MagicMock()
        mock_event.object = "message"
        mock_event.status = "completed"
        yield mock_event

    return AsyncMock(side_effect=_mock_handler)


@pytest.fixture
def temp_project_dir(tmp_path):
    """
    Temporary directory with YOUR_PROJECT structure.
    """
    from pathlib import Path
    project_dir = tmp_path / ".your_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir
```

### 方法 3：HTTP Mock 扩展

如果你的项目使用 HTTP 调用，参考此模式创建 HTTP mock：

```python
# tests/fixtures/mock_http.py

class MockHttpResponse:
    """Mock HTTP response - implement based on your HTTP client."""

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
    Mock HTTP session for testing.
    Customize based on your HTTP client (aiohttp, requests, httpx).
    """

    def __init__(self):
        self._responses = []
        self._calls = []

    def expect_post(self, url=None, response_status=200, response_json=None):
        """Expect a POST request."""
        self._responses.append({
            "method": "POST",
            "url": url,
            "response": MockHttpResponse(
                status=response_status,
                json_data=response_json
            ),
        })

    async def post(self, url, **kwargs):
        self._calls.append({"method": "POST", "url": url})
        return self._find_response("POST", url)

    def _find_response(self, method, url):
        for resp in self._responses:
            if resp["method"] == method and (resp["url"] is None or resp["url"] in url):
                return resp["response"]
        return MockHttpResponse(status=404)

    @property
    def call_count(self):
        return len(self._calls)
```

## 推荐的项目结构

```
your_project/
├── src/
│   └── your_package/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # 项目级别的 fixtures
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── mock_http.py     # HTTP 相关的 mock
│   └── unit/
│       └── test_module.py
```

## 关键原则

1. **通用性优先**：Skill 只包含通用的、不绑定项目的 fixtures
2. **项目扩展**：项目自己在 tests/conftest.py 中定义特定 fixtures
3. **文档清晰**: 每个 fixture 都要有清晰的 docstring 和使用示例
4. **按需使用**：不要为了 fixture 而 fixture，简单场景可以直接在测试中 mock
