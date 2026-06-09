"""Tests for checks/version_check.py."""

import sys
from unittest.mock import patch, MagicMock

import pytest

from remo.checks.version_check import (
    _compare_versions,
    _parse_version,
    run_version_check,
)


class TestParseVersion:
    def test_simple_version(self):
        assert _parse_version("3.11.2") == (3, 11, 2)

    def test_two_part_version(self):
        assert _parse_version("3.11") == (3, 11)

    def test_single_version(self):
        assert _parse_version("3") == (3,)

    def test_version_in_output_string(self):
        """Parses version from noisy output like 'Python 3.11.2'."""
        result = _parse_version("Python 3.11.2")
        assert result == (3, 11, 2)

    def test_no_version_returns_none(self):
        assert _parse_version("no version here") is None


class TestCompareVersions:
    def test_equal_versions_pass(self):
        assert _compare_versions((3, 11), (3, 11)) is True

    def test_greater_major_passes(self):
        assert _compare_versions((4, 0), (3, 9)) is True

    def test_lesser_minor_fails(self):
        assert _compare_versions((3, 10), (3, 11)) is False

    def test_patch_comparison(self):
        assert _compare_versions((3, 11, 2), (3, 11, 0)) is True

    def test_different_lengths_padded(self):
        assert _compare_versions((3, 11), (3, 11, 0)) is True


class TestRunVersionCheck:
    def test_python_version_meets_minimum(self):
        """Python is always available — test against a very low minimum."""
        result = run_version_check("python", "2.0")
        assert result.status == "pass"
        assert result.tool == "python"

    def test_tool_not_found_returns_missing(self):
        """A non-existent tool returns status 'missing', not an exception."""
        result = run_version_check("nonexistent_tool_xyz_12345", "1.0")
        assert result.status == "missing"
        assert result.found is None
        assert "not found" in result.message

    def test_version_below_minimum_fails(self):
        """Mock a tool version that's below minimum."""
        with patch("remo.checks.version_check._get_tool_version") as mock_ver:
            with patch("remo.checks.version_check.shutil.which") as mock_which:
                mock_which.return_value = "/usr/bin/node"
                mock_ver.return_value = "v16.14.0"
                result = run_version_check("node", "18.0")
        assert result.status == "fail"
        assert "18.0" in result.message

    def test_version_meets_minimum_passes(self):
        """Mock a tool version that meets minimum."""
        with patch("remo.checks.version_check._get_tool_version") as mock_ver:
            with patch("remo.checks.version_check.shutil.which") as mock_which:
                mock_which.return_value = "/usr/bin/node"
                mock_ver.return_value = "v20.0.0"
                result = run_version_check("node", "18.0")
        assert result.status == "pass"
