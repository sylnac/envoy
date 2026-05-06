"""Tests for envoy.template."""
from __future__ import annotations

import pytest

from envoy.template import find_placeholders, render_template


# ---------------------------------------------------------------------------
# find_placeholders
# ---------------------------------------------------------------------------

def test_find_placeholders_brace_syntax():
    assert find_placeholders("DB_URL=${DB_HOST}:${DB_PORT}") == ["DB_HOST", "DB_PORT"]


def test_find_placeholders_bare_syntax():
    assert find_placeholders("export FOO=$BAR") == ["BAR"]


def test_find_placeholders_mixed_syntax():
    result = find_placeholders("${A} and $B")
    assert result == ["A", "B"]


def test_find_placeholders_deduplicates():
    result = find_placeholders("${X} ${X} $X")
    assert result == ["X"]


def test_find_placeholders_none():
    assert find_placeholders("no placeholders here") == []


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_basic_substitution():
    rendered, missing = render_template("HOST=${DB_HOST}", {"DB_HOST": "localhost"})
    assert rendered == "HOST=localhost"
    assert missing == []


def test_render_missing_placeholder_left_intact():
    rendered, missing = render_template("X=${UNKNOWN}", {})
    assert rendered == "X=${UNKNOWN}"
    assert missing == ["UNKNOWN"]


def test_render_partial_substitution():
    env = {"A": "hello"}
    rendered, missing = render_template("${A} ${B}", env)
    assert rendered == "hello ${B}"
    assert missing == ["B"]


def test_render_multiple_values():
    env = {"HOST": "db", "PORT": "5432", "NAME": "mydb"}
    tpl = "postgresql://${HOST}:${PORT}/${NAME}"
    rendered, missing = render_template(tpl, env)
    assert rendered == "postgresql://db:5432/mydb"
    assert missing == []


def test_render_bare_dollar_syntax():
    rendered, missing = render_template("$FOO", {"FOO": "bar"})
    assert rendered == "bar"
    assert missing == []


def test_render_empty_template():
    rendered, missing = render_template("", {"A": "1"})
    assert rendered == ""
    assert missing == []


def test_render_missing_deduplicated():
    _, missing = render_template("${X} and ${X}", {})
    assert missing == ["X"]


def test_render_no_env():
    rendered, missing = render_template("plain text", {})
    assert rendered == "plain text"
    assert missing == []
