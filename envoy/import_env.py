"""Import env variables from the current shell environment or a foreign .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envoy.parser import parse_env_file, parse_env_string
from envoy.profile import load_profile, save_profile, profile_exists


@dataclass
class ImportResult:
    profile: str
    imported: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.imported) + len(self.overwritten)


def import_from_env(
    project: str,
    profile: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
    prefix: Optional[str] = None,
) -> ImportResult:
    """Import variables from the current process environment into a profile."""
    result = ImportResult(profile=profile)
    existing = load_profile(project, profile) if profile_exists(project, profile) else {}

    source: Dict[str, str] = dict(os.environ)
    if prefix:
        source = {k: v for k, v in source.items() if k.startswith(prefix)}
    if keys:
        source = {k: v for k, v in source.items() if k in keys}

    updated = dict(existing)
    for key, value in source.items():
        if key in existing and not overwrite:
            result.skipped.append(key)
        elif key in existing:
            updated[key] = value
            result.overwritten.append(key)
        else:
            updated[key] = value
            result.imported.append(key)

    save_profile(project, profile, updated)
    return result


def import_from_file(
    project: str,
    profile: str,
    path: Path,
    overwrite: bool = False,
) -> ImportResult:
    """Import variables from a foreign .env file into a profile."""
    result = ImportResult(profile=profile)
    existing = load_profile(project, profile) if profile_exists(project, profile) else {}
    source = parse_env_file(path)

    updated = dict(existing)
    for key, value in source.items():
        if key in existing and not overwrite:
            result.skipped.append(key)
        elif key in existing:
            updated[key] = value
            result.overwritten.append(key)
        else:
            updated[key] = value
            result.imported.append(key)

    save_profile(project, profile, updated)
    return result
