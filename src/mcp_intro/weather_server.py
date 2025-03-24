from mcp.server.fastmcp import FastMCP
from loguru import logger

mcp = FastMCP("Weather", port=8083)

@mcp.tool()
async def get_weather_city(city: str) -> str:
    """Get weather for city."""
    logger.debug(f"Getting weather for city: {city}")
    return f"The temperature in {city} is 28 degrees Celsius."


if __name__ == "__main__":
    logger.debug("Starting Weather server")
    mcp.run(transport="sse")