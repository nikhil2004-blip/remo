"""Tests for config/loader.py — load, merge, and locate .remo files."""

import json
import pytest
from pathlib import Path

from remo.config.loader import (
    ConfigError,
    _merge_configs,
    load_config,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def remo_dir(tmp_path):
    """A temp directory with a valid .remo file."""
    remo = {
        "project": "TestProject",
        "startup": ["step 1", "step 2"],
        "shortcuts": {"dev": "python app.py"},
    }
    (tmp_path / ".remo").write_text(json.dumps(remo))
    return tmp_path


@pytest.fixture
def remo_with_local(remo_dir):
    """A temp directory with both .remo and .remo.local."""
    local = {
        "startup": ["local step"],
        "shortcuts": {"dev": "python app.py --debug"},
    }
    (remo_dir / ".remo.local").write_text(json.dumps(local))
    return remo_dir


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestLoadConfig:
    def test_load_valid_remo(self, remo_dir):
        """Loading a valid .remo returns correct dict and path."""
        config, config_dir = load_config(remo_dir)
        assert config["project"] == "TestProject"
        assert config_dir == remo_dir

    def test_load_remo_and_local_merged(self, remo_with_local):
        """Loading .remo + .remo.local merges them correctly."""
        config, _ = load_config(remo_with_local)
        # startup: local appends to base
        assert "step 1" in config["startup"]
        assert "local step" in config["startup"]
        assert config["startup"].index("step 1") < config["startup"].index("local step")
        # shortcuts: local overrides base
        assert config["shortcuts"]["dev"] == "python app.py --debug"

    def test_missing_remo_raises_config_error(self, tmp_path):
        """Missing .remo raises ConfigError with clear message."""
        with pytest.raises(ConfigError) as exc_info:
            load_config(tmp_path)
        assert "No .remo file" in str(exc_info.value)
        assert exc_info.value.hint  # hint must be present

    def test_invalid_json_raises_config_error(self, tmp_path):
        """Invalid JSON in .remo raises ConfigError pointing to the problem."""
        (tmp_path / ".remo").write_text('{"project": "Test", bad json}')
        with pytest.raises(ConfigError) as exc_info:
            load_config(tmp_path)
        assert "Invalid JSON" in str(exc_info.value)


class TestMergeConfigs:
    def test_startup_appends(self):
        base = {"project": "P", "startup": ["a", "b"]}
        local = {"startup": ["c"]}
        merged = _merge_configs(base, local)
        assert merged["startup"] == ["a", "b", "c"]

    def test_shortcuts_override(self):
        base = {"project": "P", "shortcuts": {"dev": "cmd1", "test": "pytest"}}
        local = {"shortcuts": {"dev": "cmd2"}}
        merged = _merge_configs(base, local)
        assert merged["shortcuts"]["dev"] == "cmd2"
        assert merged["shortcuts"]["test"] == "pytest"  # unchanged

    def test_other_keys_overridden(self):
        base = {"project": "Old"}
        local = {"project": "New"}
        merged = _merge_configs(base, local)
        assert merged["project"] == "New"

    def test_empty_local_leaves_base_unchanged(self):
        base = {"project": "P", "startup": ["step1"]}
        merged = _merge_configs(base, {})
        assert merged == base
