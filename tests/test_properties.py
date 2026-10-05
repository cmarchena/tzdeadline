from datetime import datetime
from zoneinfo import ZoneInfo

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from tzdeadline.core.converter import convert

COMMON_ZONES = [
    "UTC",
    "Europe/Madrid",
    "America/Los_Angeles",
    "America/New_York",
    "Asia/Tokyo",
    "Australia/Sydney",
]


@given(
    year=st.integers(2020, 2030),
    month=st.integers(1, 12),
    day=st.integers(1, 28),  # avoid month-end edge cases
    hour=st.integers(0, 23),
    minute=st.sampled_from([0, 15, 30, 45]),
    from_tz=st.sampled_from(COMMON_ZONES),
    to_tz=st.sampled_from(COMMON_ZONES),
)
@settings(max_examples=100)
def test_same_utc_instant(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    from_tz: str,
    to_tz: str,
) -> None:
    dt = datetime(year, month, day, hour, minute)
    converted = convert(dt, from_tz, to_tz).converted_dt
    original_utc = dt.replace(tzinfo=ZoneInfo(from_tz)).astimezone(ZoneInfo("UTC"))
    assert converted.astimezone(ZoneInfo("UTC")) == original_utc


@given(
    year=st.integers(2020, 2030),
    month=st.integers(1, 12),
    day=st.integers(1, 28),
    hour=st.integers(0, 23),
    minute=st.sampled_from([0, 15, 30, 45]),
    from_tz=st.sampled_from(COMMON_ZONES),
    to_tz=st.sampled_from(COMMON_ZONES),
)
@settings(max_examples=100)
def test_round_trip_wall_time(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    from_tz: str,
    to_tz: str,
) -> None:
    dt = datetime(year, month, day, hour, minute)
    try:
        there = convert(dt, from_tz, to_tz).converted_dt
        back = convert(there.replace(tzinfo=None), to_tz, from_tz).converted_dt
    except Exception:
        assume(False)
        return
    assert back.replace(tzinfo=None) == dt