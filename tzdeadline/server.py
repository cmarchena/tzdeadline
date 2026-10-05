"""tzdeadline.server — canonical MCP server exposing convert_time."""

from __future__ import annotations

try:
    # MCP SDK 2.x: FastMCP was renamed to MCPServer and the module moved.
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    # MCP SDK 1.x keeps the original path.
    from mcp.server.fastmcp import FastMCP

from tzdeadline.core.converter import ConversionError, convert
from tzdeadline.core.formatter import format_countdown, format_iso
from tzdeadline.core.parser import ParseError, parse_datetime

mcp = FastMCP("tzdeadline")


def convert_time_dict(
    datetime_str: str,
    source_tz: str,
    target_tz: str,
) -> dict:
    """Pure convert logic shared by the MCP tool and compat shims."""
    try:
        dt = parse_datetime(datetime_str)
    except ParseError as exc:
        return {"error": str(exc)}

    try:
        result = convert(dt, source_tz, target_tz)
    except ConversionError as exc:
        return {"error": str(exc)}

    return {
        "converted_datetime": format_iso(result.converted_dt),
        "countdown": format_countdown(result.converted_dt),
    }


@mcp.tool()
def convert_time(
    datetime_str: str,
    source_tz: str,
    target_tz: str,
) -> dict:
    """Convert a local date-time from one IANA timezone to another.

    datetime_str examples: "2026-10-05 23:59:00" or "2026-10-05T23:59:00".

    Returns {"converted_datetime": str, "countdown": str} on success,
    or {"error": str} on invalid input.
    """
    return convert_time_dict(datetime_str, source_tz, target_tz)


if __name__ == "__main__":
    mcp.run()
