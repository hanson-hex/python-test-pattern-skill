---
name: python-test-pattern
description: Python testing skill that analyzes source code and auto-generates unit tests. Supports pytest/unittest, mock, async testing, HTTP/WebSocket mock.
version: 0.3.0
---

# Python Test Generator

Intelligently analyzes Python source code and generates high-quality unit tests.

## When to Activate

- Generate unit tests: when new features/modules need test coverage
- Improve test coverage: when existing tests are insufficient
- Review test quality: when checking whether current tests are complete

## Workflow

### Step 1: Analyze Source Structure

Identify characteristics of the code under test:

```
1. Read source file, identify:
   - Class and function definitions
   - Constructor parameters and initialization logic
   - External dependencies (HTTP, database, filesystem, etc.)
   - Synchronous vs asynchronous methods
   - Factory methods (from_env, from_config)

2. Determine test strategy:
   - Simple functions → direct assertion tests
   - External dependencies → mock isolation tests
   - HTTP calls → HTTP mock tests
   - WebSocket → async mock tests
   - File operations → temp file fixture
```

### Step 2: Select Test Pattern

| Code Characteristic | Pattern Reference |
|---------------------|-------------------|
| Sync functions/classes | sync_unit_test.md |
| Async methods | async_unit_test.md |
| HTTP dependencies | http_mock.md |
| WebSocket | websocket_test.md |
| Callbacks | async_unit_test.md |
| Factory methods | sync_unit_test.md |
| Complex methods (multi-branch/multi-step) | complex_method_test.md |
| Exception paths/error handling | exception_test.md |
| Missing third-party libs | third_party_mock.md |

### Step 3: Generate Test Code

Generate tests following the AAA pattern (Arrange-Act-Assert):

```python
# 1. Arrange: prepare test data and mocks
@pytest.fixture
def instance():
    """Create {Class} instance."""
    return {Class}(...)

# 2. Act: execute the code under test
result = instance.method()

# 3. Assert: verify the result
assert result == expected
```

### Step 4: Cover Boundary Conditions

Add boundary tests for each test method:

| Boundary Type | Test Case |
|---------------|-----------|
| Null/None | test_{method}_with_none |
| Empty list/string | test_{method}_with_empty |
| Invalid input | test_{method}_invalid_input_raises |
| Extreme values | test_{method}_max_length |
| Disabled state | test_{method}_when_disabled |

## Pattern Reference

| Pattern File | Use Case |
|--------------|----------|
| `patterns/sync_unit_test.md` | Sync function/class tests |
| `patterns/async_unit_test.md` | Async method tests |
| `patterns/http_mock.md` | HTTP dependency mock |
| `patterns/class_based_test.md` | Test class organization |
| `patterns/patch_patterns.md` | Patch usage guide |
| `patterns/third_party_mock.md` | Missing third-party lib mock |
| `patterns/complex_method_test.md` | Complex method tests |
| `patterns/exception_test.md` | Exception path tests |
| `patterns/websocket_test.md` | WebSocket tests |
| `patterns/test_debugging.md` | Test debugging & troubleshooting |
| `patterns/mock_best_practices.md` | Mock object best practices |

## Fixtures

The skill provides the following common fixtures (`fixtures/generic_fixtures.py`):

| Fixture | Purpose |
|---------|---------|
| `async_noop` | Async no-op function |
| `async_return_value` | Factory for async functions that return specific values |
| `mock_http_response` | HTTP response mock factory |
| `mock_http_session` | HTTP session mock |
| `temp_dir` | Temporary directory (tmp_path alias) |
| `call_counter` | Call counter |
| `event_collector` | Event collector |
| `empty_values` | Common empty values list (boundary testing) |

Project-specific fixtures should be placed in the project's `tests/conftest.py`.

## HTTP Mock

```python
# Create mock response
mock_resp = mock_http_response(
    status=200,
    json_data={"success": True}
)

# Configure mock session
mock_session = MagicMock()
mock_session.post = AsyncMock(return_value=mock_resp)

# Run the test
result = await instance.api_call()
assert result is True
mock_session.post.assert_called_once()
```

For complex HTTP mock needs, create your own MockHttpSession in the project.

## Code Quality

After generating tests, check for common issues:

| Check | Problem | Solution |
|-------|---------|----------|
| **Line length** | E501: Line too long | Use parentheses for line breaks or extract variables |
| **Duplicate imports** | W0404: Reimport | Consolidate at the top of the file |
| **Pydantic version** | Import failure in test env | Mock the entire module or avoid Pydantic |

See `patterns/code_quality_fixes.md` for details.

## FAQ

### Q1: How to handle missing third-party library dependencies?

Mock them in `tests/conftest.py`:

```python
import sys
from unittest.mock import MagicMock

# Mock missing third-party libraries
for module in ['thirdparty_sdk', 'external_api']:
    sys.modules[module] = MagicMock()
```

See `patterns/third_party_mock.md` for details.

### Q2: How to avoid pre-commit style errors?

When generating tests, ensure:

1. **Line length**: limit to 79 characters
2. **Unused variables**: delete or rename to `_`
3. **Import order**: stdlib → third-party → local
4. **Type annotations**: avoid forward references, use string quotes

Example:
```python
# ✅ Correct
def test_example(my_client):  # no type annotation needed
    pass

# ❌ Avoid
from __future__ import annotations  # usable in Python 3.7+
# but mypy may error — prefer omitting return type annotations in test functions
```

### Q3: Which HTTP mock pattern should I use?

Choose based on the HTTP library the project uses:

| Library | Mock Class |
|---------|------------|
| aiohttp | MockAiohttpSession |
| httpx | MockHttpxClient |
| requests | MockRequestsResponse |

### Q4: How should test classes be organized?

Organize by priority and functionality:

```python
class Test{ClassName}Init:          # P0: initialization
class Test{ClassName}FactoryMethods: # P0: factory methods
class Test{ClassName}CoreFeature:   # P1: core features
class Test{ClassName}Utilities:     # P2: utility methods
```

## References

### Skill Internal

- patterns/sync_unit_test.md
- patterns/async_unit_test.md
- patterns/http_mock.md
- patterns/class_based_test.md
- patterns/patch_patterns.md
- patterns/third_party_mock.md
- patterns/complex_method_test.md
- patterns/exception_test.md
- patterns/websocket_test.md
- fixtures/generic_fixtures.py

### External Docs

- pytest official docs: https://docs.pytest.org/
- unittest.mock docs: https://docs.python.org/3/library/unittest.mock.html
