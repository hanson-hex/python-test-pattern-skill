#!/bin/bash
# Python Test Pattern Skill 安装脚本
# 支持 Claude Code、Cursor、GitHub Copilot 等工具

set -e

SKILL_NAME="python-test-pattern"
REPO_URL="https://github.com/hanson-hex/python-test-pattern-skill"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Installing Python Test Pattern Skill..."

# 检测 AI 工具
detect_ai_tool() {
    if [ -d "$HOME/.claude" ] || command -v claude &> /dev/null; then
        echo "claude"
    elif [ -d "$HOME/.cursor" ] || command -v cursor &> /dev/null; then
        echo "cursor"
    elif [ -f ".github/copilot-instructions.md" ]; then
        echo "copilot"
    else
        echo "unknown"
    fi
}

# 安装到 Claude Code
install_claude() {
    local skill_dir="$HOME/.claude/skills/$SKILL_NAME"

    echo -e "${YELLOW}Detected Claude Code${NC}"
    echo "Installing to: $skill_dir"

    mkdir -p "$HOME/.claude/skills"

    if [ -d "$skill_dir" ]; then
        echo "Skill already exists, updating..."
        rm -rf "$skill_dir"
    fi

    # 从 GitHub 克隆
    if command -v git &> /dev/null; then
        git clone --depth 1 "$REPO_URL.git" "$skill_dir" 2>/dev/null || {
            echo -e "${RED}Failed to clone from GitHub${NC}"
            echo "Trying curl download..."
            curl -fsSL "$REPO_URL/archive/refs/heads/main.zip" -o "/tmp/$SKILL_NAME.zip"
            unzip -q "/tmp/$SKILL_NAME.zip" -d "/tmp/"
            mv "/tmp/$SKILL_NAME-main" "$skill_dir"
        }
    else
        echo -e "${RED}Git not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Installed to Claude Code${NC}"
}

# 安装到 Cursor (作为 prompts)
install_cursor() {
    local prompts_dir=".cursor/prompts"

    echo -e "${YELLOW}Detected Cursor${NC}"
    echo "Installing to: $prompts_dir"

    mkdir -p "$prompts_dir"

    # 转换 SKILL.md 为 Cursor prompts
    cat > "$prompts_dir/python-test-generator.md" << 'EOF'
---
name: Python Test Generator
description: Generate comprehensive unit tests for Python code
---

# Python Test Generator

You are an expert Python testing engineer. When generating tests, follow these principles:

## Test Structure (AAA Pattern)
1. **Arrange**: Set up test data and mocks
2. **Act**: Execute the code being tested
3. **Assert**: Verify the results

## Testing Patterns

### Synchronous Code
- Use pytest with descriptive test names
- Group related tests in classes
- Use fixtures for common setup

### Asynchronous Code
- Use @pytest.mark.asyncio
- Use AsyncMock for async methods
- Don't forget to await coroutines

### HTTP Dependencies
- Mock the HTTP client, not the response
- Use side_effect for sequential requests
- Verify request parameters

### Third-party Libraries
- Mock at conftest.py level
- Use MagicMock for missing modules
- Test behavior, not implementation

## Code Quality
- Max line length: 79 characters
- Avoid unused imports
- No duplicate imports
- Set MagicMock attributes explicitly

## Boundary Cases to Test
- None/null values
- Empty collections
- Invalid/malformed input
- Maximum length values
- Disabled state

## Mock Best Practices
```python
# Always set attributes explicitly
mock_message.text = "Hello"
mock_message.photo = []  # Not None for MagicMock
mock_message.document = None
```

Async methods must use AsyncMock:
```python
mock_bot.get_file = AsyncMock(return_value=mock_file)
```
EOF

    # 复制 patterns 作为 context
    mkdir -p "$prompts_dir/context"
    cp -r patterns/* "$prompts_dir/context/" 2>/dev/null || true

    echo -e "${GREEN}✓ Installed to Cursor${NC}"
}

# 安装到项目 (通用)
install_project() {
    local target_dir="${1:-.ai-patterns}"

    echo "Installing to project: $target_dir"

    mkdir -p "$target_dir"

    # 创建通用 prompts
    cat > "$target_dir/TESTING_GUIDE.md" << 'EOF'
# Python Testing Guide

## Quick Reference

### Generate Tests for New Code
```
Generate unit tests for [module/class] following AAA pattern:
- Arrange: Set up mocks and test data
- Act: Call the method
- Assert: Verify results
```

### Test Coverage Checklist
- [ ] Init/factory methods
- [ ] Core functionality
- [ ] Error handling
- [ ] Edge cases (None, empty, invalid)
- [ ] Async methods use AsyncMock
- [ ] HTTP calls are mocked

### Mock Configuration Template
```python
@pytest.fixture
def mock_complete():
    """Fully configured mock with all attributes set."""
    m = MagicMock()
    # Content
    m.text = ""
    m.caption = None
    # Media - default empty
    m.photo = []
    m.document = None
    m.video = None
    m.voice = None
    m.audio = None
    # Metadata
    m.entities = []
    m.message_id = "123"
    return m
```

## Common Patterns

See `patterns/` directory for detailed examples.
EOF

    # 复制详细模式
    mkdir -p "$target_dir/patterns"
    cp -r patterns/* "$target_dir/patterns/" 2>/dev/null || true

    echo -e "${GREEN}✓ Installed to $target_dir/${NC}"
}

# 主流程
main() {
    local tool=${1:-"auto"}

    if [ "$tool" = "auto" ]; then
        tool=$(detect_ai_tool)
    fi

    case "$tool" in
        claude)
            install_claude
            ;;
        cursor)
            install_cursor
            ;;
        project)
            install_project "$2"
            ;;
        *)
            echo -e "${YELLOW}AI tool not detected or not supported${NC}"
            echo "Installing as project-level patterns..."
            install_project
            ;;
    esac

    echo ""
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo ""
    echo "Usage:"
    echo "  - Claude Code: Restart to load the skill"
    echo "  - Cursor: Use @python-test-generator in chat"
    echo "  - Other: Reference patterns/ directory for templates"
}

# 显示帮助
show_help() {
    echo "Python Test Pattern Skill Installer"
    echo ""
    echo "Usage:"
    echo "  curl -fsSL $REPO_URL/raw/main/install.sh | bash"
    echo "  curl -fsSL $REPO_URL/raw/main/install.sh | bash -s -- [tool]"
    echo ""
    echo "Options:"
    echo "  auto     - Auto-detect AI tool (default)"
    echo "  claude   - Install for Claude Code"
    echo "  cursor   - Install for Cursor"
    echo "  project  - Install to current directory"
    echo ""
    echo "Examples:"
    echo "  # Auto-detect"
    echo "  bash install.sh"
    echo ""
    echo "  # Force install for specific tool"
    echo "  bash install.sh claude"
    echo ""
    echo "  # Install to specific directory"
    echo "  bash install.sh project ./my-patterns"
}

# 处理参数
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
