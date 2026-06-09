"""Check that a required file exists on disk."""

from pathlib import Path
from typing import NamedTuple


class FileCheckResult(NamedTuple):
    """Result of a file existence check."""

    status: str  # "pass" | "fail"
    path: str
    message: str


def run_file_check(path: str, base_dir: Path = Path(".")) -> FileCheckResult:
    """Assert that a file exists.

    Args:
        path: File path to check (relative to base_dir or absolute).
        base_dir: Directory to resolve relative paths against.

    Returns:
        FileCheckResult with status and message.
    """
    target = Path(path)
    if not target.is_absolute():
        target = base_dir / path

    if target.exists():
        return FileCheckResult(
            status="pass",
            path=str(path),
            message="exists",
        )

    return FileCheckResult(
        status="fail",
        path=str(path),
        message=f"file not found: {target}",
    )
