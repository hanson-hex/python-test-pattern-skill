# Python Test Pattern Skill

智能分析 Python 源码并生成高质量单元测试的 Claude Code Skill。

> **English docs**: [README.md](README.md)

## 功能特性

- **智能源码分析** — 自动识别类结构、依赖和测试策略
- **多框架支持** — pytest/unittest、mock、异步测试
- **HTTP/WebSocket Mock** — 完整的外部依赖隔离方案
- **代码质量保证** — 内置 pylint 修复、重复导入处理
- **Pydantic 兼容** — 测试环境版本冲突解决方案

## 适用场景

| 场景 | 说明 |
|------|------|
| 生成单元测试 | 为新功能/模块补充测试 |
| 完善测试覆盖 | 已有测试但覆盖不足 |
| 审查测试质量 | 检查现有测试完整性 |

## 安装

### 方式 1: 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/hanson-hex/python-test-pattern-skill/main/install.sh | bash
```

### 方式 2: 手动安装

```bash
# 克隆仓库
git clone https://github.com/hanson-hex/python-test-pattern-skill.git

# 复制到 Claude Code skills 目录
mkdir -p ~/.claude/skills/
cp -r python-test-pattern-skill ~/.claude/skills/python-test-pattern

# 重启 Claude Code
```

### 方式 3: 项目级安装（团队协作）

```bash
# 复制到项目内，团队成员共享
mkdir -p .claude/skills/
cp -r python-test-pattern-skill .claude/skills/python-test-pattern
git add .claude/skills/python-test-pattern
git commit -m "Add python-test-pattern skill"
```

## 使用方法

在 Claude Code 中提到测试时，Claude 会自动识别并调用此 skill。

### 示例对话

```
"为 Channel 模块生成单元测试"
"检查测试覆盖率是否完整"
"完善 logging 模块的测试"
"为这个类写测试"
```

## Skill 结构

```
python-test-pattern/
├── SKILL.md                         # 技能主定义
├── patterns/                        # 测试模式库
│   ├── sync_unit_test.md            # 同步代码测试
│   ├── async_unit_test.md           # 异步方法测试
│   ├── http_mock.md                 # HTTP 依赖 mock
│   ├── websocket_test.md            # WebSocket 测试
│   ├── complex_method_test.md       # 复杂方法测试
│   ├── exception_test.md            # 异常路径测试
│   ├── class_based_test.md          # 测试类组织方式
│   ├── patch_patterns.md            # Patch 用法详解
│   ├── dataclass_test.md            # Dataclass / Protocol 测试
│   ├── third_party_mock.md          # 第三方库缺失 mock
│   ├── mock_best_practices.md       # Mock 对象最佳实践
│   ├── code_quality_fixes.md        # 代码质量修复
│   ├── project_specific_fixtures.md # 项目 fixture 扩展指南
│   └── test_debugging.md            # 调试与问题处理
├── fixtures/                        # 通用 fixtures
│   └── generic_fixtures.py
└── examples/                        # 使用示例
    ├── channel_test_example.md
    └── http_mock_example.md
```

## 测试模式速查

| 代码特征 | 参考模式 |
|---------|---------|
| 同步函数/类 | `patterns/sync_unit_test.md` |
| 异步方法 | `patterns/async_unit_test.md` |
| HTTP 依赖 | `patterns/http_mock.md` |
| WebSocket | `patterns/websocket_test.md` |
| 复杂方法 | `patterns/complex_method_test.md` |
| 异常处理 | `patterns/exception_test.md` |
| 第三方库缺失 | `patterns/third_party_mock.md` |
| Dataclass / Protocol | `patterns/dataclass_test.md` |

## 核心原则

1. **AAA 模式** — Arrange（准备）→ Act（执行）→ Assert（断言）
2. **Mock 完整性** — 显式设置所有可能访问的属性
3. **异步正确** — 使用 AsyncMock 替代 MagicMock
4. **边界覆盖** — 空值、空列表、异常输入、极限值

## Fixtures 列表

| Fixture | 用途 |
|---------|------|
| `async_noop` | 异步空操作函数 |
| `async_return_value` | 返回特定值的异步函数工厂 |
| `mock_http_response` | HTTP 响应 mock 工厂 |
| `mock_http_session` | HTTP 会话 mock |
| `temp_dir` | 临时目录 |
| `call_counter` | 调用计数器 |
| `event_collector` | 事件收集器 |
| `empty_values` | 常见空值列表（边界测试） |

## 常见问题

### Q: 如何处理缺失的第三方库依赖？

在 `tests/conftest.py` 中统一 mock：

```python
import sys
from unittest.mock import MagicMock

for module in ['thirdparty_sdk', 'external_api']:
    sys.modules[module] = MagicMock()
```

详见 `patterns/third_party_mock.md`

### Q: 如何避免 pre-commit 代码风格错误？

1. **行长度**：限制在 79 字符内
2. **未使用变量**：删除或改为 `_`
3. **导入顺序**：标准库 → 第三方 → 本地

详见 `patterns/code_quality_fixes.md`

### Q: HTTP Mock 选择哪个模式？

| 库 | Mock 类 |
|----|---------|
| aiohttp | MockAiohttpSession |
| httpx | MockHttpxClient |
| requests | MockRequestsResponse |

## 贡献

欢迎提交 Issue 和 PR！

```bash
git clone https://github.com/hanson-hex/python-test-pattern-skill.git
cd python-test-pattern-skill

# 修改后提交
gh pr create
```

## License

MIT
