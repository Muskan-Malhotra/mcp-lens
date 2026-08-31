import time
import uuid


async def trace_tool_call(tool_name, arguments):
    """
    Execute an MCP tool call and capture what happened.
    """

    trace_id = str(uuid.uuid4())
    started = time.perf_counter()

    print(f"[LENS] - {tool_name}")

    try:
        trace = {
            "trace_id": trace_id,
            "tool": tool_name,
            "arguments": arguments,
            "status": "success"
        }

        return trace

    except Exception as error:

        trace = {
            "trace_id": trace_id,
            "tool": tool_name,
            "arguments": arguments,
            "status": "error",
            "error": str(error),
        }

        return trace