"""Check a shell command's exit code."""

import subprocess
from typing import NamedTuple, Optional


class CmdCheckResult(NamedTuple):
    """Result of a command exit-code check."""

    status: str  # "pass" | "fail"
    cmd: str
    label: str
    exit_code: Optional[int]
    message: str


def run_cmd_check(cmd: str, label: Optional[str] = None) -> CmdCheckResult:
    """Run a shell command and check that it exits with code 0.

    Args:
        cmd: Shell command string to execute.
        label: Human-readable label for display (defaults to cmd).

    Returns:
        CmdCheckResult with status and exit code.
    """
    display_label = label or cmd

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            timeout=15,
        )
        if result.returncode == 0:
            return CmdCheckResult(
                status="pass",
                cmd=cmd,
                label=display_label,
                exit_code=0,
                message="running (exit 0)",
            )
        return CmdCheckResult(
            status="fail",
            cmd=cmd,
            label=display_label,
            exit_code=result.returncode,
            message=f"exited with code {result.returncode}",
        )
    except subprocess.TimeoutExpired:
        return CmdCheckResult(
            status="fail",
            cmd=cmd,
            label=display_label,
            exit_code=None,
            message="command timed out after 15s",
        )
    except Exception as exc:
        return CmdCheckResult(
            status="fail",
            cmd=cmd,
            label=display_label,
            exit_code=None,
            message=f"error running command: {exc}",
        )
