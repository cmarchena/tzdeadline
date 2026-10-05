"""Unit tests for tzdeadline.server.convert_time (MCP handler)."""

from tzdeadline.server import convert_time


class TestMcpHandler:
    def test_valid_input_returns_keys(self):
        result = convert_time("2025-06-15 10:00:00", "UTC", "UTC")
        assert "converted_datetime" in result
        assert "countdown" in result
        assert "2025-06-15T10:00:00+00:00" in result["converted_datetime"]

    def test_invalid_timezone_returns_error(self):
        result = convert_time("2025-06-15 10:00:00", "Mars/Olympus_Mons", "UTC")
        assert "error" in result

    def test_unparseable_datetime_returns_error(self):
        result = convert_time("not-a-date", "UTC", "UTC")
        assert "error" in result
