"""Emoji / icon definitions with ASCII fallbacks for Windows terminals."""

import platform
import sys
from typing import Dict

_IS_WINDOWS = platform.system() == "Windows"

# Try to detect if the terminal can render unicode (Windows Terminal can, cmd.exe often can't)
def _supports_unicode() -> bool:
    """Check if the current terminal likely supports Unicode emoji."""
    if not _IS_WINDOWS:
        return True
    # Windows Terminal sets WT_SESSION env var
    import os
    if os.environ.get("WT_SESSION"):
        return True
    # ANSICON or ConEmu
    if os.environ.get("ANSICON") or os.environ.get("ConEmuANSI"):
        return True
    # Fall back to checking stdout encoding
    try:
        return sys.stdout.encoding and sys.stdout.encoding.lower().startswith("utf")
    except Exception:
        return False


_USE_UNICODE = _supports_unicode()

# Emoji → ASCII fallback map
_ICONS: Dict[str, str] = {
    "checklist": "📋" if _USE_UNICODE else "[LIST]",
    "shortcut": "⚡" if _USE_UNICODE else ">>",
    "log": "📓" if _USE_UNICODE else "[LOG]",
    "reminder": "⏰" if _USE_UNICODE else "[TIME]",
    "success": "✓" if _USE_UNICODE else "[OK]",
    "fail": "✗" if _USE_UNICODE else "[FAIL]",
    "warn": "!" if _USE_UNICODE else "[WARN]",
    "info": "·" if _USE_UNICODE else "·",
    "remo": "remo" if _USE_UNICODE else "remo",
}


def icon(name: str) -> str:
    """Return the icon string for the given name (unicode or ASCII fallback)."""
    return _ICONS.get(name, name)
