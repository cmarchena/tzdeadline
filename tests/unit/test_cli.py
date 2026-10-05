"""Unit tests for tzdeadline.__main__ (CLI)."""

import pytest

from tzdeadline.__main__ import main


class TestCli:
    def test_valid_input_exits_zero_with_iso_and_countdown(self, capsys):
        main(["2025-06-15 10:00:00", "UTC", "UTC"])
        out, _ = capsys.readouterr()
        assert "2025-06-15T10:00:00+00:00" in out
        assert "days," in out

    def test_bad_datetime_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["not-a-date", "UTC", "UTC"])
        assert exc.value.code == 1
        _, err = capsys.readouterr()
        assert err != ""

    def test_bad_timezone_exits_one(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["2025-06-15 10:00:00", "Mars/Olympus_Mons", "UTC"])
        assert exc.value.code == 1
        _, err = capsys.readouterr()
        assert err != ""
