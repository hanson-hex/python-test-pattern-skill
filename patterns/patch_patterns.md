# Python Patch 模式

## 何时使用 Patch

- 替换外部依赖（HTTP、数据库、文件系统）
- 控制不可预测的行为（随机数、时间）
- 模拟故障路径

## 基本 Patch 模式

### 1. Patch 函数

```python
from unittest.mock import patch

def test_function():
    with patch("module.submodule.function_name") as mock_func:
        mock_func.return_value = "mocked_result"
        result = function_under_test()
        assert result == "expected"
```

### 2. Patch 类

```python
def test_class():
    with patch("module.ClassName") as MockClass:
        mock_instance = MockClass.return_value
        mock_instance.method.return_value = "result"
        
        result = function_that_uses_class()
        
        MockClass.assert_called_once()
        assert result == "expected"
```

### 3. Patch 对象属性

```python
def test_attribute():
    with patch.object(instance, "attribute_name", "new_value"):
        result = instance.method()
        assert result == "expected"
```

## Patch 路径规则

**关键原则**：patch 对象被导入的位置，而不是定义的位置。

```python
# 被测代码 (mymodule.py)
from external.lib import SomeClass

def use_it():
    obj = SomeClass()  # 使用 SomeClass

# 测试代码
# ❌ 错误：patch 定义位置
with patch("external.lib.SomeClass"):
    ...

# ✅ 正确：patch 被导入的位置
with patch("mymodule.SomeClass"):
    ...
```

## 常见模式

### 上下文管理器

```python
with patch("module.target") as mock:
    result = test_function()
    mock.assert_called_once()
```

### 装饰器

```python
@patch("module.target1")
@patch("module.target2")
def test_function(mock2, mock1):
    ...
```

### 叠加多个 Patch

```python
with patch("module.target1") as mock1:
    with patch("module.target2") as mock2:
        result = test_function()
```

## 启动时导入 vs 运行时导入

### 模块级别导入（常见）

```python
# module.py
from external.service import ExternalService  # 模块加载时导入

def start():
    service = ExternalService()

# test.py - patch 导入位置（被测模块中的引用）
with patch("module.ExternalService") as MockService:
    mock_instance = MockService.return_value
    mock_instance.connect.return_value = True
    result = start()
    assert result is True
```

### 函数内部导入（延迟加载）

```python
# module.py
def start():
    from external.service import ExternalService  # 运行时导入
    service = ExternalService()

# test.py - 需要 patch 导入源（原始定义位置）
with patch("external.service.ExternalService") as MockService:
    mock_instance = MockService.return_value
    mock_instance.connect.return_value = True
    result = start()
    assert result is True
```

## 调试 Patch 问题

如果 patch 不生效：

1. 检查 patch 路径是否正确
2. 确认是在调用位置 patch，而不是定义位置
3. 对于延迟导入，确保 patch 在导入之前设置

```python
# 调试：打印实际被调用的对象
from module import target
print(target)  # 看是否被 mock
```
