"""Tag profiles with arbitrary labels for grouping and filtering."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envoy.profile import _profile_dir


def _tag_file(project: str) -> Path:
    return _profile_dir(project) / ".tags.json"


def _load_tags(project: str) -> Dict[str, List[str]]:
    """Return mapping of profile_name -> list of tags."""
    path = _tag_file(project)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_tags(project: str, data: Dict[str, List[str]]) -> None:
    path = _tag_file(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def add_tag(project: str, profile: str, tag: str) -> List[str]:
    """Add *tag* to *profile*. Returns updated tag list."""
    data = _load_tags(project)
    tags = data.get(profile, [])
    if tag not in tags:
        tags.append(tag)
    data[profile] = tags
    _save_tags(project, data)
    return tags


def remove_tag(project: str, profile: str, tag: str) -> List[str]:
    """Remove *tag* from *profile*. Returns updated tag list."""
    data = _load_tags(project)
    tags = [t for t in data.get(profile, []) if t != tag]
    data[profile] = tags
    _save_tags(project, data)
    return tags


def get_tags(project: str, profile: str) -> List[str]:
    """Return tags for a single profile."""
    return _load_tags(project).get(profile, [])


def profiles_with_tag(project: str, tag: str) -> List[str]:
    """Return all profiles that carry *tag*."""
    data = _load_tags(project)
    return [p for p, tags in data.items() if tag in tags]


def clear_tags(project: str, profile: str) -> None:
    """Remove all tags from *profile*."""
    data = _load_tags(project)
    data.pop(profile, None)
    _save_tags(project, data)
