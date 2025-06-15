from fastmcp import FastMCP
from typing import Union
import json

mcp = FastMCP(
    name="CalculatorServer",
    instructions="""Calculator server supporting basic mathematical operations.
    
    Use the calculate tool with:
    - method: operation type (add, subtract, multiply, divide, power, modulo)
    - args: list of numbers (floats/integers)
    
    Operations:
    - add/subtract/multiply/divide: support 2+ arguments
    - power/modulo: require exactly 2 arguments
    
    Examples:
    - calculate("add", [1, 2, 3]) → 6
    - calculate("subtract", [10, 3, 2]) → 5 (10-3-2)
    - calculate("multiply", [2, 3, 4]) → 24
    - calculate("divide", [100, 5, 2]) → 10 (100/5/2)
    - calculate("power", [2, 3]) → 8 (2³)
    - calculate("modulo", [10, 3]) → 1 (10%3)
    """,
)

@mcp.tool()
def calculate(method: str, args: list[float]) -> Union[int, float]:
    """
    Calculate the result of the given method and arguments.
    """
    if method == "add":
        result = sum(args)
    elif method == "subtract":
        if len(args) < 2:
            raise ValueError("Subtraction requires at least 2 arguments")
        result = args[0]
        for arg in args[1:]:
            result -= arg
    elif method == "multiply":
        result = 1
        for arg in args:
            result *= arg
    elif method == "divide":
        if len(args) < 2:
            raise ValueError("Division requires at least 2 arguments")
        result = args[0]
        for arg in args[1:]:
            if arg == 0:
                raise ValueError("Cannot divide by zero")
            result /= arg
    elif method == "power":
        if len(args) != 2:
            raise ValueError("Power operation requires exactly 2 arguments")
        result = args[0] ** args[1]
    elif method == "modulo":
        if len(args) != 2:
            raise ValueError("Modulo operation requires exactly 2 arguments")
        if args[1] == 0:
            raise ValueError("Cannot modulo by zero")
        result = args[0] % args[1]
    else:
        raise ValueError(f"Invalid method: {method}")
    
    # Return integer if result is a whole number
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result

oprations = [
    {
        "name": "add",
        "description": "Addition operation",
        "min_args": 2,
        "max_args": None,
        "example": "calculate('add', [1, 2, 3]) → 6"
    },
    {
        "name": "subtract", 
        "description": "Subtraction operation (left-to-right)",
        "min_args": 2,
        "max_args": None,
        "example": "calculate('subtract', [10, 3, 2]) → 5"
    },
    {
        "name": "multiply",
        "description": "Multiplication operation",
        "min_args": 2,
        "max_args": None,
        "example": "calculate('multiply', [2, 3, 4]) → 24"
    },
    {
        "name": "divide",
        "description": "Division operation (left-to-right)",
        "min_args": 2,
        "max_args": None,
        "example": "calculate('divide', [100, 5, 2]) → 10"
    },
    {
        "name": "power",
        "description": "Power operation (base^exponent)",
        "min_args": 2,
        "max_args": 2,
        "example": "calculate('power', [2, 3]) → 8"
    },
    {
        "name": "modulo",
        "description": "Modulo operation (a % b)",
        "min_args": 2,
        "max_args": 2,
        "example": "calculate('modulo', [10, 3]) → 1"
    }
]

@mcp.resource("data://config")
def get_config() -> str:
    """
    提供计算器服务器的配置信息
    """
    config = {
        "name": "CalculatorServer",
        "version": "1.0.0",
        "description": "MCP Calculator Server supporting basic mathematical operations",
        "supported_operations": list(map(lambda x: x["name"], oprations)),
        "features": [
            "Integer optimization (returns int when result is whole number)",
            "Error handling for division by zero",
            "Support for both integer and float inputs",
            "Argument validation for each operation"
        ],
        "author": "MCP Learning Project",
        "framework": "FastMCP",
        "python_version": ">=3.10"
    }
    
    return json.dumps(config, indent=2, ensure_ascii=False)

@mcp.resource("data://operation/{name}")
def get_operation(name: str) -> str:
    """
    Get the operation with the given name.
    """
    for operation in oprations:
        if operation["name"] == name:
            return json.dumps(operation, indent=2, ensure_ascii=False)
    return json.dumps({"error": "Operation not found"}, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()