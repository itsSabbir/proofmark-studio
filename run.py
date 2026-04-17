#!/usr/bin/env python3
"""Proofmark Studio launcher wrapper."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    command = [
        "pwsh",
        "-ExecutionPolicy",
        "Bypass",
        "-NoLogo",
        "-NoProfile",
        "-File",
        str(repo_root / "scripts" / "launch-local.ps1"),
        "start",
        *sys.argv[1:],
    ]
    try:
        return subprocess.call(command, cwd=repo_root)
    except FileNotFoundError:
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from web_app import main as web_main  # noqa: WPS433 - runtime fallback

        return web_main()


if __name__ == "__main__":
    raise SystemExit(main())

