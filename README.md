# learn-mcp
基于项目来学习 MCP (Model Context Protocol) 开发

## 项目介绍

这是一个学习 MCP 开发的示例项目，包含两个功能完整的 MCP 服务器：

1. **计算器服务器** (`calculator.py`): 提供基础数学运算功能
2. **提示流服务器** (`prompt_flow.py`): 提供各种 Prompt 模板功能

## 功能特性

### 计算器服务器 (calculator.py)

支持以下数学运算：

- **加法 (add)**: 支持 2+ 个数字相加
- **减法 (subtract)**: 支持 2+ 个数字连续相减 (a-b-c-...)
- **乘法 (multiply)**: 支持 2+ 个数字相乘
- **除法 (divide)**: 支持 2+ 个数字连续相除 (a/b/c/...)，自动检查除零错误
- **幂运算 (power)**: 需要恰好 2 个参数 (底数^指数)
- **取模 (modulo)**: 需要恰好 2 个参数 (a%b)

特色功能：
- Context 日志记录和进度追踪
- 静态资源配置读取 (`data://config`)
- 整数优化返回

### 提示流服务器 (prompt_flow.py)

提供多种 Prompt 模板：

- **explain_topic**: 生成主题解释请求模板
- **start_roleplay**: 生成角色扮演对话开场（多消息）
- **generate_report**: 生成格式化报告模板
- **code_review**: 生成代码审查提示模板
- **learning_plan**: 生成个性化学习计划模板

静态资源：
- `data://prompts`: 获取所有可用提示模板列表

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 运行服务器

```bash
# 运行计算器服务器
uv run calculator.py

# 运行提示流服务器
uv run prompt_flow.py
```

### 3. 测试服务器

安装并使用 MCP Inspector：

```bash
# 安装 MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 方法1：使用配置文件启动（推荐）
mcp-inspector --config .mcp.json --server calculator     # 测试计算器
mcp-inspector --config .mcp.json --server prompt-flow    # 测试提示流

# 方法2：直接启动（需要手动连接服务器）
mcp-inspector
```

配置文件 `.mcp.json` 内容：
```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": ["run", "calculator.py"],
      "cwd": "/path/to/learn-mcp"
    },
    "prompt-flow": {
      "command": "uv",
      "args": ["run", "prompt_flow.py"],
      "cwd": "/path/to/learn-mcp"
    }
  }
}
```

然后在浏览器中打开 Inspector 界面进行测试。

## 使用示例

### 计算器服务器示例

```python
# 加法：1 + 2 + 3 = 6
calculate("add", [1, 2, 3])

# 减法：10 - 3 - 2 = 5
calculate("subtract", [10, 3, 2])

# 乘法：2 * 3 * 4 = 24
calculate("multiply", [2, 3, 4])

# 除法：100 / 5 / 2 = 10
calculate("divide", [100, 5, 2])

# 幂运算：2^3 = 8
calculate("power", [2, 3])

# 取模：10 % 3 = 1
calculate("modulo", [10, 3])
```

### 提示流服务器示例

```python
# 解释主题
explain_topic("量子计算")
# 返回: "请你详细解释一下「量子计算」的概念，包括其定义、原理、应用场景等方面的内容。"

# 角色扮演开场
start_roleplay("莎士比亚")
# 返回多条消息的对话开场

# 生成报告
generate_report("销售数据分析", [100, 200, 150, 300])
# 返回格式化的 Markdown 报告模板

# 代码审查
code_review("Python", "def hello(): print('world')")
# 返回详细的代码审查提示

# 学习计划
learning_plan("机器学习", "初级", "3个月")
# 返回个性化学习计划模板
```

## 项目结构

```
learn-mcp/
├── README.md           # 项目文档
├── CLAUDE.md          # Claude Code 指导文档
├── calculator.py       # MCP 计算器服务器
├── prompt_flow.py      # MCP 提示流服务器
├── .mcp.json          # MCP Inspector 配置文件
├── pyproject.toml      # Python 项目配置
└── uv.lock            # 依赖锁文件
```

## 技术栈

- **FastMCP**: 快速构建 MCP 服务器的 Python 框架
- **uv**: 现代 Python 包管理器
- **MCP Inspector**: MCP 服务器测试工具
