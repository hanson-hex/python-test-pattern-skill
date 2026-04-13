# 第三方库缺失 Mock 模式

## 模式概述

当被测代码依赖未安装的第三方库（如企业微信的 `aibot`、飞书的 `lark-oapi` 等）时使用此模式。

## 快速诊断

如果遇到以下错误，说明需要使用此模式：

```
ModuleNotFoundError: No module named 'xxx'
```

或 pytest 收集测试时失败：

```
ERROR tests/unit/test_xxx.py - ModuleNotFoundError: No module named 'xxx'
```

## 问题场景

```python
# src/myapp/external/websocket_client.py
from thirdparty_sdk import WSClient, WSClientOptions  # 未安装的第三方库

class MyClient(BaseClient):
    def start(self):
        client = WSClient()  # 依赖第三方库
```

直接导入会导致 `ModuleNotFoundError`。

## 解决方案

### 方法 1：在 conftest.py 中 Mock 整个模块（推荐）

```python
# tests/conftest.py
import sys
from unittest.mock import MagicMock

# Mock 缺失的第三方库
sys.modules['thirdparty_sdk'] = MagicMock()
sys.modules['external_api'] = MagicMock()
```

### 方法 2：在测试文件中延迟导入

```python
# tests/unit/test_client.py
# pylint: disable=import-error
def test_init():
    from unittest.mock import patch, MagicMock

    with patch.dict('sys.modules', {'thirdparty_sdk': MagicMock()}):
        from myapp.external.websocket_client import MyClient
        client = MyClient(...)
```

### 方法 3：Fixture 中动态导入

```python
@pytest.fixture
def client_instance(mock_handler, tmp_path):
    """Create client with mocked third-party deps."""
    with patch.dict('sys.modules', {'thirdparty_sdk': MagicMock()}):
        from myapp.external.websocket_client import MyClient
        client = MyClient(
            handler=mock_handler,
            enabled=True,
        )
        yield client
```

## 完整示例

### conftest.py 配置

```python
# tests/conftest.py
import sys
from unittest.mock import MagicMock

# 预 mock 所有缺失的第三方库
_MISSING_MODULES = {
    'thirdparty_sdk',
    'external_api',
    'proprietary_lib',
}

for module in _MISSING_MODULES:
    if module not in sys.modules:
        sys.modules[module] = MagicMock()
```

### 测试中使用

```python
# tests/unit/test_client.py
from unittest.mock import AsyncMock, MagicMock, patch

class TestMyClient:
    def test_start_missing_credentials(self, mock_handler, tmp_path):
        """Test start fails gracefully with missing credentials."""
        from myapp.external.websocket_client import MyClient

        client = MyClient(
            handler=mock_handler,
            enabled=True,
            api_key="",
        )

        # Should not raise even though thirdparty_sdk is mocked
        result = client.start()
        assert result is None
```

## 注意事项

1. **在 conftest.py 中统一处理**：避免每个测试文件都重复 mock
2. **mock 的内容**：只需要 mock 被测代码实际使用的类/函数
3. **类型注解**：如果第三方库用于类型注解，使用 `TYPE_CHECKING` 保护

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thirdparty_sdk import WSClient  # 仅类型检查时导入
```

## 常见场景

| 场景 | 库示例 | Mock 建议 |
|------|--------|-----------|
| WebSocket SDK | `websocket_sdk` | Mock Client, Connection |
| Message Queue | `mq_client` | Mock Producer, Consumer |
| AI/ML API | `ai_platform` | Mock Model, Prediction |
| Payment Gateway | `payment_sdk` | Mock Payment, Refund |

