# Changelog

Release notes and tool-promotion history. Dates follow the commit order on `main`.

## Phase 18 — polish + SEO (in progress)

- Sitemap now enumerates every live and beta tool, respecting feature flags.
- Tool stub pages carry `meta description`, OpenGraph, and Twitter card tags so social shares aren't naked.
- `/about` and `/changelog` pages render from first-party Markdown.

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
