# 代码质量与测试环境修复模式

## 问题 1: pylint E501 Line Too Long

**现象:**
```
E501 Line too long (88 > 79 characters)
```

**解决方案:**

### 方法 1: 字符串换行 (推荐)
```python
# ❌ 错误 - 超过 79 字符
raise ValueError(f"Failed to initialize {self.__class__.__name__}: {str(e)}")

# ✅ 正确 - 括号内隐式连接
raise ValueError(
    f"Failed to initialize {self.__class__.__name__}: {str(e)}"
)

# ✅ 正确 - 三引号字符串
error_msg = """
This is a very long error message that explains
what went wrong in detail.
"""
```

### 方法 2: 拆分长行
```python
# ❌ 错误
result = self.some_method(arg1, arg2, arg3, arg4, arg5, arg6)

# ✅ 正确 - 每行一个参数
result = self.some_method(
    arg1,
    arg2,
    arg3,
    arg4,
)
```

### 方法 3: 变量提取
```python
# ❌ 错误
assert channel.bot is not None, f"Bot is None after initialization for {channel.__class__.__name__}"

# ✅ 正确
channel_name = channel.__class__.__name__
assert channel.bot is not None, f"Bot is None after init for {channel_name}"
```

---

## 问题 2: 重复导入警告 (W0404 / R0401)

**现象:**
```
W0404: Reimport 'MagicMock' (imported line 5)
R0401: Cyclic import
```

**解决方案:**

### 统一顶层导入
```python
# ✅ 正确 - 所有导入放在文件顶部
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Optional

# 测试类中使用
class TestExample:
    def test_something(self):
        mock = MagicMock()  # 不再重复导入
```

### 避免嵌套导入 (除非必要)
```python
# ❌ 错误 - 不必要的嵌套导入
class TestExample:
    def test_something(self):
        from unittest.mock import MagicMock
        mock = MagicMock()

# ✅ 正确 - 统一顶层导入
from unittest.mock import MagicMock

class TestExample:
    def test_something(self):
        mock = MagicMock()
```

### 特殊情况: fixture 中延迟导入
```python
# ✅ 正确 - 避免循环导入
@pytest.fixture
def mock_client():
    from myapp.client import Client
    return MagicMock(spec=Client)
```

---

## 问题 3: Pydantic 测试环境问题

**现象:**
```
E0611: No name 'BaseModel' in module 'pydantic'
TypeError: Metaclass conflict when mocking Pydantic models
```

**原因:**
测试环境可能安装不同版本的 Pydantic (v1 vs v2)，导致模型导入失败。

**解决方案:**

### 方法 1: mock 整个 pydantic 模块
```python
# tests/conftest.py
import sys
from unittest.mock import MagicMock

# 预 mock pydantic，避免版本冲突
pydantic_mock = MagicMock()
pydantic_mock.BaseModel = MagicMock()
pydantic_mock.Field = MagicMock()
pydantic_mock.validator = MagicMock()
sys.modules['pydantic'] = pydantic_mock
```

### 方法 2: fixture 中创建 Mock Config
```python
# ✅ 正确 - 不依赖真实 Pydantic
@pytest.fixture
def mock_config():
    """创建 Mock Config，替代 Pydantic 模型。"""
    config = MagicMock()
    config.enabled = True
    config.timeout = 30
    config.api_key = "test_key"
    # 显式设置所有可能访问的属性
    config.host = "https://api.example.com"
    config.port = 443
    return config
```

### 方法 3: 使用 Monkeypatch 修改配置
```python
# ✅ 正确 - 不实例化 Pydantic 模型
class TestChannel:
    def test_with_config(self, monkeypatch):
        # 直接设置环境变量，绕过 Pydantic
        monkeypatch.setenv("API_KEY", "test_key")
        monkeypatch.setenv("TIMEOUT", "30")

        channel = Channel.from_env()
        assert channel.api_key == "test_key"
```

### 方法 4: 条件补丁 (兼容 v1/v2)
```python
# tests/conftest.py
try:
    from pydantic import BaseModel
except ImportError:
    # Pydantic v2 可能使用不同导入
    try:
        from pydantic.v1 import BaseModel
    except ImportError:
        BaseModel = MagicMock()

# 测试中使用
@pytest.fixture
def mock_model():
    model = MagicMock()
    model.model_dump.return_value = {"key": "value"}  # v2 风格
    model.dict.return_value = {"key": "value"}  # v1 风格
    return model
```

---

## 快速检查清单

生成测试代码后，检查以下项目：

```
□ 行长度 - 所有行 ≤ 79 字符
□ 导入语句 - 只出现在文件顶部
□ 无重复导入
□ Mock 完整 - 所有访问的属性已设置
□ 异步正确 - AsyncMock 用于异步方法
□ 无 Pydantic 依赖 - 使用 Mock 替代真实模型
```

---

## 自动修复命令

```bash
# 自动格式化代码
black tests/ --line-length 79

# 自动排序导入
isort tests/ --profile black

# 检查 pylint 问题
pylint tests/unit/channels/test_*.py --disable=all --enable=E501,W0404
```
