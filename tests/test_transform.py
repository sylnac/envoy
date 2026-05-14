"""Tests for envoy.transform."""
import pytest

from envoy.profile import save_profile, load_profile
from envoy.transform import (
    TransformResult,
    ok,
    transform_profile,
    BUILTIN_TRANSFORMS,
)


@pytest.fixture()
def proj(tmp_path):
    return str(tmp_path)


def _seed(proj, profile, data):
    save_profile(proj, profile, data)


# ---------------------------------------------------------------------------
# ok() helper
# ---------------------------------------------------------------------------

def test_ok_on_fresh_result():
    assert ok(TransformResult(profile="dev")) is True


# ---------------------------------------------------------------------------
# upper / lower / strip
# ---------------------------------------------------------------------------

def test_upper_transform_changes_values(proj):
    _seed(proj, "dev", {"HOST": "localhost", "ENV": "development"})
    result = transform_profile(proj, "dev", "upper")
    assert result.transformed == 2
    assert load_profile(proj, "dev") == {"HOST": "LOCALHOST", "ENV": "DEVELOPMENT"}


def test_lower_transform(proj):
    _seed(proj, "dev", {"HOST": "LOCALHOST"})
    result = transform_profile(proj, "dev", "lower")
    assert load_profile(proj, "dev")["HOST"] == "localhost"
    assert result.transformed == 1


def test_strip_transform_removes_whitespace(proj):
    _seed(proj, "dev", {"HOST": "  localhost  ", "PORT": "8080"})
    result = transform_profile(proj, "dev", "strip")
    assert load_profile(proj, "dev")["HOST"] == "localhost"
    assert result.transformed == 1  # PORT unchanged
    assert result.skipped == 1


# ---------------------------------------------------------------------------
# key filter
# ---------------------------------------------------------------------------

def test_transform_limited_to_keys(proj):
    _seed(proj, "dev", {"HOST": "localhost", "PORT": "8080"})
    result = transform_profile(proj, "dev", "upper", keys=["HOST"])
    env = load_profile(proj, "dev")
    assert env["HOST"] == "LOCALHOST"
    assert env["PORT"] == "8080"  # untouched
    assert result.transformed == 1
    assert result.skipped == 1


# ---------------------------------------------------------------------------
# dry_run
# ---------------------------------------------------------------------------

def test_dry_run_does_not_persist(proj):
    _seed(proj, "dev", {"HOST": "localhost"})
    result = transform_profile(proj, "dev", "upper", dry_run=True)
    assert result.transformed == 1
    assert load_profile(proj, "dev")["HOST"] == "localhost"  # unchanged on disk


# ---------------------------------------------------------------------------
# callable transform
# ---------------------------------------------------------------------------

def test_callable_transform(proj):
    _seed(proj, "dev", {"URL": "http://example.com"})
    result = transform_profile(proj, "dev", lambda v: v.replace("http", "https"))
    assert load_profile(proj, "dev")["URL"] == "https://example.com"
    assert result.transformed == 1


# ---------------------------------------------------------------------------
# changes dict
# ---------------------------------------------------------------------------

def test_changes_dict_records_old_and_new(proj):
    _seed(proj, "dev", {"HOST": "localhost"})
    result = transform_profile(proj, "dev", "upper")
    assert "HOST" in result.changes
    assert result.changes["HOST"] == ("localhost", "LOCALHOST")


# ---------------------------------------------------------------------------
# error cases
# ---------------------------------------------------------------------------

def test_unknown_transform_raises(proj):
    _seed(proj, "dev", {"K": "v"})
    with pytest.raises(ValueError, match="Unknown transform"):
        transform_profile(proj, "dev", "rot13")


def test_missing_profile_raises(proj):
    with pytest.raises(FileNotFoundError):
        transform_profile(proj, "ghost", "upper")


def test_invalid_transform_type_raises(proj):
    _seed(proj, "dev", {"K": "v"})
    with pytest.raises(TypeError):
        transform_profile(proj, "dev", 42)  # type: ignore
