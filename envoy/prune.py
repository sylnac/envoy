"""Prune stale or duplicate keys across profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.profile import load_profile, save_profile, list_profiles


@dataclass
class PruneResult:
    profile: str
    removed_keys: List[str] = field(default_factory=list)
    dry_run: bool = False

    @property
    def ok(self) -> bool:
        return True

    @property
    def count(self) -> int:
        return len(self.removed_keys)

    def summary(self) -> str:
        action = "Would remove" if self.dry_run else "Removed"
        if not self.removed_keys:
            return f"{self.profile}: nothing to prune"
        keys = ", ".join(self.removed_keys)
        return f"{self.profile}: {action} {self.count} key(s): {keys}"


def prune_empty_values(
    project_dir: str,
    profile: str,
    dry_run: bool = False,
) -> PruneResult:
    """Remove keys whose values are empty strings."""
    env = load_profile(project_dir, profile)
    removed = [k for k, v in env.items() if v == ""]
    if not dry_run and removed:
        pruned = {k: v for k, v in env.items() if v != ""}
        save_profile(project_dir, profile, pruned)
    return PruneResult(profile=profile, removed_keys=removed, dry_run=dry_run)


def prune_keys_not_in_schema(
    project_dir: str,
    profile: str,
    schema_keys: List[str],
    dry_run: bool = False,
) -> PruneResult:
    """Remove keys that are not present in *schema_keys*."""
    env = load_profile(project_dir, profile)
    allowed = set(schema_keys)
    removed = [k for k in env if k not in allowed]
    if not dry_run and removed:
        pruned = {k: v for k, v in env.items() if k in allowed}
        save_profile(project_dir, profile, pruned)
    return PruneResult(profile=profile, removed_keys=removed, dry_run=dry_run)


def prune_all_profiles(
    project_dir: str,
    schema_keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict[str, PruneResult]:
    """Run pruning across every profile in the project."""
    results: Dict[str, PruneResult] = {}
    for name in list_profiles(project_dir):
        if schema_keys is not None:
            results[name] = prune_keys_not_in_schema(
                project_dir, name, schema_keys, dry_run=dry_run
            )
        else:
            results[name] = prune_empty_values(
                project_dir, name, dry_run=dry_run
            )
    return results
