# Proofmark Studio

Proofmark Studio is the central hub for the Proofmark product line. It is designed to make the whole document workflow understandable at a glance: where text gets inspected, where PDFs get assembled, what already exists, and what comes next.

This repo intentionally follows the same overall approach as `proofmark-pdf`:

- a single-file FastAPI app for easy deployment
- premium SaaS-style inline HTML, CSS, and JavaScript
- local launch scripts that manage ports, preflight checks, and browser opening

## What is in this first version

- A polished Proofmark Studio hub page with a radial "spokes on a wheel" studio map
- Live launch cards for:
  - Proofmark Text Inspection Studio
  - Proofmark PDF
- A clear workflow story so anyone landing on the page can understand the current system and the roadmap
- Supporting routes for health, policies, sitemap, and robots

## Linked app URLs

The hub reads these environment variables when you want the buttons to point at deployed or custom local URLs:

- `PROOFMARK_TEXT_STUDIO_URL`
- `PROOFMARK_PDF_URL`
- `PROOFMARK_SITE_URL`
- `CREATOR_SITE`

Defaults are included in [.env.example](.env.example).

## Install

```bash
cd C:\Users\sabbir\Dev\GitHub\tools\proofmark-studio
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

## Run locally

```bash
python run.py
```

Useful variants:

```bash
python run.py --open-browser
python web_app.py --list-ports
pwsh -File .\scripts\launch-local.ps1 start -Detached
pwsh -File .\scripts\launch-local.ps1 status
```

The launcher defaults to `http://127.0.0.1:8020` and will fall forward to another open port if needed.

## Test

```bash
pwsh -File .\run_tests.ps1
```

## Deploy

`vercel.json` is configured for a single-file FastAPI entry point, matching the pattern used in `proofmark-pdf`.
