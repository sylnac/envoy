"""Profile grouping — tag profiles into named groups and query by group."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profile import _profile_dir, profile_exists


def _group_file(project: str) -> Path:
    return _profile_dir(project) / ".groups.json"


def _load_groups(project: str) -> Dict[str, List[str]]:
    gf = _group_file(project)
    if not gf.exists():
        return {}
    return json.loads(gf.read_text())


def _save_groups(project: str, data: Dict[str, List[str]]) -> None:
    gf = _group_file(project)
    gf.parent.mkdir(parents=True, exist_ok=True)
    gf.write_text(json.dumps(data, indent=2))


@dataclass
class GroupResult:
    group: str
    members: List[str] = field(default_factory=list)
    added: Optional[str] = None
    removed: Optional[str] = None


def add_to_group(project: str, group: str, profile: str) -> GroupResult:
    """Add *profile* to *group*; profile must exist."""
    if not profile_exists(project, profile):
        raise FileNotFoundError(f"Profile '{profile}' not found in project '{project}'")
    data = _load_groups(project)
    members = data.setdefault(group, [])
    added = None
    if profile not in members:
        members.append(profile)
        added = profile
    _save_groups(project, data)
    return GroupResult(group=group, members=list(members), added=added)


def remove_from_group(project: str, group: str, profile: str) -> GroupResult:
    """Remove *profile* from *group*."""
    data = _load_groups(project)
    members = data.get(group, [])
    removed = None
    if profile in members:
        members.remove(profile)
        removed = profile
    data[group] = members
    _save_groups(project, data)
    return GroupResult(group=group, members=list(members), removed=removed)


def get_group(project: str, group: str) -> List[str]:
    """Return profiles belonging to *group*."""
    return list(_load_groups(project).get(group, []))


def list_groups(project: str) -> Dict[str, List[str]]:
    """Return all groups and their members."""
    return dict(_load_groups(project))


def delete_group(project: str, group: str) -> bool:
    """Delete a group entirely; returns True if it existed."""
    data = _load_groups(project)
    existed = group in data
    data.pop(group, None)
    _save_groups(project, data)
    return existed
