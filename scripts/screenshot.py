"""Capture README screenshots for ProofMark Studio.

Assumes the three-process stack is already running:
  * Hub at http://127.0.0.1:8020
  * ProofMark PDF at http://127.0.0.1:8010
  * Text Inspection at http://127.0.0.1:8000

Run with the repo venv:
    .venv/Scripts/python scripts/screenshot.py

Idempotent — re-running overwrites existing PNGs under docs/screenshots/.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from playwright.async_api import Page, async_playwright

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
VIEWPORT = {"width": 1440, "height": 900}


async def shoot(page: Page, url: str, name: str, *, full_page: bool = False, setup: callable | None = None) -> None:
    await page.goto(url, wait_until="networkidle")
    if setup is not None:
        await setup(page)
    await page.wait_for_timeout(500)
    path = OUT_DIR / name
    await page.screenshot(path=str(path), full_page=full_page)
    print(f"  {name:30s} {path.stat().st_size // 1024:>5d} KB")


async def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Writing to {OUT_DIR}")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport=VIEWPORT, device_scale_factor=2)
        page = await ctx.new_page()

        # Hub home — hero + popular + organize group
        await shoot(page, "http://127.0.0.1:8020/", "hub-home.png")

        # All-tools view
        await shoot(
            page,
            "http://127.0.0.1:8020/#tools",
            "hub-catalog.png",
            setup=lambda pg: pg.keyboard.press("g"),
        )

        # Command palette (Cmd+K)
        async def open_palette(pg: Page) -> None:
            await pg.keyboard.press("Control+k")
            await pg.wait_for_timeout(300)
        await shoot(page, "http://127.0.0.1:8020/", "hub-palette.png", setup=open_palette)

        # Shortcuts cheat-sheet (?)
        async def open_shortcuts(pg: Page) -> None:
            await pg.keyboard.press("Shift+Slash")  # "?" on US keyboard
            await pg.wait_for_timeout(300)
        await shoot(page, "http://127.0.0.1:8020/", "hub-shortcuts.png", setup=open_shortcuts)

        # About (markdown-driven)
        await shoot(page, "http://127.0.0.1:8020/about", "hub-about.png")

        # Changelog (markdown-driven)
        await shoot(page, "http://127.0.0.1:8020/changelog", "hub-changelog.png")

        # Pretty 404
        await shoot(page, "http://127.0.0.1:8020/this-path-does-not-exist", "hub-404.png")

        # Live tool — Merge PDF on sibling app
        await shoot(page, "http://127.0.0.1:8010/merge-pdf", "tool-merge-pdf.png")

        # Live tool — PDF to Text
        await shoot(page, "http://127.0.0.1:8010/pdf-to-text", "tool-pdf-to-text.png")

        # Text Inspection sibling landing
        await shoot(page, "http://127.0.0.1:8000/", "tool-text-inspection.png")

        # Roadmap-mode catalog (beta + planned tiles re-appear) — illustrates the env toggle
        await ctx.clear_cookies()
        await page.goto("http://127.0.0.1:8020/")
        await shoot(
            page,
            "http://127.0.0.1:8020/#tools",
            "hub-catalog-live-only.png",
            setup=lambda pg: pg.keyboard.press("g"),
        )

        await browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
