"""CLI helpers for the 'envoy merge' command."""

from typing import Optional

from envoy.merge import merge_profiles, merge_with_conflicts, MergeStrategy
from envoy.profile import load_profile, save_profile, profile_exists
from envoy.diff import diff_profiles


def cmd_merge(
    base_profile: str,
    other_profile: str,
    output_profile: Optional[str] = None,
    strategy: MergeStrategy = "theirs",
    dry_run: bool = False,
    show_conflicts: bool = True,
) -> int:
    """Merge two profiles and optionally save the result.

    Args:
        base_profile: Name of the base profile.
        other_profile: Name of the profile to merge into base.
        output_profile: Name to save the merged result under.
                        Defaults to base_profile if None.
        strategy: Conflict resolution strategy.
        dry_run: If True, print result without saving.
        show_conflicts: If True, print conflicting keys to stdout.

    Returns:
        Exit code (0 = success, 1 = error).
    """
    if not profile_exists(base_profile):
        print(f"error: profile '{base_profile}' does not exist.")
        return 1

    if not profile_exists(other_profile):
        print(f"error: profile '{other_profile}' does not exist.")
        return 1

    base = load_profile(base_profile)
    other = load_profile(other_profile)

    try:
        if show_conflicts and strategy != "error":
            merged, conflicts = merge_with_conflicts(base, other)
            if conflicts:
                print(f"Conflicts resolved ({strategy}) on keys: {', '.join(conflicts)}")
            # Re-run with actual strategy in case it differs from default
            merged = merge_profiles(base, other, strategy=strategy)
        else:
            merged = merge_profiles(base, other, strategy=strategy)
    except ValueError as exc:
        print(f"error: {exc}")
        return 1

    diff = diff_profiles(base, merged)
    if not diff.has_changes:
        print("No changes after merge.")
        return 0

    print(f"Merge summary: {diff.summary}")

    if dry_run:
        print("(dry-run) merged result not saved.")
        return 0

    destination = output_profile or base_profile
    save_profile(destination, merged)
    print(f"Saved merged profile as '{destination}'.")
    return 0
