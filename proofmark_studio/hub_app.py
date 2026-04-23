"""ProofMark Studio hub — thin FastAPI that serves the React SPA + orchestrates sibling tools.

Architecture note: the hub does NOT import PDF or text-cleaner. Sibling apps run as
independent FastAPI processes on their own ports; the hub just serves the catalog UI
and forwards clicks via redirects. See docs/architecture.md.
"""
from __future__ import annotations

import argparse
import os
import socket
import subprocess
import webbrowser
from pathlib import Path
from threading import Timer
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

try:  # pragma: no cover - env loading is best-effort
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from proofmark_studio import feature_flags as _flags
from proofmark_studio import tool_registry as _registry

# ─── Constants ────────────────────────────────────────────────────────────
APP_NAME = "ProofMark Studio"
APP_DESCRIPTION = "ProofMark Studio is the working hub for the ProofMark product line."
APP_KICKER = "Working hub"
CREATOR_NAME = "Sabbir Hossain"
CREATOR_SITE = os.environ.get("CREATOR_SITE", "https://sabbir.ca/")

# Sibling tool base URLs — overridable via env for prod (Vercel rewrites make these ""
# so paths become same-origin relative like /pdf/merge-pdf).
PROOFMARK_PDF_BASE = os.environ.get("PROOFMARK_PDF_BASE", "http://127.0.0.1:8010")
PROOFMARK_TEXT_BASE = os.environ.get("PROOFMARK_TEXT_BASE", "http://127.0.0.1:8000")
PROOFMARK_SITE_URL = os.environ.get("PROOFMARK_SITE_URL", CREATOR_SITE)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8020
# Fallback chain — avoids stepping on sibling ports (8000, 8010)
KNOWN_PORTS = (8020, 8021, 8022, 8030, 8040)

PACKAGE_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_ROOT / "static"
HUB_INDEX = STATIC_DIR / "hub" / "index.html"

# ─── FastAPI app ──────────────────────────────────────────────────────────
app = FastAPI(title=APP_NAME, description=APP_DESCRIPTION)

# CSP relaxed enough for React UMD + Babel standalone + Google Fonts.
# Tightening for prod happens in Phase 9 once the React hub is built to a static bundle.
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "object-src 'none'; base-uri 'self'; form-action 'self';"
    ),
}


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


# ─── Static assets (JSX + HTML + images) ──────────────────────────────────
# Mounted at /static so index.html references /static/hub/src/app.jsx etc.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ─── Routes ───────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def hub_index() -> FileResponse:
    """Serve the React SPA shell."""
    if not HUB_INDEX.exists():
        raise HTTPException(status_code=500, detail="Hub assets missing; reinstall required.")
    return FileResponse(str(HUB_INDEX), media_type="text/html")


@app.get("/go/proofmark-pdf", include_in_schema=False)
def go_pdf() -> RedirectResponse:
    return RedirectResponse(url=PROOFMARK_PDF_BASE, status_code=307)


@app.get("/go/text-inspection", include_in_schema=False)
def go_text() -> RedirectResponse:
    return RedirectResponse(url=PROOFMARK_TEXT_BASE, status_code=307)


@app.get("/go/proofmark-site", include_in_schema=False)
def go_site() -> RedirectResponse:
    return RedirectResponse(url=PROOFMARK_SITE_URL, status_code=307)


@app.get("/api/health")
def api_health() -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "service": "proofmark-studio",
        "hub_version": "0.4.0",
    })


@app.get("/api/studio-map")
def api_studio_map() -> JSONResponse:
    """Backward-compatible platform-map payload consumed by the React hub sidebar."""
    spokes = [
        {"id": "text", "title": "Text Inspection", "tone": "live", "url": "/go/text-inspection"},
        {"id": "pdf", "title": "ProofMark PDF", "tone": "live", "url": "/go/proofmark-pdf"},
        {"id": "tools", "title": "Document Suite", "tone": "planned"},
        {"id": "review", "title": "Review & QA", "tone": "planned"},
        {"id": "site", "title": "ProofMark Site", "tone": "live", "url": "/go/proofmark-site"},
        {"id": "ai", "title": "AI & Automation", "tone": "planned"},
    ]
    return JSONResponse({"service": "proofmark-studio", "spokes": spokes})


