"""Per-tool feature flags — hub-side copy.

Kept in lockstep with ``proofmark_pdf/feature_flags.py``. Copy (not import)
because the three sibling repos deploy independently to Vercel and have no
shared-package infra yet. Small enough to diff-match manually.
"""
from __future__ import annotations

import os
from typing import Mapping

_OFF_VALUES = frozenset({"false", "0", "off", "no", "disabled"})
_ON_VALUES = frozenset({"true", "1", "on", "yes", "enabled"})


def flag_env_name(slug: str) -> str:
    return f"TOOL_{slug.replace('-', '_').upper()}_ENABLED"


def is_enabled(slug: str) -> bool:
    raw = os.environ.get(flag_env_name(slug))
    if raw is None:
        return True
    return raw.strip().lower() not in _OFF_VALUES


def show_all_tiles() -> bool:
    """Roadmap/dev view: when truthy, beta+planned tiles appear in the catalog.

    Default ``False``: users only see tools that work fully. Production stays
    honest — a tile is only visible if it does what it advertises. Flipping
    this to ``true`` (local dev, roadmap review) restores the full catalog.
    """
    raw = os.environ.get("PROOFMARK_SHOW_ALL_TILES", "")
    return raw.strip().lower() in _ON_VALUES


def is_displayed(slug: str, entry: Mapping[str, object]) -> bool:
    """Should ``slug`` appear on user-facing surfaces (catalog, sitemap, router)?

    A tool is displayed when:
      * its per-tool ``TOOL_<SLUG>_ENABLED`` flag is on, AND
      * either ``PROOFMARK_SHOW_ALL_TILES`` is truthy OR the tool is ``live``.
    """
    if not is_enabled(slug):
        return False
    if show_all_tiles():
        return True
    return entry.get("status") == "live"


__all__ = ["flag_env_name", "is_enabled", "show_all_tiles", "is_displayed"]
