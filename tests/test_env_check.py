"""Tests for checks/env_check.py."""

import pytest
from pathlib import Path

from remo.checks.env_check import run_env_check


@pytest.fixture
def env_dir(tmp_path):
    """Return a temp dir with .env.example containing 4 keys."""
    (tmp_path / ".env.example").write_text(
        "DATABASE_URL=\nSECRET_KEY=\nDEBUG=\nALLOWED_HOSTS=\n"
    )
    return tmp_path


class TestEnvCheck:
    def test_all_keys_present_passes(self, env_dir):
        """.env with all keys from .env.example → status pass."""
        (env_dir / ".env").write_text(
            "DATABASE_URL=postgres://\nSECRET_KEY=abc\nDEBUG=true\nALLOWED_HOSTS=*\n"
        )
        result = run_env_check(".env.example", base_dir=env_dir)
        assert result.status == "pass"
        assert result.missing_keys == []
        assert result.total_count == 4
        assert result.present_count == 4

    def test_missing_keys_fail(self, env_dir):
        """.env missing 2 keys → status fail, both keys in missing_keys."""
        (env_dir / ".env").write_text("DATABASE_URL=postgres://\nSECRET_KEY=abc\n")
        result = run_env_check(".env.example", base_dir=env_dir)
        assert result.status == "fail"
        assert "DEBUG" in result.missing_keys
        assert "ALLOWED_HOSTS" in result.missing_keys
        assert len(result.missing_keys) == 2

    def test_missing_example_file_skips(self, tmp_path):
        """.env.example missing → status skip, no crash."""
        result = run_env_check(".env.example", base_dir=tmp_path)
        assert result.status == "skip"
        assert "not found" in result.message

    def test_empty_env_all_keys_missing(self, env_dir):
        """Empty .env → all keys missing → status fail."""
        (env_dir / ".env").write_text("")
        result = run_env_check(".env.example", base_dir=env_dir)
        assert result.status == "fail"
        assert result.missing_keys == ["DATABASE_URL", "SECRET_KEY", "DEBUG", "ALLOWED_HOSTS"]
        assert result.present_count == 0

    def test_env_file_missing_all_keys_fail(self, env_dir):
        """.env not present → status fail, all keys shown."""
        result = run_env_check(".env.example", base_dir=env_dir)
        assert result.status == "fail"
        assert result.total_count == 4

    def test_env_with_comments_skipped(self, tmp_path):
        """Comments in .env files should be ignored."""
        (tmp_path / ".env.example").write_text(
            "# Required vars\nDATABASE_URL=\n# Another comment\nSECRET_KEY=\n"
        )
        (tmp_path / ".env").write_text(
            "DATABASE_URL=postgres://\nSECRET_KEY=abc\n"
        )
        result = run_env_check(".env.example", base_dir=tmp_path)
        assert result.status == "pass"
