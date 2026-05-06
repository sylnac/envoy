"""Audit log: record and query CLI actions performed on profiles."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


def _audit_dir(project_root: str = ".") -> Path:
    return Path(project_root) / ".envoy" / "audit"


def _audit_file(project_root: str = ".") -> Path:
    return _audit_dir(project_root) / "log.jsonl"


def record_action(
    action: str,
    profile: str,
    details: Optional[dict] = None,
    project_root: str = ".",
) -> dict:
    """Append an audit entry and return it."""
    _audit_dir(project_root).mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "details": details or {},
    }
    with _audit_file(project_root).open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def load_audit_log(project_root: str = ".") -> List[dict]:
    """Return all audit entries in chronological order."""
    path = _audit_file(project_root)
    if not path.exists():
        return []
    entries = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def filter_log(
    entries: List[dict],
    action: Optional[str] = None,
    profile: Optional[str] = None,
) -> List[dict]:
    """Filter audit entries by action and/or profile name."""
    result = entries
    if action:
        result = [e for e in result if e["action"] == action]
    if profile:
        result = [e for e in result if e["profile"] == profile]
    return result


def format_entry(entry: dict) -> str:
    """Return a human-readable single-line representation of an entry."""
    ts = entry["timestamp"]
    action = entry["action"]
    profile = entry["profile"]
    details = entry.get("details", {})
    detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
    base = f"[{ts}] {action} profile={profile}"
    return f"{base} ({detail_str})" if detail_str else base
