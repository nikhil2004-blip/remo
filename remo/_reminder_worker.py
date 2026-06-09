"""Detached reminder worker — run as a subprocess, sleep, then notify.

Usage (internal — spawned by remo remind):
    python -m remo._reminder_worker <seconds> <message> [project_name]
"""

import sys
import time


def main() -> None:
    """Sleep for the specified duration then fire a notification."""
    if len(sys.argv) < 3:
        sys.exit(1)

    try:
        seconds = int(sys.argv[1])
    except ValueError:
        sys.exit(1)

    message = sys.argv[2]
    project_name = sys.argv[3] if len(sys.argv) > 3 else "remo"

    time.sleep(seconds)

    title = f"remo · {project_name}"
    from remo.notifications.dispatcher import notify
    notify(title, message)


if __name__ == "__main__":
    main()
