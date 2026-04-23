"""Tool registry — single source of truth for slug → {status, group, parent, url, title, desc}.

Must mirror `static/hub/src/tools.jsx` (display metadata). Backend owns:
  - status: 'live' | 'beta' | 'planned'
  - parent: 'proofmark-pdf' | 'text-cleaner' | None
  - url:    computed from sibling base URLs; None for stubs

Adding a new tool:
  1) Add entry here with title, desc, group, status, parent, path (on parent).
  2) Add matching tile to tools.jsx (title, group, desc, icon).
  3) That's it. Hub catalog picks it up automatically via /api/tools.

Env-var base URLs make this dev-vs-prod agnostic (Phase 9 Vercel rewrites):
  PROOFMARK_PDF_BASE=""   in prod \u2192 URLs become /pdf/merge-pdf (same-origin)
  PROOFMARK_PDF_BASE="http://127.0.0.1:8010"  locally \u2192 full URLs
"""
from __future__ import annotations

import os
from typing import Dict, Optional

# Base URLs read from env (re-read here so registry stays decoupled from hub_app imports).
PDF_BASE = os.environ.get("PROOFMARK_PDF_BASE", "http://127.0.0.1:8010")
TEXT_BASE = os.environ.get("PROOFMARK_TEXT_BASE", "http://127.0.0.1:8000")


def _pdf(path: str) -> str:
    return f"{PDF_BASE}{path}" if PDF_BASE else f"/pdf{path}"


def _text(path: str) -> str:
    return f"{TEXT_BASE}{path}" if TEXT_BASE else f"/text{path}"


# ─── Groups (mirror GROUPS in tools.jsx) ──────────────────────────────────
GROUPS: Dict[str, Dict[str, str]] = {
    "organize":     {"label": "Organize PDF",        "tone": "#ff7a45"},
    "convert-from": {"label": "Convert from PDF",    "tone": "#a57cff"},
    "convert-to":   {"label": "Convert to PDF",      "tone": "#7cb0ff"},
    "edit":         {"label": "View & Edit",         "tone": "#5ee59b"},
    "sign":         {"label": "Sign & Secure",       "tone": "#ff6b8a"},
    "proof":        {"label": "Proofing",            "tone": "#62e0d9"},
    "ai":           {"label": "AI PDF",              "tone": "#f0c674"},
    "workflow":     {"label": "Workflow",            "tone": "#8a96b8"},
}


# ─── Tool catalog (slug → entry) ──────────────────────────────────────────
# status: 'live' redirects to url; 'beta' and 'planned' render the stub page.
# parent: used by stub page for the "Open [Parent Tool]" button.
# url: only meaningful for live tools; stubs ignore.
def _t(title: str, desc: str, group: str, status: str,
       parent: Optional[str] = None, path: str = "") -> Dict[str, object]:
    # URL is only set for LIVE tools \u2014 beta/planned go through the stub page.
    # The stub's "Open parent app" button uses PARENT_URLS, not this field.
    # NOTE: keep paths WITHOUT trailing slashes (Vercel rewrite `/pdf/:path*` won't
    # match `/pdf/`). Use "" for sibling home, "?foo=bar" for querystrings, or
    # "/specific-route" for specific routes.
    url: Optional[str] = None
    if status == "live":
        if parent == "proofmark-pdf":
            url = _pdf(path)
        elif parent == "text-cleaner":
            url = _text(path)
    return {
        "title": title, "desc": desc, "group": group,
        "status": status, "parent": parent, "url": url,
    }


