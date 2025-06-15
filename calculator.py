from fastmcp import FastMCP
from typing import Union

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


if __name__ == "__main__":
    mcp.run()