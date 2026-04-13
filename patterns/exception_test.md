# 异常路径测试模式

## 模式概述

异常路径测试验证代码在错误、异常和边界条件下的行为。这是确保代码健壮性的关键。

## 异常类型覆盖

### 1. 外部依赖异常

```python
class TestExternalDependencyExceptions:
    """Test handling of external service failures."""

    def test_http_4xx_error_handled(self, channel, mock_session):
        """Test handling of client errors (400-499)."""
        mock_session.expect_post(
            url="https://api.example.com/send",
            response_status=400,
            response_json={"error": "Bad Request"},
        )
        result = await channel.send_message("test")
        assert result is False  # Graceful failure

    def test_http_5xx_error_retries(self, channel, mock_session):
        """Test handling of server errors (500-599)."""
        mock_session.expect_post(
            url="https://api.example.com/send",
            response_status=500,
            response_json={"error": "Internal Server Error"},
        )
        result = await channel.send_message("test")
        # Verify retry logic or graceful failure

    def test_network_timeout_handled(self, channel, mock_session):
        """Test handling of network timeouts."""
        mock_session.post.side_effect = TimeoutError("Connection timeout")
        result = await channel.send_message("test")
        assert result is False

    def test_connection_error_logged(self, channel, mock_session, caplog):
        """Test connection errors are logged."""
        mock_session.post.side_effect = ConnectionError("Connection refused")
        with caplog.at_level(logging.ERROR):
            await channel.send_message("test")
        assert "connection" in caplog.text.lower()
```

### 2. 输入验证异常

```python
class TestInputValidationExceptions:
    """Test handling of invalid inputs."""

    def test_none_input_raises_valueerror(self, processor):
        """Test None input raises appropriate exception."""
        with pytest.raises(ValueError, match="input cannot be None"):
            processor.process(None)

    def test_empty_string_raises_valueerror(self, processor):
        """Test empty string input validation."""
        with pytest.raises(ValueError, match="input cannot be empty"):
            processor.process("")

    def test_invalid_type_raises_typeerror(self, processor):
        """Test type validation."""
        with pytest.raises(TypeError, match="expected str, got int"):
            processor.process(123)

    @pytest.mark.parametrize("invalid_input", [
        "",           # empty
        "   ",        # whitespace only
        "\n\t",       # control chars
        "a" * 10000,  # too long
    ])
    def test_invalid_inputs_raise_exception(self, processor, invalid_input):
        """Test various invalid inputs."""
        with pytest.raises(ValueError):
            processor.process(invalid_input)
```

### 3. 状态异常

```python
class TestStateExceptions:
    """Test handling of invalid state transitions."""

    def test_operation_before_init_raises(self, service):
        """Test operation before initialization."""
        with pytest.raises(RuntimeError, match="not initialized"):
            service.process_data("test")

    def test_double_init_raises(self, service):
        """Test double initialization."""
        service.initialize()
        with pytest.raises(RuntimeError, match="already initialized"):
            service.initialize()

    def test_operation_after_close_raises(self, service):
        """Test operation after cleanup."""
        service.initialize()
        service.close()
        with pytest.raises(RuntimeError, match="already closed"):
            service.process_data("test")
```

### 4. 资源异常

```python
class TestResourceExceptions:
    """Test handling of resource failures."""

    def test_file_not_found_handled(self, loader, tmp_path):
        """Test missing file handling."""
        nonexistent = tmp_path / "nonexistent.txt"
        result = loader.load(nonexistent)
        assert result is None  # Graceful handling

    def test_permission_denied_handled(self, loader, tmp_path, monkeypatch):
        """Test permission error handling."""
        test_file = tmp_path / "readonly.txt"
        test_file.write_text("content")

        # Simulate permission denied
        def mock_open(*args, **kwargs):
            raise PermissionError("Access denied")
        monkeypatch.setattr("builtins.open", mock_open)

        result = loader.load(test_file)
        assert result is None

    def test_disk_full_during_write(self, writer, tmp_path):
        """Test disk full handling."""
        with patch.object(Path, 'write_bytes') as mock_write:
            mock_write.side_effect = OSError("No space left on device")
            result = writer.write(tmp_path / "test.dat", b"data")
            assert result is False
```

## 异常链测试

验证异常链和上下文保留：

```python
class TestExceptionChaining:
    """Test exception chaining preserves context."""

    def test_original_exception_preserved(self, service):
        """Test original exception is preserved in chain."""
        with pytest.raises(ServiceError) as exc_info:
            service.process_with_wrapper("invalid")

        # Verify the chain
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_exception_message_contains_context(self, service):
        """Test exception message includes helpful context."""
        with pytest.raises(ServiceError, match="processing failed for item"):
            service.process_with_wrapper("invalid")
```

