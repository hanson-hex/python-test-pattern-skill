# Channel 测试完整示例

## 场景

为 Channel 模块生成完整的单元测试和契约测试。

## 生成的测试结构

```
tests/
├── contract/channels/
│   └── test_my_channel_contract.py   # 契约测试
└── unit/channels/
    └── test_my_channel.py            # 单元测试
```

## 示例代码

### 被测代码

```python
# src/myapp/channels/my_channel.py
from typing import Optional, Callable
from myapp.channels.base import BaseChannel


class MyChannel(BaseChannel):
    """My custom channel implementation."""

    def __init__(
        self,
        handler: Optional[Callable] = None,
        enabled: bool = True,
        api_key: str = "",
        timeout: int = 30,
    ):
        super().__init__(handler=handler, enabled=enabled)
        self.api_key = api_key
        self.timeout = timeout
        self.bot = None

    @classmethod
    def from_env(cls) -> "MyChannel":
        """Create instance from environment variables."""
        import os
        return cls(
            api_key=os.getenv("MY_API_KEY", ""),
            timeout=int(os.getenv("MY_TIMEOUT", "30")),
            enabled=os.getenv("MY_ENABLED", "true").lower() == "true",
        )

    async def start(self) -> None:
        """Start the channel."""
        if not self.enabled:
            return
        self.bot = await self._create_bot()
        await self._start_listening()

    async def stop(self) -> None:
        """Stop the channel."""
        if self.bot:
            await self.bot.close()
            self.bot = None

    async def _create_bot(self):
        """Create bot instance."""
        from some_sdk import Bot
        return Bot(api_key=self.api_key)
```

### 生成的契约测试

```python
# tests/contract/channels/test_my_channel_contract.py
"""MyChannel contract tests."""

from tests.contract.channels import ChannelContractTest
from myapp.channels.my_channel import MyChannel


class TestMyChannelContract(ChannelContractTest):
    """Verify MyChannel satisfies BaseChannel contract."""

    CHANNEL_CLASS = MyChannel

    @classmethod
    def create_instance(cls):
        """Create MyChannel instance for testing."""
        return MyChannel(
            handler=lambda msg: None,
            enabled=True,
            api_key="test_key",
            timeout=30,
        )
```

### 生成的单元测试

```python
# tests/unit/channels/test_my_channel.py
"""MyChannel unit tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from myapp.channels.my_channel import MyChannel


class TestMyChannelInit:
    """Test initialization."""

    def test_init_stores_config(self):
        """Should store all config parameters."""
        channel = MyChannel(
            handler=lambda: None,
            enabled=True,
            api_key="test_key",
            timeout=60,
        )

        assert channel.api_key == "test_key"
        assert channel.timeout == 60
        assert channel.enabled is True

    def test_init_creates_none_bot(self):
        """Should initialize bot as None."""
        channel = MyChannel()

        assert channel.bot is None


class TestMyChannelFromEnv:
    """Test factory method from_env."""

    def test_from_env_reads_vars(self, monkeypatch):
        """Should read from environment variables."""
        monkeypatch.setenv("MY_API_KEY", "env_key")
        monkeypatch.setenv("MY_TIMEOUT", "45")
        monkeypatch.setenv("MY_ENABLED", "true")

        channel = MyChannel.from_env()

        assert channel.api_key == "env_key"
        assert channel.timeout == 45
        assert channel.enabled is True

    def test_from_env_uses_defaults(self, monkeypatch):
        """Should use defaults when vars not set."""
        monkeypatch.delenv("MY_API_KEY", raising=False)
        monkeypatch.delenv("MY_TIMEOUT", raising=False)
        monkeypatch.delenv("MY_ENABLED", raising=False)

        channel = MyChannel.from_env()

        assert channel.api_key == ""
        assert channel.timeout == 30
        assert channel.enabled is True


class TestMyChannelStart:
    """Test start method."""

    @pytest.mark.asyncio
    async def test_start_creates_bot(self):
        """Should create bot when enabled."""
        channel = MyChannel(enabled=True, api_key="test_key")

        with patch.object(channel, "_create_bot", new_callable=AsyncMock) as mock_create:
            mock_bot = MagicMock()
            mock_create.return_value = mock_bot

            await channel.start()

            assert channel.bot is mock_bot
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_skips_when_disabled(self):
        """Should not create bot when disabled."""
        channel = MyChannel(enabled=False)

        with patch.object(channel, "_create_bot", new_callable=AsyncMock) as mock_create:
            await channel.start()

            assert channel.bot is None
            mock_create.assert_not_called()


class TestMyChannelStop:
    """Test stop method."""

    @pytest.mark.asyncio
    async def test_stop_closes_bot(self):
        """Should close and clear bot."""
        channel = MyChannel()
        mock_bot = MagicMock()
        mock_bot.close = AsyncMock()
        channel.bot = mock_bot

        await channel.stop()

        mock_bot.close.assert_called_once()
        assert channel.bot is None

    @pytest.mark.asyncio
    async def test_stop_handles_none_bot(self):
        """Should handle when bot is None."""
        channel = MyChannel()

        # Should not raise
        await channel.stop()

        assert channel.bot is None
```

## 测试执行

```bash
# Run contract tests
pytest tests/contract/channels/test_my_channel_contract.py -v

# Run unit tests
pytest tests/unit/channels/test_my_channel.py -v

# Run with coverage
pytest tests/unit/channels/test_my_channel.py --cov=myapp.channels.my_channel -v
```

## 关键模式说明

1. **AsyncMock**: 用于 mock 异步方法 (`_create_bot`, `close`)
2. **monkeypatch**: 用于修改环境变量
3. **patch.object**: 用于 mock 实例方法
4. **new_callable=AsyncMock**: 将同步 mock 转为异步
