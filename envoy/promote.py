"""Profile promotion: copy a profile's values up to a target environment tier."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy.profile import load_profile, save_profile, profile_exists
from envoy.history import record_snapshot


@dataclass
class PromoteResult:
    source: str
    destination: str
    keys_promoted: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)
    ok: bool = True
    error: Optional[str] = None


def promote_profile(
    project: str,
    source: str,
    destination: str,
    *,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
    record_history: bool = True,
) -> PromoteResult:
    """Promote values from *source* profile into *destination* profile.

    Parameters
    ----------
    project:      project identifier
    source:       name of the profile to promote from (e.g. "staging")
    destination:  name of the profile to promote into (e.g. "production")
    overwrite:    when True, existing keys in destination are replaced
    keys:         optional allowlist of keys to promote; None means all keys
    record_history: snapshot destination before mutating when True
    """
    if not profile_exists(project, source):
        return PromoteResult(
            source=source,
            destination=destination,
            ok=False,
            error=f"Source profile '{source}' does not exist.",
        )

    src_env: Dict[str, str] = load_profile(project, source)
    dst_env: Dict[str, str] = load_profile(project, destination) if profile_exists(project, destination) else {}

    if record_history and dst_env:
        record_snapshot(project, destination, dst_env)

    result = PromoteResult(source=source, destination=destination)

    candidates = {k: v for k, v in src_env.items() if keys is None or k in keys}

    for key, value in candidates.items():
        if key in dst_env and not overwrite:
            result.keys_skipped.append(key)
        else:
            if key in dst_env:
                result.overwritten.append(key)
            dst_env[key] = value
            result.keys_promoted.append(key)

    save_profile(project, destination, dst_env)
    return result
