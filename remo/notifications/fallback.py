"""Universal terminal fallback notification."""

import sys


def send(title: str, message: str) -> bool:
    """Print a terminal bell + rich panel as a fallback notification."""
    sys.stdout.write("\a")
    sys.stdout.flush()

    try:
        from remo.ui.panels import print_reminder_panel
        print_reminder_panel(title, message)
        return True
    except Exception:
        print(f"\n{'=' * 60}")
        print(f"  REMINDER: {title}")
        print(f"  {message}")
        print(f"{'=' * 60}\n")
        return True
