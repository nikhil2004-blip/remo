"""remo check — run all environment checks defined in .remo config."""

import sys
from pathlib import Path
from typing import Any, Dict

import click
from rich.console import Console
from rich.rule import Rule

from remo.ui.colors import COLORS

console = Console()


def _run_single_check(check_def: Dict[str, Any], base_dir: Path) -> None:
    """Run a single check definition and print the result."""
    check_type = check_def.get("type")

    if check_type == "env":
        from remo.checks.env_check import run_env_check
        example_file = check_def.get("file", ".env.example")
        result = run_env_check(example_file, base_dir=base_dir)
        label = ".env"
        if result.status == "pass":
            console.print(
                f"  [{COLORS['success']}]✓[/]  [bold]{label}[/]"
                f"      [dim]{result.message}[/]"
            )
        elif result.status == "skip":
            console.print(
                f"  [{COLORS['warning']}]![/]  [bold]{label}[/]"
                f"      [dim]{result.message}[/]"
            )
        else:
            console.print(
                f"  [{COLORS['error']}]✗[/]  [bold]{label}[/]"
                f"      [dim]{result.message}[/]"
            )

    elif check_type == "version":
        from remo.checks.version_check import run_version_check
        tool = check_def.get("tool", "")
        min_ver = check_def.get("min", "0")
        result = run_version_check(tool, min_ver)

        if result.status == "pass":
            console.print(
                f"  [{COLORS['success']}]✓[/]  [bold]{tool}[/]"
                f"      [dim]{result.message}[/]"
            )
        elif result.status == "missing":
            console.print(
                f"  [{COLORS['warning']}]![/]  [bold]{tool}[/]"
                f"      [dim]not found (shortcuts using {tool} will fail)[/]"
            )
        else:
            console.print(
                f"  [{COLORS['error']}]✗[/]  [bold]{tool}[/]"
                f"      [dim]{result.message}[/]"
            )

    elif check_type == "file":
        from remo.checks.file_check import run_file_check
        path = check_def.get("path", "")
        result = run_file_check(path, base_dir=base_dir)
        label = path

        if result.status == "pass":
            console.print(
                f"  [{COLORS['success']}]✓[/]  [bold]{label}[/]"
                f"      [dim]{result.message}[/]"
            )
        else:
            console.print(
                f"  [{COLORS['error']}]✗[/]  [bold]{label}[/]"
                f"      [dim]{result.message}[/]"
            )

    elif check_type == "cmd":
        from remo.checks.cmd_check import run_cmd_check
        cmd = check_def.get("cmd", "")
        label = check_def.get("label", cmd)
        result = run_cmd_check(cmd, label=label)

        if result.status == "pass":
            console.print(
                f"  [{COLORS['success']}]✓[/]  [bold]{label}[/]"
                f"      [dim]{result.message}[/]"
            )
        else:
            console.print(
                f"  [{COLORS['error']}]✗[/]  [bold]{label}[/]"
                f"      [dim]{result.message}[/]"
            )
    else:
        console.print(f"  [dim]?  unknown check type: {check_type!r}[/]")


@click.command()
@click.option(
    "--env-only",
    is_flag=True,
    default=False,
    help="Only run the .env vs .env.example check.",
)
def check(env_only: bool) -> None:
    """Run all environment checks defined in .remo config."""
    from remo.config.loader import load_config, ConfigError

    try:
        config, config_dir = load_config()
    except ConfigError as exc:
        console.print(f"[red]✗ Error:[/red] {exc}")
        if exc.hint:
            console.print(f"[dim]  Hint: {exc.hint}[/dim]")
        sys.exit(1)

    checks = config.get("checks", [])

    if env_only:
        checks = [c for c in checks if c.get("type") == "env"]
        if not checks:
            console.print(
                f"[{COLORS['warning']}]![/] No env checks defined in .remo."
            )
            return

    project_name = config.get("project", "Project")
    console.print()
    console.print(Rule(
        f"  [{COLORS['header']}]Environment Check — {project_name}[/]  ",
        style=COLORS["dim"],
    ))

    if not checks:
        console.print(
            f"  [dim]No checks defined in .remo. "
            "Add a 'checks' section to get started.[/]"
        )
        return

    for check_def in checks:
        _run_single_check(check_def, config_dir)

    console.print()
