"""Secret diffing utilities — compare two env profiles and report changes."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, value in sorted(self.added.items()):
            lines.append(f"+ {key}={value}")
        for key, value in sorted(self.removed.items()):
            lines.append(f"- {key}={value}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        if not lines:
            lines.append("(no changes)")
        return "\n".join(lines)


def diff_profiles(
    base: Dict[str, str], target: Dict[str, str]
) -> DiffResult:
    """Compare two env dicts and return a DiffResult.

    Args:
        base: The reference (e.g., current) profile.
        target: The profile to compare against.

    Returns:
        DiffResult describing additions, removals, and changes.
    """
    result = DiffResult()
    all_keys = set(base) | set(target)

    for key in all_keys:
        in_base = key in base
        in_target = key in target

        if in_base and not in_target:
            result.removed[key] = base[key]
        elif in_target and not in_base:
            result.added[key] = target[key]
        elif base[key] != target[key]:
            result.changed[key] = (base[key], target[key])
        else:
            result.unchanged[key] = base[key]

    return result
