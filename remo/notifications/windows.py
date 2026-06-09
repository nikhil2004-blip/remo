"""Windows notification via PowerShell toast."""

import subprocess


def send(title: str, message: str) -> bool:
    """Send a Windows toast notification via PowerShell. Returns True on success."""
    # Escape single quotes to avoid script injection
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
