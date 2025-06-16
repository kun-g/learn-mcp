# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) learning project featuring a calculator server built with FastMCP. The server provides mathematical operations through MCP tools that can be tested and integrated with AI assistants.

## Development Commands

### Package Management
- **Install dependencies**: `uv sync`
- **Run the calculator server**: `uv run calculator.py`

### Linting and Type Checking
- **Lint code**: `uv run ruff check`
- **Format code**: `uv run ruff format`
- **Type check**: `uv run mypy .`
- **Run all checks**: `uv run ruff check && uv run ruff format && uv run mypy .`

### Testing
- **Run tests**: `uv run pytest`
- **Run tests with coverage**: `uv run pytest --cov`
- **Run specific test file**: `uv run pytest tests/test_calculator.py`
- **Run tests in verbose mode**: `uv run pytest -v`

### Testing and Development
- **Install MCP Inspector**: `npm install -g @modelcontextprotocol/inspector`
- **Test with config file**: `mcp-inspector --config mcp-config.json --server calculator`
- **Test manually**: `mcp-inspector` (then manually connect to server)

## Architecture

### Core Components
- `calculator.py`: Single-file MCP server using FastMCP framework
  - Defines one tool: `calculate(method: str, args: list[float]) -> Union[int, float]`
  - Returns integers when possible (e.g., 6 instead of 6.0)
  - Supports 6 mathematical operations with different argument requirements
- `sitemap_server.py`: Sitemap parsing MCP server
  - 4 tools: parse_sitemap, analyze_sitemap, validate_sitemap, extract_domain_info
  - Supports standard sitemaps and sitemap index files
  - Provides detailed URL analysis and validation

### MCP Tool Design
The calculator tool uses a method-dispatch pattern:
- **Multi-argument operations**: add, subtract, multiply, divide (require 2+ args)
- **Two-argument operations**: power, modulo (require exactly 2 args)
- **Error handling**: Division by zero, invalid methods, insufficient arguments
- **Type optimization**: Returns `int` for whole numbers, `float` otherwise

### Configuration
- `mcp-config.json`: Inspector configuration for automated testing
- `pyproject.toml`: Minimal Python project setup with FastMCP dependency
- Uses `uv` as package manager (modern pip/poetry alternative)

## Key Implementation Details

### Return Type Strategy
The calculate function returns `Union[int, float]` and automatically converts float results to integers when they represent whole numbers using `result.is_integer()`.

### Operation Logic
- **Chained operations**: subtract/divide perform left-to-right operations (a-b-c, a/b/c)
- **Accumulative operations**: add uses `sum()`, multiply uses iterative multiplication
- **Validation**: Each operation validates argument count and values before execution

### MCP Integration
Server uses FastMCP's declarative approach:
- Single `@mcp.tool()` decorator exposes the function
- Comprehensive instructions embedded in server initialization
- Automatic JSON-RPC handling and type marshalling

## Development Workflow

This project follows a **Test-Driven Development (TDD)** workflow to ensure code quality and reliability:

### 1. Planning Phase
- Define clear requirements and acceptance criteria
- Break down features into testable units
- Create task list using TodoWrite tool

### 2. Test-First Development
- Write unit tests **before** implementing functionality
- Tests should cover:
  - Happy path scenarios
  - Edge cases and error conditions  
  - Input validation
  - Expected return types and values

### 3. Implementation Cycle
```bash
# 1. Write failing tests
uv run pytest tests/test_new_feature.py  # Should fail

# 2. Implement minimal code to make tests pass
# Edit source files...

# 3. Run tests until they pass
uv run pytest tests/test_new_feature.py

# 4. Refactor and clean up code
uv run ruff check --fix
uv run ruff format
uv run mypy .

# 5. Commit working code
git add .
git commit -m "feat: implement new feature with tests"
```

### 4. Quality Gates
Before any commit, ensure:
- [ ] All tests pass: `uv run pytest`
- [ ] Code is formatted: `uv run ruff format`
- [ ] No lint errors: `uv run ruff check`
- [ ] Type checks pass: `uv run mypy .`
- [ ] Coverage is maintained: `uv run pytest --cov`

### 5. Commit Guidelines
- **Test commits**: `test: add tests for feature X`
- **Feature commits**: `feat: implement feature X`
- **Fix commits**: `fix: resolve issue with Y`
- **Refactor commits**: `refactor: improve code structure`
- USE Chinese

This workflow ensures reliable, maintainable code with comprehensive test coverage.