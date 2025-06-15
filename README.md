# learn-mcp
基于项目来学习 MCP (Model Context Protocol) 开发

## 项目介绍

这是一个学习 MCP 开发的示例项目，包含一个功能完整的计算器服务器。

## 功能特性

计算器服务器支持以下数学运算：

- **加法 (add)**: 支持 2+ 个数字相加
- **减法 (subtract)**: 支持 2+ 个数字连续相减 (a-b-c-...)
- **乘法 (multiply)**: 支持 2+ 个数字相乘
- **除法 (divide)**: 支持 2+ 个数字连续相除 (a/b/c/...)，自动检查除零错误
- **幂运算 (power)**: 需要恰好 2 个参数 (底数^指数)
- **取模 (modulo)**: 需要恰好 2 个参数 (a%b)

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 运行服务器

```bash
uv run calculator.py
```

### 3. 测试服务器

安装并使用 MCP Inspector：

```bash
# 安装 MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 方法1：使用配置文件启动
mcp-inspector --config mcp-config.json --server calculator

# 方法2：直接启动（需要手动连接服务器）
mcp-inspector
```

配置文件 `mcp-config.json` 内容：
```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": ["run", "calculator.py"],
      "cwd": "your path to /learn-mcp"
    }
  }
}
```

然后在浏览器中打开 Inspector 界面进行测试。

## 使用示例

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

## 项目结构

```
learn-mcp/
├── README.md           # 项目文档
├── calculator.py       # MCP 计算器服务器
├── pyproject.toml      # Python 项目配置
└── uv.lock            # 依赖锁文件
```

## 技术栈

- **FastMCP**: 快速构建 MCP 服务器的 Python 框架
- **uv**: 现代 Python 包管理器
- **MCP Inspector**: MCP 服务器测试工具
