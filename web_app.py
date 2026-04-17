"""Proofmark Studio hub page."""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import webbrowser
from datetime import datetime
from threading import Timer
from typing import Dict, List, Optional, Tuple

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

APP_NAME = "Proofmark Studio"
APP_DESCRIPTION = "Proofmark Studio is the working hub for the Proofmark product line."
APP_KICKER = "Working hub"
CREATOR_NAME = "Sabbir Hossain"
CREATOR_SITE = os.environ.get("CREATOR_SITE", "https://sabbir.ca/")
CREATOR_GITHUB = "https://github.com/itsSabbir"
CREATOR_LINKEDIN = "https://www.linkedin.com/in/itssabbir"
PROOFMARK_SITE_URL = os.environ.get("PROOFMARK_SITE_URL", CREATOR_SITE)
PROOFMARK_TEXT_STUDIO_URL = os.environ.get("PROOFMARK_TEXT_STUDIO_URL", "http://127.0.0.1:8000")
PROOFMARK_PDF_URL = os.environ.get("PROOFMARK_PDF_URL", "http://127.0.0.1:8010")
TEXT_STUDIO_ROUTE = "/go/text-inspection"
PROOFMARK_PDF_ROUTE = "/go/proofmark-pdf"
PROOFMARK_SITE_ROUTE = "/go/proofmark-site"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8020
KNOWN_PORTS = (8020, 8021, 8030, 8040, 8000, 8001, 8010)
NAV_LINKS: Tuple[Tuple[str, str, str], ...] = (
    ("home", "/", "Studio"),
    ("tools", "/#tools", "Tools"),
    ("text", TEXT_STUDIO_ROUTE, "Text Inspection"),
    ("pdf", PROOFMARK_PDF_ROUTE, "Proofmark PDF"),
    ("site", PROOFMARK_SITE_ROUTE, "Proofmark site"),
)

app = FastAPI(title=APP_NAME)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self';"
    ),
}


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


def _safe_origin(request: Request) -> str:
    return str(request.base_url).rstrip("/")


def _attrs(url: str) -> str:
    return ""


def _studio_spokes() -> List[Dict[str, str]]:
    return [
        {
            "slug": "text-inspection",
            "title": "Proofmark Text Inspection Studio",
            "label": "Text",
            "eyebrow": "Live",
            "status": "Live now",
            "tone": "live",
            "phase": "Live today",
            "summary": "Clean and inspect text before it moves into layout or export.",
            "url": TEXT_STUDIO_ROUTE,
            "radius": "clamp(154px, 23vw, 250px)",
            "angle": "-90deg",
            "color": "#0f766e",
        },
        {
            "slug": "proofmark-pdf",
            "title": "Proofmark PDF",
            "label": "PDF",
            "eyebrow": "Live",
            "status": "Live now",
            "tone": "live",
            "phase": "Live today",
            "summary": "Merge and split files now, then grow the wider PDF layer from here.",
            "url": PROOFMARK_PDF_ROUTE,
            "radius": "clamp(154px, 23vw, 248px)",
            "angle": "-30deg",
            "color": "#155eef",
        },
        {
            "slug": "document-tools",
            "title": "Document tools",
            "label": "Tools",
            "eyebrow": "Planned",
            "status": "Planned",
            "tone": "planned",
            "phase": "Next layer",
            "summary": "The broader family of editing, conversion, signing, and document-production tools.",
            "url": "#mind-map",
            "radius": "clamp(150px, 23vw, 244px)",
            "angle": "30deg",
            "color": "#b45309",
        },
        {
            "slug": "review-qa",
            "title": "Review & QA",
            "label": "Review",
            "eyebrow": "Planned",
            "status": "Planned",
            "tone": "planned",
            "phase": "Future lane",
            "summary": "Checks, standards, review passes, and quality workflows across projects.",
            "url": "#mind-map",
            "radius": "clamp(154px, 23vw, 244px)",
            "angle": "90deg",
            "color": "#475467",
        },
        {
            "slug": "proofmark-site",
            "title": "Proofmark site",
            "label": "Site",
            "eyebrow": "Live",
            "status": "Live now",
            "tone": "live",
            "phase": "Live today",
            "summary": "The public-facing site and parent brand entry point for the product line.",
            "url": PROOFMARK_SITE_ROUTE,
            "radius": "clamp(152px, 23vw, 244px)",
            "angle": "150deg",
            "color": "#1d4ed8",
        },
        {
            "slug": "ai-automation",
            "title": "AI & automation",
            "label": "Automation",
            "eyebrow": "Planned",
            "status": "Planned",
            "tone": "planned",
            "phase": "Future lane",
            "summary": "Assistants, automations, and workflow support across the broader platform.",
            "url": "#mind-map",
            "radius": "clamp(152px, 23vw, 244px)",
            "angle": "210deg",
            "color": "#0f766e",
        },
    ]


def _icon_svg() -> str:
    return """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128 128' role='img' aria-labelledby='t d'>
  <title id='t'>Proofmark Studio</title><desc id='d'>Proofmark Studio hub icon.</desc>
  <rect width='128' height='128' rx='24' fill='#002A5C'/>
  <circle cx='64' cy='64' r='16' fill='#FFFFFF'/>
  <circle cx='64' cy='64' r='26' fill='none' stroke='#9FB6D5' stroke-width='2' stroke-dasharray='5 6'/>
  <g stroke='#DCE5F0' stroke-width='3' stroke-linecap='round'>
    <line x1='64' y1='64' x2='64' y2='25'/><line x1='64' y1='64' x2='96' y2='44'/><line x1='64' y1='64' x2='98' y2='84'/>
    <line x1='64' y1='64' x2='64' y2='103'/><line x1='64' y1='64' x2='30' y2='84'/><line x1='64' y1='64' x2='32' y2='44'/>
  </g>
  <g fill='#FFFFFF'><circle cx='64' cy='22' r='8'/><circle cx='99' cy='42' r='8'/><circle cx='99' cy='86' r='8'/><circle cx='64' cy='106' r='8'/><circle cx='29' cy='86' r='8'/><circle cx='29' cy='42' r='8'/></g>
</svg>"""


