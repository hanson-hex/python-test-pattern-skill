# Missing Third-party Library Mock Pattern

## Overview

Use this pattern when the code under test depends on third-party libraries that are not installed
(e.g., enterprise WeChat's `aibot`, Feishu's `lark-oapi`, etc.).

## Quick Diagnosis

If you see one of the following errors, this pattern applies:

```
ModuleNotFoundError: No module named 'xxx'
```

Or pytest fails to collect tests:

```
ERROR tests/unit/test_xxx.py - ModuleNotFoundError: No module named 'xxx'
```

## Problem Scenario

```python
# src/myapp/external/websocket_client.py
from thirdparty_sdk import WSClient, WSClientOptions  # uninstalled third-party lib

class MyClient(BaseClient):
    def start(self):
        client = WSClient()  # depends on third-party lib
```

A direct import raises `ModuleNotFoundError`.

## Solutions

### Method 1: Mock the entire module in conftest.py (Recommended)

```python
# tests/conftest.py
import sys
from unittest.mock import MagicMock

# Mock missing third-party libraries
sys.modules['thirdparty_sdk'] = MagicMock()
sys.modules['external_api'] = MagicMock()
```

### Method 2: Lazy import inside the test file

```python
# tests/unit/test_client.py
# pylint: disable=import-error
def test_init():
    from unittest.mock import patch, MagicMock

    with patch.dict('sys.modules', {'thirdparty_sdk': MagicMock()}):
        from myapp.external.websocket_client import MyClient
        client = MyClient(...)
```

### Method 3: Dynamic import inside a fixture

```python
@pytest.fixture
def client_instance(mock_handler, tmp_path):
    """Create client with mocked third-party deps."""
    with patch.dict('sys.modules', {'thirdparty_sdk': MagicMock()}):
        from myapp.external.websocket_client import MyClient
        client = MyClient(
            handler=mock_handler,
            enabled=True,
        )
        yield client
```

## Complete Example

### conftest.py Configuration

```python
# tests/conftest.py
import sys
from unittest.mock import MagicMock

# Pre-mock all missing third-party libraries
_MISSING_MODULES = {
    'thirdparty_sdk',
    'external_api',
    'proprietary_lib',
}

for module in _MISSING_MODULES:
    if module not in sys.modules:
        sys.modules[module] = MagicMock()
```

### Usage in Tests

```python
# tests/unit/test_client.py
from unittest.mock import AsyncMock, MagicMock, patch

class TestMyClient:
    def test_start_missing_credentials(self, mock_handler, tmp_path):
        """Test start fails gracefully with missing credentials."""
        from myapp.external.websocket_client import MyClient

        client = MyClient(
            handler=mock_handler,
            enabled=True,
            api_key="",
        )

        # Should not raise even though thirdparty_sdk is mocked
        result = client.start()
        assert result is None
```

## Notes

1. **Centralize in conftest.py**: avoid duplicating mock setup across test files
2. **Mock only what is used**: only mock the classes/functions actually accessed by the code under test
3. **Type annotations**: if the third-party library is used only for type annotations, use `TYPE_CHECKING`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thirdparty_sdk import WSClient  # imported only during type checking
```

## Common Scenarios

| Scenario | Library Example | Mock Suggestion |
|----------|-----------------|-----------------|
| WebSocket SDK | `websocket_sdk` | Mock Client, Connection |
| Message Queue | `mq_client` | Mock Producer, Consumer |
| AI/ML API | `ai_platform` | Mock Model, Prediction |
| Payment Gateway | `payment_sdk` | Mock Payment, Refund |
