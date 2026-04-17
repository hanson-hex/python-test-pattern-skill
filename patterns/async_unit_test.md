# Async Code Test Pattern

## Overview

Use this pattern when testing methods defined with `async def`.

## Key Rules

1. **Only use `@pytest.mark.asyncio` on async test methods**
2. **Do NOT use `pytestmark = pytest.mark.asyncio` at class or module level**
3. **Use `AsyncMock` for mocking async methods**

## Template

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


class Test{class_name}Async:
    """
    Async method test class.

    Note: Do NOT use @pytest.mark.asyncio on the class.
    Only use the decorator on individual async test methods.
    """
    
    @pytest.fixture
    def mock_process(self):
        """Create mock process handler."""
        async def mock_handler(*args, **kwargs):
            mock_event = MagicMock()
            mock_event.object = "message"
            mock_event.status = "completed"
            yield mock_event
        return AsyncMock(side_effect=mock_handler)
    
    @pytest.fixture
    def instance(self, mock_process):
        """Create {class_name} instance."""
        from {module_path} import {class_name}
        return {class_name}(process=mock_process)
    
    @pytest.mark.asyncio
    async def test_{method}_success(self, instance):
        """Test {method} executes successfully — async methods require the decorator."""
        result = await instance.{method}()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_{method}_when_disabled(self, instance):
        """Test {method} does nothing when disabled."""
        instance.enabled = False
        result = await instance.{method}()
        assert result is None
    
    def test_sync_method(self, instance):
        """Sync methods do NOT need @pytest.mark.asyncio."""
        result = instance.sync_method()
        assert result == expected
```

## ❌ Avoid Global pytestmark

```python
# ❌ Wrong: this marks all tests (including sync) as async
pytestmark = pytest.mark.asyncio

# ✅ Correct: only add the decorator to async methods
@pytest.mark.asyncio
async def test_async(): ...

def test_sync(): ...  # sync tests need no decorator
```

## AsyncMock Usage

```python
# mock async method to return a specific value
mock_async_method = AsyncMock(return_value="expected_result")

# mock async method to raise an exception
mock_async_method = AsyncMock(side_effect=Exception("error"))

# mock async generator
async def mock_generator():
    yield item1
    yield item2
mock_async_gen = AsyncMock(side_effect=mock_generator)
```

## Third-party Library Mock

When tests depend on third-party libraries (e.g., paho-mqtt):

```python
@pytest.fixture
def mock_mqtt_client():
    """Create mock for third-party library client."""
    client = MagicMock()
    client.connect = Mock()
    client.loop_start = Mock()
    client.publish = Mock()
    return client

# Usage in tests
async def test_start(self, mock_mqtt_client):
    with patch("path.to.module.mqtt.Client", return_value=mock_mqtt_client):
        await instance.start()
    
    mock_mqtt_client.connect.assert_called_once()
```

## Patch Path Notes

When patching a class that is imported inside the module under test:

```python
# Scenario: runtime import inside the module under test
# module.py
async def start():
    from external.service import ExternalService  # imported at runtime
    service = ExternalService()
    return await service.connect()

# Test
# ❌ Wrong: patch the location in the module under test
with patch("module.ExternalService"):
    ...

# ✅ Correct: patch the original import source
with patch("external.service.ExternalService") as MockService:
    mock_instance = MockService.return_value
    mock_instance.connect = AsyncMock(return_value=True)
    result = await start()
    assert result is True
```

## Logging Test Notes

**Recommendation**: prefer testing functional behavior over log output.

```python
# ✅ Recommended: test functional behavior
assert instance.connected is False

# ⚠️ Optional: test logs (depends on logging configuration)
caplog.set_level("ERROR", logger="module.name")
assert "error message" in caplog.text
```

Different projects may have different logging configurations — log assertions can make tests brittle.

## Notes

1. Never use `time.sleep` in async tests; use `asyncio.sleep` instead
2. Use `asyncio.gather` for concurrency tests
3. Use `asyncio.wait_for` for test timeouts
4. Mock objects remain set as attributes even if a method raises an exception
