"""Minimal Markdown → HTML renderer for first-party content (/about, /changelog).

Only the subset we actually author: `# h1`..`### h3`, paragraphs, `-` lists,
`**bold**`, `_italic_`, `` `code` ``, `[text](url)`. Inputs are escaped first
so the renderer is safe even though content is first-party.

Not a replacement for a real Markdown parser. Intentionally bounded so we
don't add a dep just for two static pages.
"""
from __future__ import annotations

import html
import re
from typing import List


def render(source: str) -> str:
    """Render a tiny Markdown subset to safe HTML."""
    blocks = _split_blocks(source)
    parts: List[str] = []
    for block in blocks:
        rendered = _render_block(block)
        if rendered:
            parts.append(rendered)
    return "\n".join(parts)


def _split_blocks(source: str) -> List[str]:
    normalized = source.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    return [b for b in re.split(r"\n{2,}", normalized) if b.strip()]


def _render_block(block: str) -> str:
    lines = block.split("\n")
    first = lines[0]
    if first.startswith("### "):
        return f"<h3>{_inline(first[4:])}</h3>"
    if first.startswith("## "):
        return f"<h2>{_inline(first[3:])}</h2>"
    if first.startswith("# "):
        return f"<h1>{_inline(first[2:])}</h1>"
    if all(re.match(r"^\s*-\s+", ln) for ln in lines):
        items = "".join(f"<li>{_inline(re.sub(r'^\s*-\s+', '', ln))}</li>" for ln in lines)
        return f"<ul>{items}</ul>"
    joined = " ".join(ln.strip() for ln in lines)
    return f"<p>{_inline(joined)}</p>"


def _inline(text: str) -> str:
    """Escape first, then re-apply the small set of inline markers."""
    out = html.escape(text, quote=False)
    # Order matters: code first so its contents aren't re-parsed, then links, then emphasis.
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"<em>\1</em>", out)
    return out
