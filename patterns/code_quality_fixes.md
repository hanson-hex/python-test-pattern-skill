# Code Quality & Test Environment Fixes

## Issue 1: pylint E501 Line Too Long

**Symptom:**
```
E501 Line too long (88 > 79 characters)
```

**Solutions:**

### Method 1: String line continuation (Recommended)
```python
# ❌ Wrong — exceeds 79 characters
raise ValueError(f"Failed to initialize {self.__class__.__name__}: {str(e)}")

# ✅ Correct — implicit continuation inside parentheses
raise ValueError(
    f"Failed to initialize {self.__class__.__name__}: {str(e)}"
)

# ✅ Correct — triple-quoted string
error_msg = """
This is a very long error message that explains
what went wrong in detail.
"""
```

### Method 2: Split long lines
```python
# ❌ Wrong
result = self.some_method(arg1, arg2, arg3, arg4, arg5, arg6)

# ✅ Correct — one argument per line
result = self.some_method(
    arg1,
    arg2,
    arg3,
    arg4,
)
```

### Method 3: Extract variables
```python
# ❌ Wrong
assert channel.bot is not None, f"Bot is None after initialization for {channel.__class__.__name__}"

# ✅ Correct
channel_name = channel.__class__.__name__
assert channel.bot is not None, f"Bot is None after init for {channel_name}"
```

---

## Issue 2: Duplicate Import Warnings (W0404 / R0401)

**Symptom:**
```
W0404: Reimport 'MagicMock' (imported line 5)
R0401: Cyclic import
```

**Solutions:**

### Consolidate top-level imports
```python
# ✅ Correct — all imports at the top of the file
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Optional

# Use in test classes without re-importing
class TestExample:
    def test_something(self):
        mock = MagicMock()
```

### Avoid nested imports (unless necessary)
```python
# ❌ Wrong — unnecessary nested import
class TestExample:
    def test_something(self):
        from unittest.mock import MagicMock
        mock = MagicMock()

# ✅ Correct — consolidated top-level import
from unittest.mock import MagicMock

class TestExample:
    def test_something(self):
        mock = MagicMock()
```

### Special case: lazy imports in fixtures
```python
# ✅ Correct — avoids circular imports
@pytest.fixture
def mock_client():
    from myapp.client import Client
    return MagicMock(spec=Client)
```

---

## Issue 3: Pydantic Test Environment Problems

**Symptom:**
```
E0611: No name 'BaseModel' in module 'pydantic'
TypeError: Metaclass conflict when mocking Pydantic models
```

**Root cause:**
The test environment may have a different version of Pydantic (v1 vs v2), causing model imports to fail.

**Solutions:**

### Method 1: Mock the entire pydantic module
```python
# tests/conftest.py
import sys
from unittest.mock import MagicMock

# Pre-mock pydantic to avoid version conflicts
pydantic_mock = MagicMock()
pydantic_mock.BaseModel = MagicMock()
pydantic_mock.Field = MagicMock()
pydantic_mock.validator = MagicMock()
sys.modules['pydantic'] = pydantic_mock
```

### Method 2: Create a Mock Config in a fixture
```python
# ✅ Correct — no dependency on real Pydantic
@pytest.fixture
def mock_config():
    """Create a Mock Config, replacing the Pydantic model."""
    config = MagicMock()
    config.enabled = True
    config.timeout = 30
    config.api_key = "test_key"
    # Explicitly set all attributes that may be accessed
    config.host = "https://api.example.com"
    config.port = 443
    return config
```

### Method 3: Use monkeypatch to modify config
```python
# ✅ Correct — bypass Pydantic by not instantiating it
class TestChannel:
    def test_with_config(self, monkeypatch):
        # Set env vars directly to bypass Pydantic
        monkeypatch.setenv("API_KEY", "test_key")
        monkeypatch.setenv("TIMEOUT", "30")

        channel = Channel.from_env()
        assert channel.api_key == "test_key"
```

### Method 4: Conditional patch (v1/v2 compatibility)
```python
# tests/conftest.py
try:
    from pydantic import BaseModel
except ImportError:
    try:
        from pydantic.v1 import BaseModel
    except ImportError:
        BaseModel = MagicMock()

# Usage in tests
@pytest.fixture
def mock_model():
    model = MagicMock()
    model.model_dump.return_value = {"key": "value"}  # v2 style
    model.dict.return_value = {"key": "value"}         # v1 style
    return model
```

---

## Quick Checklist

After generating test code, verify the following:

```
□ Line length — all lines ≤ 79 characters
□ Import statements — only at the top of the file
□ No duplicate imports
□ Mock is complete — all accessed attributes are set
□ Async is correct — AsyncMock used for async methods
□ No Pydantic dependency — use Mock instead of real Pydantic models
```

---

## Auto-fix Commands

```bash
# Auto-format code
black tests/ --line-length 79

# Auto-sort imports
isort tests/ --profile black

# Check pylint issues
pylint tests/unit/channels/test_*.py --disable=all --enable=E501,W0404
```
