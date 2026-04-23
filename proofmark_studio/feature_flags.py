"""Per-tool feature flags — hub-side copy.

Kept in lockstep with ``proofmark_pdf/feature_flags.py``. Copy (not import)
because the three sibling repos deploy independently to Vercel and have no
shared-package infra yet. Small enough to diff-match manually.
"""
from __future__ import annotations

import os

_OFF_VALUES = frozenset({"false", "0", "off", "no", "disabled"})


def flag_env_name(slug: str) -> str:
    return f"TOOL_{slug.replace('-', '_').upper()}_ENABLED"


def is_enabled(slug: str) -> bool:
    raw = os.environ.get(flag_env_name(slug))
    if raw is None:
        return True
    return raw.strip().lower() not in _OFF_VALUES


__all__ = ["flag_env_name", "is_enabled"]
