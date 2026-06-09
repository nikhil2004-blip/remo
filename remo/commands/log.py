"""remo log — append and display the project micro-log."""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.rule import Rule

from remo.ui.colors import COLORS
from remo.ui.icons import icon

console = Console()

LOG_FILENAME = ".remo.log"
DEFAULT_DISPLAY_COUNT = 10
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"


def _get_log_path(config_dir: Optional[Path] = None) -> Path:
    """Return path to .remo.log, using config_dir if provided."""
    if config_dir is not None:
        return config_dir / LOG_FILENAME

    # Try to find config_dir from loader
    try:
        from remo.config.loader import load_config
        _, config_dir = load_config()
        return config_dir / LOG_FILENAME
    except Exception:
        return Path.cwd() / LOG_FILENAME


def _read_entries(log_path: Path) -> List[str]:
    """Read all log entries from the log file."""
    if not log_path.exists():
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as fh:
            return [line.rstrip() for line in fh if line.strip()]
    except OSError:
        return []


def _append_entry(log_path: Path, message: str) -> None:
    """Append a timestamped entry to the log file."""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    entry = f"[{timestamp}]  {message}"
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(entry + "\n")
    except OSError as exc:
        console.print(f"[red]✗ Error:[/red] Could not write to log: {exc}")
        sys.exit(1)


@click.command()
@click.argument("message", required=False, default=None)
@click.option("--all", "show_all", is_flag=True, default=False, help="Show full log history.")
def log(message: Optional[str], show_all: bool) -> None:
    """Append a note to the project log, or display recent entries.

    \b
    Examples:
      remo log "fixed auth redirect bug"    # append entry
      remo log                              # show last 10 entries
      remo log --all                        # show all entries
    """
    try:
        from remo.config.loader import load_config, ConfigError
        _, config_dir = load_config()
        log_path = config_dir / LOG_FILENAME
        project_name = None
        try:
            config, _ = load_config()
            project_name = config.get("project", "Project")
        except Exception:
            pass
    except Exception:
        # Graceful: use cwd if no .remo found
        log_path = Path.cwd() / LOG_FILENAME
        project_name = os.path.basename(os.getcwd())

    if message:
        # Append mode
        _append_entry(log_path, message)
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        console.print(
            f"  [{COLORS['success']}]✓[/] Logged: "
            f"[dim][{timestamp}][/dim] {message}"
        )
    else:
        # Display mode
        entries = _read_entries(log_path)

        console.print()
        console.print(Rule(
            f"  [{COLORS['header']}]{icon('log')} Project Log"
            f"{f' — {project_name}' if project_name else ''}[/]  ",
            style=COLORS["dim"],
        ))

        if not entries:
            console.print(
                f"  [dim]No entries yet. Use [bold]remo log \"message\"[/bold] to add one.[/]"
            )
        else:
            display = entries if show_all else entries[-DEFAULT_DISPLAY_COUNT:]
            if not show_all and len(entries) > DEFAULT_DISPLAY_COUNT:
                console.print(
                    f"  [dim]Showing last {DEFAULT_DISPLAY_COUNT} of {len(entries)} entries. "
                    "Use [bold]--all[/bold] for full history.[/]"
                )
            for entry in display:
                console.print(f"  {entry}")

        console.print()
