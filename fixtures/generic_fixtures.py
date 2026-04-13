# -*- coding: utf-8 -*-
"""
Generic Python Test Fixtures

These fixtures can be used in any Python project that uses pytest.
No project-specific dependencies or assumptions.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Generator, Optional
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest


# =============================================================================
# Async Testing Fixtures
# =============================================================================


@pytest.fixture
def async_noop() -> Callable:
    """
    Create an async no-op function.

    Useful when you need to mock an async function that does nothing.

    Example:
        async def test_something(async_noop):
            instance.async_method = async_noop
            await instance.async_method()  # Does nothing, no error
    """
    async def _noop(*_args, **_kwargs) -> None:
        pass
    return _noop


@pytest.fixture
def async_return_value() -> Callable[[Any], Callable]:
    """
    Create a factory for async functions that return a specific value.

    Example:
        async def test_something(async_return_value):
            get_data = async_return_value({"key": "value"})
            result = await get_data()
            assert result == {"key": "value"}
    """
    def _factory(return_value: Any) -> Callable:
        async def _async_func(*_args, **_kwargs) -> Any:
            return return_value
        return _async_func
    return _factory


@pytest.fixture
def async_side_effects() -> Callable[[list], Callable]:
    """
    Create a factory for async generators from a list of values.

    Example:
        async def test_stream(async_side_effects):
            stream = async_side_effects([1, 2, 3])
            results = []
            async for item in stream():
                results.append(item)
            assert results == [1, 2, 3]
    """
    def _factory(items: list) -> Callable:
        async def _async_gen(*_args, **_kwargs):
            for item in items:
                yield item
        return _async_gen
    return _factory


@pytest.fixture
def mock_async_context_manager():
    """
    Create a mock async context manager.

    Example:
        async def test_with_session(mock_async_context_manager):
            mock_session = mock_async_context_manager()
            mock_session.get.return_value = MockResponse()

            async with mock_session() as session:
                response = await session.get("http://example.com")
    """
    class _AsyncContextManager:
        def __init__(self, return_value=None):
            self._return_value = return_value or MagicMock()

        async def __aenter__(self):
            return self._return_value

        async def __aexit__(self, *args):
            pass

    def _factory(return_value=None):
        return _AsyncContextManager(return_value)

    return _factory


# =============================================================================
# Directory and File Fixtures
# =============================================================================


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """
    Create a temporary directory for test files.

    The directory is automatically cleaned up after the test.
    This is just an alias for pytest's built-in tmp_path for clarity.

    Example:
        def test_file_operations(temp_dir):
            test_file = temp_dir / "test.txt"
            test_file.write_text("Hello")
            assert test_file.read_text() == "Hello"
    """
    return tmp_path


# =============================================================================
# HTTP Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_http_response():
    """
    Create a factory for HTTP response mocks.

    Example:
        async def test_api_call(mock_http_response):
            response = mock_http_response(
                status=200,
                json_data={"success": True}
            )
            assert response.status == 200
            assert await response.json() == {"success": True}
    """
    class _MockResponse:
        def __init__(
            self,
            status: int = 200,
            json_data: Optional[dict] = None,
            text_data: str = "",
            headers: Optional[dict] = None,
        ):
            self.status = status
            self._json_data = json_data or {}
            self._text_data = text_data
            self.headers = headers or {}

        async def json(self, **_kwargs) -> dict:
            return self._json_data

        async def text(self) -> str:
            return self._text_data

        async def read(self) -> bytes:
            return self._text_data.encode()

    def _factory(**kwargs) -> _MockResponse:
        return _MockResponse(**kwargs)

    return _factory


@pytest.fixture
def mock_http_session():
    """
    Create a mock HTTP session fixture.

    Simplified version - for complex scenarios, use project-specific mocks.

    Example:
        async def test_http_call(mock_http_session):
            session = mock_http_session
            session.get.return_value = MockResponse(status=200)

            response = await session.get("http://example.com")
            assert response.status == 200
    """
    session = MagicMock()
    session.get = AsyncMock()
    session.post = AsyncMock()
    session.put = AsyncMock()
    session.delete = AsyncMock()
    session.close = AsyncMock()
    return session


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def mock_config_object():
    """
    Create a generic configuration mock.

    Useful for testing classes that accept config objects.

    Example:
        def test_service(mock_config_object):
            config = mock_config_object(
                host="localhost",
                port=8080,
                enabled=True
            )
            service = MyService(config)
            assert service.host == "localhost"
    """
    def _factory(**kwargs) -> Mock:
        return Mock(**kwargs)
    return _factory


@pytest.fixture
def env_vars_cleaner(monkeypatch) -> Callable:
    """
    Create a helper to temporarily set and then clean up environment variables.

    Example:
        def test_env_config(env_vars_cleaner):
            restore = env_vars_cleaner({"API_KEY": "secret", "DEBUG": "1"})
            try:
                config = load_config()
                assert config.api_key == "secret"
            finally:
                restore()  # Clean up
    """
    def _set_vars(vars_dict: dict) -> Callable:
        original_values = {}
        for key, value in vars_dict.items():
            original_values[key] = _get_env_var(key)
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, str(value))

        def _restore():
            for key, original_value in original_values.items():
                if original_value is None:
                    monkeypatch.delenv(key, raising=False)
                else:
                    monkeypatch.setenv(key, original_value)

        return _restore

    def _get_env_var(key: str) -> Optional[str]:
        import os
        return os.environ.get(key)

    return _set_vars


# =============================================================================
# Utility Fixtures
# =============================================================================


@pytest.fixture
def call_counter():
    """
    Create a simple call counter for tracking function invocations.

    Example:
        def test_callback(call_counter):
            counter = call_counter()
            instance.set_callback(counter)
            instance.do_something()
            assert counter.count == 1
    """
    class _CallCounter:
        def __init__(self):
            self.count = 0
            self.args_history = []
            self.kwargs_history = []

        def __call__(self, *args, **kwargs):
            self.count += 1
            self.args_history.append(args)
            self.kwargs_history.append(kwargs)

        def was_called(self) -> bool:
            return self.count > 0

        def was_called_times(self, times: int) -> bool:
            return self.count == times

        def last_call_args(self):
            return self.args_history[-1] if self.args_history else None

    return _CallCounter


@pytest.fixture
def event_collector():
    """
    Create a collector for gathering items yielded by generators.

    Useful for testing async generators or iterables.

    Example:
        async def test_generator(event_collector):
            collector = event_collector()

            async for event in async_generator():
                collector.collect(event)

            assert len(collector.items) == 3
    """
    class _EventCollector:
        def __init__(self):
            self.items = []

        def collect(self, item):
            self.items.append(item)

        def __len__(self):
            return len(self.items)

        def __iter__(self):
            return iter(self.items)

        def __getitem__(self, index):
            return self.items[index]

    return _EventCollector


# =============================================================================
# Type-specific Test Data Fixtures
# =============================================================================


@pytest.fixture
def empty_values() -> list:
    """Common empty values for boundary testing."""
    return [None, "", [], {}, 0, False]


@pytest.fixture
def invalid_string_values() -> list:
    """Common invalid string inputs for testing validation."""
    return [None, "", "   ", "\n\t", "\x00", "\xff\xfe"]
