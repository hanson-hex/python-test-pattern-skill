# Mock 对象最佳实践

## 生成测试时的 Mock 配置检查清单

当你在编写测试时，按照以下清单配置 Mock 对象，可以避免常见的测试失败。

### 清单 1: MagicMock 属性初始化

在使用 `MagicMock()` 时，务必显式初始化以下类型的属性：

```python
# 列表/集合属性 - 初始化为空列表
mock.message.photo = []
mock.message.entities = []
mock.message.attachments = []

# 可选对象属性 - 初始化为 None
mock.message.document = None
mock.message.video = None
mock.message.voice = None
mock.message.audio = None
mock.message.caption_entities = None

# 字符串属性 - 初始化为空字符串或适当值
mock.message.text = ""
mock.message.caption = ""
mock.user.name = "test_user"

# 布尔属性 - 明确设置为 True/False
mock.message.is_bot = False
mock.channel.enabled = False
```

**为什么重要：**
MagicMock 的默认行为是为未设置的属性返回新的 MagicMock 对象。这会导致条件判断 `if mock.message.photo:` 意外为 True。

---

### 清单 2: 异步方法 Mock

对于异步方法，使用 `AsyncMock`：

```python
from unittest.mock import MagicMock, AsyncMock

# 创建 mock
mock_bot = MagicMock()

# 异步方法使用 AsyncMock
mock_bot.get_file = AsyncMock(return_value=mock_file)
mock_bot.send_message = AsyncMock(return_value=True)
mock_bot.download_file = AsyncMock(return_value=b"file_content")

# 同步方法保持使用 MagicMock
mock_bot.get_username = MagicMock(return_value="bot_name")
```

**常见错误：**
```python
# 错误 - 普通 MagicMock 不能 await
mock_bot.get_file = MagicMock(return_value=mock_file)
file = await mock_bot.get_file()  # TypeError!

# 正确
mock_bot.get_file = AsyncMock(return_value=mock_file)
file = await mock_bot.get_file()  # 正常工作
```

---

### 清单 3: 嵌套 Mock 对象

对于深层嵌套的属性访问，创建专门的 Mock 工厂：

```python
def create_mock_message(
    text: str = "",
    has_photo: bool = False,
    has_document: bool = False,
) -> MagicMock:
    """创建配置完整的 Message Mock."""
    mock = MagicMock()
    mock.text = text
    mock.caption = None
    mock.photo = [] if not has_photo else [MagicMock(file_id="photo_123")]
    mock.document = None if not has_document else MagicMock(file_id="doc_123")
    mock.video = None
    mock.voice = None
    mock.audio = None
    mock.entities = []
    mock.caption_entities = None
    return mock
```

---

### 清单 4: 测试前验证代码路径

在编写测试前，确认代码中的条件分支：

```python
# 被测代码
def process_message(message):
    if message.photo:  # 检查点 1
        handle_photo(message.photo)
    elif message.document:  # 检查点 2
        handle_document(message.document)
    elif message.text:  # 检查点 3
        handle_text(message.text)
```

对应的测试配置：
```python
def test_text_only_message():
    mock_msg = MagicMock()
    mock_msg.photo = []  # 禁用检查点 1
    mock_msg.document = None  # 禁用检查点 2
    mock_msg.text = "Hello"  # 启用检查点 3
    # ... 测试代码
```

---

### 清单 5: Config/Options Mock

测试配置类时，注意 None 和缺省值的处理：

```python
# 选项 1: 使用实际默认值
class MockConfig:
    enabled = False  # 不是 None
    timeout = 30  # 不是 None
    prefix = ""  # 空字符串而不是 None

# 选项 2: 使用 spec 确保属性匹配
from unittest.mock import MagicMock
config = MagicMock(spec=ActualConfig)
config.enabled = False
config.timeout = 30
```

**注意代码实现：**
- `getattr(config, "enabled", False)` - 当属性不存在时返回默认值
- `getattr(config, "enabled", False) or False` - 当属性为 None/空时强制为 False

测试应匹配代码的实际行为。

---

## 快速模板

### 消息类 Mock 模板

```python
@pytest.fixture
def mock_message():
    """配置完整的 Message Mock."""
    m = MagicMock()
    # 内容
    m.text = ""
    m.caption = None
    # 媒体 - 默认空
    m.photo = []
    m.document = None
    m.video = None
    m.voice = None
    m.audio = None
    # 元数据
    m.entities = []
    m.caption_entities = None
    m.message_id = "123"
    # 用户信息
    m.from_user = MagicMock()
    m.from_user.id = "user_123"
    m.from_user.username = "test_user"
    m.from_user.is_bot = False
    return m
```

### 机器人/客户端 Mock 模板

```python
@pytest.fixture
def mock_bot():
    """配置完整的 Bot Mock."""
    bot = MagicMock()
    bot.username = "test_bot"
    bot.id = "bot_123"
    # 异步方法
    bot.get_file = AsyncMock()
    bot.send_message = AsyncMock()
    bot.download_file = AsyncMock(return_value=b"content")
    return bot
```

---

## 调试技巧

如果测试失败时怀疑是 Mock 问题：

```python
# 添加调试输出查看实际值
print(f"mock.photo = {mock.message.photo}")
print(f"bool(mock.photo) = {bool(mock.message.photo)}")
print(f"type = {type(mock.message.photo)}")

# 这将帮助你发现 MagicMock 默认返回值问题
```
