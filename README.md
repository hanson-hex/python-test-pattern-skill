# Python Test Pattern Skill

A Claude Code Skill that intelligently analyzes Python source code and auto-generates high-quality unit tests.

> **中文文档**: [README_zh.md](README_zh.md)

## Features

- **Smart source analysis** — automatically identifies class structure, dependencies, and test strategy
- **Multi-framework support** — pytest/unittest, mock, async testing
- **HTTP/WebSocket mock** — complete isolation for external dependencies
- **Code quality assurance** — built-in pylint fixes, duplicate import handling
- **Pydantic compatible** — resolves version conflict issues in test environments

## When to Use

| Scenario | Description |
|----------|-------------|
| Generate unit tests | Add coverage for new features/modules |
| Improve test coverage | Existing tests are insufficient |
| Review test quality | Check whether current tests are complete |

## Installation

### Option 1: One-line install

```bash
curl -fsSL https://raw.githubusercontent.com/hanson-hex/python-test-pattern-skill/main/install.sh | bash
```

### Option 2: Manual install

```bash
# Clone the repo
git clone https://github.com/hanson-hex/python-test-pattern-skill.git

# Copy to Claude Code skills directory
mkdir -p ~/.claude/skills/
cp -r python-test-pattern-skill ~/.claude/skills/python-test-pattern

# Restart Claude Code
```

### Option 3: Project-level install (team sharing)

```bash
# Copy into the project for shared team use
mkdir -p .claude/skills/
cp -r python-test-pattern-skill .claude/skills/python-test-pattern
git add .claude/skills/python-test-pattern
git commit -m "Add python-test-pattern skill"
```

## Usage

In Claude Code, mention testing and Claude will automatically recognize and apply this skill.

### Example Prompts

```
"Generate unit tests for the Channel module"
"Check if test coverage is complete"
"Improve tests for the logging module"
"Write tests for this class"
```

## Skill Structure

```
python-test-pattern/
├── SKILL.md                         # Skill definition
├── patterns/                        # Test pattern library
│   ├── sync_unit_test.md            # Sync code tests
│   ├── async_unit_test.md           # Async method tests
│   ├── http_mock.md                 # HTTP dependency mock
│   ├── websocket_test.md            # WebSocket tests
│   ├── complex_method_test.md       # Complex method tests
│   ├── exception_test.md            # Exception path tests
│   ├── class_based_test.md          # Test class organization
│   ├── patch_patterns.md            # Patch usage guide
│   ├── dataclass_test.md            # Dataclass / Protocol tests
│   ├── third_party_mock.md          # Missing third-party lib mock
│   ├── mock_best_practices.md       # Mock object best practices
│   ├── code_quality_fixes.md        # Code quality fixes
│   ├── project_specific_fixtures.md # Project fixture extension guide
│   └── test_debugging.md            # Debugging & troubleshooting
├── fixtures/                        # Common fixtures
│   └── generic_fixtures.py
└── examples/                        # Usage examples
    ├── channel_test_example.md
    └── http_mock_example.md
```

## Pattern Quick Reference

| Code Characteristic | Pattern |
|---------------------|---------|
| Sync functions/classes | `patterns/sync_unit_test.md` |
| Async methods | `patterns/async_unit_test.md` |
| HTTP dependencies | `patterns/http_mock.md` |
| WebSocket | `patterns/websocket_test.md` |
| Complex methods | `patterns/complex_method_test.md` |
| Exception handling | `patterns/exception_test.md` |
| Missing third-party libs | `patterns/third_party_mock.md` |
| Dataclass / Protocol | `patterns/dataclass_test.md` |

## Core Principles

1. **AAA Pattern** — Arrange → Act → Assert
2. **Complete mocks** — explicitly set all attributes that may be accessed
3. **Async correctness** — use `AsyncMock` instead of `MagicMock` for async methods
4. **Boundary coverage** — None, empty list, invalid input, extreme values

## Fixtures

| Fixture | Purpose |
|---------|---------|
| `async_noop` | Async no-op function |
| `async_return_value` | Factory for async functions returning specific values |
| `mock_http_response` | HTTP response mock factory |
| `mock_http_session` | HTTP session mock |
| `temp_dir` | Temporary directory |
| `call_counter` | Call counter |
| `event_collector` | Event collector |
| `empty_values` | Common empty values for boundary testing |

## FAQ

### Q: How to handle missing third-party library dependencies?

Mock them in `tests/conftest.py`:

```python
import sys
from unittest.mock import MagicMock

for module in ['thirdparty_sdk', 'external_api']:
    sys.modules[module] = MagicMock()
```

See `patterns/third_party_mock.md`.

### Q: How to avoid pre-commit style errors?

1. **Line length**: limit to 79 characters
2. **Unused variables**: delete or rename to `_`
3. **Import order**: stdlib → third-party → local

See `patterns/code_quality_fixes.md`.

### Q: Which HTTP mock should I use?

| Library | Mock Class |
|---------|------------|
| aiohttp | MockAiohttpSession |
| httpx | MockHttpxClient |
| requests | MockRequestsResponse |

## Contributing

Issues and PRs are welcome!

```bash
git clone https://github.com/hanson-hex/python-test-pattern-skill.git
cd python-test-pattern-skill

# Make changes and submit
gh pr create
```

## License

MIT
