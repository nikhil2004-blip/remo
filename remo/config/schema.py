"""Validate the .remo config schema."""

import re
from typing import Any, Dict, List


# Allowed time unit pattern e.g. "30m", "2h", "90s"
_TIME_PATTERN = re.compile(r"^\d+[smh]$")

# Known check types
_KNOWN_CHECK_TYPES = {"env", "version", "file", "cmd"}

# All known top-level keys — unknowns get a warning (not an error)
_KNOWN_KEYS = {"project", "startup", "reminders", "checks", "shortcuts"}


def _validate_reminder(reminder: Any, idx: int) -> List[str]:
    """Validate a single reminder entry; return list of error messages."""
    errors: List[str] = []
    if not isinstance(reminder, dict):
        errors.append(f"reminders[{idx}]: must be an object, got {type(reminder).__name__}")
        return errors

    after = reminder.get("after")
    if after is None:
        errors.append(f"reminders[{idx}]: missing required field 'after'")
    elif not isinstance(after, str) or not _TIME_PATTERN.match(after):
        errors.append(
            f"reminders[{idx}]: 'after' must be a time string like '30m', '2h', '90s' — got {after!r}"
        )

    message = reminder.get("message")
    if message is None:
        errors.append(f"reminders[{idx}]: missing required field 'message'")
    elif not isinstance(message, str):
        errors.append(f"reminders[{idx}]: 'message' must be a string")

    return errors


def _validate_check(check: Any, idx: int) -> List[str]:
    """Validate a single check entry; return list of error messages."""
    errors: List[str] = []
    if not isinstance(check, dict):
        errors.append(f"checks[{idx}]: must be an object")
        return errors

    check_type = check.get("type")
    if check_type not in _KNOWN_CHECK_TYPES:
        errors.append(
            f"checks[{idx}]: unknown type {check_type!r}. Must be one of: {sorted(_KNOWN_CHECK_TYPES)}"
        )
        return errors

    if check_type == "env" and "file" not in check:
        errors.append(f"checks[{idx}] (env): missing required field 'file' (path to .env.example)")

    if check_type == "version":
        if "tool" not in check:
            errors.append(f"checks[{idx}] (version): missing required field 'tool'")
        if "min" not in check:
            errors.append(f"checks[{idx}] (version): missing required field 'min'")

    if check_type == "file" and "path" not in check:
        errors.append(f"checks[{idx}] (file): missing required field 'path'")

    if check_type == "cmd" and "cmd" not in check:
        errors.append(f"checks[{idx}] (cmd): missing required field 'cmd'")

    return errors


def validate_config(config: Dict[str, Any]) -> None:
    """Validate the merged config dict.

    Raises ConfigError with a clear message on any validation failure.
    Prints warnings for unknown keys (forward compatibility).
    """
    from remo.config.loader import ConfigError

    if not isinstance(config, dict):
        raise ConfigError("Config must be a JSON object (dict), not a list or scalar.")

    errors: List[str] = []
    warnings: List[str] = []

    # Check for unknown top-level keys
    for key in config:
        if key not in _KNOWN_KEYS:
            warnings.append(f"Unknown field '{key}' (will be ignored — forward compat)")

    # project: required, must be a string
    project = config.get("project")
    if project is None:
        errors.append("Missing required field 'project' (project name string)")
    elif not isinstance(project, str) or not project.strip():
        errors.append("'project' must be a non-empty string")

    # startup: optional list of strings
    startup = config.get("startup")
    if startup is not None:
        if not isinstance(startup, list):
            errors.append("'startup' must be a list of strings")
        else:
            for i, item in enumerate(startup):
                if not isinstance(item, str):
                    errors.append(f"startup[{i}]: must be a string, got {type(item).__name__}")

    # reminders: optional list of reminder objects
    reminders = config.get("reminders")
    if reminders is not None:
        if not isinstance(reminders, list):
            errors.append("'reminders' must be a list")
        else:
            for i, r in enumerate(reminders):
                errors.extend(_validate_reminder(r, i))

    # checks: optional list of check objects
    checks = config.get("checks")
    if checks is not None:
        if not isinstance(checks, list):
            errors.append("'checks' must be a list")
        else:
            for i, c in enumerate(checks):
                errors.extend(_validate_check(c, i))

    # shortcuts: optional dict of string → string
    shortcuts = config.get("shortcuts")
    if shortcuts is not None:
        if not isinstance(shortcuts, dict):
            errors.append("'shortcuts' must be a JSON object (dict)")
        else:
            for name, cmd in shortcuts.items():
                if not isinstance(cmd, str):
                    errors.append(f"shortcuts['{name}']: command must be a string")

    if errors:
        detail = "\n  ".join(errors)
        raise ConfigError(
            f"Invalid .remo config:\n  {detail}",
            hint="Fix the fields above and re-run remo.",
        )

    # Print warnings (non-fatal)
    if warnings:
        import sys
        for w in warnings:
            print(f"[remo warning] {w}", file=sys.stderr)
