"""
tzdeadline.core.parser
~~~~~~~~~~~~~~~~~~~~~~
Parse raw datetime strings into datetime objects.
"""

from datetime import datetime


class ParseError(ValueError):
    """Raised when a datetime string cannot be parsed."""


def parse_datetime(dt_string: str) -> datetime:
    """
    Parse dt_string into a datetime object.

    Accepted formats:
      - "YYYY-MM-DDTHH:MM:SS"         (ISO 8601 T-separator, naive)
      - "YYYY-MM-DD HH:MM:SS"         (space separator, naive)
      - "YYYY-MM-DDTHH:MM:SS+HH:MM"   (with UTC offset)
      - "YYYY-MM-DD HH:MM:SS+HH:MM"   (with UTC offset)

    Returns:
        A naive datetime when no UTC offset is present, or a datetime carrying
        the literal offset as a fixed timezone object when an offset is present.

    Raises:
        ParseError: if the string does not match any accepted format.
    """
    try:
        return datetime.fromisoformat(dt_string)
    except ValueError:
        raise ParseError(
            f"Unable to parse datetime string: {dt_string!r}. "
            "Expected ISO 8601 format such as '2025-12-31T23:59:00' or "
            "'2025-12-31 23:59:00' (with optional UTC offset, e.g. '+05:30')."
        )
