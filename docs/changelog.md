# Changelog

Release notes and tool-promotion history. Dates follow the commit order on `main`.

## Phase 18 — polish + SEO (in progress)

- Dynamic **OpenGraph cards** at `/og/<slug>.png` — 1200×630 PNGs rendered with the brand fonts (Instrument Serif + Geist), group color tints the accent stripe and status pill, in-process LRU cache plus HTTP `Cache-Control` for crawler-friendly serving. Tool stub pages and the markdown content pages now reference their own OG image so social shares look like a real product.
- Catalog is now **live-only by default**. Beta and planned tiles stay in the registry for the roadmap but are hidden from every user-facing surface: catalog, sitemap, command palette, pinned/workflow views, and the `/tool/{slug}` router. Roadmap mode (`PROOFMARK_SHOW_ALL_TILES=true`) restores the full catalog for local dev and plan review.
- Sitemap enumerates every displayed tool, respecting feature flags and the display mode.
- Tool stub pages carry `meta description`, OpenGraph, and Twitter card tags so social shares aren't naked.
- `/about` and `/changelog` pages render from first-party Markdown via a tiny safe `markdown_lite` module — no new dependency added.
- `?` key opens a keyboard-shortcuts cheat-sheet that documents every binding the hub registers.
- 404 and 500 pages render chrome-matched HTML for humans; `/api` and `/static` keep the JSON error contract for programmatic callers.

Still blocked on Phase 17 infra (database + auth): Stripe plans, usage tracking, and the dashboard.

## Phase 16 — AI family (complete)

- Promoted `ai-pdf-assistant`, `chat-with-pdf`, `ai-pdf-summarizer`, and `translate-pdf` to live.

## Phase 15 — Sign & Secure (complete)

- Promoted `sign-pdf`, `unlock-pdf`, `protect-pdf`, and `flatten-pdf` to live.
- `request-signatures` stays beta pending signer-routing infra.

## Phase 14 — View & Edit (complete)

- Promoted `crop-pdf`, `watermark-pdf`, `redact-pdf`, and `pdf-form-filler` to live.
- `pdf-reader` and `edit-pdf` stay beta.

## Phase 13 — Convert to PDF (complete)

- Promoted `jpg-to-pdf`, `html-to-pdf`, `markdown-to-pdf`, and `pdf-ocr` to live.
- Office converters (`word-to-pdf`, `excel-to-pdf`, `ppt-to-pdf`) stay beta — they require a self-hosted LibreOffice runtime.

## Phase 12 — Convert from PDF (complete)

- Promoted `pdf-to-text`, `pdf-to-jpg`, `pdf-to-png`, `pdf-to-markdown`, and `pdf-to-html` to live.

## Phase 11 — Organize family (complete)

- Promoted `compress-pdf`, `rotate-pdf`, `delete-pdf-pages`, `number-pages`, and `organize-pdf` to live.

## Phase 10 — Shared foundation (complete)

- Feature-flag module, `/api/tools` respects flags, tool-registry slug index, observability baseline, and the _Adding a tool_ recipe.
