from mcp.server.fastmcp import FastMCP
from loguru import logger

mcp = FastMCP("Math", port=8082)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    logger.debug(f"Adding {a} and {b}")
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    logger.debug(f"Multiplying {a} and {b}")
    return a * b

if __name__ == "__main__":
    logger.debug("Starting Math server")
    mcp.run(transport="sse")