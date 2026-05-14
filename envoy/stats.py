"""Profile statistics: key counts, secret ratios, and per-profile summaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envoy.profile import list_profiles, load_profile
from envoy.secrets import is_secret_key


@dataclass
class ProfileStats:
    profile: str
    total_keys: int
    secret_keys: int
    empty_values: int
    keys: List[str] = field(default_factory=list)

    @property
    def plain_keys(self) -> int:
        return self.total_keys - self.secret_keys

    @property
    def secret_ratio(self) -> float:
        if self.total_keys == 0:
            return 0.0
        return self.secret_keys / self.total_keys


@dataclass
class ProjectStats:
    profiles: List[ProfileStats] = field(default_factory=list)

    @property
    def total_profiles(self) -> int:
        return len(self.profiles)

    @property
    def total_keys(self) -> int:
        return sum(p.total_keys for p in self.profiles)

    @property
    def unique_keys(self) -> int:
        all_keys: set = set()
        for p in self.profiles:
            all_keys.update(p.keys)
        return len(all_keys)

    def by_profile(self) -> Dict[str, ProfileStats]:
        return {p.profile: p for p in self.profiles}


def profile_stats(project: str, profile: str) -> ProfileStats:
    """Compute statistics for a single profile."""
    env = load_profile(project, profile)
    total = len(env)
    secrets = sum(1 for k in env if is_secret_key(k))
    empty = sum(1 for v in env.values() if v == "")
    return ProfileStats(
        profile=profile,
        total_keys=total,
        secret_keys=secrets,
        empty_values=empty,
        keys=list(env.keys()),
    )


def project_stats(project: str) -> ProjectStats:
    """Compute statistics across all profiles in a project."""
    profiles = list_profiles(project)
    stats = [profile_stats(project, p) for p in profiles]
    return ProjectStats(profiles=stats)
