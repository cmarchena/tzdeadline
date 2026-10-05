# tzdeadline

Convert a date-time from one IANA timezone to another and show a
human-readable countdown. All timezone arithmetic is offline via the
Python 3.11+ standard library (`zoneinfo`) — no network calls.

## What it does

- Parses an ISO 8601 date-time string (`2025-12-31T23:59:00`,
  `2025-12-31 23:59:00`, with optional `±HH:MM` offset).
- Attaches the source IANA zone (wall-clock semantics: an embedded
  offset is stripped and the digits are re-interpreted in the source
  zone), then converts to the target zone.
- Prints/returns the result as ISO 8601 with UTC offset plus a
  countdown (`in X days, Y hours, Z minutes` /
  `X days, Y hours, Z minutes ago`).
- Exposes the same logic as one MCP tool, `convert_time`, for AI
  assistants.

## Requirements

- Python `>=3.11`
- Dependencies: `mcp>=1.2,<3` (works with MCP SDK v1 and v2 via a
  compat import). Dev: `pytest`, `hypothesis`.
- Console script: `tzdeadline = tzdeadline.__main__:main`
  (`pyproject.toml`).

## Installation

Pick one (from the project root):

```console
$ uv tool install -e .        # recommended: puts `tzdeadline` on your PATH
$ pip install -e .            # alternative, if you have pip
$ pipx install -e .           # alternative, isolated install
```

No install needed if you just want to try it — run the module directly:

```console
$ python3 -m tzdeadline "2026-10-05 23:59" America/Los_Angeles Europe/Madrid
```

Troubleshooting `bash: command not found: tzdeadline`:

1. Make sure it is installed (`uv tool list` should show `tzdeadline`).
2. Make sure `~/.local/bin` is on your `PATH`:
   `export PATH="$HOME/.local/bin:$PATH"`.
3. Open a new shell (or `hash -r`) after installing.

## How to use

### 1. Command line

```text
tzdeadline <datetime> <source_tz> <target_tz>
```

Run `tzdeadline --help` to see all arguments.

```console
$ tzdeadline "2026-10-05 23:59" America/Los_Angeles Europe/Madrid
2026-10-06T08:59:00+02:00
in 0 days, 14 hours, 25 minutes
```

A deadline in the past is labelled as elapsed:

```console
$ tzdeadline "2020-01-01 00:00" UTC UTC
2020-01-01T00:00:00+00:00
2455 days, 3 hours, 10 minutes ago
```

- Exit 0 on success (ISO line + countdown line on stdout).
- Exit 1 with a message on stderr on `ParseError` (bad date-time)
  or `ConversionError` (unknown zone):

```console
$ tzdeadline "not-a-date" UTC UTC
error: Unable to parse datetime string: 'not-a-date'. ...
$ tzdeadline "2026-10-05 23:59" Mars/Olympus_Mons UTC
error: Unknown timezone: 'Mars/Olympus_Mons'
```

### 2. MCP server

Canonical module: `tzdeadline/server.py`. Compat entry keeping the
historic `from_tz`/`to_tz` names: `tzdeadline/mcp_server.py`. Both
register exactly one tool, `convert_time`, and return the same shape:

```json
{ "converted_datetime": "2026-10-06T08:59:00+02:00", "countdown": "in 0 days, ..." }
```

on success, or `{ "error": "..." }` on invalid input (never raises).

Client config:

```json
{
  "mcpServers": {
    "tzdeadline": {
      "command": "python",
      "args": ["-m", "tzdeadline.mcp_server"]
    }
  }
}
```

> Use `-m tzdeadline.server` for the canonical
> `source_tz`/`target_tz` parameter names.

Example tool call and response:

```text
convert_time("2026-10-05 23:59", "America/Los_Angeles", "Europe/Madrid")
→ {"converted_datetime": "2026-10-06T08:59:00+02:00", "countdown": "in ..."}
convert_time("not-a-date", "UTC", "UTC")
→ {"error": "Unable to parse datetime string: 'not-a-date'. ..."}
```

### 3. Python library (`tzdeadline.core`)

```python
from tzdeadline.core.parser import parse_datetime
from tzdeadline.core.converter import convert
from tzdeadline.core.formatter import format_iso, format_countdown

dt = parse_datetime("2026-10-05 23:59")          # raises ParseError on garbage
result = convert(dt, "America/Los_Angeles", "Europe/Madrid")  # raises ConversionError on bad zone
print(format_iso(result.converted_dt))          # 2026-10-06T08:59:00+02:00
print(format_countdown(result.converted_dt))    # in ... / ... ago
```

## Errors

| Type | Trigger | CLI | MCP |
| --- | --- | --- | --- |
| `ParseError` | unparseable date-time | stderr + exit 1 | `{"error": ...}` |
| `ConversionError` | unknown IANA zone | stderr + exit 1 | `{"error": ...}` |

## Tests

`pytest tests/` — example/unit tests
(`tests/unit/test_parser|converter|formatter|cli|mcp_handler.py`)
plus Hypothesis property tests (`@settings(max_examples=100)`):
`tests/property/test_round_trip.py` (P1/P2/P6),
`tests/property/test_error_conditions.py` (P3/P4/P7),
`tests/property/test_countdown.py` (P5);
legacy `tests/test_properties.py` retained.

## Layout

```text
tzdeadline/core/{parser,converter,formatter}.py
tzdeadline/__main__.py      # CLI
tzdeadline/server.py        # canonical MCP server
tzdeadline/mcp_server.py    # compat MCP entry (from_tz/to_tz)
tests/unit/ tests/property/
```
