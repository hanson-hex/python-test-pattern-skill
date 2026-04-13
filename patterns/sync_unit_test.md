# 同步代码测试模式

## 模式概述

测试无外部依赖的简单函数和类时使用此模式。

## 测试类结构

```python
import pytest
from unittest.mock import Mock, MagicMock


class Test{class_name}Init:
    """测试初始化"""
    
    def test_init_stores_basic_config(self):
        """构造函数应存储基本配置参数"""
        instance = {class_name}(
            param1="value1",
            param2="value2",
        )
        
        assert instance.param1 == "value1"
        assert instance.param2 == "value2"
    
    def test_init_creates_required_data_structures(self):
        """构造函数应初始化内部数据结构"""
        instance = {class_name}()
        
        assert hasattr(instance, "_internal_dict")
        assert isinstance(instance._internal_dict, dict)


class Test{class_name}FactoryMethods:
    """测试工厂方法"""
    
    def test_from_env_reads_env_vars(self, monkeypatch):
        """from_env 应正确读取环境变量"""
        monkeypatch.setenv("{ENV_VAR}", "test_value")
        
        instance = {class_name}.from_env()
        
        assert instance.config == "test_value"
    
    def test_from_env_uses_defaults(self, monkeypatch):
        """from_env 缺失变量时应使用默认值"""
        monkeypatch.delenv("{ENV_VAR}", raising=False)
        
        instance = {class_name}.from_env()
        
        assert instance.config == "default_value"
    
    def test_from_config_uses_config_object(self):
        """from_config 应使用配置对象的值"""
        config = Mock()
        config.enabled = True
        config.value = "test"
        
        instance = {class_name}.from_config(config=config)
        
        assert instance.enabled is True
        assert instance.value == "test"


class Test{class_name}Properties:
    """测试属性访问"""
    
    def test_{property}_returns_expected_value(self):
        """{property} 应返回预期值"""
        instance = {class_name}()
        
        result = instance.{property}
        
        assert result == expected_value
```

## 工具函数测试

```python
class Test{function_name}:
    """测试 {function_name} 函数"""
    
    def test_{function}_with_valid_input(self):
        """有效输入应返回正确结果"""
        result = {function}(valid_input)
        
        assert result == expected_output
    
    def test_{function}_with_empty_input(self):
        """空输入应处理正确"""
        result = {function}("")
        
        assert result == expected_for_empty
    
    def test_{function}_invalid_input_raises(self):
        """无效输入应抛出异常"""
        with pytest.raises(ValueError, match="expected error"):
            {function}(invalid_input)
```

## 参数化测试

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
    """测试不同输入的处理"""
    result = instance.method(input_value)
    
    assert result == expected_result
```
