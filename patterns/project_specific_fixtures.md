# Project-specific Fixtures Extension Guide

This skill provides generic Python test fixtures (`fixtures/generic_fixtures.py`).

**Recommendation**: put project-specific fixtures in your project's `tests/conftest.py` or `tests/fixtures/` directory.

## How to Extend

### Method 1: Reference generic fixtures directly

```python
# tests/conftest.py
import pytest
from fixtures.generic_fixtures import (
    mock_async_context_manager,
    mock_http_response,
    call_counter,
)

# Use directly or create aliases
@pytest.fixture
def http_response(mock_http_response):
    """Alias for mock_http_response."""
    return mock_http_response
```

### Method 2: Create project-specific fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock

# Fixtures created for project-specific classes
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

### Method 3: HTTP Mock Extension

If your project makes HTTP calls, create an HTTP mock following this pattern:

```python
# tests/fixtures/mock_http.py

class MockHttpResponse:
    """Mock HTTP response — implement based on your HTTP client."""

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

## Recommended Project Structure

```
your_project/
├── src/
│   └── your_package/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # project-level fixtures
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── mock_http.py     # HTTP-related mocks
│   └── unit/
│       └── test_module.py
```

## Key Principles

1. **Generic first**: the skill only includes generic, project-agnostic fixtures
2. **Project extension**: projects define their own fixtures in `tests/conftest.py`
3. **Clear documentation**: every fixture should have a clear docstring and usage example
4. **Use only what you need**: don't create fixtures for their own sake — simple cases can mock inline
