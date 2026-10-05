"""MCP server exposing convert_time for Kiro."""

from __future__ import annotations

from datetime import datetime

try:
    # MCP SDK 2.x: FastMCP was renamed to MCPServer and the module moved.
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    # MCP SDK 1.x keeps the original path.
    from mcp.server.fastmcp import FastMCP

from tzdeadline.core.converter import ConversionError, convert

mcp = FastMCP("tzdeadline")


@mcp.tool()
def convert_time(
    datetime_str: str,
    from_tz: str,
    to_tz: str,
) -> str:
    """Convert a local date-time from one IANA timezone to another.

    datetime_str examples: "2026-10-05 23:59" or "2026-10-05T23:59"
    """
    cleaned = datetime_str.strip().replace("T", " ")
    try:
        try:
            dt = datetime.strptime(cleaned, "%Y-%m-%d %H:%M")
        except ValueError:
            dt = datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S")
    except ValueError as exc:
        return f"error: unable to parse datetime {datetime_str!r} ({exc})"

    try:
        result = convert(dt, from_tz, to_tz)
    except ConversionError as exc:
        return f"error: {exc}"

    out = result.converted_dt
    return f"{out.isoformat()} ({result.target_tz})"


if __name__ == "__main__":
    mcp.run()