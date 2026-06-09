"""remo startup panel — displayed when `remo` is run with no arguments."""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from remo.config.global_config import get_sessions_dir, load_global_config
from remo.ui.colors import COLORS
from remo.ui.icons import icon

console = Console()

_SESSION_DIR = None  # Resolved lazily


def _get_project_hash(config_dir: Path) -> str:
    """Create a stable hash from the project directory path."""
    return hashlib.md5(str(config_dir.resolve()).encode()).hexdigest()[:12]


def _get_session_file(config_dir: Path) -> Path:
    """Return the session state file path for this project."""
    sessions_dir = get_sessions_dir()
    project_hash = _get_project_hash(config_dir)
    return sessions_dir / f"{project_hash}.json"


def _load_session(session_file: Path) -> Dict[str, Any]:
    """Load session state from disk or return an empty dict."""
    if session_file.exists():
        try:
            with open(session_file, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_session(session_file: Path, session: Dict[str, Any]) -> None:
    """Persist session state to disk."""
    try:
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(session_file, "w", encoding="utf-8") as fh:
            json.dump(session, fh, indent=2)
    except OSError:
        pass


def _format_time_ago(iso_str: str) -> str:
    """Format an ISO timestamp as a human-readable 'X ago' string."""
    try:
        then = datetime.fromisoformat(iso_str)
        # Make aware if naive
        if then.tzinfo is None:
            then = then.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - then
        seconds = int(delta.total_seconds())
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            return f"{seconds // 60}m ago"
        elif seconds < 86400:
            return f"{seconds // 3600}h ago"
        else:
            days = seconds // 86400
            return f"{days}d ago"
    except Exception:
        return "unknown"


def _get_last_log_entry(config_dir: Path) -> Optional[str]:
    """Return the most recent entry from .remo.log, or None."""
    log_path = config_dir / ".remo.log"
    if not log_path.exists():
        return None
    try:
        with open(log_path, "r", encoding="utf-8") as fh:
            lines = [l.rstrip() for l in fh if l.strip()]
        return lines[-1] if lines else None
    except OSError:
        return None


def _launch_auto_reminders(
    reminders: list, project_name: str, config_dir: Path
) -> None:
    """Spawn detached subprocess reminders for all auto-reminders in config."""
    import subprocess
    from remo.commands.remind import parse_time

    for reminder in reminders:
        after_str = reminder.get("after", "")
        message = reminder.get("message", "")
        if not after_str or not message:
            continue
        try:
            seconds = parse_time(after_str)
        except ValueError:
            continue

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
                cwd=str(config_dir),
            )
        except OSError:
            pass


def show_startup() -> None:
    """Show the remo startup panel for the current project.

    Reads .remo config, displays startup checklist, shortcuts, last log entry,
    and pending reminders. Launches auto-reminders as detached subprocesses.
    """
    from remo.config.loader import load_config, ConfigError

    global_cfg = load_global_config()
    theme = global_cfg.get("theme", "default")
    minimal = theme == "minimal"

    try:
        config, config_dir = load_config()
    except ConfigError as exc:
        console.print(f"[red]✗ Error:[/red] {exc}")
        if exc.hint:
            console.print(f"[dim]  Hint: {exc.hint}[/dim]")
        sys.exit(1)

    project_name = config.get("project", "Unnamed Project")
    startup_steps = config.get("startup", [])
    shortcuts_dict = config.get("shortcuts", {})
    reminders = config.get("reminders", [])

    # Session state
    session_file = _get_session_file(config_dir)
    session = _load_session(session_file)
    now_iso = datetime.now(timezone.utc).isoformat()
    last_opened_iso = session.get("last_opened")
    last_opened_str = _format_time_ago(last_opened_iso) if last_opened_iso else "first time"

    # Update session
    session["last_opened"] = now_iso
    session["project"] = project_name
    session["started"] = now_iso
    _save_session(session_file, session)

    if minimal:
        # Plain text output for CI / piping
        print(f"remo · {project_name}  (last opened: {last_opened_str})")
        if startup_steps:
            print("\nStartup Checklist:")
            for i, step in enumerate(startup_steps, 1):
                print(f"  {i}  {step}")
        if shortcuts_dict:
            print(f"\nShortcuts: {' · '.join(shortcuts_dict.keys())}")
    else:
        # Rich panel display
        # ── Header ──
        header_left = Text()
        header_left.append("remo", style=f"bold {COLORS['header']}")
        header_left.append("  ·  ", style="dim")
        header_left.append(project_name, style="bold white")
        header_right = Text(f"last opened: {last_opened_str}", style=COLORS["dim"])

        header_content = Columns(
            [header_left, header_right], expand=True, align="right"
        )
        console.print(Panel(header_content, border_style=COLORS["header"]))
        console.print()

        # ── Startup checklist ──
        if startup_steps:
            console.print(
                f"  [{COLORS['header']}]{icon('checklist')} Startup Checklist[/]"
            )
            console.print(
                f"  [{COLORS['dim']}]{'─' * 49}[/]"
            )
            for i, step in enumerate(startup_steps, 1):
                console.print(f"   [dim]{i:>2}[/]  {step}")
            console.print()

        # ── Shortcuts ──
        if shortcuts_dict:
            shortcut_names = " · ".join(shortcuts_dict.keys())
            console.print(
                f"  [{COLORS['header']}]{icon('shortcut')} Shortcuts[/]"
                f"   [{COLORS['dim']}]{shortcut_names}[/]"
            )

        # ── Last log ──
        last_log = _get_last_log_entry(config_dir)
        if last_log:
            console.print(
                f"  [{COLORS['header']}]{icon('log')} Last log[/]"
                f"    [{COLORS['dim']}]{last_log}[/]"
            )

        # ── Reminders ──
        if reminders:
            reminder_parts = [
                f"{r.get('after')} → \"{r.get('message')}\""
                for r in reminders
                if r.get("after") and r.get("message")
            ]
            if reminder_parts:
                console.print(
                    f"  [{COLORS['warning']}]{icon('reminder')} Reminders[/]"
                    f"   [{COLORS['dim']}]auto-fires in: {',  '.join(reminder_parts)}[/]"
                )

        console.print()
        console.print(
            f"  [dim]Type  [bold]remo log[/bold]   to add a note"
            f"   |   [bold]remo run <shortcut>[/bold]   to start[/]"
        )
        console.print()

    # Launch auto-reminders as detached subprocesses
    _launch_auto_reminders(reminders, project_name, config_dir)