def _og_image_svg() -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 630' role='img' aria-labelledby='ot od'>
  <title id='ot'>{APP_NAME}</title><desc id='od'>Open Graph card for Proofmark Studio.</desc>
  <defs><linearGradient id='bg' x1='0' y1='0' x2='1' y2='1'><stop offset='0' stop-color='#002A5C'/><stop offset='1' stop-color='#001A3D'/></linearGradient></defs>
  <rect width='1200' height='630' fill='url(#bg)'/><rect x='70' y='70' width='1060' height='490' rx='30' fill='#FFFFFF' opacity='0.05'/>
  <circle cx='270' cy='315' r='72' fill='#FFFFFF'/><circle cx='270' cy='315' r='118' fill='none' stroke='#88A4C8' stroke-width='3' stroke-dasharray='8 12' opacity='0.75'/>
  <g stroke='#DCE5F0' stroke-width='4' stroke-linecap='round'><line x1='270' y1='315' x2='270' y2='170'/><line x1='270' y1='315' x2='395' y2='230'/><line x1='270' y1='315' x2='410' y2='385'/><line x1='270' y1='315' x2='270' y2='470'/><line x1='270' y1='315' x2='135' y2='385'/><line x1='270' y1='315' x2='150' y2='230'/></g>
  <g fill='#FFFFFF'><circle cx='270' cy='150' r='24'/><circle cx='418' cy='220' r='24'/><circle cx='426' cy='395' r='24'/><circle cx='270' cy='482' r='24'/><circle cx='122' cy='395' r='24'/><circle cx='122' cy='220' r='24'/></g>
  <text x='520' y='220' fill='#FFFFFF' font-family='Cambria, Georgia, serif' font-size='92' font-weight='700' letter-spacing='-3'>{APP_NAME}</text>
  <text x='520' y='286' fill='#DCE5F0' font-family='Aptos, Segoe UI, sans-serif' font-size='34' font-weight='500'>The working hub for live projects and the wider Proofmark platform.</text>
  <g transform='translate(520 360)'><rect width='220' height='58' rx='14' fill='#FFFFFF'/><text x='110' y='38' fill='#002A5C' font-family='Aptos, Segoe UI, sans-serif' font-size='22' font-weight='700' text-anchor='middle'>Text inspection</text></g>
  <g transform='translate(760 360)'><rect width='180' height='58' rx='14' fill='#FFFFFF'/><text x='90' y='38' fill='#002A5C' font-family='Aptos, Segoe UI, sans-serif' font-size='22' font-weight='700' text-anchor='middle'>Proofmark PDF</text></g>
  <text x='520' y='540' fill='#9FB6D5' font-family='Aptos, Segoe UI, sans-serif' font-size='22' font-weight='500'>Part of the Proofmark product line by {CREATOR_NAME}</text>
