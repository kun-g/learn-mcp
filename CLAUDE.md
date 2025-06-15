# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) learning project featuring a calculator server built with FastMCP. The server provides mathematical operations through MCP tools that can be tested and integrated with AI assistants.

## Development Commands

### Package Management
- **Install dependencies**: `uv sync`
- **Run the calculator server**: `uv run calculator.py`

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