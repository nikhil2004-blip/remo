"""Tests for config/schema.py — validate_config."""

import pytest

from remo.config.loader import ConfigError
from remo.config.schema import validate_config


class TestValidConfig:
    def test_full_valid_schema_passes(self):
        config = {
            "project": "TestProject",
            "startup": ["step 1", "step 2"],
            "reminders": [{"after": "30m", "message": "Push"}],
            "checks": [
                {"type": "env", "file": ".env.example"},
                {"type": "version", "tool": "python", "min": "3.9"},
                {"type": "file", "path": "requirements.txt"},
                {"type": "cmd", "cmd": "echo hi", "label": "echo"},
            ],
            "shortcuts": {"dev": "python app.py"},
        }
        # Should not raise
        validate_config(config)

    def test_minimal_valid_schema_passes(self):
        """Only 'project' is required."""
        validate_config({"project": "Minimal"})

    def test_missing_optional_fields_passes(self):
        """All optional fields can be omitted."""
        validate_config({"project": "OnlyRequired"})


class TestInvalidConfig:
    def test_missing_project_raises(self):
        with pytest.raises(ConfigError) as exc_info:
            validate_config({"startup": ["step 1"]})
        assert "project" in str(exc_info.value).lower()

    def test_empty_project_raises(self):
        with pytest.raises(ConfigError):
            validate_config({"project": "  "})

    def test_bad_reminder_time_format_raises(self):
        """Reminder with invalid time format (e.g. '30x') raises ConfigError."""
        with pytest.raises(ConfigError) as exc_info:
            validate_config({
                "project": "P",
                "reminders": [{"after": "30x", "message": "test"}],
            })
        assert "after" in str(exc_info.value).lower()

    def test_reminder_missing_message_raises(self):
        with pytest.raises(ConfigError):
            validate_config({
                "project": "P",
                "reminders": [{"after": "30m"}],
            })

    def test_reminder_missing_after_raises(self):
        with pytest.raises(ConfigError):
            validate_config({
                "project": "P",
                "reminders": [{"message": "hello"}],
            })

    def test_unknown_check_type_raises(self):
        with pytest.raises(ConfigError):
            validate_config({
                "project": "P",
                "checks": [{"type": "unknown_type"}],
            })

    def test_env_check_missing_file_raises(self):
        with pytest.raises(ConfigError):
            validate_config({
                "project": "P",
                "checks": [{"type": "env"}],  # missing "file"
            })

    def test_version_check_missing_tool_raises(self):
        with pytest.raises(ConfigError):
            validate_config({
                "project": "P",
                "checks": [{"type": "version", "min": "3.9"}],
            })

    def test_shortcuts_must_be_dict(self):
        with pytest.raises(ConfigError):
            validate_config({
                "project": "P",
                "shortcuts": ["not", "a", "dict"],
            })


class TestUnknownFields:
    def test_unknown_field_does_not_raise(self):
        """Unknown fields should NOT raise — forward compatibility."""
        # Should print a warning to stderr but not raise
        # (We just verify it doesn't raise ConfigError)
        import sys
        from io import StringIO
        stderr_capture = StringIO()
        old_stderr = sys.stderr
        sys.stderr = stderr_capture
        try:
            validate_config({"project": "P", "unknown_future_field": True})
        finally:
            sys.stderr = old_stderr
        # No exception means forward compat works
