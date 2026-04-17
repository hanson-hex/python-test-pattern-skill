# Synchronous Code Test Pattern

## Overview

Use this pattern when testing simple functions and classes with no external dependencies.

## Test Class Structure

```python
import pytest
from unittest.mock import Mock, MagicMock


class Test{class_name}Init:
    """Test initialization."""
    
    def test_init_stores_basic_config(self):
        """Constructor should store basic config parameters."""
        instance = {class_name}(
            param1="value1",
            param2="value2",
        )
        
        assert instance.param1 == "value1"
        assert instance.param2 == "value2"
    
    def test_init_creates_required_data_structures(self):
        """Constructor should initialize internal data structures."""
        instance = {class_name}()
        
        assert hasattr(instance, "_internal_dict")
        assert isinstance(instance._internal_dict, dict)


class Test{class_name}FactoryMethods:
    """Test factory methods."""
    
    def test_from_env_reads_env_vars(self, monkeypatch):
        """from_env should read environment variables correctly."""
        monkeypatch.setenv("{ENV_VAR}", "test_value")
        
        instance = {class_name}.from_env()
        
        assert instance.config == "test_value"
    
    def test_from_env_uses_defaults(self, monkeypatch):
        """from_env should use defaults when env vars are missing."""
        monkeypatch.delenv("{ENV_VAR}", raising=False)
        
        instance = {class_name}.from_env()
        
        assert instance.config == "default_value"
    
    def test_from_config_uses_config_object(self):
        """from_config should use values from the config object."""
        config = Mock()
        config.enabled = True
        config.value = "test"
        
        instance = {class_name}.from_config(config=config)
        
        assert instance.enabled is True
        assert instance.value == "test"


class Test{class_name}Properties:
    """Test property access."""
    
    def test_{property}_returns_expected_value(self):
        """{property} should return the expected value."""
        instance = {class_name}()
        
        result = instance.{property}
        
        assert result == expected_value
```

## Utility Function Tests

```python
class Test{function_name}:
    """Tests for {function_name} function."""
    
    def test_{function}_with_valid_input(self):
        """Valid input should return correct result."""
        result = {function}(valid_input)
        
        assert result == expected_output
    
    def test_{function}_with_empty_input(self):
        """Empty input should be handled correctly."""
        result = {function}("")
        
        assert result == expected_for_empty
    
    def test_{function}_invalid_input_raises(self):
        """Invalid input should raise an exception."""
        with pytest.raises(ValueError, match="expected error"):
            {function}(invalid_input)
```

## Parametrized Tests

```python
import pytest


@pytest.mark.parametrize(
    "input_value,expected_result",
    [
        ("input1", "output1"),
        ("input2", "output2"),
        ("input3", "output3"),
    ],
)
def test_{method}_with_various_inputs(
    self,
    input_value,
    expected_result,
):
    """Test handling of various inputs."""
    result = instance.method(input_value)
    
    assert result == expected_result
```
