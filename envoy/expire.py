"""Profile key expiry — mark keys with a TTL and detect stale entries."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from envoy.profile import _profile_dir


def _expiry_file(project_root: str) -> Path:
    return _profile_dir(project_root) / ".expiry.json"


def _load_expiry(project_root: str) -> Dict[str, Dict[str, str]]:
    path = _expiry_file(project_root)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiry(project_root: str, data: Dict[str, Dict[str, str]]) -> None:
    path = _expiry_file(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


@dataclass
class ExpireResult:
    profile: str
    key: str
    expires_at: str
    already_set: bool = False


@dataclass
class StaleResult:
    profile: str
    stale: List[str] = field(default_factory=list)
    active: List[str] = field(default_factory=list)

    @property
    def has_stale(self) -> bool:
        return len(self.stale) > 0


def set_expiry(project_root: str, profile: str, key: str, expires_at: str) -> ExpireResult:
    """Set an ISO-8601 expiry timestamp for *key* in *profile*."""
    data = _load_expiry(project_root)
    profile_data = data.get(profile, {})
    already_set = key in profile_data
    profile_data[key] = expires_at
    data[profile] = profile_data
    _save_expiry(project_root, data)
    return ExpireResult(profile=profile, key=key, expires_at=expires_at, already_set=already_set)


def clear_expiry(project_root: str, profile: str, key: str) -> bool:
    """Remove the expiry entry for *key*. Returns True if it existed."""
    data = _load_expiry(project_root)
    profile_data = data.get(profile, {})
    existed = key in profile_data
    if existed:
        del profile_data[key]
        data[profile] = profile_data
        _save_expiry(project_root, data)
    return existed


def get_expiry(project_root: str, profile: str, key: str) -> Optional[str]:
    """Return the ISO-8601 expiry string for *key*, or None."""
    return _load_expiry(project_root).get(profile, {}).get(key)


def check_stale(project_root: str, profile: str, now: Optional[datetime] = None) -> StaleResult:
    """Return keys in *profile* whose expiry has passed."""
    if now is None:
        now = datetime.now(timezone.utc)
    profile_data = _load_expiry(project_root).get(profile, {})
    stale, active = [], []
    for key, ts in profile_data.items():
        try:
            expires = datetime.fromisoformat(ts)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        (stale if expires <= now else active).append(key)
    return StaleResult(profile=profile, stale=sorted(stale), active=sorted(active))