</svg>"""


def _nav(active: str) -> str:
    links = []
    for key, href, label in NAV_LINKS:
        if key == "tools":
            links.append(_tools_menu())
            continue
        css = "nav-link active" if key == active else "nav-link"
        links.append(f"<a class='{css}' href='{href}'{_attrs(href)}>{label}</a>")
    return (
        "<div class='topbar'><a class='brand-lockup' href='/' aria-label='Proofmark Studio home'>"
        "<img class='brand-icon' src='/icon.svg' alt='Proofmark Studio icon' width='44' height='44'>"
        f"<span><span class='brand-name'>{APP_NAME}</span><span class='brand-kicker'>{APP_KICKER}</span></span></a>"
        "<nav class='site-nav'>" + "".join(links) + "</nav></div>"
    )


def _footer() -> str:
    year = datetime.now().year
    return (
        "<footer class='site-footer'><div class='footer-row'>"
        f"<div><div class='footer-title'>{APP_NAME}</div><p>Proofmark Studio connects the live projects and planned lanes across the Proofmark product line.</p></div>"
        "<div class='footer-links'>"
        "<a href='/'>Proofmark Studio</a>"
        f"<a href='{TEXT_STUDIO_ROUTE}'{_attrs(TEXT_STUDIO_ROUTE)}>Text Inspection</a>"
        f"<a href='{PROOFMARK_PDF_ROUTE}'{_attrs(PROOFMARK_PDF_ROUTE)}>Proofmark PDF</a>"
        f"<a href='{PROOFMARK_SITE_ROUTE}'{_attrs(PROOFMARK_SITE_ROUTE)}>Proofmark site</a>"
        "<a href='/privacy'>Privacy</a><a href='/terms'>Terms</a>"
        "</div></div>"
        f"<div class='footer-meta'>Built by {CREATOR_NAME}. Copyright {year} Proofmark Studio.</div></footer>"
    )


def _tool_catalog() -> List[Tuple[str, List[Dict[str, str]]]]:
    def stub(slug: str, title: str, summary: str) -> Dict[str, str]:
        return {"slug": slug, "title": title, "status": "Stub", "summary": summary, "url": f"/tools/{slug}"}

    return [
        (
            "Live now",
            [
                {"slug": "proofmark-studio", "title": "Proofmark Studio", "status": "Hub", "summary": "The central hub for the Proofmark product line.", "url": "/"},
                {"slug": "proofmark-text-inspection-studio", "title": "Proofmark Text Inspection Studio", "status": "Live now", "summary": "Current text inspection and cleanup workflow.", "url": TEXT_STUDIO_ROUTE},
                {"slug": "proofmark-pdf", "title": "Proofmark PDF", "status": "Live now", "summary": "Current merge and split workflow for PDF files.", "url": PROOFMARK_PDF_ROUTE},
                {"slug": "proofmark-site", "title": "Proofmark site", "status": "Live now", "summary": "Public-facing Proofmark site and brand entry point.", "url": PROOFMARK_SITE_ROUTE},
            ],
        ),
        (
            "Workflow",
            [
                stub("project-intake", "Project intake", "Capture source files, project setup, and intake details in one place."),
                stub("review-queue", "Review queue", "Centralize review passes, pending work, and internal checkpoints."),
                stub("delivery-center", "Delivery center", "Package final outputs, exports, and client-ready delivery flows."),
                stub("standards-library", "Standards library", "Keep style guides, QA rules, and reusable standards close to the work."),
                stub("publishing-hub", "Publishing hub", "Handle publishing-ready exports and downstream distribution workflows."),
            ],
        ),
        (
            "Proofing",
            [
                {"slug": "proofmark-text-inspection-studio", "title": "Proofmark Text Inspection Studio", "status": "Live now", "summary": "Current text inspection and cleanup workflow.", "url": TEXT_STUDIO_ROUTE},
            ],
        ),
        (
            "Compress",
            [
                stub("compress-pdf", "Compress PDF", "Reduce PDF size without losing the route or navigation shape later."),
            ],
        ),
        (
            "Organize",
            [
                {"slug": "merge-pdf", "title": "Merge PDF", "status": "Live now", "summary": "Combine multiple PDFs into one file in Proofmark PDF.", "url": PROOFMARK_PDF_ROUTE},
                {"slug": "split-pdf", "title": "Split PDF", "status": "Live now", "summary": "Split a PDF by ranges, chunks, or selected pages in Proofmark PDF.", "url": PROOFMARK_PDF_ROUTE},
                stub("rotate-pdf", "Rotate PDF", "Rotate pages and normalize orientation across a document."),
                stub("delete-pdf-pages", "Delete PDF Pages", "Remove unwanted pages before delivery."),
                stub("extract-pdf-pages", "Extract PDF Pages", "Pull selected PDF pages into a new document."),
                stub("organize-pdf", "Organize PDF", "Resequence, combine, and reorganize page structure."),
            ],
        ),
        (
            "View & Edit",
            [
                stub("edit-pdf", "Edit PDF", "Edit PDF content and layout inside the future document suite."),
                stub("pdf-annotator", "PDF Annotator", "Add comments, highlights, and callouts directly on PDF pages."),
                stub("pdf-reader", "PDF Reader", "Read documents in a focused Proofmark viewing experience."),
                stub("number-pages", "Number Pages", "Add running page numbers and structured numbering patterns."),
                stub("crop-pdf", "Crop PDF", "Crop page edges and reset trim boundaries."),
                stub("redact-pdf", "Redact PDF", "Remove or permanently hide sensitive document content."),
                stub("watermark-pdf", "Watermark PDF", "Apply branded or legal watermarks to document pages."),
                stub("pdf-form-filler", "PDF Form Filler", "Fill forms and output finished PDFs cleanly."),
                stub("share-pdf", "Share PDF", "Create share-friendly document delivery flows."),
            ],
        ),
        (
            "Convert from PDF",
            [
                stub("pdf-to-word", "PDF to Word", "Convert PDFs into editable Word documents."),
                stub("pdf-to-excel", "PDF to Excel", "Extract tables and structured data into spreadsheets."),
                stub("pdf-to-ppt", "PDF to PPT", "Turn PDF pages into slide-ready PowerPoint content."),
                stub("pdf-to-jpg", "PDF to JPG", "Export PDF pages as JPG images."),
                stub("pdf-to-png", "PDF to PNG", "Export PDF pages as PNG images."),
                stub("pdf-to-webp", "PDF to WebP", "Export PDF pages to lightweight WebP images."),
                stub("pdf-to-html", "PDF to HTML", "Convert PDF pages into web-ready HTML output."),
                stub("pdf-to-text", "PDF to Text", "Extract clean text from PDF files."),
                stub("pdf-to-markdown", "PDF to Markdown", "Convert PDFs into markdown-friendly content."),
                stub("pdf-to-csv", "PDF to CSV", "Extract table-like PDF data into CSV output."),
                stub("pdf-to-json", "PDF to JSON", "Turn PDF structure and extracted data into JSON."),
                stub("pdf-to-xml", "PDF to XML", "Convert document structure into XML output."),
                stub("pdf-to-svg", "PDF to SVG", "Export pages or vectors into SVG."),
                stub("pdf-to-epub", "PDF to EPUB", "Convert PDFs into EPUB for reading workflows."),
            ],
        ),
        (
            "Convert to PDF",
            [
                stub("word-to-pdf", "Word to PDF", "Convert Word documents into clean PDF output."),
                stub("excel-to-pdf", "Excel to PDF", "Turn spreadsheets into PDF reports."),
                stub("ppt-to-pdf", "PPT to PDF", "Export PowerPoint decks into PDFs."),
                stub("jpg-to-pdf", "JPG to PDF", "Combine JPG images into PDFs."),
                stub("png-to-pdf", "PNG to PDF", "Convert PNG images into PDF pages."),
                stub("webp-to-pdf", "WebP to PDF", "Convert WebP assets into PDF output."),
                stub("html-to-pdf", "HTML to PDF", "Generate PDFs from HTML documents or markup."),
                stub("markdown-to-pdf", "Markdown to PDF", "Render markdown into final PDF output."),
                stub("txt-to-pdf", "TXT to PDF", "Turn plain text files into PDF documents."),
                stub("rtf-to-pdf", "RTF to PDF", "Convert rich text files into PDF."),
                stub("odt-to-pdf", "ODT to PDF", "Convert OpenDocument text files into PDF."),
                stub("csv-to-pdf", "CSV to PDF", "Turn CSV tables into printable PDF layouts."),
                stub("json-to-pdf", "JSON to PDF", "Render structured JSON into PDF output."),
                stub("xml-to-pdf", "XML to PDF", "Transform XML inputs into PDF documents."),
                stub("svg-to-pdf", "SVG to PDF", "Convert SVG graphics into PDF output."),
                stub("epub-to-pdf", "EPUB to PDF", "Turn EPUB content into PDFs."),
                stub("mobi-to-pdf", "MOBI to PDF", "Convert MOBI ebooks into PDF."),
                stub("pdf-ocr", "PDF OCR", "Run OCR and produce searchable PDF output."),
            ],
        ),
        (
            "Sign & Security",
            [
                stub("sign-pdf", "Sign PDF", "Add signatures to PDF files cleanly."),
                stub("request-signatures", "Request Signatures", "Route documents for requested signatures."),
                stub("unlock-pdf", "Unlock PDF", "Remove access restrictions when allowed."),
                stub("protect-pdf", "Protect PDF", "Add protection layers to finished PDFs."),
                stub("flatten-pdf", "Flatten PDF", "Flatten annotations and interactive layers."),
                stub("pdf-scanner", "PDF Scanner", "Capture paper documents into PDF workflow."),
            ],
        ),
        (
            "AI PDF",
            [
                stub("ai-pdf-assistant", "AI PDF Assistant", "Use an assistant layer to work with PDF content."),
                stub("chat-with-pdf", "Chat with PDF", "Ask questions against a PDF in a conversational flow."),
                stub("ai-pdf-summarizer", "AI PDF Summarizer", "Generate summaries from PDF documents."),
                stub("translate-pdf", "Translate PDF", "Translate PDFs into additional languages."),
                stub("ai-question-generator", "AI Question Generator", "Generate questions or review prompts from PDF content."),
            ],
        ),
    ]


def _tool_lookup() -> Dict[str, Dict[str, str]]:
    lookup: Dict[str, Dict[str, str]] = {}
    for group, items in _tool_catalog():
        for item in items:
            lookup[item["slug"]] = {**item, "group": group}
    return lookup


def _tools_menu() -> str:
    group_markup = []
    for title, items_data in _tool_catalog():
        items = []
        for item in items_data:
            href = item["url"]
            items.append(
                "<a class='dropdown-item' "
                f"href='{href}'{_attrs(href)}>"
                f"<span class='dropdown-item__label'>{item['title']}</span>"
                f"<span class='dropdown-item__meta'>{item['status']}</span>"
                "</a>"
            )
        group_markup.append(
            "<div class='dropdown-group'>"
            f"<div class='dropdown-group__title'>{title}</div>"
            f"{''.join(items)}"
            "</div>"
        )
    return (
        "<details class='tools-menu'>"
        "<summary class='tools-summary nav-link'><span class='tools-summary__icon' aria-hidden='true'>"
        "<span></span><span></span><span></span>"
        "<span></span><span></span><span></span>"
        "<span></span><span></span><span></span>"
        "</span><span>Tools</span></summary>"
        "<div class='tools-dropdown'>"
        f"{''.join(group_markup)}"
        "</div>"
        "</details>"
    )


def _head(title: str, description: str, origin: str, path: str) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": APP_NAME,
        "description": description,
        "url": f"{origin}{path}",
        "creator": {"@type": "Person", "name": CREATOR_NAME, "url": CREATOR_SITE},
    }
    return f"""
    <meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>{title}</title><meta name='description' content='{description}'>
    <meta property='og:title' content='{title}'><meta property='og:description' content='{description}'><meta property='og:type' content='website'>
    <meta property='og:url' content='{origin}{path}'><meta property='og:image' content='{origin}/og-image.svg'>
    <meta name='twitter:card' content='summary_large_image'><meta name='twitter:title' content='{title}'><meta name='twitter:description' content='{description}'><meta name='twitter:image' content='{origin}/og-image.svg'>
    <link rel='icon' href='/icon.svg' type='image/svg+xml'><script type='application/ld+json'>{json.dumps(schema)}</script>
    """


def _css() -> str:
    return """
    :root{--bg:#f3f6fb;--surface:#ffffff;--surface-soft:#f7f9fc;--surface-tint:#eef4ff;--text:#0f172a;--muted:#617082;--line:#dde5ef;--line-strong:#cfd9e6;--accent:#155eef;--accent-dark:#174cd3;--accent-soft:#e8f0ff;--live:#155eef;--planned:#475467;--shadow:0 20px 54px rgba(15,23,42,.06);--shadow-soft:0 10px 24px rgba(15,23,42,.04);--pill:999px;--max:1240px}
    *{box-sizing:border-box} html{scroll-behavior:smooth} body{margin:0;font-family:Aptos,"Segoe UI",sans-serif;background:radial-gradient(circle at top,rgba(21,94,239,.06),transparent 30%),linear-gradient(180deg,#f8fafc 0%,#f3f6fb 100%);color:var(--text)} a{color:inherit}
    .page-shell{width:min(var(--max),calc(100% - 32px));margin:0 auto;padding:18px 0 40px}
    .topbar{display:flex;align-items:center;gap:18px;padding:10px 16px;background:rgba(255,255,255,.94);border:1px solid var(--line);border-radius:18px;position:sticky;top:10px;z-index:30;box-shadow:var(--shadow-soft);backdrop-filter:blur(12px)}
    .brand-lockup{display:inline-flex;align-items:center;gap:12px;text-decoration:none}.brand-lockup span{display:inline-flex;flex-direction:column}.brand-name{font-size:1.18rem;font-weight:700;line-height:1.1}.brand-kicker{color:var(--muted);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase}
    .site-nav{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-left:auto}
    .nav-link,.tools-summary{display:inline-flex;align-items:center;gap:8px;padding:14px 0 12px;border:0;border-bottom:2px solid transparent;border-radius:0;text-decoration:none;font-weight:600;color:var(--muted);background:transparent;transition:color .16s ease,border-color .16s ease;cursor:pointer}
    .nav-link:hover,.nav-link.active,.tools-menu[open] .tools-summary{color:var(--accent-dark);border-color:var(--accent-dark)}
    .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:11px 16px;border-radius:14px;text-decoration:none;font-weight:600;border:1px solid transparent;transition:background .16s ease,color .16s ease,border-color .16s ease,box-shadow .16s ease;cursor:pointer}
    .btn-secondary{background:var(--surface);border-color:var(--line-strong);color:var(--text)}.btn-primary{background:var(--accent);border-color:var(--accent);color:#fff}.btn-primary:hover{background:var(--accent-dark);border-color:var(--accent-dark)}.btn:hover{box-shadow:var(--shadow-soft)}
    .tools-menu{position:relative}.tools-summary{list-style:none}.tools-summary::-webkit-details-marker{display:none}
    .tools-summary__icon{display:grid;grid-template-columns:repeat(3,4px);gap:3px;align-items:center}.tools-summary__icon span{width:4px;height:4px;border-radius:99px;background:currentColor;display:block}
    .tools-dropdown{position:absolute;top:calc(100% + 16px);left:-12px;min-width:1100px;padding:22px 24px;background:var(--surface);border:1px solid var(--line);border-radius:24px;box-shadow:0 30px 80px rgba(15,23,42,.12);display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:22px}
    .dropdown-group{padding:2px}.dropdown-group__title{font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:8px}
    .dropdown-item{display:block;padding:7px 10px 7px 14px;border-radius:12px;text-decoration:none;margin-top:4px;position:relative}.dropdown-item:before{content:"";width:6px;height:6px;border-radius:99px;background:#9fb2cc;position:absolute;left:0;top:15px}.dropdown-item:hover{background:var(--surface-tint)}
    .dropdown-item__label{display:block;font-size:.94rem;font-weight:700;color:var(--text)}.dropdown-item__meta{display:block;margin-top:4px;font-size:.79rem;color:var(--muted)}
    .hero{margin-top:18px;padding:26px 28px 30px;background:linear-gradient(180deg,#ffffff 0%,#fbfcfe 100%);border:1px solid var(--line);border-radius:34px;box-shadow:var(--shadow);overflow:hidden}
    .hero-grid{display:block}
    .hero-copy-panel{padding:4px 4px 18px;max-width:720px}
    .eyebrow{display:inline-flex;align-items:center;gap:8px;color:var(--accent-dark);font-size:.76rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase}.eyebrow:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--accent)}
    h1,h2,h3{margin:0;letter-spacing:-.04em}.hero h1{margin-top:16px;font-size:clamp(3.1rem,6vw,5.2rem);line-height:.94;max-width:11ch}
    .hero-copy{margin:16px 0 0;max-width:44rem;color:var(--muted);font-size:1.04rem;line-height:1.72}
    .mindmap-card{position:relative;padding:22px 24px 24px;background:radial-gradient(circle at 50% 40%,rgba(21,94,239,.12),transparent 0%,transparent 28%),linear-gradient(180deg,#fdfefe 0%,#f5f8fc 100%);border:1px solid var(--line);border-radius:30px;min-height:720px;overflow:hidden}
    .mindmap-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:18px}
    .mindmap-heading{font-size:1rem;font-weight:700}.mindmap-subcopy{margin-top:6px;max-width:34rem;color:var(--muted);font-size:.95rem;line-height:1.62}
    .mindmap-legend{display:flex;flex-wrap:wrap;gap:8px}
    .mindmap-tag{display:inline-flex;align-items:center;gap:8px;padding:8px 10px;border:1px solid var(--line);border-radius:var(--pill);background:rgba(255,255,255,.88);font-size:.8rem;color:var(--muted);white-space:nowrap}
    .mindmap-tag:before{content:"";width:8px;height:8px;border-radius:50%}.mindmap-tag--live:before{background:var(--accent)}.mindmap-tag--planned:before{background:#98a2b3}
    .mindmap-canvas{position:relative;width:100%;min-height:660px}
    .mindmap-ring{position:absolute;left:50%;top:54%;transform:translate(-50%,-50%);border-radius:50%;border:1px dashed rgba(21,94,239,.14)}
    .mindmap-ring--outer{width:clamp(480px,58vw,640px);height:clamp(480px,58vw,640px)}.mindmap-ring--inner{width:clamp(250px,31vw,360px);height:clamp(250px,31vw,360px)}
    .mindmap-line{position:absolute;left:50%;top:54%;width:var(--radius);height:2px;transform-origin:0 50%;transform:rotate(var(--angle));background:linear-gradient(90deg,var(--tone),rgba(255,255,255,0));opacity:.4;border-radius:var(--pill)}
    .mindmap-core{position:absolute;left:50%;top:54%;width:270px;transform:translate(-50%,-50%);border-radius:34px;background:linear-gradient(180deg,rgba(255,255,255,.96) 0%,rgba(247,250,253,.92) 100%);border:1px solid var(--line-strong);box-shadow:0 30px 60px rgba(15,23,42,.10);text-align:center;padding:26px 24px}
    .mindmap-core strong{display:block;font-size:1.48rem;font-weight:700}.mindmap-core span{display:block;margin-top:8px;color:var(--muted);line-height:1.55;font-size:.93rem}
    .mindmap-node{position:absolute;left:50%;top:54%;width:182px;border-radius:20px;background:rgba(255,255,255,.98);border:1px solid rgba(15,23,42,.08);box-shadow:0 16px 34px rgba(15,23,42,.06);text-decoration:none;overflow:hidden;transform:translate(-50%,-50%) rotate(var(--angle)) translateX(var(--radius)) rotate(calc(-1 * var(--angle)));transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
    .mindmap-node:hover{transform:translate(-50%,-50%) rotate(var(--angle)) translateX(calc(var(--radius) + 8px)) rotate(calc(-1 * var(--angle)));box-shadow:0 22px 40px rgba(15,23,42,.09);border-color:rgba(15,23,42,.14)}
    .mindmap-node__bar{display:block;height:4px;background:var(--tone)}
    .mindmap-node__body{display:block;padding:14px 15px 16px}
    .mindmap-node__label{display:block;font-size:.71rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:8px}
    .mindmap-node__title{display:block;font-size:.98rem;font-weight:700;line-height:1.32}
    .mindmap-node__status{display:inline-flex;margin-top:10px;padding:6px 10px;border-radius:var(--pill);font-size:.76rem;font-weight:700}
    .mindmap-node--live .mindmap-node__status{background:var(--accent-soft);color:var(--live)}.mindmap-node--planned .mindmap-node__status{background:#eef2f6;color:var(--planned)}
    .site-footer{margin-top:18px;padding:20px 24px;background:var(--surface);border:1px solid var(--line);border-radius:22px;box-shadow:var(--shadow-soft)}.footer-row{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.footer-title{font-size:1.02rem;font-weight:700}.site-footer p,.footer-meta,.footer-links a{color:var(--muted);line-height:1.6}.footer-links{display:flex;flex-wrap:wrap;gap:16px}.footer-links a{text-decoration:none}.footer-links a:hover{color:var(--text)}.footer-meta{margin-top:16px;padding-top:16px;border-top:1px solid var(--line);font-size:.92rem}
    .legal-card{padding:34px;background:var(--surface);border:1px solid var(--line);border-radius:24px;box-shadow:var(--shadow);margin-top:18px}.legal-card h1{margin-top:16px;font-size:clamp(2.2rem,4vw,3.2rem)}.legal-card section{margin-top:24px}.legal-card p{color:var(--muted);line-height:1.72}
    .stub-card{margin-top:18px;padding:34px;background:linear-gradient(180deg,#ffffff 0%,#fbfcfe 100%);border:1px solid var(--line);border-radius:30px;box-shadow:var(--shadow)}
    .stub-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
    .stub-badge,.stub-group{display:inline-flex;align-items:center;padding:8px 12px;border-radius:var(--pill);font-size:.78rem;font-weight:700}
    .stub-badge{background:var(--accent-soft);color:var(--accent-dark)}
    .stub-group{background:var(--surface-soft);border:1px solid var(--line);color:var(--muted)}
    .stub-card h1{margin-top:18px;font-size:clamp(2.4rem,5vw,4rem);line-height:.96;max-width:12ch}
    .stub-copy{margin:16px 0 0;max-width:44rem;color:var(--muted);font-size:1.02rem;line-height:1.72}
    .stub-note{margin-top:22px;padding:18px 20px;border-radius:20px;background:var(--surface-soft);border:1px solid var(--line);color:var(--muted);line-height:1.68}
    .stub-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}
    @media (max-width:1260px){.tools-dropdown{min-width:920px;grid-template-columns:repeat(3,minmax(0,1fr))}}
    @media (max-width:1024px){.mindmap-card{min-height:auto}.mindmap-canvas{min-height:620px}.tools-dropdown{position:static;min-width:0;width:min(100vw - 48px,900px);margin-top:12px;grid-template-columns:repeat(2,minmax(0,1fr))}.footer-row{display:block}.footer-links{margin-top:16px}}
    @media (max-width:720px){.page-shell{width:min(var(--max),calc(100% - 18px))}.topbar{position:static;padding:14px;align-items:flex-start;flex-wrap:wrap}.site-nav{gap:14px}.nav-link{display:none}.tools-summary{display:inline-flex}.hero,.mindmap-card,.site-footer,.legal-card,.stub-card{padding:20px}.hero h1,.stub-card h1{max-width:100%}.mindmap-head{display:block}.mindmap-legend{margin-top:12px}.mindmap-canvas{min-height:540px}.mindmap-ring--outer{width:400px;height:400px}.mindmap-ring--inner{width:250px;height:250px}.mindmap-core{width:206px;padding:20px 16px}.mindmap-node{width:150px}.mindmap-node__body{padding:12px}.tools-dropdown{grid-template-columns:1fr;width:min(100vw - 36px,860px)}}
    """


def _legal(title: str, intro: str, sections: List[Tuple[str, List[str]]]) -> str:
    return (
        "<main><div class='legal-card'><div class='eyebrow'>Proofmark Studio Policy</div>"
        f"<h1>{title}</h1><p class='legal-intro'>{intro}</p>"
        + "".join(f"<section><h2>{h}</h2>{''.join(f'<p>{p}</p>' for p in ps)}</section>" for h, ps in sections)
        + "</div></main>"
    )


def _mind_map(spokes: List[Dict[str, str]]) -> str:
    lines = "".join(
        f"<span class='mindmap-line' style='--angle:{spoke['angle']}; --radius:{spoke['radius']}; --tone:{spoke['color']};'></span>"
        for spoke in spokes
    )
    nodes = []
    for spoke in spokes:
        nodes.append(
            f"<a class='mindmap-node mindmap-node--{spoke['tone']}' href='{spoke['url']}'{_attrs(spoke['url'])} style='--angle:{spoke['angle']}; --radius:{spoke['radius']}; --tone:{spoke['color']};'>"
            "<span class='mindmap-node__bar'></span>"
            "<span class='mindmap-node__body'>"
            f"<span class='mindmap-node__label'>{spoke['label']}</span>"
            f"<span class='mindmap-node__title'>{spoke['title']}</span>"
            f"<span class='mindmap-node__status'>{spoke['status']}</span>"
            "</span>"
            "</a>"
        )
    return (
        "<section class='mindmap-card' id='mind-map' aria-label='Proofmark Studio product map'>"
        "<div class='mindmap-head'>"
        "<div><div class='mindmap-heading'>Platform map</div><div class='mindmap-subcopy'>One wheel for the live Proofmark projects now and the next lanes that belong around them.</div></div>"
        "<div class='mindmap-legend'><span class='mindmap-tag mindmap-tag--live'>Live now</span><span class='mindmap-tag mindmap-tag--planned'>Planned</span></div>"
        "</div>"
        "<div class='mindmap-canvas'>"
        "<div class='mindmap-ring mindmap-ring--outer'></div>"
        "<div class='mindmap-ring mindmap-ring--inner'></div>"
        f"{lines}"
        "<div class='mindmap-core'><div><strong>Proofmark Studio</strong><span>The central map for the live projects and the next Proofmark lanes.</span></div></div>"
        f"{''.join(nodes)}"
        "</div>"
        "</section>"
    )


def _home_body() -> str:
    spokes = _studio_spokes()
    return (
        "<main id='maincontent'><section class='hero'><div class='hero-grid'><div class='hero-copy-panel'>"
        "<div class='eyebrow'>Proofmark Studio</div>"
        "<h1>The hub for the Proofmark product line.</h1>"
        "<p class='hero-copy'>Use the wheel to move through the live projects now and to see the next lanes clearly. The Tools menu stays at the top as the working index.</p>"
        "</div>"
        f"{_mind_map(spokes)}</div></section></main>"
    )


def _tool_stub_body(tool: Dict[str, str]) -> str:
    live_href = "/"
    live_label = "Back to Proofmark Studio"
    if tool["group"] == "Proofing":
        live_href = TEXT_STUDIO_ROUTE
        live_label = "Open Text Inspection"
    elif tool["group"] in {"Compress", "Organize", "View & Edit", "Convert from PDF", "Convert to PDF", "Sign & Security", "AI PDF"}:
        live_href = PROOFMARK_PDF_ROUTE
        live_label = "Open Proofmark PDF"

    return (
        "<main><section class='stub-card'>"
        "<div class='eyebrow'>Proofmark Studio</div>"
        "<div class='stub-meta'>"
        f"<span class='stub-group'>{tool['group']}</span>"
        f"<span class='stub-badge'>{tool['status']}</span>"
        "</div>"
        f"<h1>{tool['title']}</h1>"
        f"<p class='stub-copy'>{tool['summary']}</p>"
        "<div class='stub-note'>"
        "This route is reserved inside Proofmark Studio so the broader suite already has a clean product slot, path, and navigation model. "
        "The working implementation can land here without changing the hub structure later."
        "</div>"
        "<div class='stub-actions'>"
        "<a class='btn btn-primary' href='/'>Return to the hub</a>"
        f"<a class='btn btn-secondary' href='{live_href}'{_attrs(live_href)}>{live_label}</a>"
        "</div>"
        "</section></main>"
    )


def _page(active: str, title: str, description: str, body: str, origin: str, path: str) -> str:
    return f"<!doctype html><html lang='en'><head>{_head(title, description, origin, path)}<style>{_css()}</style></head><body><div class='page-shell'>{_nav(active)}{body}{_footer()}</div></body></html>"


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    origin = _safe_origin(request)
    return _page("home", f"{APP_NAME} | Hub page for the Proofmark product line", APP_DESCRIPTION, _home_body(), origin, "/")


@app.get("/tools/{slug}", response_class=HTMLResponse)
def tool_page(slug: str, request: Request):
    tool = _tool_lookup().get(slug)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool["url"] != f"/tools/{slug}":
        return RedirectResponse(url=tool["url"], status_code=307)
    origin = _safe_origin(request)
    description = f"{tool['title']} is a planned route inside Proofmark Studio."
    return _page("tools", f"{tool['title']} | {APP_NAME}", description, _tool_stub_body(tool), origin, f"/tools/{slug}")


@app.get(TEXT_STUDIO_ROUTE)
def go_text_inspection():
    return RedirectResponse(url=PROOFMARK_TEXT_STUDIO_URL, status_code=307)


@app.get(PROOFMARK_PDF_ROUTE)
def go_proofmark_pdf():
    return RedirectResponse(url=PROOFMARK_PDF_URL, status_code=307)


@app.get(PROOFMARK_SITE_ROUTE)
def go_proofmark_site():
    return RedirectResponse(url=PROOFMARK_SITE_URL, status_code=307)


@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    origin = _safe_origin(request)
    body = _legal(
        "Privacy Policy",
        "Proofmark Studio is currently a hub page that routes into tools and explains the wider product line. This build does not ask for accounts or store personal project data.",
        [
            ("What this hub stores", ["This version of Proofmark Studio does not offer sign-in, uploads, or persistent workspace storage.", "If you click through to linked tools, those tools govern how they handle your data and files."]),
            ("Destinations", ["Buttons on this page route you directly into local or deployed Proofmark tools.", "This hub does not embed or proxy those tools yet; you control those destinations through environment variables when you deploy or run the app locally."]),
            ("Contact", [f"For questions about this build, contact {CREATOR_NAME} through {CREATOR_SITE}, GitHub, or LinkedIn."]),
        ],
    )
    return _page("privacy", f"Privacy Policy | {APP_NAME}", "Privacy details for the Proofmark Studio hub.", body, origin, "/privacy")


@app.get("/terms", response_class=HTMLResponse)
def terms(request: Request):
    origin = _safe_origin(request)
    body = _legal(
        "Terms of Use",
        "Proofmark Studio is offered as a product hub and planning surface for the Proofmark ecosystem. Use it for lawful business and creative workflow work.",
        [
            ("Use of the service", ["You may use this hub to understand and access the Proofmark workflow.", "Do not misuse the service, automate abusive traffic, or represent this build as your own hosted product without written permission."]),
            ("Linked applications", ["Linked tools may be separate applications with their own behavior, limits, and policies.", "Always verify your final outputs before distributing them to clients or collaborators."]),
            ("Changes", ["This build is the start of Proofmark Studio and will evolve as new workflow lanes are added.", "Product scope, links, and capabilities may change without notice as the ecosystem grows."]),
        ],
    )
    return _page("terms", f"Terms of Use | {APP_NAME}", "Terms for using the Proofmark Studio hub.", body, origin, "/terms")


@app.get("/icon.svg")
def icon():
    return Response(content=_icon_svg(), media_type="image/svg+xml")


@app.get("/og-image.svg")
def og_image():
    return Response(content=_og_image_svg(), media_type="image/svg+xml")


@app.get("/robots.txt")
def robots_txt(request: Request):
    origin = _safe_origin(request)
    return Response(content=f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {origin}/sitemap.xml\n", media_type="text/plain")


@app.get("/sitemap.xml")
def sitemap_xml(request: Request):
    origin = _safe_origin(request)
    tool_paths = [item["url"] for item in _tool_lookup().values() if item["url"].startswith("/tools/")]
    tags = "".join(f"<url><loc>{origin}{path}</loc></url>" for path in ("/", "/privacy", "/terms", *tool_paths))
    return Response(content="<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>" + tags + "</urlset>", media_type="application/xml")


@app.get("/api/health")
def api_health():
    spokes = _studio_spokes()
    return JSONResponse({"status": "ok", "service": "proofmark-studio", "live_tools": sum(1 for s in spokes if s["tone"] == "live"), "planned_spokes": sum(1 for s in spokes if s["tone"] == "planned")})


@app.get("/api/studio-map")
def api_studio_map():
    return JSONResponse({"service": "proofmark-studio", "spokes": _studio_spokes()})


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _listening_pid(port: int) -> Optional[int]:
    if os.name != "nt":
        return None
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "$escapedPort = [regex]::Escape(':"
            + str(port)
            + "'); $pattern = '^\\s*TCP\\s+\\S+$escapedPort\\s+\\S+\\s+LISTENING\\s+(\\d+)\\s*$'; "
            "$line = netstat -ano -p tcp | Select-String -Pattern $pattern | Select-Object -First 1; "
            "if ($line) { $match = [regex]::Match($line.Line, $pattern); if ($match.Success) { $match.Groups[1].Value } }"
        ),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        raw = result.stdout.strip()
        return int(raw) if raw.isdigit() else None
    except Exception:
        return None


def _kill_port(port: int) -> bool:
    pid = _listening_pid(port)
    if not pid:
        return False
    try:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, capture_output=True)
        return True
    except Exception:
        return False


def _find_port(host: str, requested: int) -> int:
    seen = set()
    for port in (requested, *KNOWN_PORTS):
        if port in seen:
            continue
        seen.add(port)
        if not _port_in_use(host, port):
            return port
    for port in range(requested, requested + 25):
        if port in seen:
            continue
        if not _port_in_use(host, port):
            return port
    raise RuntimeError(f"Could not find an open port starting at {requested}.")


def _port_report(host: str = DEFAULT_HOST) -> str:
    return "\n".join(f"{host}:{port} - {'busy' if _port_in_use(host, port) else 'open'}" for port in KNOWN_PORTS)


def _smoke_test() -> int:
    page = _home_body()
    required = [APP_NAME, "Proofmark PDF", "Proofmark Text Inspection Studio", "The hub for the Proofmark product line."]
    missing = [item for item in required if item not in page]
    if missing:
        print("Smoke test failed. Missing:", ", ".join(missing))
        return 1
    print("Smoke test passed.")
    return 0


def _schedule_browser(url: str) -> None:
    Timer(0.8, lambda: webbrowser.open(url)).start()


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Run the {APP_NAME} web server.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--kill-port", action="store_true", help="Stop anything already listening on the requested port before starting.")
    parser.add_argument("--open-browser", action="store_true", help="Open the app in your browser after startup.")
    parser.add_argument("--list-ports", action="store_true", help="Print the status of common local dev ports and exit.")
    parser.add_argument("--smoke-test", action="store_true", help="Render the hub markup and validate the core sections.")
    args = parser.parse_args()

    if args.list_ports:
        print(_port_report(args.host))
        return 0
    if args.smoke_test:
        return _smoke_test()
    if args.kill_port and _port_in_use(args.host, args.port):
        _kill_port(args.port)
    selected = _find_port(args.host, args.port)
    if selected != args.port:
        print(f"Port {args.port} is busy. Starting on {selected} instead.")
    url = f"http://{args.host}:{selected}"
    if args.open_browser:
        _schedule_browser(url)
    print(f"{APP_NAME} running at {url}")
    uvicorn.run("web_app:app", host=args.host, port=selected, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
