"""Rich panels and layout helpers for remo UI."""

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from remo.ui.colors import COLORS, SUCCESS, WARNING, ERROR, HEADER, DIM

console = Console()


def make_header_panel(project_name: str, last_opened: str) -> Panel:
    """Build the top header panel: project name + last opened timestamp."""
    title_text = Text()
    title_text.append("remo", style=f"bold {COLORS['header']}")
    title_text.append("  ·  ", style="dim")
    title_text.append(project_name, style=f"bold white")

    right_text = Text(f"last opened: {last_opened}", style=COLORS["dim"])

    # Combine into a single renderable
    from rich.columns import Columns
    header = Columns([title_text, right_text], expand=True, align="right")
    return Panel(header, border_style=COLORS["header"])


def print_rule(title: str = "") -> None:
    """Print a horizontal rule with optional title."""
    console.print(Rule(title, style=COLORS["dim"]))


def print_success(label: str, message: str) -> None:
    """Print a green success line."""
    console.print(f"  {SUCCESS}✓[/]  [bold]{label}[/]  [dim]{message}[/]")


def print_failure(label: str, message: str) -> None:
    """Print a red failure line."""
    console.print(f"  {ERROR}✗[/]  [bold]{label}[/]  [dim]{message}[/]")


def print_warning(label: str, message: str) -> None:
    """Print a yellow warning line."""
    console.print(f"  {WARNING}![/]  [bold]{label}[/]  [dim]{message}[/]")


def print_reminder_panel(title: str, message: str) -> None:
    """Print a bright reminder panel (universal fallback for notifications)."""
    panel = Panel(
        f"[bold white]{message}[/]",
        title=f"[bold {COLORS['warning']}]{title}[/]",
        border_style=COLORS["warning"],
        padding=(1, 2),
    )
    console.print(panel)
