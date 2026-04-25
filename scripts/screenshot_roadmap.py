"""Capture the roadmap-mode catalog screenshot.

Run only when the hub was booted with PROOFMARK_SHOW_ALL_TILES=true.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

OUT = Path(__file__).resolve().parent.parent / "docs" / "screenshots" / "hub-catalog-roadmap.png"


async def main() -> int:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = await ctx.new_page()
        await page.goto("http://127.0.0.1:8020/", wait_until="networkidle")
        await page.keyboard.press("g")  # "All tools" view
        await page.wait_for_timeout(600)
        await page.screenshot(path=str(OUT))
        await browser.close()
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
