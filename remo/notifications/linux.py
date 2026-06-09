"""Linux notification via notify-send."""

import shutil
import subprocess


def send(title: str, message: str) -> bool:
    """Send notification via notify-send. Returns True on success."""
    if shutil.which("notify-send") is None:
        return False
    try:
        result = subprocess.run(
            ["notify-send", title, message],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False
