"""Check that a tool meets a minimum version requirement."""

import re
import shutil
import subprocess
from typing import List, NamedTuple, Optional, Tuple


class VersionCheckResult(NamedTuple):
    """Result of a version check."""

    status: str  # "pass" | "fail" | "missing"
    tool: str
    required: str
    found: Optional[str]
    message: str


def _parse_version(version_str: str) -> Optional[Tuple[int, ...]]:
    """Parse a version string like '3.11.2' into a tuple of ints."""
    match = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", version_str)
    if not match:
        return None
    parts = [int(g) for g in match.groups() if g is not None]
    return tuple(parts)


def _get_tool_version(tool: str) -> Optional[str]:
    """Run `tool --version` and return the output, or None if not found."""
    if shutil.which(tool) is None:
        return None

    # Some tools use `--version`, some use `version`, some use `-v`
    for flag in ["--version", "-v", "version"]:
        try:
            result = subprocess.run(
                [tool, flag],
                capture_output=True,
                text=True,
                timeout=5,
            )
            output = (result.stdout + result.stderr).strip()
            if output:
                return output
        except (subprocess.TimeoutExpired, OSError):
            continue

    return None


def _compare_versions(found: Tuple[int, ...], required: Tuple[int, ...]) -> bool:
    """Return True if found >= required."""
    # Pad shorter tuple with zeros
    max_len = max(len(found), len(required))
    found_padded = found + (0,) * (max_len - len(found))
    req_padded = required + (0,) * (max_len - len(required))
    return found_padded >= req_padded


def run_version_check(tool: str, min_version: str) -> VersionCheckResult:
    """Check that `tool` is installed and meets the minimum version.

    Args:
        tool: The tool name (e.g., "python", "node").
        min_version: Minimum required version string (e.g., "3.11").

    Returns:
        VersionCheckResult with status and details.
    """
    version_output = _get_tool_version(tool)

    if version_output is None:
        return VersionCheckResult(
            status="missing",
            tool=tool,
            required=min_version,
            found=None,
            message=f"{tool} not found in PATH",
        )

    found_version = _parse_version(version_output)
    req_version = _parse_version(min_version)

    if found_version is None or req_version is None:
        return VersionCheckResult(
            status="fail",
            tool=tool,
            required=min_version,
            found=version_output,
            message=f"could not parse version from output: {version_output!r}",
        )

    found_str = ".".join(str(x) for x in found_version)

    if _compare_versions(found_version, req_version):
        return VersionCheckResult(
            status="pass",
            tool=tool,
            required=min_version,
            found=found_str,
            message=f"found {found_str} (>= {min_version})",
        )

    return VersionCheckResult(
        status="fail",
        tool=tool,
        required=min_version,
        found=found_str,
        message=f"need >= {min_version}, found {found_str}",
    )
