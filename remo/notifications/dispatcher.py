"""Cross-platform notification dispatcher.

Strategy: Try desktop notification first (via plyer), fall back to terminal.
"""

import platform
import sys
from typing import Optional

_OS = platform.system()  # 'Darwin', 'Linux', 'Windows'


def _fallback_notify(title: str, message: str) -> None:
    """Universal fallback: rich panel + terminal bell."""
    # Ring the bell first
    sys.stdout.write("\a")
    sys.stdout.flush()

    # Then print a rich panel
    try:
        from remo.ui.panels import print_reminder_panel
        print_reminder_panel(title, message)
    except Exception:
        # Absolute last resort — plain print
        print(f"\n{'='*60}")
        print(f"  REMINDER: {title}")
        print(f"  {message}")
        print(f"{'='*60}\n")


def _try_plyer(title: str, message: str) -> bool:
    """Attempt a desktop notification via plyer. Returns True on success."""
    try:
        from plyer import notification  # type: ignore[import]
        notification.notify(
            title=title,
            message=message,
            app_name="remo",
            timeout=10,
        )
        return True
    except Exception:
        return False


def _try_macos_osascript(title: str, message: str) -> bool:
    """macOS fallback: osascript AppleScript notification."""
    import subprocess
    try:
        script = f'display notification "{message}" with title "{title}"'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def _try_linux_notify_send(title: str, message: str) -> bool:
    """Linux fallback: notify-send."""
    import shutil
    import subprocess
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


def _try_windows_toast(title: str, message: str) -> bool:
    """Windows fallback: PowerShell toast notification."""
    import subprocess
    safe_title = title.replace("'", "''")
    safe_message = message.replace("'", "''")
    ps_script = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, "
        "ContentType = WindowsRuntime] | Out-Null; "
        "$template = [Windows.UI.Notifications.ToastNotificationManager]"
        "::GetTemplateContent("
        "[Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
        f"$template.GetElementsByTagName('text')[0].AppendChild("
        f"$template.CreateTextNode('{safe_title}')) | Out-Null; "
        f"$template.GetElementsByTagName('text')[1].AppendChild("
        f"$template.CreateTextNode('{safe_message}')) | Out-Null; "
        "[Windows.UI.Notifications.ToastNotificationManager]"
        "::CreateToastNotifier('{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe').Show("
        "[Windows.UI.Notifications.ToastNotification]::new($template))"
    )
    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def notify(title: str, message: str) -> None:
    """Send a desktop notification, falling back to terminal output.

    Tries plyer first (cross-platform), then OS-specific fallbacks,
    then terminal output as the final fallback.
    """
    # Try plyer (works on all platforms with proper setup)
    if _try_plyer(title, message):
        return

    # OS-specific fallbacks
    if _OS == "Darwin" and _try_macos_osascript(title, message):
        return
    if _OS == "Linux" and _try_linux_notify_send(title, message):
        return
    if _OS == "Windows" and _try_windows_toast(title, message):
        return

    # Universal terminal fallback
    _fallback_notify(title, message)