## 异步异常测试

```python
class TestAsyncExceptions:
    """Test exception handling in async code."""

    @pytest.mark.asyncio
    async def test_async_operation_timeout(self, async_client):
        """Test async timeout handling."""
        with patch.object(async_client, '_send', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = asyncio.TimeoutError()
            result = await async_client.send_with_timeout("test", timeout=1.0)
            assert result is None

    @pytest.mark.asyncio
    async def test_cancelled_task_handled(self, async_service):
        """Test asyncio.CancelledError handling."""
        async def slow_operation():
            await asyncio.sleep(10)

        task = asyncio.create_task(async_service.run_slow())
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task
```

## 边界条件测试

```python
class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""

    @pytest.mark.parametrize("size,expected", [
        (0, True),           # empty
        (1, True),           # single item
        (999, True),         # just under limit
        (1000, True),        # at limit
        (1001, False),       # just over limit
    ])
    def test_size_limits(self, buffer, size, expected):
        """Test size boundary conditions."""
        result = buffer.allocate(size)
        assert result == expected

    def test_concurrent_access_thread_safe(self, cache):
        """Test thread safety under concurrent access."""
        errors = []

        def worker():
            try:
                for i in range(100):
                    cache.get_or_set(f"key_{i}", lambda: f"value_{i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Concurrent errors: {errors}"
```

## 优雅降级测试

```python
class TestGracefulDegradation:
    """Test graceful degradation when features fail."""

    def test_fallback_to_simple_method(self, rich_sender):
        """Test fallback when rich media fails."""
        with patch.object(rich_sender, 'send_rich') as mock_rich:
            mock_rich.side_effect = APIError("Rich media unavailable")

            # Should fallback to simple text
            result = rich_sender.send("Hello", use_rich=True)
            assert result is True  # Succeeded via fallback

    def test_partial_completion_accepted(self, batch_processor):
        """Test partial batch completion."""
        items = ["a", "b", "c"]
        with patch.object(batch_processor, '_process_one') as mock_process:
            # Fail on second item
            mock_process.side_effect = [True, False, True]

            result = batch_processor.process_batch(items)
            assert result.completed == 2
            assert result.failed == 1
```

## 日志验证

```python
class TestExceptionLogging:
    """Test that exceptions are properly logged."""

    def test_exception_logged_at_error_level(self, service, caplog):
        """Verify exceptions are logged at appropriate level."""
        with patch.object(service, '_internal_call') as mock_call:
            mock_call.side_effect = RuntimeError("Something broke")

            with caplog.at_level(logging.ERROR):
                service.process("test")

        assert "Something broke" in caplog.text
        assert "ERROR" in caplog.text

    def test_warning_logged_for_recoverable_error(self, service, caplog):
        """Test warnings for recoverable errors."""
        with patch.object(service, '_internal_call') as mock_call:
            mock_call.side_effect = ConnectionError("Transient error")

            with caplog.at_level(logging.WARNING):
                service.process("test")

        assert "retry" in caplog.text.lower()
```

## 最佳实践

1. **具体异常**：测试具体的异常类型，而不是通用的 Exception
2. **错误消息**：验证错误消息包含有用的上下文
3. **副作用**：验证异常发生后没有不良的副作用
4. **状态恢复**：验证异常后对象状态保持一致
5. **日志记录**：验证异常被正确记录

## 测试模板

```python
class Test{Class}Exceptions:
    """P1: Exception handling tests for {Class}.

    Covers:
    - External dependency failures
    - Input validation errors
    - State violations
    - Resource failures
    """

    # === External Dependency Exceptions ===

    def test_{operation}_http_error_{code}_handled(self, instance, mock_dep):
        """Test HTTP {code} error handling."""
        pass

    def test_{operation}_network_timeout_handled(self, instance, mock_dep):
        """Test network timeout handling."""
        pass

    # === Input Validation Exceptions ===

    def test_{operation}_none_input_raises(self, instance):
        """Test None input raises ValueError."""
        pass

    def test_{operation}_invalid_type_raises(self, instance):
        """Test invalid type raises TypeError."""
        pass

    # === State Exceptions ===

    def test_{operation}_before_init_raises(self, instance):
        """Test operation before initialization raises."""
        pass

    # === Resource Exceptions ===

    def test_{operation}_resource_unavailable_handled(self, instance):
        """Test resource failure handling."""
        pass
```
