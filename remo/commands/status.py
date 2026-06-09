"""remo status — show session time, queued reminders, and last log entry."""

import sys
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console
from rich.rule import Rule

from remo.ui.colors import COLORS
from remo.ui.icons import icon

console = Console()


@click.command()
def status() -> None:
    """Show current session status: elapsed time, reminders, last log entry."""
    from remo.config.loader import load_config, ConfigError

    try:
        config, config_dir = load_config()
    except ConfigError as exc:
        console.print(f"[red]✗ Error:[/red] {exc}")
        if exc.hint:
            console.print(f"[dim]  Hint: {exc.hint}[/dim]")
        sys.exit(1)

    from remo.commands.startup import _get_session_file, _load_session

    project_name = config.get("project", "Project")
    reminders = config.get("reminders", [])

    session_file = _get_session_file(config_dir)
    session = _load_session(session_file)

    console.print()
    console.print(Rule(
        f"  [{COLORS['header']}]Session Status — {project_name}[/]  ",
        style=COLORS["dim"],
    ))

    # Session start time + elapsed
    started_iso = session.get("started")
    if started_iso:
        try:
            started = datetime.fromisoformat(started_iso)
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            local_started = started.astimezone()
            now = datetime.now(timezone.utc)
            delta = now - started
            minutes = int(delta.total_seconds() // 60)
            hours = minutes // 60
            mins = minutes % 60
            if hours > 0:
                elapsed_str = f"{hours}h {mins}m"
            else:
                elapsed_str = f"{mins}m"
            started_str = local_started.strftime("%H:%M")
            console.print(
                f"  [{COLORS['header']}]Session:[/]    "
                f"started at {started_str}, elapsed [bold]{elapsed_str}[/]"
            )
        except Exception:
            console.print(f"  [{COLORS['header']}]Session:[/]    unknown")
    else:
        console.print(
            f"  [{COLORS['header']}]Session:[/]    "
            f"[dim]not started yet — run [bold]remo[/bold] to open session[/]"
        )

    # Queued reminders count
    reminder_count = len(reminders)
    if reminder_count > 0:
        reminder_labels = [
            f"{r.get('after')} → \"{r.get('message')}\""
            for r in reminders
        ]
        console.print(
            f"  [{COLORS['warning']}]{icon('reminder')} Reminders:[/]  "
            f"[bold]{reminder_count}[/] queued  [dim]({', '.join(reminder_labels)})[/]"
        )
    else:
        console.print(
            f"  [{COLORS['warning']}]{icon('reminder')} Reminders:[/]  "
            f"[dim]none[/]"
        )

    # Last log entry
    log_path = config_dir / ".remo.log"
    last_entry = None
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as fh:
                lines = [l.rstrip() for l in fh if l.strip()]
            last_entry = lines[-1] if lines else None
        except OSError:
            pass

    if last_entry:
        console.print(
            f"  [{COLORS['header']}]{icon('log')} Last log:[/]   "
            f"[dim]{last_entry}[/]"
        )
    else:
        console.print(
            f"  [{COLORS['header']}]{icon('log')} Last log:[/]   "
            f"[dim]no entries yet[/]"
        )

    console.print()
