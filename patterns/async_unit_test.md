# 异步代码测试模式

## 模式概述

测试包含 `async def` 的方法时使用此模式。

## 关键点

1. **只在 async def 方法上使用 @pytest.mark.asyncio**
2. **不要在类或全局使用 pytestmark = pytest.mark.asyncio**
3. **AsyncMock 用于 mock 异步方法**

## 模板代码

```python
import pytest
from unittest.mock import AsyncMock, MagicMock


class Test{class_name}Async:
    """
    异步方法测试类。
    
    注意：不要在类上使用 @pytest.mark.asyncio
    只对异步测试方法使用装饰器
    """
    
    @pytest.fixture
    def mock_process(self):
        """Create mock process handler."""
        async def mock_handler(*args, **kwargs):
            mock_event = MagicMock()
            mock_event.object = "message"
            mock_event.status = "completed"
            yield mock_event
        return AsyncMock(side_effect=mock_handler)
    
    @pytest.fixture
    def instance(self, mock_process):
        """Create {class_name} instance."""
        from {module_path} import {class_name}
        return {class_name}(process=mock_process)
    
    @pytest.mark.asyncio
    async def test_{method}_success(self, instance):
        """测试 {method} 成功执行 - 异步方法需要装饰器"""
        result = await instance.{method}()
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_{method}_when_disabled(self, instance):
        """测试禁用时 {method} 不执行操作"""
        instance.enabled = False
        result = await instance.{method}()
        assert result is None
    
    def test_sync_method(self, instance):
        """同步方法不需要 @pytest.mark.asyncio"""
        result = instance.sync_method()
        assert result == expected
```

## ❌ 避免全局 pytestmark

```python
# ❌ 错误：这会导致所有测试（包括同步）都被当作异步处理
pytestmark = pytest.mark.asyncio

# ✅ 正确：只为需要的异步方法添加装饰器
@pytest.mark.asyncio
async def test_async(): ...

def test_sync(): ...  # 同步测试不需要装饰器
```

## AsyncMock 详细用法

```python
# mock 异步方法返回特定值
mock_async_method = AsyncMock(return_value="expected_result")

# mock 异步方法抛出异常
mock_async_method = AsyncMock(side_effect=Exception("error"))

# mock 异步生成器
async def mock_generator():
    yield item1
    yield item2
mock_async_gen = AsyncMock(side_effect=mock_generator)
```

## 第三方库 Mock

当测试依赖第三方库（如 paho-mqtt）时：

```python
@pytest.fixture
def mock_mqtt_client():
    """Create mock for third-party library client."""
    client = MagicMock()
    client.connect = Mock()
    client.loop_start = Mock()
    client.publish = Mock()
    return client

# 在测试中使用
async def test_start(self, mock_mqtt_client):
    with patch("path.to.module.mqtt.Client", return_value=mock_mqtt_client):
        await instance.start()
    
    mock_mqtt_client.connect.assert_called_once()
```

## Patch 路径注意事项

当测试内部导入的类时，需要 patch 正确的模块路径：

```python
# 场景：被测代码内部导入
# module.py
async def start():
    from external.service import ExternalService  # 运行时导入
    service = ExternalService()
    return await service.connect()

# 测试
# ❌ 错误：patch 被测模块位置
with patch("module.ExternalService"):
    ...

# ✅ 正确：patch 原始导入源
with patch("external.service.ExternalService") as MockService:
    mock_instance = MockService.return_value
    mock_instance.connect = AsyncMock(return_value=True)
    result = await start()
    assert result is True
```

## 日志测试注意事项

**建议**：优先测试功能行为而非日志输出。

```python
# ✅ 推荐：测试功能行为
assert instance.connected is False

# ⚠️ 可选：测试日志（依赖 logging 配置）
caplog.set_level("ERROR", logger="module.name")
assert "error message" in caplog.text
```

不同项目可能有不同的 logging 配置，日志断言可能导致测试不稳定。

## 注意事项

1. 不要在 async test 中使用 time.sleep，改用 asyncio.sleep
2. 并发测试使用 asyncio.gather
3. 测试超时使用 asyncio.wait_for
4. Mockito 对象会被设置为属性，即使方法抛出异常
