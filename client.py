import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


server_params = StdioServerParameters(
    command="uv",
    args=["run", "python", "sample/server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Connect to the MCP server
            await session.initialize()

            # Discover available tools
            tools = await session.list_tools()

            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Call our first tool
            result = await session.call_tool(
                "search_customer",
                arguments={"name": "Alice"},
            )

            print("\nSearch result:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())