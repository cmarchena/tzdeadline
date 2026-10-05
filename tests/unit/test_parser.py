"""Unit tests for tzdeadline.core.parser."""

from datetime import datetime, timezone, timedelta

import pytest

from tzdeadline.core.parser import ParseError, parse_datetime


class TestParseError:
    def test_is_value_error_subclass(self):
        assert issubclass(ParseError, ValueError)

    def test_can_be_raised_and_caught_as_value_error(self):
        with pytest.raises(ValueError):
            raise ParseError("test")


class TestParseDatetime:
    # --- Accepted format: T-separator, naive ---
    def test_iso_t_separator_naive(self):
        result = parse_datetime("2025-12-31T23:59:00")
        assert result == datetime(2025, 12, 31, 23, 59, 0)
        assert result.tzinfo is None

    # --- Accepted format: space separator, naive ---
    def test_space_separator_naive(self):
        result = parse_datetime("2025-12-31 23:59:00")
        assert result == datetime(2025, 12, 31, 23, 59, 0)
        assert result.tzinfo is None

    # --- Accepted format: T-separator with UTC offset ---
    def test_iso_t_separator_with_utc_offset(self):
        result = parse_datetime("2025-12-31T23:59:00+05:30")
        expected_offset = timezone(timedelta(hours=5, minutes=30))
        assert result == datetime(2025, 12, 31, 23, 59, 0, tzinfo=expected_offset)
        assert result.tzinfo is not None
        assert result.utcoffset() == timedelta(hours=5, minutes=30)

    # --- Accepted format: space separator with UTC offset ---
    def test_space_separator_with_utc_offset(self):
        result = parse_datetime("2025-12-31 23:59:00+05:30")
        expected_offset = timezone(timedelta(hours=5, minutes=30))
        assert result == datetime(2025, 12, 31, 23, 59, 0, tzinfo=expected_offset)
        assert result.tzinfo is not None
        assert result.utcoffset() == timedelta(hours=5, minutes=30)

    # --- Negative UTC offset ---
    def test_negative_utc_offset(self):
        result = parse_datetime("2025-07-04T12:00:00-05:00")
        assert result.utcoffset() == timedelta(hours=-5)

    # --- UTC offset of zero ---
    def test_zero_utc_offset(self):
        result = parse_datetime("2025-01-01T00:00:00+00:00")
        assert result.utcoffset() == timedelta(0)

    # --- Error cases ---
    def test_garbage_input_raises_parse_error(self):
        with pytest.raises(ParseError):
            parse_datetime("not-a-date")

    def test_empty_string_raises_parse_error(self):
        with pytest.raises(ParseError):
            parse_datetime("")

    def test_date_only_accepted_as_midnight(self):
        # datetime.fromisoformat in Python 3.11+ accepts bare dates as midnight
        result = parse_datetime("2025-12-31")
        assert result == datetime(2025, 12, 31, 0, 0, 0)
        assert result.tzinfo is None

    def test_wrong_separator_raises_parse_error(self):
        with pytest.raises(ParseError):
            parse_datetime("2025/12/31 23:59:00")

    def test_parse_error_message_contains_input(self):
        bad_input = "totally-wrong"
        with pytest.raises(ParseError, match="totally-wrong"):
            parse_datetime(bad_input)

    def test_parse_error_is_parse_error_type(self):
        with pytest.raises(ParseError):
            parse_datetime("2025-13-01T00:00:00")  # month 13 is invalid
