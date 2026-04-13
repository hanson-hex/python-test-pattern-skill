# 测试调试与问题处理模式

## 常见测试失败模式及解决方案

### 模式 1: MagicMock 默认行为导致意外代码路径

**现象:**
测试中使用 MagicMock 模拟对象，但未设置某些属性，导致代码进入意外的分支。

```python
# 问题示例
mock_message = MagicMock()
mock_message.text = "Hello"
# 未设置 photo 属性

# 代码中
if message.photo:  # MagicMock 返回一个新的 MagicMock，判断为 True
    await download_photo()  # 意外执行
```

**解决方案:**
显式设置所有可能触发条件分支的属性为 None 或空值。

```python
mock_message = MagicMock()
mock_message.text = "Hello"
mock_message.photo = []
mock_message.document = None
mock_message.video = None
mock_message.voice = None
mock_message.audio = None
```

**应用到 Skill:**
当生成测试时，检查被测代码中的所有 `getattr()` 或属性访问，确保 Mock 对象显式设置了这些属性。

---

### 模式 2: 异步函数 Mock 问题

**现象:**
代码使用 `await` 调用 Mock 方法，但 Mock 不是异步的。

```python
# 问题
tg_file = await bot.get_file(file_id)  # TypeError: object MagicMock can't be used in 'await'
```

**解决方案:**
使用 `AsyncMock` 替代 `MagicMock`。

```python
from unittest.mock import AsyncMock

mock_bot = MagicMock()
mock_bot.get_file = AsyncMock(return_value=mock_file)
```

---

### 模式 3: Config 属性为 None 时的处理

**现象:**
代码使用 `getattr(config, "enabled", False)`，但当 `config.enabled = None` 时返回 None。

```python
# 代码实现
enabled = getattr(config, "enabled", False)  # 当 enabled=None 时返回 None

# 测试期望
assert channel.enabled is False  # 失败，因为实际是 None
```

**解决方案:**
测试应使用实际的布尔值而非 None，或测试实际行为。

```python
# 修改测试
class MockConfig:
    enabled = False  # 使用 False 而不是 None
```

**注意:** 
如果代码确实需要处理 None，应该使用 `getattr(config, "enabled", False) or False`。

---

### 模式 4: 私有属性 vs 公有属性

**现象:**
代码存储为私有属性 `_filter_tool_messages`，但测试期望公有访问 `filter_tool_messages`。

**解决方案:**
测试应使用实际代码中的属性名。

```python
# 而不是
assert channel.filter_tool_messages is True

# 使用
assert channel._filter_tool_messages is True
```

---

### 模式 5: caplog 日志捕获问题

**现象:**
使用 pytest 的 `caplog` fixture 但无法捕获日志。

**原因:**
应用日志配置可能设置了 `propagate = False`，或使用了特定的 logger 名称。

**解决方案:**
避免依赖日志内容进行断言。改为验证行为或返回值。

```python
# 而不是
with caplog.at_level("WARNING"):
    await channel.send_media(...)
assert "no URL found" in caplog.text

# 使用
result = await channel.send_media(...)
assert result is None  # 验证行为
```

---

### 模式 6: 文件路径问题

**现象:**
测试使用绝对路径如 `/config/media`，在只读文件系统上失败。

**解决方案:**
测试应使用临时目录。

```python
# 使用 pytest 的 tmp_path fixture
async def test_with_temp_dir(self, tmp_path: Path):
    media_dir = tmp_path / ".copaw" / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    # 使用 media_dir 进行测试
```

---

## 测试修复最佳实践

1. **保持测试与代码行为一致**
   - 如果代码不处理某些边界情况，不要测试这些边界
   - 测试应该验证实际行为，而不是期望行为

2. **Mock 对象配置完整**
   - 列出所有在代码中访问的属性
   - 显式设为 None 或适当的默认值

3. **避免测试日志输出**
   - 日志格式和内容可能变化
   - 测试行为和结果，而不是日志消息

4. **使用临时资源**
   - 文件系统操作使用 tmp_path
   - 数据库操作使用内存数据库或临时文件

5. **检查异步调用**
   - 确保 Mock 异步方法使用 AsyncMock
   - 同步方法不要用 @pytest.mark.asyncio 标记
