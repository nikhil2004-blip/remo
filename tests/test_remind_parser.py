"""Tests for commands/remind.py — time parser."""

import pytest

from remo.commands.remind import parse_time


class TestParseTime:
    def test_minutes(self):
        assert parse_time("30m") == 1800

    def test_hours(self):
        assert parse_time("2h") == 7200

    def test_seconds(self):
        assert parse_time("90s") == 90

    def test_one_second(self):
        assert parse_time("1s") == 1

    def test_one_minute(self):
        assert parse_time("1m") == 60

    def test_large_value(self):
        assert parse_time("90m") == 5400

    def test_no_unit_raises(self):
        """Time without unit should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_time("5")
        assert "unit" in str(exc_info.value).lower() or "format" in str(exc_info.value).lower()

    def test_zero_raises(self):
        """Zero duration should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_time("0m")
        assert "0" in str(exc_info.value) or "greater" in str(exc_info.value).lower()

    def test_invalid_unit_raises(self):
        """Unknown unit should raise ValueError."""
        with pytest.raises(ValueError):
            parse_time("30x")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_time("")

    def test_negative_raises(self):
        """Negative values are rejected (no match for regex)."""
        with pytest.raises(ValueError):
            parse_time("-5m")

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is handled."""
        assert parse_time("  10m  ") == 600
