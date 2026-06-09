"""Check .env file against .env.example — report missing keys."""

from pathlib import Path
from typing import Dict, List, NamedTuple


class EnvCheckResult(NamedTuple):
    """Result of an .env check."""

    status: str  # "pass" | "fail" | "skip"
    missing_keys: List[str]
    present_count: int
    total_count: int
    message: str


def _parse_env_keys(path: Path) -> List[str]:
    """Parse key names from a .env-style file (ignores comments and blanks)."""
    keys: List[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                if key:
                    keys.append(key)
    return keys


def run_env_check(
    example_file: str,
    env_file: str = ".env",
    base_dir: Path = Path("."),
) -> EnvCheckResult:
    """Compare .env against .env.example and report missing keys.

    Args:
        example_file: Path to the .env.example file (relative to base_dir).
        env_file: Path to the .env file (relative to base_dir).
        base_dir: Directory to resolve paths against.

    Returns:
        EnvCheckResult with status, missing keys, and counts.
    """
    example_path = base_dir / example_file
    env_path = base_dir / env_file

    if not example_path.exists():
        return EnvCheckResult(
            status="skip",
            missing_keys=[],
            present_count=0,
            total_count=0,
            message=f"{example_file} not found — skipping env check",
        )

    example_keys = _parse_env_keys(example_path)
    total = len(example_keys)

    if not env_path.exists():
        return EnvCheckResult(
            status="fail",
            missing_keys=example_keys,
            present_count=0,
            total_count=total,
            message=f".env not found — all {total} keys missing",
        )

    env_keys = set(_parse_env_keys(env_path))
    missing = [k for k in example_keys if k not in env_keys]
    present = total - len(missing)

    if missing:
        return EnvCheckResult(
            status="fail",
            missing_keys=missing,
            present_count=present,
            total_count=total,
            message=f"missing keys: {', '.join(missing)}",
        )

    return EnvCheckResult(
        status="pass",
        missing_keys=[],
        present_count=total,
        total_count=total,
        message=f"all {total} keys present",
    )