@app.get("/api/local-projects")
def api_local_projects() -> JSONResponse:
    """Project inventory — preserved for backward compat with pre-React callers."""
    projects = [
        {"slug": "proofmark-studio", "title": APP_NAME, "status": "hub"},
        {"slug": "proofmark-pdf", "title": "ProofMark PDF", "status": "live"},
        {"slug": "proofmark-text-inspection-studio", "title": "Text Inspection", "status": "live"},
    ]
    return JSONResponse({"service": "proofmark-studio", "projects": projects})


@app.get("/api/tools")
def api_tools() -> JSONResponse:
    """Runtime tool registry \u2014 React catalog merges this into its display metadata.
    Keeping URL+status server-side means the React catalog can't drift from reality.
    Per-tool env flags (TOOL_<SLUG>_ENABLED=false) demote the tile to 'planned'."""
    tools: Dict[str, Dict[str, object]] = {}
    counts = {"total": 0, "live": 0, "beta": 0, "planned": 0}
    for slug, t in _registry.TOOLS.items():
        entry: Dict[str, object] = {
            "status": t["status"], "parent": t["parent"], "url": t["url"],
            "title": t["title"], "group": t["group"],
        }
        if not _flags.is_enabled(slug):
            # Flag-demoted: hide the live URL and mark paused for the React catalog badge.
            entry["status"] = "planned"
            entry["paused"] = True
            entry["url"] = None
        tools[slug] = entry
        counts["total"] += 1
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    return JSONResponse({
        "service": "proofmark-studio",
        "tools": tools,
        "counts": counts,
    })


# ─── Tool router ─────────────────────────────────────────────────────────
@app.get("/tool/{slug}", response_class=HTMLResponse)
def tool_router(slug: str, request: Request):
    """Live tools redirect to sibling app. Beta/planned or flag-off \u2192 stub."""
    entry = _registry.TOOLS.get(slug)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {slug}")
    if entry["status"] == "live" and entry["url"] and _flags.is_enabled(slug):
        return RedirectResponse(url=entry["url"], status_code=307)
    # Beta, planned, or flag-demoted \u2192 stub page
    demoted = dict(entry)
    if not _flags.is_enabled(slug):
        demoted["status"] = "planned"
    return HTMLResponse(content=_render_stub(slug, demoted))


