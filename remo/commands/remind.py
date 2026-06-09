"""remo remind — set a one-off reminder that fires after a given time."""

import re
import subprocess
import sys
from typing import Tuple

import click
from rich.console import Console

from remo.ui.colors import COLORS

console = Console()

_TIME_PATTERN = re.compile(r"^(\d+)([smh])$")

# Threshold above which we warn about very long reminders
_VERY_LONG_HOURS = 99


def parse_time(time_str: str) -> int:
    """Parse a time string like '30m', '2h', '90s' into seconds.

    Args:
        time_str: Time string with unit (s/m/h).

    Returns:
        Number of seconds.

    Raises:
        ValueError: If the format is invalid or value is <= 0.
    """
    match = _TIME_PATTERN.match(time_str.strip())
    if not match:
        raise ValueError(
            f"Invalid time format: {time_str!r}. "
            "Use <number><unit> where unit is s, m, or h. "
            "Examples: 30s  10m  2h"
        )

    value = int(match.group(1))
    unit = match.group(2)

    if value <= 0:
        raise ValueError("Time must be greater than 0.")

    multipliers = {"s": 1, "m": 60, "h": 3600}
    return value * multipliers[unit]


def _spawn_reminder(seconds: int, message: str, project_name: str) -> None:
    """Spawn a detached subprocess that will fire the reminder after `seconds`."""
    try:
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "remo._reminder_worker",
                str(seconds),
                message,
                project_name,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        console.print(
            f"[red]✗ Error:[/red] Failed to spawn reminder subprocess: {exc}"
        )
        sys.exit(1)


def _get_project_name() -> str:
    """Try to get project name from .remo config; fall back to directory name."""
    try:
        from remo.config.loader import load_config
        config, _ = load_config()
        return config.get("project", "remo")
    except Exception:
        import os
        return os.path.basename(os.getcwd())


@click.command()
@click.argument("time_str", metavar="<time>")
@click.argument("message")
@click.option(
    "--persist",
    is_flag=True,
    default=False,
    help="Persist reminder across terminal close (uses cron on Unix, Task Scheduler on Windows).",
)
def remind(time_str: str, message: str, persist: bool) -> None:
    """Set a one-off reminder that fires after <time>.

    \b
    TIME FORMAT:  <number><unit>
    Units:        s = seconds, m = minutes, h = hours
    Examples:     remo remind 30m "Push to GitHub"
                  remo remind 2h "Run tests"
                  remo remind 90s "Check if server started"
    """
    try:
        seconds = parse_time(time_str)
    except ValueError as exc:
        console.print(f"[red]✗ Error:[/red] {exc}")
        console.print(f"[dim]  Hint: Use formats like 30s, 10m, 2h[/dim]")
        sys.exit(1)

    # Warn about very long reminders (> 99 hours)
    hours = seconds / 3600
    if hours > _VERY_LONG_HOURS:
        console.print(
            f"[{COLORS['warning']}]! Warning:[/] That's {hours:.0f} hours — "
            "are you sure? (Ctrl+C to cancel, Enter to proceed)"
        )
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            console.print("[dim]Cancelled.[/dim]")
            sys.exit(0)

    project_name = _get_project_name()

    if persist:
        # TODO: implement cron / Task Scheduler persist
        console.print(
            f"[{COLORS['warning']}]! Note:[/] --persist is not yet implemented. "
            "Reminder will run in the current session only."
        )

    _spawn_reminder(seconds, message, project_name)

    # Human-readable confirmation
    if seconds < 60:
        human_time = f"{seconds}s"
    elif seconds < 3600:
        human_time = f"{seconds // 60}m"
    else:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        human_time = f"{h}h {m}m" if m else f"{h}h"

    console.print(
        f"  [{COLORS['success']}]✓[/] Reminder set: "
        f"[bold]\"{message}\"[/] "
        f"[dim]in {human_time}[/dim]"
    )
