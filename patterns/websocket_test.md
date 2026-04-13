# WebSocket 测试模式

## 模式概述

WebSocket 测试需要处理连接生命周期、消息收发、状态管理和重连逻辑。使用此模式测试使用 WebSocket 的组件。

## WebSocket 组件识别

```python
class WebSocketClient:
    def __init__(self):
        self._ws = None
        self._connected = False
        self._message_queue = Queue()

    async def connect(self, uri: str):
        """Establish WebSocket connection."""
        self._ws = await websockets.connect(uri)
        self._connected = True
        asyncio.create_task(self._receive_loop())

    async def send(self, message: dict):
        """Send message through WebSocket."""
        if not self._connected:
            raise ConnectionError("Not connected")
        await self._ws.send(json.dumps(message))

    async def _receive_loop(self):
        """Background receive loop."""
        async for message in self._ws:
            await self._handle_message(message)
```

## Test Patterns

### 1. Connection Lifecycle Tests

```python
class TestWebSocketLifecycle:
    """Test WebSocket connection lifecycle."""

    @pytest.mark.asyncio
    async def test_connect_establishes_connection(self, client, mock_ws):
        """Test connection establishment."""
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = mock_ws
            await client.connect("wss://example.com/ws")
            mock_connect.assert_called_once_with("wss://example.com/ws")

    @pytest.mark.asyncio
    async def test_connect_starts_receive_loop(self, client, mock_ws):
        """Test receive loop starts after connection."""
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = mock_ws
            with patch.object(client, '_receive_loop') as mock_loop:
                await client.connect("wss://example.com/ws")
                mock_loop.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_closes_websocket(self, client, mock_ws):
        """Test clean disconnection."""
        client._ws = mock_ws
        client._connected = True

        await client.disconnect()

        mock_ws.close.assert_called_once()
        assert not client._connected
```

### 2. Message Send Tests

```python
class TestWebSocketSend:
    """Test sending messages through WebSocket."""

    @pytest.mark.asyncio
    async def test_send_serializes_json(self, client, mock_ws):
        """Test message serialization."""
        client._ws = mock_ws
        client._connected = True

        message = {"type": "chat", "content": "hello"}
        await client.send(message)

        mock_ws.send.assert_called_once_with('{"type": "chat", "content": "hello"}')

    @pytest.mark.asyncio
    async def test_send_raises_when_disconnected(self, client):
        """Test send fails gracefully when not connected."""
        with pytest.raises(ConnectionError, match="Not connected"):
            await client.send({"type": "test"})

    @pytest.mark.asyncio
    async def test_send_binary_data(self, client, mock_ws):
        """Test sending binary messages."""
        client._ws = mock_ws
        client._connected = True

        binary_data = b"\x00\x01\x02\x03"
        await client.send_binary(binary_data)

        mock_ws.send.assert_called_once_with(binary_data)
```

### 3. Message Receive Tests

```python
class TestWebSocketReceive:
    """Test receiving messages from WebSocket."""

    @pytest.mark.asyncio
    async def test_receive_parses_json(self, client, mock_ws):
        """Test JSON message parsing."""
        mock_ws.__aiter__ = AsyncMock(return_value=iter([
            '{"type": "message", "content": "hello"}',
        ]))

        with patch.object(client, '_handle_message') as mock_handler:
            await client._receive_loop()
            mock_handler.assert_called_once_with({"type": "message", "content": "hello"})

    @pytest.mark.asyncio
    async def test_receive_handles_malformed_json(self, client, mock_ws, caplog):
        """Test graceful handling of malformed messages."""
        mock_ws.__aiter__ = AsyncMock(return_value=iter([
            'invalid json {',
        ]))

        with caplog.at_level(logging.ERROR):
            await client._receive_loop()

        assert "JSON decode error" in caplog.text
```

### 4. Reconnection Tests

```python
class TestWebSocketReconnection:
    """Test WebSocket reconnection logic."""

    @pytest.mark.asyncio
    async def test_reconnect_on_abnormal_close(self, client):
        """Test automatic reconnection after abnormal close."""
        connect_calls = []

        async def mock_connect(*args, **kwargs):
            connect_calls.append(1)
            if len(connect_calls) == 1:
                raise websockets.ConnectionClosed(None, None)
            return MagicMock()

        with patch('websockets.connect', mock_connect):
            await client.connect_with_retry("wss://example.com/ws")
            assert len(connect_calls) == 2  # Initial + retry

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, client):
        """Test reconnection backoff strategy."""
        delays = []

        async def mock_sleep(delay):
            delays.append(delay)

        with patch('asyncio.sleep', mock_sleep):
            with patch('websockets.connect', side_effect=[
                websockets.ConnectionClosed(None, None),
                websockets.ConnectionClosed(None, None),
                MagicMock(),  # Success on 3rd try
            ]):
                await client.connect_with_retry("wss://example.com/ws", max_retries=3)

        # Verify exponential backoff: 1s, 2s
        assert delays == [1.0, 2.0]

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, client):
        """Test failure after max retries."""
        with patch('websockets.connect', side_effect=websockets.ConnectionClosed(None, None)):
            with pytest.raises(ConnectionError, match="Max retries exceeded"):
                await client.connect_with_retry("wss://example.com/ws", max_retries=3)
```

### 5. State Management Tests

