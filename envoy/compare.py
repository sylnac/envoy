"""Side-by-side profile comparison utility."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from envoy.profile import load_profile, profile_exists
from envoy.secrets import mask_secrets


@dataclass
class CompareResult:
    profile_a: str
    profile_b: str
    only_in_a: Dict[str, str] = field(default_factory=dict)
    only_in_b: Dict[str, str] = field(default_factory=dict)
    in_both_same: Dict[str, str] = field(default_factory=dict)
    in_both_different: Dict[str, tuple] = field(default_factory=dict)  # key -> (val_a, val_b)

    @property
    def all_keys(self) -> Set[str]:
        return (
            set(self.only_in_a)
            | set(self.only_in_b)
            | set(self.in_both_same)
            | set(self.in_both_different)
        )

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.in_both_different)


def compare_profiles(
    project: str,
    profile_a: str,
    profile_b: str,
    redact: bool = False,
) -> CompareResult:
    """Compare two profiles and return a structured result."""
    env_a = load_profile(project, profile_a) if profile_exists(project, profile_a) else {}
    env_b = load_profile(project, profile_b) if profile_exists(project, profile_b) else {}

    if redact:
        env_a = mask_secrets(env_a)
        env_b = mask_secrets(env_b)

    keys_a = set(env_a)
    keys_b = set(env_b)

    result = CompareResult(profile_a=profile_a, profile_b=profile_b)

    for key in keys_a - keys_b:
        result.only_in_a[key] = env_a[key]

    for key in keys_b - keys_a:
        result.only_in_b[key] = env_b[key]

    for key in keys_a & keys_b:
        if env_a[key] == env_b[key]:
            result.in_both_same[key] = env_a[key]
        else:
            result.in_both_different[key] = (env_a[key], env_b[key])

    return result


def summary(result: CompareResult) -> str:
    """Return a human-readable summary of a CompareResult."""
    lines: List[str] = [
        f"Comparing '{result.profile_a}' vs '{result.profile_b}'",
    ]
    if not result.has_differences:
        lines.append("  No differences found.")
        return "\n".join(lines)

    if result.only_in_a:
        lines.append(f"  Only in '{result.profile_a}': {sorted(result.only_in_a)}")
    if result.only_in_b:
        lines.append(f"  Only in '{result.profile_b}': {sorted(result.only_in_b)}")
    if result.in_both_different:
        lines.append(f"  Changed ({len(result.in_both_different)} key(s)):")
        for key in sorted(result.in_both_different):
            val_a, val_b = result.in_both_different[key]
            lines.append(f"    {key}: '{val_a}' -> '{val_b}'")
    return "\n".join(lines)
