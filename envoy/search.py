"""Search and filter environment variables across profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional

from envoy.profile import list_profiles, load_profile


@dataclass
class SearchResult:
    profile: str
    key: str
    value: str


@dataclass
class SearchSummary:
    results: List[SearchResult] = field(default_factory=list)
    profiles_searched: int = 0

    @property
    def total(self) -> int:
        return len(self.results)

    def by_profile(self) -> Dict[str, List[SearchResult]]:
        out: Dict[str, List[SearchResult]] = {}
        for r in self.results:
            out.setdefault(r.profile, []).append(r)
        return out


def search_profiles(
    project_dir: str,
    pattern: str,
    *,
    value_pattern: Optional[str] = None,
    profiles: Optional[List[str]] = None,
    case_sensitive: bool = False,
) -> SearchSummary:
    """Search for keys (and optionally values) matching glob patterns."""
    target_profiles = profiles if profiles is not None else list_profiles(project_dir)
    summary = SearchSummary(profiles_searched=len(target_profiles))

    for prof_name in target_profiles:
        env = load_profile(project_dir, prof_name)
        for key, value in env.items():
            k = key if case_sensitive else key.upper()
            p = pattern if case_sensitive else pattern.upper()
            if not fnmatch(k, p):
                continue
            if value_pattern is not None:
                vp = value_pattern if case_sensitive else value_pattern.upper()
                v = value if case_sensitive else value.upper()
                if not fnmatch(v, vp):
                    continue
            summary.results.append(SearchResult(profile=prof_name, key=key, value=value))

    return summary


def find_key_across_profiles(
    project_dir: str,
    key: str,
    *,
    profiles: Optional[List[str]] = None,
) -> Dict[str, Optional[str]]:
    """Return a mapping of profile -> value (or None) for a specific key."""
    target_profiles = profiles if profiles is not None else list_profiles(project_dir)
    result: Dict[str, Optional[str]] = {}
    for prof_name in target_profiles:
        env = load_profile(project_dir, prof_name)
        result[prof_name] = env.get(key)
    return result
