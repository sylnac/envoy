"""Archive and restore profiles as compressed bundles."""
from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envoy.profile import list_profiles, load_profile, save_profile, profile_path


@dataclass
class ArchiveResult:
    project: str
    archive_path: str
    profiles: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def archive_profiles(
    project: str,
    dest: str,
    profiles: Optional[List[str]] = None,
    base_dir: Optional[Path] = None,
) -> ArchiveResult:
    """Write selected (or all) profiles for *project* into a zip archive at *dest*."""
    targets = profiles if profiles is not None else list_profiles(project, base_dir=base_dir)
    result = ArchiveResult(project=project, archive_path=dest)

    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        meta = {"project": project, "profiles": []}
        for name in targets:
            try:
                data = load_profile(project, name, base_dir=base_dir)
                payload = json.dumps(data)
                zf.writestr(f"{name}.json", payload)
                meta["profiles"].append(name)
                result.profiles.append(name)
            except FileNotFoundError:
                result.errors.append(f"profile '{name}' not found")
        zf.writestr("_meta.json", json.dumps(meta))

    return result


def restore_profiles(
    project: str,
    archive_path: str,
    overwrite: bool = False,
    base_dir: Optional[Path] = None,
) -> ArchiveResult:
    """Restore profiles from a zip archive into *project*."""
    result = ArchiveResult(project=project, archive_path=archive_path)

    with zipfile.ZipFile(archive_path, "r") as zf:
        names = zf.namelist()
        for entry in names:
            if entry == "_meta.json" or not entry.endswith(".json"):
                continue
            profile_name = entry[:-5]  # strip .json
            existing = profile_path(project, profile_name, base_dir=base_dir)
            if existing.exists() and not overwrite:
                result.errors.append(f"profile '{profile_name}' already exists (use overwrite=True)")
                continue
            data = json.loads(zf.read(entry).decode())
            save_profile(project, profile_name, data, base_dir=base_dir)
            result.profiles.append(profile_name)

    return result