def _render_stub(slug: str, entry: Dict[str, object]) -> str:
    """Server-render the 'Return to hub / Open parent tool' stub matching tool-stub.png."""
    group_meta = _registry.GROUPS.get(entry["group"], {"label": entry["group"], "tone": "#7cb0ff"})
    parent = entry["parent"]
    parent_label = _registry.PARENT_LABELS.get(parent, "parent app") if parent else None
    parent_url = _registry.PARENT_URLS.get(parent) if parent else None
    status_label = {"beta": "Beta", "planned": "Planned"}.get(entry["status"], "Stub")
    tone = group_meta["tone"]

    open_btn = (
        f'<a class="btn btn-ghost" href="{parent_url}">Open {parent_label}</a>'
        if parent_url else ""
    )

    desc = entry["desc"]
    if entry["status"] == "beta":
        note = f"{entry['title']} is in beta. The working preview lives inside {parent_label or 'its parent app'}."
    else:
        note = (
            f"This slot is reserved inside ProofMark Studio so the hub already has a clean product slot "
            f"and navigation model. The working implementation can land here without reshaping the hub."
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{entry['title']} \u2014 {APP_NAME}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0a0a0b; --bg-elev: #111113; --bg-elev-2: #16161a;
      --border: #1f1f24; --border-strong: #2a2a31;
      --text: #f1f1f3; --text-muted: #8a8a94; --text-dim: #5e5e68;
      --accent: #7cb0ff; --accent-ink: #0a0a0b;
      --font-sans: 'Geist', system-ui, sans-serif;
      --font-serif: 'Instrument Serif', serif;
      --font-mono: 'Geist Mono', ui-monospace, monospace;
      --tone: {tone};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: var(--font-sans); background: var(--bg); color: var(--text); -webkit-font-smoothing: antialiased; }}
    a {{ color: inherit; text-decoration: none; }}
    .topbar {{ display: flex; align-items: center; gap: 22px; padding: 16px 28px; border-bottom: 1px solid var(--border); background: color-mix(in oklab, var(--bg) 90%, transparent); backdrop-filter: blur(14px); position: sticky; top: 0; z-index: 10; }}
    .brand {{ display: flex; align-items: center; gap: 10px; font-weight: 600; letter-spacing: -0.01em; }}
    .brand .dot {{ width: 28px; height: 28px; border-radius: 7px; background: var(--accent); color: var(--accent-ink); display: grid; place-items: center; font-weight: 800; }}
    .brand .tag {{ color: var(--text-dim); font-family: var(--font-mono); font-size: 10.5px; letter-spacing: 0.08em; text-transform: uppercase; }}
    .nav {{ margin-left: auto; display: flex; gap: 18px; font-size: 13px; color: var(--text-muted); }}
    .nav a:hover {{ color: var(--text); }}

    .main {{ max-width: 980px; margin: 0 auto; padding: 40px 32px 60px; }}
    .breadcrumb {{ display: flex; align-items: center; gap: 10px; font-family: var(--font-mono); font-size: 10.5px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 18px; }}
    .breadcrumb .dotsep {{ width: 3px; height: 3px; border-radius: 99px; background: var(--text-dim); }}
    .breadcrumb .group {{ color: var(--tone); }}

    .card {{ padding: 36px 36px 30px; border-radius: 20px; background: linear-gradient(180deg, color-mix(in oklab, var(--tone) 10%, var(--bg-elev)) 0%, var(--bg-elev) 100%); border: 1px solid color-mix(in oklab, var(--tone) 40%, var(--border)); box-shadow: 0 18px 50px rgba(0,0,0,0.35); }}
    .pill {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-size: 10.5px; font-weight: 700; font-family: var(--font-mono); letter-spacing: 0.08em; text-transform: uppercase; color: var(--tone); background: color-mix(in oklab, var(--tone) 14%, transparent); border: 1px solid color-mix(in oklab, var(--tone) 30%, transparent); }}
    h1 {{ font-family: var(--font-serif); font-weight: 400; font-size: clamp(40px, 5vw, 64px); line-height: 1; letter-spacing: -0.02em; margin: 18px 0 14px; }}
    .desc {{ font-size: 14.5px; line-height: 1.6; color: var(--text-muted); max-width: 54ch; margin: 0 0 24px; }}
    .note {{ font-size: 13.5px; line-height: 1.65; color: var(--text-muted); max-width: 60ch; margin: 0 0 28px; font-style: italic; }}
    .row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .btn {{ display: inline-flex; align-items: center; gap: 8px; padding: 11px 16px; border-radius: 11px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid transparent; transition: transform .15s, border-color .15s; }}
    .btn:hover {{ transform: translateY(-1px); }}
    .btn-primary {{ background: var(--accent); color: var(--accent-ink); }}
    .btn-ghost {{ background: var(--bg-elev-2); color: var(--text); border-color: var(--border-strong); }}

    .footer {{ max-width: 980px; margin: 60px auto 0; padding: 24px 32px 40px; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 12.5px; display: flex; gap: 18px; flex-wrap: wrap; }}
    .footer a:hover {{ color: var(--text); }}
  </style>
</head>
<body>
  <header class="topbar">
    <a href="/" class="brand"><span class="dot">\u25C7</span><span>ProofMark<br><span class="tag">Studio \u00b7 Working hub</span></span></a>
    <nav class="nav">
      <a href="/">Studio</a>
      <a href="/#tools">Tools</a>
      <a href="/go/text-inspection">Text Inspection</a>
      <a href="/go/proofmark-pdf">ProofMark PDF</a>
      <a href="/go/proofmark-site">ProofMark site</a>
    </nav>
  </header>

  <main class="main">
    <div class="breadcrumb">
      <span>PROOFMARK STUDIO</span>
      <span class="dotsep"></span>
      <span class="group">{group_meta['label']}</span>
      <span class="dotsep"></span>
      <span>{status_label}</span>
    </div>

    <section class="card">
      <span class="pill">{status_label}</span>
      <h1>{entry['title']}</h1>
      <p class="desc">{desc}</p>
      <p class="note">{note}</p>
      <div class="row">
        <a class="btn btn-primary" href="/">Return to the hub</a>
        {open_btn}
      </div>
    </section>
  </main>

  <footer class="footer">
    <span>ProofMark Studio</span>
    <span style="margin-left:auto">/tool/{slug}</span>
    <a href="/privacy">Privacy</a>
    <a href="/terms">Terms</a>
  </footer>
