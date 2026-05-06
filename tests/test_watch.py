"""Tests for envoy.watch — profile file watcher."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envoy.profile import save_profile
from envoy.watch import WatchEvent, watch_profile, _mtime


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def proj(tmp_path, monkeypatch):
    """Redirect profile storage to a temp directory."""
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    return "watchtest"


def _collect_events(
    project: str,
    profile: str,
    writes: list[dict[str, str]],
    *,
    interval: float = 0.05,
) -> list[WatchEvent]:
    """Run the watcher for *len(writes)* iterations while writing env data."""
    events: list[WatchEvent] = []

    import threading

    def _writer():
        for env in writes:
            time.sleep(interval * 0.6)
            save_profile(project, profile, env)

    t = threading.Thread(target=_writer, daemon=True)
    t.start()
    watch_profile(
        project,
        profile,
        events.append,
        interval=interval,
        max_iterations=len(writes) * 4,
    )
    t.join(timeout=5)
    return events


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------


def test_mtime_missing_file_returns_zero(tmp_path):
    assert _mtime(tmp_path / "nonexistent.env") == 0.0


def test_mtime_existing_file(tmp_path):
    f = tmp_path / "test.env"
    f.write_text("KEY=val")
    assert _mtime(f) > 0.0


# ---------------------------------------------------------------------------
# WatchEvent dataclass
# ---------------------------------------------------------------------------


def test_watch_event_has_changes_true():
    ev = WatchEvent("p", "dev", Path("x"), added=["FOO"])
    assert ev.has_changes is True


def test_watch_event_has_changes_false():
    ev = WatchEvent("p", "dev", Path("x"))
    assert ev.has_changes is False


# ---------------------------------------------------------------------------
# Integration: watch_profile detects changes
# ---------------------------------------------------------------------------


def test_watch_detects_added_key(proj):
    save_profile(proj, "dev", {"EXISTING": "1"})
    events = _collect_events(proj, "dev", [{"EXISTING": "1", "NEW_KEY": "hello"}])
    added_keys = [k for ev in events for k in ev.added]
    assert "NEW_KEY" in added_keys


def test_watch_detects_removed_key(proj):
    save_profile(proj, "dev", {"A": "1", "B": "2"})
    events = _collect_events(proj, "dev", [{"A": "1"}])
    removed_keys = [k for ev in events for k in ev.removed]
    assert "B" in removed_keys


def test_watch_detects_changed_value(proj):
    save_profile(proj, "dev", {"PORT": "8080"})
    events = _collect_events(proj, "dev", [{"PORT": "9090"}])
    changed_keys = [k for ev in events for k in ev.changed]
    assert "PORT" in changed_keys


def test_watch_no_spurious_events_when_unchanged(proj):
    save_profile(proj, "dev", {"STABLE": "yes"})
    events: list[WatchEvent] = []
    # Run several iterations with no file writes — no change events expected.
    watch_profile(
        proj,
        "dev",
        events.append,
        interval=0.05,
        max_iterations=6,
    )
    assert all(not ev.has_changes for ev in events)
