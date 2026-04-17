# Class-based Test Organization Pattern

## Overview

Organize tests into classes by functional area, with each class focused on a single test topic.

## Naming Convention

```python
class Test{ClassName}{TestArea}:
    """Tests for {ClassName} — {TestArea}."""
```

## Priority Labels

Use labels to indicate test priority:

```python
# P0: Core functionality — must test
# P1: Important functionality — recommended to test
# P2: Boundary conditions — optional supplement

# Mark in class or method docstrings
class Test{class_name}Init:
    """
    P0: Initialization tests.

    Core functionality verification.
    """
```

## Recommended Organization

```python
# P0: Initialization
class Test{class_name}Init:
    def test_init_stores_basic_config(self): ...
    def test_init_creates_required_data_structures(self): ...

# P0: Factory methods
class Test{class_name}FactoryMethods:
    def test_from_env_reads_env_vars(self): ...
    def test_from_config_uses_config_values(self): ...

# P0: Lifecycle
class Test{class_name}Lifecycle:
    async def test_start_success(self): ...
    async def test_stop_success(self): ...
    async def test_start_when_disabled(self): ...

# P1: Core features
class Test{class_name}{CoreFeature}:
    async def test_{feature}_success(self): ...
    async def test_{feature}_handles_error(self): ...

# P2: Boundary conditions / utility methods
class Test{class_name}Utilities:
    def test_{utility}_with_valid_input(self): ...
    def test_{utility}_with_empty_input(self): ...
```

## Docstring Convention

```python
def test_{method}_does_something(self):
    """
    Test that {method} performs {operation}.

    Verifies that:
    - condition 1
    - condition 2
    """
```
