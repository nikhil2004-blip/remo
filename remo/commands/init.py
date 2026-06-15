"""remo init — interactive wizard to create .remo config for a project."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from remo.ui.colors import COLORS

console = Console()


def _is_git_repo(directory: Path) -> bool:
    """Check if the directory is inside a git repository."""
    current = directory.resolve()
    for d in [current, *current.parents]:
        if (d / ".git").exists():
            return True
    return False


def _patch_gitignore(directory: Path) -> None:
    """Add .remo.local and .remo.log to .gitignore if not already present."""
    gitignore_path = directory / ".gitignore"
    entries_to_add = [".remo.local", ".remo.log"]

    existing: List[str] = []
    if gitignore_path.exists():
        try:
            with open(gitignore_path, "r", encoding="utf-8") as fh:
                existing = fh.read().splitlines()
        except OSError:
            pass

    to_add = [e for e in entries_to_add if e not in existing]
    if not to_add:
        return  # Already present

    try:
        with open(gitignore_path, "a", encoding="utf-8") as fh:
            fh.write("\n# remo — personal overrides and local log\n")
            for entry in to_add:
                fh.write(f"{entry}\n")
        console.print(
            f"  [{COLORS['success']}]✓[/] Updated .gitignore with: "
            f"[dim]{', '.join(to_add)}[/]"
        )
    except OSError as exc:
        console.print(
            f"  [{COLORS['warning']}]![/] Could not update .gitignore: {exc}"
        )


def _prompt_list(prompt: str) -> List[str]:
    """Prompt user for a list of items (one per line, blank to finish)."""
    console.print(f"  [dim]{prompt} (one per line, blank line to finish):[/]")
    items: List[str] = []
    while True:
        try:
            val = input("    > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not val:
            break
        items.append(val)
    return items


def _prompt_shortcuts() -> Dict[str, str]:
    """Prompt user for shortcut name → command pairs."""
    console.print(
        "  [dim]Define shortcuts (name=command, blank name to finish):[/]"
    )
    shortcuts: Dict[str, str] = {}
    while True:
        try:
            name = input("    shortcut name (or blank to finish): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not name:
            break
        try:
            cmd = input(f"    command for '{name}': ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if cmd:
            shortcuts[name] = cmd
    return shortcuts


def _prompt_reminders() -> List[Dict[str, str]]:
    """Prompt user for auto-reminder definitions."""
    console.print(
        "  [dim]Define auto-reminders (fires when you run remo at session start):[/]"
    )
    reminders: List[Dict[str, str]] = []
    while True:
        try:
            after = input("    fires after (e.g. 30m, 1h — blank to finish): ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not after:
            break
        try:
            message = input(f"    message for '{after}' reminder: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if message:
            reminders.append({"after": after, "message": message})
    return reminders


@click.command()
def init() -> None:
    """Interactive wizard to create .remo config for this project.

    Creates .remo (team config) and optionally .remo.local (personal).
    Automatically updates .gitignore if this is a git repository.
    """
    cwd = Path.cwd()
    remo_path = cwd / ".remo"

    console.print()
    console.print(Panel(
        f"[bold {COLORS['header']}]remo init[/]  —  setting up project config",
        border_style=COLORS["header"],
        padding=(0, 2),
    ))
    console.print()

    if remo_path.exists():
        console.print(
            f"  [{COLORS['warning']}]![/] A .remo file already exists in this directory."
        )
        try:
            overwrite = input("    Overwrite it? (y/N): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            overwrite = "n"
        if overwrite != "y":
            console.print("  [dim]Cancelled.[/]")
            sys.exit(0)

    # ── Project name ──
    console.print(Rule(f"  [{COLORS['header']}]Project Info[/]", style=COLORS["dim"]))
    try:
        project_name = input(
            f"  Project name [{os.path.basename(cwd)}]: "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        project_name = ""
    if not project_name:
        project_name = os.path.basename(cwd)

    # ── Startup checklist ──
    console.print()
    console.print(Rule(f"  [{COLORS['header']}]Startup Checklist[/]", style=COLORS["dim"]))
    startup = _prompt_list("Steps to show when opening this project")

    # ── Shortcuts ──
    console.print()
    console.print(Rule(f"  [{COLORS['header']}]Shortcuts[/]", style=COLORS["dim"]))
    shortcuts_dict = _prompt_shortcuts()

    # ── Auto-reminders ──
    console.print()
    console.print(Rule(f"  [{COLORS['header']}]Auto-Reminders[/]", style=COLORS["dim"]))
    reminders = _prompt_reminders()

    # ── Env check ──
    console.print()
    console.print(Rule(f"  [{COLORS['header']}]Environment Checks[/]", style=COLORS["dim"]))
    checks: List[Dict[str, Any]] = []
    try:
        env_example = input(
            "  Path to .env.example file (blank to skip): "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        env_example = ""
    if env_example:
        checks.append({"type": "env", "file": env_example})

    # ── Build config ──
    config: Dict[str, Any] = {"project": project_name}
    if startup:
        config["startup"] = startup
    if reminders:
        config["reminders"] = reminders
    if checks:
        config["checks"] = checks
    if shortcuts_dict:
        config["shortcuts"] = shortcuts_dict

    # ── Write .remo ──
    try:
        with open(remo_path, "w", encoding="utf-8") as fh:
            json.dump(config, fh, indent=4)
        console.print()
        console.print(
            f"  [{COLORS['success']}]✓[/] Created [bold].remo[/] for "
            f"[bold]{project_name}[/]"
        )
    except OSError as exc:
        console.print(f"  [red]✗ Error:[/red] Could not write .remo: {exc}")
        sys.exit(1)

    # ── Git integration ──
    if _is_git_repo(cwd):
        _patch_gitignore(cwd)
    else:
        console.print(
            f"  [dim]Not a git repo — skipping .gitignore update.[/]"
        )

    # Launch auto-reminders directly after init
    if reminders:
        from remo.commands.startup import _launch_auto_reminders
        _launch_auto_reminders(reminders, project_name, cwd)

    console.print()
    console.print(
        f"  [dim]Run [bold]remo[/bold] to see your startup panel, "
        f"or [bold]remo check[/bold] to validate your environment.[/]"
    )
    console.print()
