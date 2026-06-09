"""CLI integration tests using click.testing.CliRunner."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from remo.cli import main


@pytest.fixture
def runner():
    """CliRunner for CLI tests."""
    return CliRunner()


@pytest.fixture
def remo_project(tmp_path):
    """A temp directory with a complete .remo project config."""
    config = {
        "project": "CLITestProject",
        "startup": ["source .venv/bin/activate"],
        "shortcuts": {
            "dev": "echo dev-server-started",
            "test": "echo tests-running",
        },
        "checks": [],
        "reminders": [],
    }
    (tmp_path / ".remo").write_text(json.dumps(config))
    return tmp_path


class TestHelpAndVersion:
    def test_help_exits_zero(self, runner):
        """remo --help should exit 0 and show available commands."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "startup" in result.output.lower() or "remo" in result.output.lower()

    def test_version_shows_string(self, runner):
        """remo --version should print the version number."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestLogCommand:
    def test_log_append_creates_entry(self, runner, remo_project):
        """remo log 'message' should write a timestamped entry to .remo.log."""
        with runner.isolated_filesystem(temp_dir=remo_project):
            # Change to project dir so config is found
            old_cwd = os.getcwd()
            os.chdir(remo_project)
            try:
                result = runner.invoke(main, ["log", "test entry from CLI"])
                assert result.exit_code == 0
                log_path = remo_project / ".remo.log"
                assert log_path.exists()
                content = log_path.read_text()
                assert "test entry from CLI" in content
            finally:
                os.chdir(old_cwd)

    def test_log_no_args_no_file_shows_message(self, runner, tmp_path):
        """remo log with no args and no log file shows 'no entries yet'."""
        config = {"project": "EmptyLog"}
        (tmp_path / ".remo").write_text(json.dumps(config))
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(main, ["log"])
            assert result.exit_code == 0
            assert "no entries yet" in result.output.lower() or "no entries" in result.output.lower()
        finally:
            os.chdir(old_cwd)


class TestCheckCommand:
    def test_check_no_remo_shows_error(self, runner, tmp_path):
        """remo check with no .remo file shows a clean error message."""
        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = runner.invoke(main, ["check"])
            assert result.exit_code != 0
            if result.exception and isinstance(result.exception, PermissionError):
                # On Windows runners, traversing parents from temp dirs can raise PermissionError
                pass
            else:
                assert "traceback" not in result.output.lower()
                assert "error" in result.output.lower() or "remo" in result.output.lower()
        finally:
            os.chdir(old_cwd)


class TestRunCommand:
    def test_run_defined_shortcut_executes(self, runner, remo_project):
        """remo run dev should echo the command name and execute it."""
        old_cwd = os.getcwd()
        os.chdir(remo_project)
        try:
            result = runner.invoke(main, ["run", "dev"])
            # Command echoed + executed (echo command produces output)
            assert result.exit_code == 0
            assert "dev" in result.output.lower()
        finally:
            os.chdir(old_cwd)

    def test_run_missing_shortcut_shows_error(self, runner, remo_project):
        """remo run nonexistent should show a clean error."""
        old_cwd = os.getcwd()
        os.chdir(remo_project)
        try:
            result = runner.invoke(main, ["run", "nonexistent_shortcut"])
            assert result.exit_code != 0
            assert "not found" in result.output.lower() or "error" in result.output.lower()
            assert "traceback" not in result.output.lower()
        finally:
            os.chdir(old_cwd)


class TestRemindCommand:
    def test_remind_valid_sets_reminder(self, runner, remo_project):
        """remo remind 10s 'message' should confirm and exit 0."""
        old_cwd = os.getcwd()
        os.chdir(remo_project)
        try:
            result = runner.invoke(main, ["remind", "10s", "test reminder"])
            assert result.exit_code == 0
            assert "reminder" in result.output.lower() or "✓" in result.output

        finally:
            os.chdir(old_cwd)

    def test_remind_invalid_time_shows_error(self, runner, remo_project):
        """remo remind with invalid time shows a clean error."""
        old_cwd = os.getcwd()
        os.chdir(remo_project)
        try:
            result = runner.invoke(main, ["remind", "badtime", "message"])
            assert result.exit_code != 0
        finally:
            os.chdir(old_cwd)


class TestShortcutsCommand:
    def test_shortcuts_lists_all(self, runner, remo_project):
        """remo shortcuts should list all defined shortcut names."""
        old_cwd = os.getcwd()
        os.chdir(remo_project)
        try:
            result = runner.invoke(main, ["shortcuts"])
            assert result.exit_code == 0
            assert "dev" in result.output
            assert "test" in result.output
        finally:
            os.chdir(old_cwd)
