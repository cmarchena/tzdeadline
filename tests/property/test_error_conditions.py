"""Property tests: invalid timezones, invalid datetimes, MCP structured errors."""

from datetime import datetime
from zoneinfo import available_timezones

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from tzdeadline.core.converter import ConversionError, convert
from tzdeadline.core.parser import ParseError, parse_datetime
from tzdeadline.server import convert_time

VALID_ZONES = available_timezones()


# Feature: tzdeadline, Property 3: Invalid timezone identifiers always produce errors
@given(
    year=st.integers(2020, 2030),
    month=st.integers(1, 12),
    day=st.integers(1, 28),
    bad_tz=st.text(),
)
@settings(max_examples=100)
def test_invalid_timezone_raises(year: int, month: int, day: int, bad_tz: str) -> None:
    assume(bad_tz not in VALID_ZONES)
    dt = datetime(year, month, day, 12, 0, 0)
    try:
        convert(dt, bad_tz, "UTC")
    except ConversionError:
        pass
    else:
        raise AssertionError(f"expected ConversionError for source {bad_tz!r}")
    try:
        convert(dt, "UTC", bad_tz)
    except ConversionError:
        pass
    else:
        raise AssertionError(f"expected ConversionError for target {bad_tz!r}")


# Feature: tzdeadline, Property 4: Invalid datetime strings always produce errors
@given(bad_input=st.text())
@settings(max_examples=100)
def test_invalid_datetime_raises(bad_input: str) -> None:
    try:
        datetime.fromisoformat(bad_input)
    except ValueError:
        pass
    else:
        assume(False)
    try:
        parse_datetime(bad_input)
    except ParseError:
        pass
    else:
        raise AssertionError(f"expected ParseError for {bad_input!r}")


# Feature: tzdeadline, Property 7: MCP handler returns structured error for invalid inputs
@given(bad_tz=st.text(), bad_dt=st.text())
@settings(max_examples=100)
def test_mcp_handler_structured_error(bad_tz: str, bad_dt: str) -> None:
    assume(bad_tz not in VALID_ZONES)
    try:
        datetime.fromisoformat(bad_dt)
    except ValueError:
        pass
    else:
        assume(False)
    assert "error" in convert_time(bad_dt, bad_tz, "UTC")
    assert "error" in convert_time("2025-06-15 10:00:00", bad_tz, "UTC")
    assert "error" in convert_time(bad_dt, "UTC", "UTC")