</body>
</html>"""


# ─── Minimal legacy pages ────────────────────────────────────────────────
# Kept as thin server-rendered HTML. Replaced by in-SPA views in a later phase.
def _minimal_page(title: str, body_html: str) -> HTMLResponse:
    html = (
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{title} · {APP_NAME}</title>"
        f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<style>body{{font-family:system-ui,sans-serif;max-width:720px;margin:3rem auto;padding:0 1rem;"
        f"color:#18181b;line-height:1.6}}a{{color:#1e4fd6}}</style></head>"
        f"<body><p><a href='/'>\u2190 ProofMark Studio</a></p><h1>{title}</h1>{body_html}</body></html>"
    )
    return HTMLResponse(content=html)


@app.get("/privacy", response_class=HTMLResponse)
def privacy() -> HTMLResponse:
    return _minimal_page("Privacy Policy", "<p>ProofMark Studio runs locally in your browser and does not collect personal data. Files you process stay on your machine unless you explicitly export them.</p>")


@app.get("/terms", response_class=HTMLResponse)
def terms() -> HTMLResponse:
    return _minimal_page("Terms of Use", "<p>ProofMark Studio is provided as-is for document work. You are responsible for the content you process. No warranty, no guarantees \u2014 you own the results.</p>")


@app.get("/local-projects", response_class=HTMLResponse)
def local_projects_page() -> HTMLResponse:
    body = (
        "<p>Local project inventory \u2014 the apps composing ProofMark Studio on your machine.</p>"
        "<ul>"
        "<li><strong>ProofMark Studio</strong> \u2014 hub (:8020)</li>"
        "<li><a href='/go/proofmark-pdf'>ProofMark PDF</a> \u2014 merge/split/extract (:8010)</li>"
        "<li><a href='/go/text-inspection'>Text Inspection</a> \u2014 hidden chars, whitespace, typography (:8000)</li>"
        "</ul>"
    )
    return _minimal_page("Local project inventory", body)


@app.get("/robots.txt", response_class=Response)
def robots(request: Request) -> Response:
    origin = str(request.base_url).rstrip("/")
    body = f"User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: {origin}/sitemap.xml\n"
    return Response(content=body, media_type="text/plain")


@app.get("/sitemap.xml", response_class=Response)
def sitemap(request: Request) -> Response:
    origin = str(request.base_url).rstrip("/")
    urls = ["/", "/privacy", "/terms", "/local-projects"]
    tags = "".join(f"<url><loc>{origin}{u}</loc></url>" for u in urls)
    body = (
        "<?xml version='1.0' encoding='UTF-8'?>"
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>" + tags + "</urlset>"
    )
    return Response(content=body, media_type="application/xml")


# ─── Port selection + launcher (preserved from pre-React hub) ─────────────
def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _find_port(host: str, requested: int) -> int:
    seen: set[int] = set()
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


def _listening_pid(port: int) -> Optional[int]:
    if os.name != "nt":
        return None
    cmd = [
        "powershell", "-NoProfile", "-Command",
        f"(Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue | "
        f"Select-Object -First 1 -ExpandProperty OwningProcess) 2>$null",
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


def _schedule_browser(url: str) -> None:
    Timer(0.8, lambda: webbrowser.open(url)).start()


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Run the {APP_NAME} hub.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--kill-port", action="store_true",
                        help="Stop anything listening on the requested port before starting.")
    parser.add_argument("--open-browser", action="store_true",
                        help="Open the hub in your browser after startup.")
    args = parser.parse_args()

    if args.kill_port and _port_in_use(args.host, args.port):
        _kill_port(args.port)
    selected = _find_port(args.host, args.port)
    if selected != args.port:
        print(f"Port {args.port} busy. Starting on {selected} instead.")
    url = f"http://{args.host}:{selected}"
    if args.open_browser:
        _schedule_browser(url)
    print(f"{APP_NAME} running at {url}")
    uvicorn.run("web_app:app", host=args.host, port=selected, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
