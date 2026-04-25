"""Dynamic OpenGraph card renderer for /og/<slug>.png.

Renders a 1200x630 PNG (standard OG dimensions) using the brand fonts.
Caches per-slug bytes in process so repeated crawls don't re-render.

Layout (top → bottom):
  · brand mark + ProofMark Studio · Working hub  (mono eyebrow)
  · {Tool title}                                  (Instrument Serif, ~88px)
  · {Tool description}                            (Geist Regular, ~32px)
  · {STATUS} · {GROUP LABEL}                      (mono footer)

Group color (`tone`) tints the left edge accent and the status pill.
"""
from __future__ import annotations

import io
import textwrap
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from PIL import Image, ImageDraw, ImageFont

PACKAGE_ROOT = Path(__file__).resolve().parent
FONTS_DIR = PACKAGE_ROOT / "static" / "fonts"

WIDTH = 1200
HEIGHT = 630
PADDING = 80

BG = (10, 10, 11)            # --bg
BG_ELEV = (17, 17, 19)       # --bg-elev
TEXT = (241, 241, 243)       # --text
TEXT_MUTED = (138, 138, 148) # --text-muted
TEXT_DIM = (94, 94, 104)     # --text-dim

# Group tones mirror tool_registry.GROUPS for visual continuity.
TONE_DEFAULT = (124, 176, 255)  # --accent (#7cb0ff)


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS_DIR / name), size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """Greedy word-wrap that respects font metrics (not just char count)."""
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textlength(candidate, font=font) <= max_w:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _blend(fg: tuple[int, int, int], bg: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    """Linear blend foreground over background (no real alpha — RGB only)."""
    return tuple(int(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))  # type: ignore[return-value]


def render(entry: Mapping[str, object], group_label: str, group_tone: str) -> bytes:
    """Render the OG card for a tool entry. Returns PNG bytes."""
    title = str(entry.get("title", "ProofMark Studio"))
    desc = str(entry.get("desc") or entry.get("description") or "")
    status = str(entry.get("status", "live")).upper()
    tone = _hex_to_rgb(group_tone) if group_tone else TONE_DEFAULT

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Tone accent stripe down the left edge.
    draw.rectangle((0, 0, 10, HEIGHT), fill=tone)

    eyebrow_font = _font("GeistMono-Regular.ttf", 22)
    title_font = _font("InstrumentSerif-Regular.ttf", 96)
    desc_font = _font("Geist-Regular.ttf", 32)
    footer_font = _font("GeistMono-Regular.ttf", 20)

    # Brand mark — small tone-colored square + wordmark eyebrow
    mark_size = 32
    mark_y = PADDING - 4
    draw.rounded_rectangle(
        (PADDING, mark_y, PADDING + mark_size, mark_y + mark_size),
        radius=8,
        fill=tone,
    )
    eyebrow = "ProofMark Studio  ·  Working hub"
    draw.text(
        (PADDING + mark_size + 14, PADDING + 4),
        eyebrow,
        font=eyebrow_font,
        fill=TEXT_MUTED,
    )

    # Title — wrap to two lines max
    max_text_width = WIDTH - 2 * PADDING
    title_lines = _wrap(draw, title, title_font, max_text_width)[:2]
    title_y = PADDING + 92
    for i, line in enumerate(title_lines):
        draw.text((PADDING, title_y + i * 108), line, font=title_font, fill=TEXT)
    title_block_bottom = title_y + len(title_lines) * 108

    # Description — three lines max
    desc_lines = _wrap(draw, desc, desc_font, max_text_width)[:3]
    desc_y = title_block_bottom + 12
    for i, line in enumerate(desc_lines):
        draw.text((PADDING, desc_y + i * 46), line, font=desc_font, fill=TEXT_MUTED)

    # Footer — status pill + group label
    footer_y = HEIGHT - PADDING - 16
    pill_text = status
    pill_w = int(draw.textlength(pill_text, font=footer_font)) + 36
    pill_h = 36
    pill_box = (PADDING, footer_y - pill_h, PADDING + pill_w, footer_y)
    draw.rounded_rectangle(pill_box, radius=18, fill=_blend(tone, BG, 0.18), outline=tone, width=1)
    # Center-text the pill
    pill_text_w = draw.textlength(pill_text, font=footer_font)
    draw.text(
        (PADDING + (pill_w - pill_text_w) / 2, footer_y - pill_h + 7),
        pill_text,
        font=footer_font,
        fill=tone,
    )
    draw.text(
        (PADDING + pill_w + 18, footer_y - pill_h + 7),
        group_label.upper(),
        font=footer_font,
        fill=TEXT_DIM,
    )

    # Right-aligned brand domain
    domain = "proofmarkstudio.com"
    domain_w = draw.textlength(domain, font=footer_font)
    draw.text(
        (WIDTH - PADDING - domain_w, footer_y - pill_h + 7),
        domain,
        font=footer_font,
        fill=TEXT_DIM,
    )

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


@lru_cache(maxsize=128)
def render_cached(slug: str, title: str, desc: str, status: str, group_label: str, tone: str) -> bytes:
    """LRU-cached wrapper — the cache key is the visible content, so a tool
    rename in the registry invalidates naturally on next request."""
    entry = {"title": title, "desc": desc, "status": status}
    return render(entry, group_label, tone)
