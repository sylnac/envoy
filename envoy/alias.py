"""Profile alias management — assign short names to profiles."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profile import _profile_dir


def _alias_file(project_dir: str) -> Path:
    return _profile_dir(project_dir) / ".aliases.json"


def _load_aliases(project_dir: str) -> Dict[str, str]:
    path = _alias_file(project_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(project_dir: str, aliases: Dict[str, str]) -> None:
    path = _alias_file(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(aliases, indent=2))


def set_alias(project_dir: str, alias: str, profile: str) -> Dict[str, str]:
    """Map *alias* to *profile*. Returns updated alias mapping."""
    aliases = _load_aliases(project_dir)
    aliases[alias] = profile
    _save_aliases(project_dir, aliases)
    return aliases


def remove_alias(project_dir: str, alias: str) -> bool:
    """Remove *alias*. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(project_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(project_dir, aliases)
    return True


def resolve_alias(project_dir: str, alias: str) -> Optional[str]:
    """Return the profile name for *alias*, or None if not found."""
    return _load_aliases(project_dir).get(alias)


def list_aliases(project_dir: str) -> Dict[str, str]:
    """Return all alias → profile mappings."""
    return _load_aliases(project_dir)


def aliases_for_profile(project_dir: str, profile: str) -> List[str]:
    """Return every alias that points to *profile*."""
    return [a for a, p in _load_aliases(project_dir).items() if p == profile]
