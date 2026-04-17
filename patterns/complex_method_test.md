# Complex Method Test Pattern

## Overview

Use this pattern when the method under test has:
- Multi-branch logic (if/elif/else chains)
- Complex state management (multiple instance variables interacting)
- Multi-step processing flows
- Multiple dependencies to mock

## Identifying Complex Methods

Complex methods typically have these characteristics:

```python
class MyService:
    def complex_method(self,  dict) -> Result:
        # 1. Multi-branch validation
        if not data.get("required_field"):
            return Result.error("missing_field")

        # 2. State check
        if self._state != State.READY:
            return Result.error("not_ready")

        # 3. Multi-step processing
        parsed = self._parser.parse(data)
        validated = self._validator.check(parsed)
        stored = self._storage.save(validated)

        # 4. Side effects (event emission, etc.)
        self._emitter.emit("data_processed", stored.id)

        return Result.ok(stored)
```

## Test Strategies

### Strategy 1: Branch Coverage Tests

Create a separate test for each major branch:

```python
class TestComplexMethodBranches:
    """Test each logical branch separately."""

    def test_missing_required_field_returns_error(self, service):
        """Branch 1: missing required field."""
        result = service.complex_method({})
        assert result.is_error
        assert "missing_field" in result.message

    def test_not_ready_state_returns_error(self, service):
        """Branch 2: state not ready."""
        service._state = State.INITIALIZING
        result = service.complex_method({"required_field": "value"})
        assert result.is_error
        assert "not_ready" in result.message

    def test_valid_data_returns_ok(self, service):
        """Happy path: all conditions satisfied."""
        result = service.complex_method({"required_field": "value"})
        assert result.is_ok
```

### Strategy 2: Step Verification Tests

Verify each stage of a multi-step flow:

```python
class TestComplexMethodSteps:
    """Verify each processing step is called correctly."""

    def test_parser_called_with_raw_data(self, service, mock_parser):
        """Step 1: parser receives raw data."""
        service.complex_method({"required_field": "value"})
        mock_parser.parse.assert_called_once_with({"required_field": "value"})

    def test_validator_receives_parsed_data(self, service, mock_validator):
        """Step 2: validator receives parsed data."""
        service.complex_method({"required_field": "value"})
        mock_validator.check.assert_called_once()

    def test_storage_receives_validated_data(self, service, mock_storage):
        """Step 3: storage receives validated data."""
        service.complex_method({"required_field": "value"})
        mock_storage.save.assert_called_once()
```

### Strategy 3: Side Effect Verification Tests

Verify that side effects are executed correctly:

```python
class TestComplexMethodSideEffects:
    """Verify side effects (events, state changes)."""

    def test_event_emitted_with_stored_id(self, service, mock_emitter):
        """Side effect: event emission includes stored ID."""
        result = service.complex_method({"required_field": "value"})
        mock_emitter.emit.assert_called_once_with(
            "data_processed",
            result.value.id,
        )

    def test_state_unchanged_after_success(self, service):
        """State: remains READY after success."""
        original_state = service._state
        service.complex_method({"required_field": "value"})
        assert service._state == original_state
```

### Strategy 4: Integration Flow Tests

Verify data transformation through the full pipeline:

```python
class TestComplexMethodIntegration:
    """End-to-end data flow verification."""

    def test_data_flow_through_all_steps(self, service):
        """Verify data transformation across the full pipeline."""
        input_data = {"required_field": "input_value"}

        with patch.object(service._parser, 'parse') as mock_parse:
            mock_parse.return_value = {"parsed": True}

            with patch.object(service._validator, 'check') as mock_check:
                mock_check.return_value = {"validated": True}

                result = service.complex_method(input_data)

                # Verify call chain
                mock_parse.assert_called_once_with(input_data)
                mock_check.assert_called_once_with({"parsed": True})
```

## Dependency Mock Patterns

### Mock Factory Pattern

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

### Chained Return Values

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

## State Machine Tests

For state-dependent methods:

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
        """Verify method behavior across different states."""
        service._state = state
        result = service.state_dependent_method()
        assert result.status == expected_result.status
```

## Exception Path Tests

```python
class TestComplexMethodExceptions:
    """Test exception handling in complex methods."""

    def test_parser_exception_is_caught(self, service, mock_parser):
        """Parse exception is caught and converted to error result."""
        mock_parser.parse.side_effect = ParseError("Invalid format")
        result = service.complex_method({"raw": "data"})
        assert result.is_error
        assert "parse" in result.message.lower()

    def test_storage_exception_propagates(self, service, mock_storage):
        """Storage exception is handled correctly."""
        mock_storage.save.side_effect = StorageError("Disk full")
        with pytest.raises(StorageError):
            service.complex_method({"raw": "data"})
```

## Best Practices

1. **Single responsibility**: each test verifies only one aspect
2. **Naming convention**: `test_{method}_{scenario}_{expected_outcome}`
3. **Documentation**: describe the complex method in the test class docstring
4. **Layered testing**: branch tests → step tests → integration tests
5. **Mock verification**: verify not just return values, but also dependency calls

## Test Template

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
