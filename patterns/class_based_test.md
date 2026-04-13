# 类方法测试组织模式

## 模式概述

按照功能区域组织测试类，每个类专注于一个测试主题。

## 命名规范

```python
class Test{ClassName}{TestArea}:
    """测试 {ClassName} 的 {TestArea}"""
```

## 优先级标记

根据测试优先级使用标签：

```python
# P0: 核心功能，必须测试
# P1: 重要功能，建议测试
# P2: 边界条件，可补充测试

# 在类或方法文档字符串中标记
class Test{class_name}Init:
    """
    P0: 初始化测试
    
    核心功能验证
    """
```

## 推荐组织方式

```python
# P0: 初始化
class Test{class_name}Init:
    def test_init_stores_basic_config(self): ...
    def test_init_creates_required_data_structures(self): ...

# P0: 工厂方法
class Test{class_name}FactoryMethods:
    def test_from_env_reads_env_vars(self): ...
    def test_from_config_uses_config_values(self): ...

# P0: 生命周期
class Test{class_name}Lifecycle:
    async def test_start_success(self): ...
    async def test_stop_success(self): ...
    async def test_start_when_disabled(self): ...

# P1: 核心功能
class Test{class_name}{CoreFeature}:
    async def test_{feature}_success(self): ...
    async def test_{feature}_handles_error(self): ...

# P2: 边界条件/工具方法
class Test{class_name}Utilities:
    def test_{utility}_with_valid_input(self): ...
    def test_{utility}_with_empty_input(self): ...
```

## 文档字符串规范

```python
def test_{method}_does_something(self):
    """
    测试 {方法} 执行 {操作}。
    
    Verifies that:
    - 条件1
    - 条件2
    """
```
