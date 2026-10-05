"""Unit tests for tzdeadline.core.formatter."""

from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import pytest

from tzdeadline.core.formatter import format_iso, format_countdown


# ---------------------------------------------------------------------------
# format_iso
# ---------------------------------------------------------------------------

class TestFormatIso:
    def test_utc_offset_present(self):
        """ISO output must include a UTC offset (+HH:MM or -HH:MM)."""
        dt = datetime(2025, 12, 31, 23, 59, 0, tzinfo=timezone.utc)
        result = format_iso(dt)
        assert re.search(r"[+-]\d{2}:\d{2}$", result), f"No UTC offset in: {result!r}"

    def test_utc_format(self):
        """UTC datetime formats as +00:00."""
        dt = datetime(2025, 12, 31, 23, 59, 0, tzinfo=timezone.utc)
        assert format_iso(dt) == "2025-12-31T23:59:00+00:00"

    def test_positive_offset(self):
        """Datetime with +01:00 offset formats correctly."""
        tz_plus1 = timezone(timedelta(hours=1))
        dt = datetime(2025, 12, 31, 23, 59, 0, tzinfo=tz_plus1)
        assert format_iso(dt) == "2025-12-31T23:59:00+01:00"

    def test_negative_offset(self):
        """Datetime with -05:00 offset formats correctly."""
        tz_minus5 = timezone(timedelta(hours=-5))
        dt = datetime(2025, 1, 1, 9, 0, 0, tzinfo=tz_minus5)
        assert format_iso(dt) == "2025-01-01T09:00:00-05:00"

    def test_iana_zone(self):
        """format_iso works with IANA ZoneInfo objects (offset in output)."""
        dt = datetime(2025, 6, 15, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        result = format_iso(dt)
        # America/New_York in June is EDT = -04:00
        assert result == "2025-06-15T12:00:00-04:00"


# ---------------------------------------------------------------------------
# format_countdown — future deadlines
# ---------------------------------------------------------------------------

class TestFormatCountdownFuture:
    def _now(self) -> datetime:
        return datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_future_label(self):
        """Future deadlines start with 'in '."""
        dt = datetime(2025, 6, 18, 14, 12, 0, tzinfo=timezone.utc)
        result = format_countdown(dt, now=self._now())
        assert result.startswith("in ")

    def test_future_days_hours_minutes(self):
        """Exact values: 3 days, 4 hours, 12 minutes ahead of now."""
        # now = 2025-06-15 10:00:00 UTC
        # dt  = 2025-06-18 14:12:00 UTC  → +3d 4h 12m
        dt = datetime(2025, 6, 18, 14, 12, 0, tzinfo=timezone.utc)
        assert format_countdown(dt, now=self._now()) == "in 3 days, 4 hours, 12 minutes"

    def test_future_zero_days(self):
        """When the deadline is less than a day away, days=0."""
        dt = datetime(2025, 6, 15, 12, 30, 0, tzinfo=timezone.utc)
        assert format_countdown(dt, now=self._now()) == "in 0 days, 2 hours, 30 minutes"

    def test_future_zero_minutes(self):
        """Exact hour boundary: 0 minutes."""
        dt = datetime(2025, 6, 15, 11, 0, 0, tzinfo=timezone.utc)
        assert format_countdown(dt, now=self._now()) == "in 0 days, 1 hours, 0 minutes"


# ---------------------------------------------------------------------------
# format_countdown — past deadlines
# ---------------------------------------------------------------------------

class TestFormatCountdownPast:
    def _now(self) -> datetime:
        return datetime(2025, 6, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_past_label(self):
        """Past deadlines end with ' ago'."""
        dt = datetime(2025, 6, 15, 7, 30, 0, tzinfo=timezone.utc)
        result = format_countdown(dt, now=self._now())
        assert result.endswith(" ago")

    def test_past_hours_minutes(self):
        """Exact values: 2 hours 30 minutes in the past."""
        # now = 2025-06-15 10:00:00 UTC
        # dt  = 2025-06-15 07:30:00 UTC  → -2h 30m
        dt = datetime(2025, 6, 15, 7, 30, 0, tzinfo=timezone.utc)
        assert format_countdown(dt, now=self._now()) == "0 days, 2 hours, 30 minutes ago"

    def test_past_multiple_days(self):
        """Deadline several days ago."""
        dt = datetime(2025, 6, 12, 10, 0, 0, tzinfo=timezone.utc)
        assert format_countdown(dt, now=self._now()) == "3 days, 0 hours, 0 minutes ago"


# ---------------------------------------------------------------------------
# format_countdown — default now
# ---------------------------------------------------------------------------

class TestFormatCountdownDefaultNow:
    def test_default_now_returns_string(self):
        """When now is not injected, format_countdown still returns a string."""
        dt = datetime(2099, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        result = format_countdown(dt)
        assert isinstance(result, str)
        assert result.startswith("in ")
