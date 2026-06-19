"""remo run — execute a project shortcut defined in .remo config."""

import os
import subprocess
import sys
from typing import Optional

import click
from rich.console import Console
from rich.rule import Rule

from remo.ui.colors import COLORS

console = Console()


def _get_config():
    """Load config, returning (config, config_dir) or raising on error."""
    from remo.config.loader import load_config, ConfigError
    return load_config()


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("shortcut_name")
@click.argument("extra_args", nargs=-1, type=click.UNPROCESSED)
def run(shortcut_name: str, extra_args: tuple) -> None:
    """Execute a project shortcut defined in .remo config.

    \b
    Example:
      remo run dev      # runs: uvicorn main:app --reload
      remo run test     # runs: pytest tests/ -v
      remo run md name  # passes 'name' as an extra argument
    """
    from remo.config.loader import load_config, ConfigError

    try:
        config, config_dir = load_config()
    except ConfigError as exc:
        console.print(f"[red]✗ Error:[/red] {exc}")
        if exc.hint:
            console.print(f"[dim]  Hint: {exc.hint}[/dim]")
        sys.exit(1)

    shortcuts = config.get("shortcuts", {})

    if not shortcuts:
        console.print(
            f"[{COLORS['warning']}]![/] No shortcuts defined in .remo. "
            "Add a 'shortcuts' section to your .remo file."
        )
        sys.exit(1)

    if shortcut_name not in shortcuts:
        available = ", ".join(f"[bold]{k}[/bold]" for k in shortcuts)
        console.print(
            f"[red]✗ Error:[/red] Shortcut [bold]{shortcut_name!r}[/bold] not found."
        )
        console.print(f"  Available: {available}")
        sys.exit(1)

    cmd = shortcuts[shortcut_name]
    if extra_args:
        cmd = f"{cmd} {' '.join(extra_args)}"

    console.print(
        f"  [{COLORS['header']}]»[/] [bold]{shortcut_name}[/bold]: "
        f"[dim]{cmd}[/dim]"
    )
    console.print()

    # Execute the command in the project directory, passing control to the shell
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(config_dir),
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
    except OSError as exc:
        console.print(f"[red]✗ Error:[/red] Failed to run command: {exc}")
        sys.exit(1)


@click.command()
def shortcuts() -> None:
    """List all shortcuts defined for this project."""
    from remo.config.loader import load_config, ConfigError

    try:
        config, _ = load_config()
    except ConfigError as exc:
        console.print(f"[red]✗ Error:[/red] {exc}")
        if exc.hint:
            console.print(f"[dim]  Hint: {exc.hint}[/dim]")
        sys.exit(1)

    shortcuts_dict = config.get("shortcuts", {})
    project_name = config.get("project", "Project")

    console.print()
    console.print(Rule(
        f"  [{COLORS['header']}]Shortcuts — {project_name}[/]  ",
        style=COLORS["dim"],
    ))

    if not shortcuts_dict:
        console.print(
            f"  [dim]No shortcuts defined. Add a 'shortcuts' section to .remo.[/]"
        )
    else:
        max_name_len = max(len(k) for k in shortcuts_dict)
        for name, cmd in shortcuts_dict.items():
            console.print(
                f"  [{COLORS['header']}]{name:<{max_name_len}}[/]  "
                f"[dim]{cmd}[/]"
            )

    console.print()