```python
class TestWebSocketState:
    """Test WebSocket state management."""

    def test_initial_state(self, client):
        """Test initial state."""
        assert not client._connected
        assert client._ws is None

    @pytest.mark.asyncio
    async def test_state_transitions(self, client, mock_ws):
        """Test state transitions during connect/disconnect."""
        with patch('websockets.connect', new_callable=AsyncMock) as mock_connect:
            mock_connect.return_value = mock_ws

            # Initially disconnected
            assert not client._connected

            # After connect
            await client.connect("wss://example.com/ws")
            assert client._connected

            # After disconnect
            await client.disconnect()
            assert not client._connected

    def test_concurrent_access_thread_safe(self, client):
        """Test thread-safe state access."""
        errors = []

        def toggle_state():
            try:
                for _ in range(100):
                    client._connected = not client._connected
                    _ = client._connected
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=toggle_state) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
```

### 6. Heartbeat Tests

```python
class TestWebSocketHeartbeat:
    """Test WebSocket heartbeat/ping-pong."""

    @pytest.mark.asyncio
    async def test_heartbeat_sent_periodically(self, client, mock_ws):
        """Test periodic heartbeat."""
        client._ws = mock_ws
        client._connected = True

        # Start heartbeat with short interval for testing
        heartbeat_task = asyncio.create_task(
            client._heartbeat_loop(interval=0.1)
        )

        # Let it run briefly
        await asyncio.sleep(0.25)
        heartbeat_task.cancel()

        # Should have sent ~2 heartbeats
        assert mock_ws.ping.call_count >= 2

    @pytest.mark.asyncio
    async def test_missing_pong_triggers_reconnect(self, client, mock_ws):
        """Test reconnection when pong not received."""
        client._ws = mock_ws
        client._connected = True

        with patch.object(client, 'reconnect') as mock_reconnect:
            with patch.object(mock_ws, 'pong', new_callable=AsyncMock) as mock_pong:
                mock_pong.side_effect = asyncio.TimeoutError()
                await client._heartbeat_loop(interval=0.1, timeout=0.05)
                mock_reconnect.assert_called_once()
```

## Mock Fixtures

```python
@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket connection."""
    ws = MagicMock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock(return_value='{"type": "test"}')
    ws.close = AsyncMock()
    ws.ping = AsyncMock()
    ws.pong = AsyncMock()
    return ws


@pytest.fixture
def mock_websocket_client():
    """Create a mock WebSocket client factory."""
    def factory():
        client = MagicMock()
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()
        client.send = AsyncMock()
        client.receive = AsyncMock(return_value={"type": "message"})
        return client
    return factory
```

## Async Iterator Mocking

```python
def async_iter(items):
    """Helper to create async iterator for mocking."""
    async def generator():
        for item in items:
            yield item
    return generator()


# Usage in tests
@pytest.mark.asyncio
async def test_receive_multiple_messages(client, mock_ws):
    """Test receiving multiple messages."""
    messages = [
        '{"type": "msg1"}',
        '{"type": "msg2"}',
        '{"type": "msg3"}',
    ]
    mock_ws.__aiter__ = lambda self: async_iter(messages)

    received = []
    with patch.object(client, '_handle_message', side_effect=lambda m: received.append(m)):
        await client._receive_loop()

    assert len(received) == 3
```

## Testing WebSocket Handlers

```python
class TestWebSocketHandlers:
    """Test message type handlers."""

    @pytest.mark.asyncio
    async def test_dispatch_by_message_type(self, client):
        """Test message type dispatch."""
        with patch.object(client, '_handle_text') as mock_text:
            with patch.object(client, '_handle_image') as mock_image:
                await client._dispatch_message({"type": "text"})
                mock_text.assert_called_once()
                mock_image.assert_not_called()

    @pytest.mark.asyncio
    async def test_unknown_type_logged(self, client, caplog):
        """Test unknown message types are logged."""
        with caplog.at_level(logging.WARNING):
            await client._dispatch_message({"type": "unknown"})
        assert "unknown message type" in caplog.text.lower()
```

## Best Practices

1. **Mock the library, not the protocol**: Mock `websockets.connect` not individual frames
2. **Test reconnection thoroughly**: WebSocket connections are unreliable
3. **Verify cleanup**: Ensure connections are closed properly
4. **Test concurrent access**: WebSocket methods may be called from multiple threads
5. **Use short timeouts**: Keep test execution fast

## Test Template

```python
class Test{ClientName}WebSocket:
    """P1: WebSocket tests for {ClientName}.

    Covers:
    - Connection lifecycle
    - Message send/receive
    - Reconnection logic
    - Heartbeat/ping-pong
    - Error handling
    """

    # === Connection Lifecycle ===

    @pytest.mark.asyncio
    async def test_{operation}_establishes_connection(self, instance, mock_ws):
        """Test connection establishment."""
        pass

    @pytest.mark.asyncio
    async def test_{operation}_clean_disconnection(self, instance, mock_ws):
        """Test clean disconnect."""
        pass

    # === Message Operations ===

    @pytest.mark.asyncio
    async def test_send_{message_type}_success(self, instance, mock_ws):
        """Test sending {message_type} message."""
        pass

    @pytest.mark.asyncio
    async def test_receive_{message_type}_handled(self, instance, mock_ws):
        """Test receiving {message_type} message."""
        pass

    # === Reconnection ===

    @pytest.mark.asyncio
    async def test_reconnect_after_disconnect(self, instance):
        """Test reconnection logic."""
        pass

    # === Error Handling ===

    @pytest.mark.asyncio
    async def test_{operation}_error_handled(self, instance, mock_ws):
        """Test error handling."""
        pass
```
