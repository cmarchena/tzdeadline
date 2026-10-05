"""tzdeadline.core.formatter — Format datetimes as ISO 8601 and human-readable countdowns."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone


def format_iso(dt: datetime) -> str:
    """Return dt as an ISO 8601 string with UTC offset, e.g. '2025-12-31T23:59:00+01:00'."""
    return dt.isoformat()


def format_countdown(dt: datetime, now: datetime | None = None) -> str:
    """
    Return a human-readable countdown string.

    If now is None, defaults to datetime.now(tz=timezone.utc).
    Positive delta  →  "in X days, Y hours, Z minutes"
    Negative delta  →  "X days, Y hours, Z minutes ago"
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)

    delta: timedelta = dt - now
    is_future = delta.total_seconds() >= 0

    # Work with the absolute duration.
    abs_delta = abs(delta)
    total_seconds = int(abs_delta.total_seconds())

    days = total_seconds // 86400
    remaining = total_seconds % 86400
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60

    duration = f"{days} days, {hours} hours, {minutes} minutes"

    if is_future:
        return f"in {duration}"
    else:
        return f"{duration} ago"
