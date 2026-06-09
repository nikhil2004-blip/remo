"""Global config handler — ~/.remo/config.json."""

import json
import os
from pathlib import Path
from typing import Any, Dict

_GLOBAL_CONFIG_DIR = Path.home() / ".remo"
_GLOBAL_CONFIG_FILE = _GLOBAL_CONFIG_DIR / "config.json"

_DEFAULTS: Dict[str, Any] = {
    "notification": "desktop",  # "desktop" | "terminal" | "both"
    "snooze_duration": "10m",
    "theme": "default",  # "default" | "minimal"
    "show_startup": True,
}


def load_global_config() -> Dict[str, Any]:
    """Load global config, returning defaults for missing keys."""
    config = dict(_DEFAULTS)
    if _GLOBAL_CONFIG_FILE.exists():
        try:
            with open(_GLOBAL_CONFIG_FILE, "r", encoding="utf-8") as fh:
                user_config = json.load(fh)
            config.update(user_config)
        except (json.JSONDecodeError, OSError):
            pass  # Silently fall back to defaults on corrupt global config
    return config


def save_global_config(config: Dict[str, Any]) -> None:
    """Persist global config to disk."""
    _GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_GLOBAL_CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)


def get_global_config_path() -> Path:
    """Return path to global config file."""
    return _GLOBAL_CONFIG_FILE


def get_sessions_dir() -> Path:
    """Return path to sessions directory, creating it if needed."""
    sessions = _GLOBAL_CONFIG_DIR / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    return sessions
