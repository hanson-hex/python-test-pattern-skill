# Dataclass / Protocol Test Pattern

## Overview

Testing strategy for Python `dataclass`, `Protocol`, `TypedDict`, and similar structural types.
These look simple, but often contain significant business constraints — field defaults,
`__post_init__` validation, `from_*` factory methods — making them high-value and easy to test.

---

## 1. Dataclass Basic Tests

### What to Test

- Required field assignment
- Optional field default values
- `__post_init__` validation logic
- Isolation of `field(default_factory=...)` (each instance is independent)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class CallSession:
    call_sid: str
    from_number: str
    to_number: str
    status: str = "initiated"
    transcript: list = field(default_factory=list)
    meta Optional[dict] = None
```

```python
# tests/unit/test_call_session.py
class TestCallSessionDefaults:
    """P0: Field defaults and isolation."""

    def test_required_fields_stored(self):
        session = CallSession(call_sid="CA123", from_number="+1", to_number="+2")
        assert session.call_sid == "CA123"
        assert session.from_number == "+1"

    def test_default_status(self):
        session = CallSession(call_sid="CA123", from_number="+1", to_number="+2")
        assert session.status == "initiated"

    def test_transcript_is_isolated_per_instance(self):
        """default_factory ensures each instance has its own list."""
        s1 = CallSession(call_sid="CA1", from_number="+1", to_number="+2")
        s2 = CallSession(call_sid="CA2", from_number="+1", to_number="+2")
        s1.transcript.append("hello")
        assert s2.transcript == []  # must not be polluted by s1

    def test_optional_metadata_defaults_none(self):
        session = CallSession(call_sid="CA1", from_number="+1", to_number="+2")
        assert session.metadata is None
```

---

## 2. `__post_init__` Validation Tests

```python
@dataclass
class ChannelAddress:
    platform: str
    address: str

    def __post_init__(self):
        if not self.address:
            raise ValueError("address cannot be empty")
        self.platform = self.platform.lower()
```

```python
class TestChannelAddressValidation:
    """P0: Validation at construction time."""

    def test_empty_address_raises(self):
        with pytest.raises(ValueError, match="address cannot be empty"):
            ChannelAddress(platform="slack", address="")

    def test_platform_normalized_to_lowercase(self):
        addr = ChannelAddress(platform="Slack", address="U123")
        assert addr.platform == "slack"
```

---

## 3. `from_*` Factory Method Tests

```python
@dataclass
class Config:
    host: str
    port: int

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        return cls(host=data["host"], port=int(data.get("port", 8080)))

    @classmethod
    def from_env(cls) -> "Config":
        import os
        return cls(host=os.environ["HOST"], port=int(os.environ.get("PORT", 8080)))
```

```python
class TestConfigFactory:
    """P1: Factory methods."""

    def test_from_dict_basic(self):
        cfg = Config.from_dict({"host": "localhost", "port": "9000"})
        assert cfg.host == "localhost"
        assert cfg.port == 9000

    def test_from_dict_default_port(self):
        cfg = Config.from_dict({"host": "localhost"})
        assert cfg.port == 8080

    def test_from_env_reads_env(self, monkeypatch):
        monkeypatch.setenv("HOST", "myhost")
        monkeypatch.setenv("PORT", "7777")
        cfg = Config.from_env()
        assert cfg.host == "myhost"
        assert cfg.port == 7777

    def test_from_env_missing_required_raises(self, monkeypatch):
        monkeypatch.delenv("HOST", raising=False)
        with pytest.raises(KeyError):
            Config.from_env()
```

---

## 4. Protocol Tests

The Protocol itself doesn't need to be tested, but verifying that
**concrete implementations satisfy the Protocol contract** is valuable.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class MessageConverter(Protocol):
    def to_text(self, msg: dict) -> str: ...
    def from_text(self, text: str) -> dict: ...
```

```python
class TestMessageConverterProtocol:
    """P1: Verify implementations satisfy the Protocol."""

    def test_concrete_impl_satisfies_protocol(self):
        from myapp.channels.slack import SlackConverter
        converter = SlackConverter()
        assert isinstance(converter, MessageConverter)

    def test_protocol_methods_callable(self):
        from myapp.channels.slack import SlackConverter
        converter = SlackConverter()
        result = converter.to_text({"text": "hello"})
        assert isinstance(result, str)
```

---

## 5. Format Detection Logic Tests

When code selects a processing path based on input format
(e.g., key format detection, encoding detection),
cover every branch.

```python
def detect_key_format(key: bytes) -> str:
    """Returns 'hex', 'base64', or 'raw'."""
    try:
        decoded = bytes.fromhex(key.decode())
        if len(decoded) in (16, 24, 32):
            return 'hex'
    except (ValueError, UnicodeDecodeError):
        pass
    try:
        import base64
        decoded = base64.b64decode(key)
        if len(decoded) in (16, 24, 32):
            return 'base64'
    except Exception:
        pass
    return 'raw'
```

```python
class TestDetectKeyFormat:
    """P0: Cover all format branches."""

    def test_hex_key_16_bytes(self):
        key = b"0" * 32  # 32 hex chars = 16 bytes
        assert detect_key_format(key) == "hex"

    def test_base64_key_32_bytes(self):
        import base64
        raw = b"a" * 32
        key = base64.b64encode(raw)
        assert detect_key_format(key) == "base64"

    def test_raw_key_returned_as_is(self):
        key = b"not-hex-not-base64!!!"
        assert detect_key_format(key) == "raw"

    def test_empty_key_returns_raw(self):
        assert detect_key_format(b"") == "raw"
```

---

## 6. Priority Decision Table

| Scenario | Priority | Reason |
|----------|----------|--------|
| `__post_init__` validation | P0 | Triggered at construction; failures affect all callers |
| `from_*` factory methods | P0 | Primary creation entrypoint; field mapping errors are hard to spot |
| Field default values | P1 | Implicit behavior; easily broken by upgrades |
| `field(default_factory)` isolation | P1 | Classic Python pitfall — shared mutable defaults |
| Protocol compliance | P1 | Enforces interface contract; catches regressions during refactors |
| Format detection branches | P0 | Each branch is a distinct business path; missing one = blind spot |

---

## 7. Handle Optional Dependencies with `@pytest.mark.skipif`

```python
import pytest

try:
    from Crypto.Cipher import AES
    HAS_PYCRYPTO = True
except ImportError:
    HAS_PYCRYPTO = False

@pytest.mark.skipif(not HAS_PYCRYPTO, reason="pycryptodome not installed")
class TestAESEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        ...
```
