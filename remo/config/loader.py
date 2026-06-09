"""Load and merge .remo and .remo.local config files."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from remo.config.schema import validate_config

REMO_FILE = ".remo"
REMO_LOCAL_FILE = ".remo.local"


class ConfigError(Exception):
    """Raised when the config file is missing or malformed."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.hint = hint


def _load_json_file(path: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dict.

    Raises ConfigError with a friendly message on parse failure.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"Invalid JSON in {path.name}: {exc.msg} (line {exc.lineno})",
            hint=f"Check line {exc.lineno} of {path} for syntax errors.",
        ) from exc


def _merge_configs(
    base: Dict[str, Any], local: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge .remo.local into .remo following PRD merge rules.

    - startup: local list APPENDS to base list
    - shortcuts: local keys OVERRIDE matching base keys
    - all other keys: local REPLACES base
    """
    merged: Dict[str, Any] = dict(base)

    for key, local_val in local.items():
        if key == "startup":
            # Append local startup steps after base steps
            base_list = merged.get("startup", [])
            merged["startup"] = list(base_list) + list(local_val)
        elif key == "shortcuts":
            # Merge shortcuts — local overrides matching keys
            base_shortcuts = dict(merged.get("shortcuts", {}))
            base_shortcuts.update(local_val)
            merged["shortcuts"] = base_shortcuts
        else:
            merged[key] = local_val

    return merged


def find_remo_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Walk up the directory tree looking for a .remo file.

    Returns the path if found, None otherwise.
    """
    try:
        current = Path(start_dir or os.getcwd()).resolve()
        for directory in [current, *current.parents]:
            candidate = directory / REMO_FILE
            try:
                if candidate.exists():
                    return candidate
            except PermissionError:
                pass
        return None
    except Exception:
        return None


def load_config(
    directory: Optional[Path] = None,
) -> Tuple[Dict[str, Any], Path]:
    """Load and merge .remo and (optional) .remo.local configs.

    Returns (merged_config_dict, config_directory).
    Raises ConfigError if .remo is not found or is malformed.
    """
    if directory is None:
        remo_path = find_remo_file()
        if remo_path is None:
            raise ConfigError(
                "No .remo file found in this directory or any parent.",
                hint="Run `remo init` to create a .remo file for this project.",
            )
        config_dir = remo_path.parent
    else:
        directory = Path(directory).resolve()
        remo_path = directory / REMO_FILE
        if not remo_path.exists():
            raise ConfigError(
                f"No .remo file found in {directory}",
                hint="Run `remo init` to create a .remo file for this project.",
            )
        config_dir = directory

    config = _load_json_file(remo_path)

    # Load and merge .remo.local if it exists
    local_path = config_dir / REMO_LOCAL_FILE
    if local_path.exists():
        local_config = _load_json_file(local_path)
        config = _merge_configs(config, local_config)

    # Validate the merged config
    validate_config(config)

    return config, config_dir
