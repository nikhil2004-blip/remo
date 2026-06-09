"""remo snooze — snooze the most recently fired reminder."""

import subprocess
import sys

import click
from rich.console import Console

from remo.commands.remind import parse_time
from remo.ui.colors import COLORS

console = Console()

_DEFAULT_SNOOZE = "10m"


@click.command()
@click.argument("time_str", metavar="[time]", required=False, default=None)
def snooze(time_str: str) -> None:
    """Snooze the most recent reminder (default: 10 minutes).

    \b
    Examples:
      remo snooze          # snooze for 10 minutes
      remo snooze 5m       # snooze for 5 minutes
      remo snooze 30s      # snooze for 30 seconds
    """
    snooze_time = time_str or _DEFAULT_SNOOZE

    try:
        seconds = parse_time(snooze_time)
    except ValueError as exc:
        console.print(f"[red]✗ Error:[/red] {exc}")
        console.print(f"[dim]  Hint: Use formats like 5m, 30s, 1h[/dim]")
        sys.exit(1)

    # Get last reminder from session state
    last_message = _get_last_reminder_message()
    message = f"[SNOOZED] {last_message}" if last_message else "[SNOOZED] reminder"

    # Get project name
    project_name = _get_project_name()

    # Spawn snoozed reminder
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
        console.print(f"[red]✗ Error:[/red] Failed to spawn snooze: {exc}")
        sys.exit(1)

    if seconds < 60:
        human = f"{seconds}s"
    elif seconds < 3600:
        human = f"{seconds // 60}m"
    else:
        human = f"{seconds // 3600}h"

    console.print(
        f"  [{COLORS['warning']}]⏰[/] Snoozed for [bold]{human}[/]. "
        f"[dim]{message}[/]"
    )


def _get_last_reminder_message() -> str:
    """Try to retrieve the last reminder message from session state."""
    try:
        from remo.config.loader import load_config
        from remo.commands.startup import _get_session_file, _load_session
        _, config_dir = load_config()
        session_file = _get_session_file(config_dir)
        session = _load_session(session_file)
        return session.get("last_reminder", "")
    except Exception:
        return ""


def _get_project_name() -> str:
    """Get project name from .remo config or use directory name."""
    try:
        from remo.config.loader import load_config
        config, _ = load_config()
        return config.get("project", "remo")
    except Exception:
        import os
        return os.path.basename(os.getcwd())
