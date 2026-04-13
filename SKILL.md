---
name: python-test-pattern
description: Python 测试技能，通过分析源码自动生成单元测试。支持 pytest/unittest、mock、异步测试、HTTP/WebSocket mock。
version: 0.3.0
---

# Python 测试生成器

智能分析 Python 源码并生成高质量单元测试。

## When to Activate

- 生成单元测试：需要为新功能/模块补充测试时
- 完善测试覆盖：已有测试但覆盖不足时
- 审查测试质量：检查现有测试是否完整时

## 工作流程

### Step 1: 分析源码结构

识别被测代码的特征：

```
1. 读取源文件，识别：
   - 类和函数定义
   - 构造函数参数和初始化逻辑
   - 外部依赖（HTTP、数据库、文件系统等）
   - 同步 vs 异步方法
   - 工厂方法（from_env, from_config）

2. 确定测试策略：
   - 简单函数 → 直接断言测试
   - 外部依赖 → mock 隔离测试
   - HTTP 调用 → HTTP mock 测试
   - WebSocket → async mock 测试
   - 文件操作 → temp file fixture
```

### Step 2: 选择测试模式

| 代码特征 | 参考模式 |
|---------|---------|
| 同步函数/类 | sync_unit_test.md |
| 异步方法 | async_unit_test.md |
| HTTP 依赖 | http_mock.md |
| WebSocket | websocket_test.md |
| 回调机制 | async_unit_test.md |
| 工厂方法 | sync_unit_test.md |
| 复杂方法（多分支/多步骤） | complex_method_test.md |
| 异常路径/错误处理 | exception_test.md |
| 第三方库缺失 | third_party_mock.md |

### Step 3: 生成测试代码

按照 AAA 模式（Arrange-Act-Assert）生成测试：

```python
# 1. Arrange：准备测试数据和 mock
@pytest.fixture
def instance():
    """创建 {Class} 实例"""
    return {Class}(...)

# 2. Act：执行被测代码
result = instance.method()

# 3. Assert：验证结果
assert result == expected
```

### Step 4: 补充边界条件

为每个测试方法补充边界测试：

| 边界类型 | 测试用例 |
|---------|---------|
| 空值/None | test_{method}_with_none |
| 空列表/字符串 | test_{method}_with_empty |
| 异常输入 | test_{method}_invalid_input_raises |
| 极限值 | test_{method}_max_length |
| 禁用状态 | test_{method}_when_disabled |

## 模式参考

| 模式文件 | 适用场景 |
|---------|---------|
| `patterns/sync_unit_test.md` | 同步函数/类测试 |
| `patterns/async_unit_test.md` | 异步方法测试 |
| `patterns/http_mock.md` | HTTP 依赖 mock |
| `patterns/class_based_test.md` | 测试类组织方式 |
| `patterns/patch_patterns.md` | Patch 用法详解 |
| `patterns/third_party_mock.md` | 第三方库缺失 mock |
| `patterns/complex_method_test.md` | 复杂方法测试 |
| `patterns/exception_test.md` | 异常路径测试 |
| `patterns/websocket_test.md` | WebSocket 测试 |
| `patterns/test_debugging.md` | 测试调试与问题处理 |
| `patterns/mock_best_practices.md` | Mock 对象最佳实践 |

## Fixtures

技能提供以下通用 fixtures (`fixtures/generic_fixtures.py`):

| Fixture | 用途 |
|---------|------|
| `async_noop` | 异步空操作函数 |
| `async_return_value` | 返回特定值的异步函数工厂 |
| `mock_http_response` | HTTP 响应 mock 工厂 |
| `mock_http_session` | HTTP 会话 mock |
| `temp_dir` | 临时目录 (tmp_path alias) |
| `call_counter` | 调用计数器 |
| `event_collector` | 事件收集器 |
| `empty_values` | 常见空值列表 (边界测试) |

项目特定的 fixtures 应放在项目的 `tests/conftest.py` 中。

## HTTP Mock

```python
# 创建 mock 响应
mock_resp = mock_http_response(
    status=200,
    json_data={"success": True}
)

# 配置 mock session
mock_session = MagicMock()
mock_session.post = AsyncMock(return_value=mock_resp)

# 执行测试
result = await instance.api_call()
assert result is True
mock_session.post.assert_called_once()
```

对于复杂的 HTTP mock 需求，请在项目中创建自己的 MockHttpSession。

## 代码质量保证

生成测试后，检查以下常见问题：

| 检查项 | 问题 | 解决方案 |
|--------|------|----------|
| **行长度** | E501: Line too long | 使用括号换行或变量提取 |
| **重复导入** | W0404: Reimport | 统一放在文件顶部导入 |
| **Pydantic 版本** | 测试环境导入失败 | Mock 整个模块或避开 Pydantic |

详见 `patterns/code_quality_fixes.md`

## 常见问题

### Q1: 如何处理缺失的第三方库依赖？

在 `tests/conftest.py` 中统一 mock：

```python
import sys
from unittest.mock import MagicMock

# Mock 缺失的第三方库
for module in ['thirdparty_sdk', 'external_api']:
    sys.modules[module] = MagicMock()
```

详见 `patterns/third_party_mock.md`

### Q2: 如何避免 pre-commit 代码风格错误？

生成测试时注意：

1. **行长度**：限制在 79 字符内
2. **未使用变量**：删除或改为 `_`
3. **导入顺序**：标准库 → 第三方 → 本地
4. **类型注解**：避免前向引用，使用字符串引号

示例：
```python
# ✅ 正确
def test_example(my_client):  # 不用类型注解
    pass

# ❌ 避免
from __future__ import annotations  # Python 3.7+ 可用
# 但 mypy 可能报错，建议省略测试函数的返回类型注解
```

### Q3: HTTP Mock 选择哪个模式？

根据项目使用的 HTTP 库选择：

| 库 | Mock 类 |
|----|---------|
| aiohttp | MockAiohttpSession |
| httpx | MockHttpxClient |
| requests | MockRequestsResponse |

### Q4: 测试类如何组织？

按优先级和功能组织：

```python
class Test{ClassName}Init:  # P0: 初始化
class Test{ClassName}FactoryMethods:  # P0: 工厂方法
class Test{ClassName}CoreFeature:  # P1: 核心功能
class Test{ClassName}Utilities:  # P2: 工具方法
```

## 参考资源

### Skill 内部

- patterns/sync_unit_test.md
- patterns/async_unit_test.md
- patterns/http_mock.md
- patterns/class_based_test.md
- patterns/patch_patterns.md
- patterns/third_party_mock.md
- patterns/complex_method_test.md (新增)
- patterns/exception_test.md (新增)
- patterns/websocket_test.md (新增)
- fixtures/generic_fixtures.py

### 外部文档

- pytest 官方文档：https://docs.pytest.org/
- unittest.mock 文档：https://docs.python.org/3/library/unittest.mock.html
