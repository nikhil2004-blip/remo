"""Theme definitions — color palette and styles for remo UI."""

from typing import Dict

# Color tokens per PRD Section 5
COLORS: Dict[str, str] = {
    "success": "#00C853",   # Green  — pass / success / done
    "warning": "#FFD600",   # Yellow — warning / info / reminder
    "error": "#FF1744",     # Red    — fail / error / urgent
    "header": "#00B8D4",    # Cyan   — labels, headers, project name
    "body": "white",        # White  — body text
    "dim": "dim white",     # Dim    — metadata (timestamps, hints)
}

# Rich markup strings for quick use
SUCCESS = f"[bold {COLORS['success']}]"
WARNING = f"[bold {COLORS['warning']}]"
ERROR = f"[bold {COLORS['error']}]"
HEADER = f"[bold {COLORS['header']}]"
DIM = f"[{COLORS['dim']}]"
RESET = "[/]"


def is_minimal_theme(theme: str) -> bool:
    """Return True if the theme is 'minimal' (no colors/borders)."""
    return theme == "minimal"
