"""MCP server exposing convert_time for Kiro.

Backward-compatible entry point: accepts the historical ``from_tz``/``to_tz``
parameter names and delegates to :mod:`tzdeadline.server`. New clients should
prefer ``tzdeadline.server`` (``source_tz``/``target_tz``).
"""

from __future__ import annotations

try:
    # MCP SDK 2.x: FastMCP was renamed to MCPServer and the module moved.
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    # MCP SDK 1.x keeps the original path.
    from mcp.server.fastmcp import FastMCP

from tzdeadline.server import convert_time_dict

mcp = FastMCP("tzdeadline")


@mcp.tool()
def convert_time(
    datetime_str: str,
    from_tz: str,
    to_tz: str,
) -> dict:
    """Convert a local date-time from one IANA timezone to another.

    datetime_str examples: "2026-10-05 23:59" or "2026-10-05T23:59".

    Returns {"converted_datetime": str, "countdown": str} on success,
    or {"error": str} on invalid input.
    """
    return convert_time_dict(datetime_str, source_tz=from_tz, target_tz=to_tz)


if __name__ == "__main__":
    mcp.run()
