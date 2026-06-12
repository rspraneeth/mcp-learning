from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a+b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a*b #intentionally returning a product instead of difference


@mcp.tool()
def minus(a: int, b: int) -> int:
    """difference of two numbers"""
    return a-b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """multiply of two numbers"""
    return a*b

if __name__ == "__main__":
    mcp.run()
