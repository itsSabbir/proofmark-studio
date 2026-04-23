"""Thin shim — preserves the `web_app:app` / `web_app:main` entry points that
pyproject.toml, run.py, launch scripts, and tests depend on.

The real implementation lives in proofmark_studio.hub_app.
"""
from __future__ import annotations

from proofmark_studio.hub_app import (
    APP_NAME,
    APP_DESCRIPTION,
    APP_KICKER,
    CREATOR_NAME,
    CREATOR_SITE,
    DEFAULT_HOST,
    DEFAULT_PORT,
    KNOWN_PORTS,
    PROOFMARK_PDF_BASE,
    PROOFMARK_SITE_URL,
    PROOFMARK_TEXT_BASE,
    SECURITY_HEADERS,
    app,
    main,
)

__all__ = [
    "APP_NAME",
    "APP_DESCRIPTION",
    "APP_KICKER",
    "CREATOR_NAME",
    "CREATOR_SITE",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "KNOWN_PORTS",
    "PROOFMARK_PDF_BASE",
    "PROOFMARK_SITE_URL",
    "PROOFMARK_TEXT_BASE",
    "SECURITY_HEADERS",
    "app",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
