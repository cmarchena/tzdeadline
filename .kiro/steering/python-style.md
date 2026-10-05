---
inclusion: always
---

# Python style for TZ Deadline

## Stack
- Python 3.11+
- Standard library `zoneinfo` for time zones
- `pytest` and `hypothesis` for tests
- No network calls in conversion logic

## Rules
1. Every function has type hints on parameters and return values.
2. Pure conversion lives in `convert.py`: no `print`, no file I/O, no network, no reading the clock except through an injected “now” when needed for countdowns.
3. The CLI (`cli.py`) may print to stdout/stderr. Library code uses `logging`, not `print`.
4. Prefer small pure functions over classes unless a class clearly helps.
5. Invalid time zones or unparseable date-times raise clear exceptions; do not silently guess.
6. Round-trip safety: converting a local time from zone A to zone B and back to A must preserve the same local wall time when the conversion is unambiguous.

## Examples

```python
from datetime import datetime
from zoneinfo import ZoneInfo

def convert(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Attach from_tz if naive, then return the same instant in to_tz."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(from_tz))
    else:
        dt = dt.astimezone(ZoneInfo(from_tz))
    return dt.astimezone(ZoneInfo(to_tz))