# HTTP Mock Test Pattern

## Overview

Use this pattern when testing code that calls external HTTP APIs.

## Mock Patterns by HTTP Library

Different HTTP libraries require different mock classes:

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

### 3. requests (synchronous HTTP)

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

## Basic HTTP Mock (Generic)

Use the common fixtures provided by the skill:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
class Test{class_name}HTTP:
    """Test HTTP calls."""

    async def test_{api_call}_success(
        self,
        instance,
        mock_http_response,  # from skill fixtures
    ):
        """Test successful API call."""
        # Create mock response
        mock_resp = mock_http_response(
            status=200,
            json_data={"success": True, "data": "result"},
        )

        # Create mock session
        mock_session = MagicMock()
        mock_session.post = AsyncMock(return_value=mock_resp)

        # Inject mock
        instance._http = mock_session

        # Execute test
        result = await instance.{method}()

        # Verify result
        assert result is True
        mock_session.post.assert_called_once()
```

## Multiple Sequential Requests

```python
async def test_{method}_multiple_requests(self, instance, mock_http_response):
    """Test multiple sequential HTTP requests."""

    # Create multiple mock responses
    token_response = mock_http_response(
        status=200,
        json_data={"token": "abc123"},
    )
    api_response = mock_http_response(
        status=200,
        json_data={"result": "success"},
    )

    # Configure mock session to return responses in order
    mock_session = MagicMock()
    mock_session.post = AsyncMock(side_effect=[token_response, api_response])

    instance._http = mock_session
    result = await instance.{method}()

    assert result is True
    assert mock_session.post.call_count == 2
```

## Error Response Handling

```python
async def test_{method}_handles_api_error(self, instance, mock_http_response):
    """Test handling of API error responses."""

    # Simulate API returning a business error (HTTP 200 but error body)
    error_response = mock_http_response(
        status=200,
        json_data={"errcode": 40001, "errmsg": "invalid"},
    )

    mock_session = MagicMock()
    mock_session.post = AsyncMock(return_value=error_response)
    instance._http = mock_session

    result = await instance.{method}()

    # Verify error handling
    assert result is False  # or assert an exception is raised


async def test_{method}_handles_http_error(self, instance, mock_http_response):
    """Test handling of HTTP 5xx errors."""

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

## Verify Request Parameters

```python
async def test_{method}_with_correct_params(self, instance, mock_http_response):
    """Test API is called with correct parameters."""

    mock_resp = mock_http_response(status=200, json_data={})
    mock_session = MagicMock()
    mock_session.post = AsyncMock(return_value=mock_resp)
    instance._http = mock_session

    await instance.send_message("user123", "Hello")

    # Verify call arguments
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "https://api.example.com/send"
    assert "user123" in str(call_args)
```

## Advanced HTTP Mock

For more complex HTTP mock needs (e.g., request/response matching, auto-validation),
create your own MockHttpSession in the project:

```python
# In your project: tests/fixtures/http_mock.py

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

See `patterns/project_specific_fixtures.md` for more guidance.
