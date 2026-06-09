"""macOS notification via osascript / AppleScript."""

import subprocess


def send(title: str, message: str) -> bool:
    """Send notification via osascript. Returns True on success."""
    script = f'display notification "{message}" with title "{title}"'
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False
