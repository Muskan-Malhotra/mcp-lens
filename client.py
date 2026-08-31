import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from src.mcp_lens.tracer import trace_tool_call
from src.mcp_lens.analyzer import check_ambiguous_customer


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

            trace = await trace_tool_call(
                "search_customer",
                {"name": "Alice"},
                client=session
            )

            print(f"Trace: {trace}")

            # Call our first tool
            result = await session.call_tool(
                "search_customer",
                arguments={"name": "Alice"},
            )


            finding = check_ambiguous_customer(trace)

            if finding:
                print("\nMCP LENS FINDING")
                print(f"Type: {finding['type']}")
                print(f"Severity: {finding['severity']}")
                print(f"Message: {finding['message']}")
                print(f"Recommendation: {finding['recommendation']}")

                print(f"Search result: {result}")


if __name__ == "__main__":
    asyncio.run(main())