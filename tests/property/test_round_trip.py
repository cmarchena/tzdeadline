"""Property tests: round-trip conversion, parser round-trip, target-zone awareness."""

from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones

from hypothesis import given, settings
from hypothesis import strategies as st

from tzdeadline.core.converter import convert
from tzdeadline.core.parser import parse_datetime

ZONES = sorted(available_timezones())


# Feature: tzdeadline, Property 1: Round-trip timezone conversion
@given(
    year=st.integers(2020, 2030),
    month=st.integers(1, 12),
    day=st.integers(1, 28),
    hour=st.integers(0, 23),
    minute=st.sampled_from([0, 15, 30, 45]),
    from_tz=st.sampled_from(ZONES),
    to_tz=st.sampled_from(ZONES),
)
@settings(max_examples=100)
def test_round_trip_preserves_utc_instant(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    from_tz: str,
    to_tz: str,
) -> None:
    dt = datetime(year, month, day, hour, minute)
    there = convert(dt, from_tz, to_tz).converted_dt
    back = convert(there.replace(tzinfo=None), to_tz, from_tz).converted_dt
    original_utc = dt.replace(tzinfo=ZoneInfo(from_tz)).astimezone(ZoneInfo("UTC"))
    assert back.astimezone(ZoneInfo("UTC")) == original_utc


# Feature: tzdeadline, Property 2: Parser round-trip
@given(
    year=st.integers(2020, 2030),
    month=st.integers(1, 12),
    day=st.integers(1, 28),
    hour=st.integers(0, 23),
    minute=st.integers(0, 59),
    second=st.integers(0, 59),
)
@settings(max_examples=100)
def test_parser_round_trip(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> None:
    original = datetime(year, month, day, hour, minute, second)
    assert parse_datetime(original.strftime("%Y-%m-%dT%H:%M:%S")) == original
    assert parse_datetime(original.strftime("%Y-%m-%d %H:%M:%S")) == original


# Feature: tzdeadline, Property 6: Converted datetime is timezone-aware in the target zone
@given(
    year=st.integers(2020, 2030),
    month=st.integers(1, 12),
    day=st.integers(1, 28),
    hour=st.integers(0, 23),
    minute=st.sampled_from([0, 15, 30, 45]),
    from_tz=st.sampled_from(ZONES),
    to_tz=st.sampled_from(ZONES),
)
@settings(max_examples=100)
def test_converted_dt_aware_in_target_zone(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    from_tz: str,
    to_tz: str,
) -> None:
    result = convert(datetime(year, month, day, hour, minute), from_tz, to_tz)
    assert result.converted_dt.tzinfo is not None
    assert result.converted_dt.tzinfo.key == to_tz  # type: ignore[attr-defined]