TOOLS: Dict[str, Dict[str, object]] = {
    # ── Organize ──────────────────────────────────────────────────────
    "merge-pdf":          _t("Merge PDF",       "Combine multiple PDFs into a single document.",        "organize",     "live",    "proofmark-pdf", "/merge-pdf"),
    "split-pdf":          _t("Split PDF",       "Split by range, fixed chunks, or every N pages.",      "organize",     "live",    "proofmark-pdf", "/split-pdf"),
    "extract-pdf-pages":  _t("Extract Pages",   "Pull selected pages into a new file.",                 "organize",     "live",    "proofmark-pdf"),
    "organize-pdf":       _t("Organize PDF",    "Resequence and reorganize page structure visually.",   "organize",     "live",    "proofmark-pdf", "/organize-pdf"),
    "compress-pdf":       _t("Compress PDF",    "Shrink file size without losing structure.",           "organize",     "live",    "proofmark-pdf", "/compress-pdf"),
    "rotate-pdf":         _t("Rotate PDF",      "Rotate pages and normalize orientation.",              "organize",     "live",    "proofmark-pdf", "/rotate-pdf"),
    "delete-pdf-pages":   _t("Delete Pages",    "Remove unwanted pages before delivery.",               "organize",     "live",    "proofmark-pdf", "/delete-pdf-pages"),

    # ── Convert from PDF ──────────────────────────────────────────────
    "pdf-to-word":        _t("PDF to Word",     "Editable .docx output.",                               "convert-from", "planned", "proofmark-pdf"),
    "pdf-to-excel":       _t("PDF to Excel",    "Tables and data to spreadsheets.",                     "convert-from", "planned", "proofmark-pdf"),
    "pdf-to-ppt":         _t("PDF to PPT",      "Slide-ready PowerPoint output.",                       "convert-from", "planned", "proofmark-pdf"),
    "pdf-to-jpg":         _t("PDF to JPG",      "Export pages as JPG images.",                          "convert-from", "live",    "proofmark-pdf", "/pdf-to-jpg"),
    "pdf-to-png":         _t("PDF to PNG",      "Export pages as PNG images.",                          "convert-from", "live",    "proofmark-pdf", "/pdf-to-png"),
    "pdf-to-text":        _t("PDF to Text",     "Extract clean text.",                                  "convert-from", "live",    "proofmark-pdf", "/pdf-to-text"),
    "pdf-to-markdown":    _t("PDF to Markdown", "Markdown-friendly content.",                           "convert-from", "planned", "proofmark-pdf"),
    "pdf-to-html":        _t("PDF to HTML",     "Web-ready HTML output.",                               "convert-from", "planned", "proofmark-pdf"),

    # ── Convert to PDF ────────────────────────────────────────────────
    "word-to-pdf":        _t("Word to PDF",     "Convert .docx into clean PDF.",                        "convert-to",   "planned", "proofmark-pdf"),
    "excel-to-pdf":       _t("Excel to PDF",    "Spreadsheets to PDF reports.",                         "convert-to",   "planned", "proofmark-pdf"),
    "ppt-to-pdf":         _t("PPT to PDF",      "Decks to PDFs.",                                       "convert-to",   "planned", "proofmark-pdf"),
    "jpg-to-pdf":         _t("JPG to PDF",      "Combine JPGs into a PDF.",                             "convert-to",   "planned", "proofmark-pdf"),
    "html-to-pdf":        _t("HTML to PDF",     "Render HTML into PDF.",                                "convert-to",   "planned", "proofmark-pdf"),
    "markdown-to-pdf":    _t("Markdown to PDF", "Markdown to final PDF.",                               "convert-to",   "planned", "proofmark-pdf"),
    "pdf-ocr":            _t("PDF OCR",         "Make scanned PDFs searchable.",                        "convert-to",   "planned", "proofmark-pdf"),

    # ── View & Edit ───────────────────────────────────────────────────
    "edit-pdf":           _t("Edit PDF",        "Edit PDF content and layout inline.",                  "edit",         "planned", "proofmark-pdf"),
    "pdf-annotator":      _t("Annotator",       "Comments, highlights, and callouts.",                  "edit",         "beta",    "proofmark-pdf"),
    "pdf-reader":         _t("Reader",          "Focused reading experience.",                          "edit",         "planned", "proofmark-pdf"),
    "number-pages":       _t("Number Pages",    "Add running page numbers.",                            "edit",         "live",    "proofmark-pdf", "/number-pages"),
    "crop-pdf":           _t("Crop PDF",        "Crop edges and reset trim.",                           "edit",         "planned", "proofmark-pdf"),
    "redact-pdf":         _t("Redact PDF",      "Permanently remove sensitive content.",                "edit",         "planned", "proofmark-pdf"),
    "watermark-pdf":      _t("Watermark PDF",   "Brand, legal, and draft watermarks.",                  "edit",         "planned", "proofmark-pdf"),
    "pdf-form-filler":    _t("Form Filler",     "Fill forms and flatten to PDF.",                       "edit",         "planned", "proofmark-pdf"),

    # ── Sign & Secure ─────────────────────────────────────────────────
    "sign-pdf":           _t("Sign PDF",          "Add signatures cleanly.",                            "sign",         "planned", "proofmark-pdf"),
    "request-signatures": _t("Request Signatures","Route documents for signature.",                     "sign",         "planned", "proofmark-pdf"),
    "unlock-pdf":         _t("Unlock PDF",        "Remove access restrictions when allowed.",           "sign",         "planned", "proofmark-pdf"),
    "protect-pdf":        _t("Protect PDF",       "Add password and protection layers.",                "sign",         "planned", "proofmark-pdf"),
    "flatten-pdf":        _t("Flatten PDF",       "Flatten annotations and interactive layers.",        "sign",         "planned", "proofmark-pdf"),

    # ── Proofing (text-cleaner) ───────────────────────────────────────
    "text-inspection":      _t("Text Inspection",   "Hidden chars, normalize whitespace, typography.",  "proof",        "live",    "text-cleaner"),
    "inspect-hidden":       _t("Hidden Characters", "Zero-width, bidi, suspicious glyphs.",             "proof",        "live",    "text-cleaner", "?focus=hidden"),
    "normalize-whitespace": _t("Normalize Space",   "Review and normalize whitespace.",                 "proof",        "live",    "text-cleaner", "?focus=whitespace"),
    "review-typography":    _t("Typography Review", "Check typographic replacements.",                  "proof",        "live",    "text-cleaner", "?focus=typography"),
    "export-cleanup-report":_t("Cleanup Report",    "Export findings and choices.",                     "proof",        "live",    "text-cleaner", "?focus=report"),

    # ── AI ────────────────────────────────────────────────────────────
    "ai-pdf-assistant":   _t("AI Assistant",      "Work with PDFs via a chat assistant.",               "ai",           "beta",    "proofmark-pdf"),
    "chat-with-pdf":      _t("Chat with PDF",     "Ask questions against a document.",                  "ai",           "beta",    "proofmark-pdf"),
    "ai-pdf-summarizer":  _t("Summarize PDF",     "Executive summaries from long PDFs.",                "ai",           "beta",    "proofmark-pdf"),
    "translate-pdf":      _t("Translate PDF",     "Translate PDFs to other languages.",                 "ai",           "planned", "proofmark-pdf"),

    # ── Workflow ──────────────────────────────────────────────────────
    "project-intake":     _t("Project Intake",    "Capture source files and project setup.",            "workflow",     "planned"),
    "review-queue":       _t("Review Queue",      "Centralize review passes and checkpoints.",          "workflow",     "planned"),
    "delivery-center":    _t("Delivery Center",   "Package final outputs and delivery.",                "workflow",     "planned"),
    "standards-library":  _t("Standards Library", "Style guides, QA rules, reusable standards.",        "workflow",     "planned"),
    "publishing-hub":     _t("Publishing Hub",    "Publishing-ready exports and distribution.",         "workflow",     "planned"),
}


PARENT_URLS: Dict[str, str] = {
    "proofmark-pdf": PDF_BASE if PDF_BASE else "/pdf",
    "text-cleaner":  TEXT_BASE if TEXT_BASE else "/text",
}

PARENT_LABELS: Dict[str, str] = {
    "proofmark-pdf": "ProofMark PDF",
    "text-cleaner":  "Text Inspection",
}


def tool_counts() -> Dict[str, int]:
    """Live/beta/planned counts for the hub stats."""
    counts = {"total": len(TOOLS), "live": 0, "beta": 0, "planned": 0}
    for t in TOOLS.values():
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    return counts
