# Python Patch Patterns

## When to Use Patch

- Replace external dependencies (HTTP, database, filesystem)
- Control unpredictable behavior (random numbers, time)
- Simulate failure paths

## Basic Patch Patterns

### 1. Patch a Function

```python
from unittest.mock import patch

def test_function():
    with patch("module.submodule.function_name") as mock_func:
        mock_func.return_value = "mocked_result"
        result = function_under_test()
        assert result == "expected"
```

### 2. Patch a Class

```python
def test_class():
    with patch("module.ClassName") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.method.return_value = "result"
        
        result = function_that_uses_class()
        
        MockClass.assert_called_once()
        assert result == "expected"
```

### 3. Patch an Object Attribute

```python
def test_attribute():
    with patch.object(instance, "attribute_name", "new_value"):
        result = instance.method()
        assert result == "expected"
```

## Patch Path Rules

**Key principle**: patch where the object is *imported*, not where it is *defined*.

```python
# Code under test (mymodule.py)
from external.lib import SomeClass

def use_it():
    obj = SomeClass()  # uses SomeClass

# Test code
# ❌ Wrong: patch the definition location
with patch("external.lib.SomeClass"):
    ...

# ✅ Correct: patch the import location
with patch("mymodule.SomeClass"):
    ...
```

## Common Patterns

### Context Manager

```python
with patch("module.target") as mock:
    result = test_function()
    mock.assert_called_once()
```

### Decorator

```python
@patch("module.target1")
@patch("module.target2")
def test_function(mock2, mock1):
    ...
```

### Multiple Patches

```python
with patch("module.target1") as mock1:
    with patch("module.target2") as mock2:
        result = test_function()
```

## Module-level Import vs Runtime Import

### Module-level Import (common)

```python
# module.py
from external.service import ExternalService  # imported at module load

def start():
    service = ExternalService()

# test.py — patch the import location (the reference in the module under test)
with patch("module.ExternalService") as MockService:
    mock_instance = MockService.return_value
    mock_instance.connect.return_value = True
    result = start()
    assert result is True
```

### Function-level Import (lazy loading)

```python
# module.py
def start():
    from external.service import ExternalService  # imported at runtime
    service = ExternalService()

# test.py — must patch the original source (definition location)
with patch("external.service.ExternalService") as MockService:
    mock_instance = MockService.return_value
    mock_instance.connect.return_value = True
    result = start()
    assert result is True
```

## Debugging Patch Issues

If a patch is not taking effect:

1. Check that the patch path is correct
2. Confirm you are patching the call site, not the definition site
3. For lazy imports, ensure the patch is set up before the import runs

```python
# Debug: print the actual object being called
from module import target
print(target)  # check if it has been mocked
```
