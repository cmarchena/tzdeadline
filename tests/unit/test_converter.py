"""Unit tests for tzdeadline.core.converter."""

from datetime import datetime

import pytest

from tzdeadline.core.converter import ConversionError, convert


class TestConvert:
    def test_known_conversion_utc_to_new_york(self):
        # 2025-01-15 12:00 UTC -> 07:00 in America/New_York (EST, -05:00)
        result = convert(datetime(2025, 1, 15, 12, 0, 0), "UTC", "America/New_York")
        assert result.converted_dt.isoformat() == "2025-01-15T07:00:00-05:00"

    def test_result_is_aware(self):
        result = convert(datetime(2025, 6, 15, 12, 0, 0), "UTC", "Asia/Tokyo")
        assert result.converted_dt.tzinfo is not None

    def test_bad_source_raises_conversion_error(self):
        with pytest.raises(ConversionError):
            convert(datetime(2025, 1, 1, 0, 0), "Mars/Olympus_Mons", "UTC")

    def test_bad_target_raises_conversion_error(self):
        with pytest.raises(ConversionError):
            convert(datetime(2025, 1, 1, 0, 0), "UTC", "Mars/Olympus_Mons")
