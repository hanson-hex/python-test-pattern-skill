# 复杂方法测试模式

## 模式概述

当被测方法具有以下特征时使用此模式：
- 多分支逻辑（if/elif/else 链）
- 复杂的状态管理（多个实例变量交互）
- 多步骤处理流程
- 需要 mock 多个依赖

## 识别复杂方法

复杂方法通常具有以下特征：

```python
class MyService:
    def complex_method(self, data: dict) -> Result:
        # 1. 多分支验证
        if not data.get("required_field"):
            return Result.error("missing_field")

        # 2. 状态检查
        if self._state != State.READY:
            return Result.error("not_ready")

        # 3. 多步骤处理
        parsed = self._parser.parse(data)
        validated = self._validator.check(parsed)
        stored = self._storage.save(validated)

        # 4. 副作用（事件发送等）
        self._emitter.emit("data_processed", stored.id)

        return Result.ok(stored)
```

## 测试策略

### 策略 1：分支覆盖测试

为每个主要分支创建独立测试：

```python
class TestComplexMethodBranches:
    """Test each logical branch separately."""

    def test_missing_required_field_returns_error(self, service):
        """Branch 1: 缺少必填字段."""
        result = service.complex_method({})
        assert result.is_error
        assert "missing_field" in result.message

    def test_not_ready_state_returns_error(self, service):
        """Branch 2: 状态未就绪."""
        service._state = State.INITIALIZING
        result = service.complex_method({"required_field": "value"})
        assert result.is_error
        assert "not_ready" in result.message

    def test_valid_data_returns_ok(self, service):
        """Happy path: 所有条件满足."""
        result = service.complex_method({"required_field": "value"})
        assert result.is_ok
```

### 策略 2：步骤验证测试

验证多步骤流程的每个阶段：

```python
class TestComplexMethodSteps:
    """Verify each processing step is called correctly."""

    def test_parser_called_with_raw_data(self, service, mock_parser):
        """Step 1: 解析器接收原始数据."""
        service.complex_method({"required_field": "value"})
        mock_parser.parse.assert_called_once_with({"required_field": "value"})

    def test_validator_receives_parsed_data(self, service, mock_validator):
        """Step 2: 验证器接收解析后的数据."""
        service.complex_method({"required_field": "value"})
        mock_validator.check.assert_called_once()

    def test_storage_receives_validated_data(self, service, mock_storage):
        """Step 3: 存储接收验证后的数据."""
        service.complex_method({"required_field": "value"})
        mock_storage.save.assert_called_once()
```

### 策略 3：副作用验证测试

验证副作用是否正确执行：

```python
class TestComplexMethodSideEffects:
    """Verify side effects (events, state changes)."""

    def test_eventEmitted_with_stored_id(self, service, mock_emitter):
        """副作用: 事件发送包含存储 ID."""
        result = service.complex_method({"required_field": "value"})
        mock_emitter.emit.assert_called_once_with(
            "data_processed",
            result.value.id,
        )

    def test_state_unchanged_after_success(self, service):
        """状态: 成功后保持 READY 状态."""
        original_state = service._state
        service.complex_method({"required_field": "value"})
        assert service._state == original_state
```

### 策略 4：集成流程测试

验证完整流程的数据传递：

```python
class TestComplexMethodIntegration:
    """End-to-end data flow verification."""

    def test_data_flow_through_all_steps(self, service):
        """验证数据在完整流程中的转换."""
        input_data = {"required_field": "input_value"}

        with patch.object(service._parser, 'parse') as mock_parse:
            mock_parse.return_value = {"parsed": True}

            with patch.object(service._validator, 'check') as mock_check:
                mock_check.return_value = {"validated": True}

                result = service.complex_method(input_data)

                # 验证调用链
                mock_parse.assert_called_once_with(input_data)
                mock_check.assert_called_once_with({"parsed": True})
```

## 依赖 Mock 模式

### Mock 工厂模式

```python
@pytest.fixture
def mock_dependencies():
    """Create all required mocks for complex method."""
    return {
        'parser': MagicMock(),
        'validator': MagicMock(),
        'storage': MagicMock(),
        'emitter': MagicMock(),
    }

@pytest.fixture
def service(mock_dependencies):
    """Create service with mocked dependencies."""
    return MyService(
        parser=mock_dependencies['parser'],
        validator=mock_dependencies['validator'],
        storage=mock_dependencies['storage'],
        emitter=mock_dependencies['emitter'],
    )
```

### Mock 返回值链

```python
def test_complex_method_chain(mock_dependencies):
    """Test with chained return values."""
    mock_dependencies['parser'].parse.return_value = {
        "parsed_field": "parsed_value",
    }
    mock_dependencies['validator'].check.return_value = {
        "validated_field": "validated_value",
    }
    mock_dependencies['storage'].save.return_value = SavedRecord(
        id="record_123",
        data={"validated_field": "validated_value"},
    )

    result = service.complex_method({"raw": "data"})

    assert result.value.id == "record_123"
```

## 状态机测试

对于状态依赖的方法：

```python
class TestStateDependentMethods:
    """Test methods that depend on internal state."""

    @pytest.mark.parametrize("state,expected_result", [
        (State.READY, Result.ok()),
        (State.INITIALIZING, Result.error("not_ready")),
        (State.ERROR, Result.error("in_error")),
        (State.CLOSED, Result.error("closed")),
    ])
    def test_method_with_various_states(self, service, state, expected_result):
        """验证方法在不同状态下的行为."""
        service._state = state
        result = service.state_dependent_method()
        assert result.status == expected_result.status
```

## 异常路径测试

```python
class TestComplexMethodExceptions:
    """Test exception handling in complex methods."""

    def test_parser_exception_is_caught(self, service, mock_parser):
        """解析异常被捕获并转换为错误结果."""
        mock_parser.parse.side_effect = ParseError("Invalid format")
        result = service.complex_method({"raw": "data"})
        assert result.is_error
        assert "parse" in result.message.lower()

    def test_storage_exception_propagates(self, service, mock_storage):
        """存储异常被正确处理."""
        mock_storage.save.side_effect = StorageError("Disk full")
        with pytest.raises(StorageError):
            service.complex_method({"raw": "data"})
```

## 最佳实践

1. **单一职责测试**：每个测试只验证一个方面
2. **命名规范**：`test_{method}_{scenario}_{expected_outcome}`
3. **注释说明**：在测试类 docstring 中说明测试的复杂方法
4. **分层测试**：分支测试 → 步骤测试 → 集成测试
5. **Mock 验证**：不仅验证返回值，还要验证依赖调用

## 测试模板

```python
class Test{MethodName}Complex:
    """P1: Complex method tests for {method_name}.

    Method characteristics:
    - {feature 1}
    - {feature 2}
    - {feature 3}
    """

    # === Branch Coverage Tests ===

    def test_{method}_branch_{condition}_{outcome}(self, instance):
        """Test {scenario}."""
        pass

    # === Step Verification Tests ===

    def test_{method}_step_{number}_{description}(self, instance, mock_dep):
        """Verify step {number}: {description}."""
        pass

    # === Side Effect Tests ===

    def test_{method}_side_effect_{effect}(self, instance, mock_dep):
        """Verify side effect: {effect}."""
        pass

    # === Integration Tests ===

    def test_{method}_integration_full_flow(self, instance):
        """Verify complete data flow."""
        pass

    # === Exception Tests ===

    def test_{method}_exception_{scenario}(self, instance, mock_dep):
        """Verify exception handling for {scenario}."""
        pass
```
