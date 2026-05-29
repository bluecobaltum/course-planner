"""Data loading utilities.

Thin wrappers around JSON file I/O. When the project migrates to SQLite,
only this file needs to change — the engine and routes are unaffected.
"""

import json
from pathlib import Path
from typing import Any


def load_json(filepath: str) -> list[dict[str, Any]]:
    """Load and parse a JSON file from the data/ directory.

    Args:
        filepath: Path relative to the data/ directory, e.g. "courses.json".

    Returns:
        Parsed JSON content as a list of dicts.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    # Resolve relative to the data/ directory under the project root
    base_dir = Path(__file__).parent.parent / "data"
    full_path = base_dir / filepath

    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_courses() -> list[dict[str, Any]]:
    """Load all course sections from courses.json.

    Returns:
        List of course dicts. Each dict matches the Course model shape.
    """
    return load_json("courses.json")


def load_strategies() -> list[dict[str, Any]]:
    """Load all strategy cards from strategies.json.

    Returns:
        List of strategy dicts. Each dict matches the Strategy model shape.
    """
    return load_json("strategies.json")
