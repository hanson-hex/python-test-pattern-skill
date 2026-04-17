# Mock Object Best Practices

## Mock Configuration Checklist When Writing Tests

Following this checklist when configuring Mock objects avoids common test failures.

### Checklist 1: MagicMock Attribute Initialization

When using `MagicMock()`, always explicitly initialize these attribute types:

```python
# List/set attributes — initialize to empty list
mock.message.photo = []
mock.message.entities = []
mock.message.attachments = []

# Optional object attributes — initialize to None
mock.message.document = None
mock.message.video = None
mock.message.voice = None
mock.message.audio = None
mock.message.caption_entities = None

# String attributes — initialize to empty string or appropriate value
mock.message.text = ""
mock.message.caption = ""
mock.user.name = "test_user"

# Boolean attributes — explicitly set to True/False
mock.message.is_bot = False
mock.channel.enabled = False
```

**Why this matters:**
MagicMock's default behavior is to return a new MagicMock for any unset attribute.
This causes `if mock.message.photo:` to unexpectedly evaluate as `True`.

---

### Checklist 2: Async Method Mocking

For async methods, use `AsyncMock`:

```python
from unittest.mock import MagicMock, AsyncMock

# Create mock
mock_bot = MagicMock()

# Async methods use AsyncMock
mock_bot.get_file = AsyncMock(return_value=mock_file)
mock_bot.send_message = AsyncMock(return_value=True)
mock_bot.download_file = AsyncMock(return_value=b"file_content")

# Sync methods keep using MagicMock
mock_bot.get_username = MagicMock(return_value="bot_name")
```

**Common mistake:**
```python
# Wrong — regular MagicMock cannot be awaited
mock_bot.get_file = MagicMock(return_value=mock_file)
file = await mock_bot.get_file()  # TypeError!

# Correct
mock_bot.get_file = AsyncMock(return_value=mock_file)
file = await mock_bot.get_file()  # works correctly
```

---

### Checklist 3: Nested Mock Objects

For deeply nested attribute access, create dedicated mock factories:

```python
def create_mock_message(
    text: str = "",
    has_photo: bool = False,
    has_document: bool = False,
) -> MagicMock:
    """Create a fully configured Message Mock."""
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

### Checklist 4: Verify Code Paths Before Writing Tests

Before writing a test, confirm the conditional branches in the code:

```python
# Code under test
def process_message(message):
    if message.photo:          # checkpoint 1
        handle_photo(message.photo)
    elif message.document:     # checkpoint 2
        handle_document(message.document)
    elif message.text:         # checkpoint 3
        handle_text(message.text)
```

Corresponding test configuration:
```python
def test_text_only_message():
    mock_msg = MagicMock()
    mock_msg.photo = []         # disable checkpoint 1
    mock_msg.document = None    # disable checkpoint 2
    mock_msg.text = "Hello"     # enable checkpoint 3
    # ... test code
```

---

### Checklist 5: Config/Options Mock

When testing config classes, pay attention to `None` vs default values:

```python
# Option 1: use actual default values
class MockConfig:
    enabled = False  # not None
    timeout = 30     # not None
    prefix = ""      # empty string, not None

# Option 2: use spec to enforce attribute matching
from unittest.mock import MagicMock
config = MagicMock(spec=ActualConfig)
config.enabled = False
config.timeout = 30
```

**Watch the implementation:**
- `getattr(config, "enabled", False)` — returns default when attribute is missing
- `getattr(config, "enabled", False) or False` — forces `False` when attribute is `None`/empty

Tests should match the actual behavior of the code.

---

## Quick Templates

### Message Mock Template

```python
@pytest.fixture
def mock_message():
    """Fully configured Message Mock."""
    m = MagicMock()
    # Content
    m.text = ""
    m.caption = None
    # Media — empty by default
    m.photo = []
    m.document = None
    m.video = None
    m.voice = None
    m.audio = None
    # Metadata
    m.entities = []
    m.caption_entities = None
    m.message_id = "123"
    # User info
    m.from_user = MagicMock()
    m.from_user.id = "user_123"
    m.from_user.username = "test_user"
    m.from_user.is_bot = False
    return m
```

### Bot/Client Mock Template

```python
@pytest.fixture
def mock_bot():
    """Fully configured Bot Mock."""
    bot = MagicMock()
    bot.username = "test_bot"
    bot.id = "bot_123"
    # Async methods
    bot.get_file = AsyncMock()
    bot.send_message = AsyncMock()
    bot.download_file = AsyncMock(return_value=b"content")
    return bot
```

---

## Debugging Tips

If a test is failing and you suspect a Mock issue:

```python
# Add debug output to inspect actual values
print(f"mock.photo = {mock.message.photo}")
print(f"bool(mock.photo) = {bool(mock.message.photo)}")
print(f"type = {type(mock.message.photo)}")

# This helps surface unexpected MagicMock default return values
```
