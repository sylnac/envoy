"""Template rendering: fill a .env template with values from a profile."""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Matches ${VAR_NAME} or $VAR_NAME placeholders
_PLACEHOLDER_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def find_placeholders(template: str) -> List[str]:
    """Return a list of unique variable names referenced in *template*."""
    names: list[str] = []
    seen: set[str] = set()
    for m in _PLACEHOLDER_RE.finditer(template):
        name = m.group(1) or m.group(2)
        if name not in seen:
            names.append(name)
            seen.add(name)
    return names


def render_template(template: str, env: Dict[str, str]) -> Tuple[str, List[str]]:
    """Substitute placeholders in *template* using *env*.

    Returns
    -------
    rendered : str
        The template with all known placeholders replaced.
    missing : list[str]
        Variable names that appeared in the template but were absent from *env*.
    """
    missing: list[str] = []

    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        name = m.group(1) or m.group(2)
        if name in env:
            return env[name]
        missing.append(name)
        return m.group(0)  # leave placeholder intact

    rendered = _PLACEHOLDER_RE.sub(_replace, template)
    # de-duplicate while preserving order
    seen: set[str] = set()
    unique_missing = [x for x in missing if not (x in seen or seen.add(x))]  # type: ignore[func-returns-value]
    return rendered, unique_missing


def render_template_file(path: str, env: Dict[str, str]) -> Tuple[str, List[str]]:
    """Read a template file from *path* and render it against *env*."""
    with open(path, "r", encoding="utf-8") as fh:
        template = fh.read()
    return render_template(template, env)
