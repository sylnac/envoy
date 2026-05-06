"""Profile merging utilities for envoy.

Allows merging multiple profiles together with configurable conflict resolution.
"""

from typing import Dict, List, Literal

MergeStrategy = Literal["ours", "theirs", "error"]


def merge_profiles(
    base: Dict[str, str],
    *others: Dict[str, str],
    strategy: MergeStrategy = "theirs",
) -> Dict[str, str]:
    """Merge multiple env profiles into one.

    Args:
        base: The base profile to start from.
        *others: Additional profiles to merge in, applied left to right.
        strategy: How to handle key conflicts.
            - "ours": keep the value from the earlier (left) profile.
            - "theirs": overwrite with the value from the later (right) profile.
            - "error": raise a ValueError on any conflict.

    Returns:
        A new dict representing the merged profile.

    Raises:
        ValueError: If strategy is "error" and a conflicting key is found.
    """
    result = dict(base)

    for other in others:
        for key, value in other.items():
            if key in result:
                if strategy == "error":
                    raise ValueError(
                        f"Merge conflict on key '{key}': "
                        f"'{result[key]}' vs '{value}'"
                    )
                elif strategy == "theirs":
                    result[key] = value
                # strategy == "ours": keep existing value, do nothing
            else:
                result[key] = value

    return result


def merge_with_conflicts(
    base: Dict[str, str],
    other: Dict[str, str],
) -> tuple[Dict[str, str], List[str]]:
    """Merge two profiles and return the merged result along with conflict keys.

    Args:
        base: The base profile.
        other: The profile to merge in.

    Returns:
        A tuple of (merged_dict, conflict_keys) where conflict_keys is a list
        of keys that existed in both profiles with different values.
    """
    result = dict(base)
    conflicts: List[str] = []

    for key, value in other.items():
        if key in result:
            if result[key] != value:
                conflicts.append(key)
                result[key] = value  # default to "theirs"
        else:
            result[key] = value

    return result, conflicts
