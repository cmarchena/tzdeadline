"""Property tests: countdown direction reflects past vs. future."""

from datetime import datetime, timezone

from hypothesis import given, settings
from hypothesis import strategies as st

from tzdeadline.core.formatter import format_countdown


def _utc_datetimes() -> st.SearchStrategy:
    return st.datetimes(
        min_value=datetime(2000, 1, 1), max_value=datetime(2030, 1, 1)
    ).map(lambda d: d.replace(tzinfo=timezone.utc))


# Feature: tzdeadline, Property 5: Countdown direction reflects past vs. future
@given(dt=_utc_datetimes(), now=_utc_datetimes())
@settings(max_examples=100)
def test_countdown_direction(dt: datetime, now: datetime) -> None:
    result = format_countdown(dt, now=now)
    assert ("ago" in result) == (dt < now)
