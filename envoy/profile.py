"""Profile management for envoy — load, save, and list named .env profiles."""

import os
from pathlib import Path
from typing import Dict, List, Optional

from envoy.parser import parse_env_file, serialize_env

DEFAULT_PROFILE_DIR = ".envoy"


def _profile_dir(base: Optional[str] = None) -> Path:
    """Return the path to the profiles directory."""
    root = Path(base) if base else Path.cwd()
    return root / DEFAULT_PROFILE_DIR


def profile_path(name: str, base: Optional[str] = None) -> Path:
    """Return the file path for a named profile."""
    return _profile_dir(base) / f"{name}.env"


def list_profiles(base: Optional[str] = None) -> List[str]:
    """Return a sorted list of available profile names."""
    directory = _profile_dir(base)
    if not directory.exists():
        return []
    return sorted(
        p.stem for p in directory.iterdir() if p.suffix == ".env" and p.is_file()
    )


def load_profile(name: str, base: Optional[str] = None) -> Dict[str, str]:
    """Load and parse a named profile. Raises FileNotFoundError if missing."""
    path = profile_path(name, base)
    if not path.exists():
        raise FileNotFoundError(f"Profile '{name}' not found at {path}")
    return parse_env_file(str(path))


def save_profile(
    name: str, data: Dict[str, str], base: Optional[str] = None
) -> Path:
    """Serialize and save a dict to a named profile file. Returns the path."""
    directory = _profile_dir(base)
    directory.mkdir(parents=True, exist_ok=True)
    path = profile_path(name, base)
    path.write_text(serialize_env(data), encoding="utf-8")
    return path


def delete_profile(name: str, base: Optional[str] = None) -> bool:
    """Delete a named profile. Returns True if deleted, False if not found."""
    path = profile_path(name, base)
    if path.exists():
        path.unlink()
        return True
    return False


def profile_exists(name: str, base: Optional[str] = None) -> bool:
    """Return True if the named profile exists."""
    return profile_path(name, base).exists()
