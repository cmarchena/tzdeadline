"""tzdeadline.core.converter — timezone conversion logic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class ConversionError(ValueError):
    """Raised when a timezone identifier is not recognised by zoneinfo."""


@dataclass(frozen=True)
class ConversionResult:
    """Result of a timezone conversion."""

    converted_dt: datetime  # timezone-aware, expressed in target zone
    source_tz: str          # original IANA identifier
    target_tz: str          # target IANA identifier


def convert(
    dt: datetime,
    source_tz: str,
    target_tz: str,
) -> ConversionResult:
    """
    Attach source_tz to dt, then convert to target_tz.

    If dt is already timezone-aware (e.g. it carries a fixed UTC offset from
    parsing), the offset is stripped via ``dt.replace(tzinfo=None)`` before the
    IANA source zone is attached.  This preserves wall-clock time semantics —
    the digits on the clock face are kept and re-interpreted in the named zone.

    Args:
        dt:        A naive or offset-aware datetime representing the source time.
        source_tz: IANA timezone identifier for the source zone.
        target_tz: IANA timezone identifier for the target zone.

    Returns:
        A :class:`ConversionResult` whose ``converted_dt`` is timezone-aware
        and expressed in the requested target zone.

    Raises:
        ConversionError: if source_tz or target_tz is not recognised by zoneinfo.
    """
    # Load both ZoneInfo objects up-front so we surface errors early.
    # ZoneInfo raises ZoneInfoNotFoundError for unknown names but plain
    # ValueError for malformed ones (e.g. ""), so catch both to honour
    # Property 3: any non-IANA string SHALL raise ConversionError.
    try:
        source_zone = ZoneInfo(source_tz)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ConversionError(f"Unknown timezone: {source_tz!r}") from exc

    try:
        target_zone = ZoneInfo(target_tz)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ConversionError(f"Unknown timezone: {target_tz!r}") from exc

    # If dt already carries offset information, strip it so the wall-clock
    # reading is preserved when we attach the IANA zone.
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    converted = dt.replace(tzinfo=source_zone).astimezone(target_zone)

    return ConversionResult(
        converted_dt=converted,
        source_tz=source_tz,
        target_tz=target_tz,
    )
