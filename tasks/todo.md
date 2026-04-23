# ProofMark Studio — Master TODO

> **Next-chat start here.** Read this file top-to-bottom, then open the full plan at
> `C:\Users\sabbir\.claude\plans\proofmark-studio-tool-buildout.md` for per-step
> acceptance criteria. Work unchecked items in order. Check off as you complete.

---

## 📍 Where we are

**Done (Phases 0–9):** consolidation + React hub + StudioCanvas art + tool router +
stub pages + multi-process launcher + 49-tool registry + Vercel deploy with SmallPDF-style
rewrites. **173 tests pass** across 3 sibling apps.

**Live hub URL (Vercel prod):**
https://proofmark-studio-ij7v4i8xk-sabbirs-projects-eab46ba9.vercel.app/

**GitHub remotes:**
- hub: https://github.com/itsSabbir/proofmark-studio
- pdf: https://github.com/itsSabbir/proofmark-pdf
- text: https://github.com/itsSabbir/text-remover

**Local paths:**
- `C:\Users\sabbir\Dev\GitHub\tools\proofmark-studio` (hub)
- `C:\Users\sabbir\Dev\GitHub\tools\proofmark-pdf` (sibling)
- `C:\Users\sabbir\Dev\GitHub\tools\text-cleaner` (sibling)

**Currently: 36 tools live, 8 beta, 5 planned.**

**Catalog display policy:** live-only by default — users only see tiles that
work end-to-end. Beta + planned tiles stay registered for the roadmap but
are hidden from every user-facing surface. Flip `PROOFMARK_SHOW_ALL_TILES=true`
for local dev / plan review to restore the full catalog. See
`docs/feature-flags.md#catalog-display-mode`.

---

## 🔁 Session resume checklist (run this once per fresh chat)

Ensure the stack still works before touching anything new.

- [ ] Open a PowerShell in `proofmark-studio/`.
- [ ] Run `.\run-all.cmd` — hub on :8020, pdf on :8010, text on :8000 should all be READY within 6s.
- [ ] Visit http://127.0.0.1:8020/ — React SPA loads, art background visible, no grid.
- [ ] pytest each repo:
      `cd proofmark-studio && .venv\Scripts\python -m pytest`   → 17 pass
      `cd ..\proofmark-pdf && .venv\Scripts\python -m pytest`   → 87 pass
      `cd ..\text-cleaner  && .venv\Scripts\python -m pytest`   → 69 pass
- [ ] Ctrl+C the launcher → all three ports freed.
- [ ] `git status` in each repo → clean working tree.
- [ ] Confirm Vercel CLI: `vercel whoami` → `itssabbir`.
- [ ] Hit the live hub in a browser: `/`, `/tool/merge-pdf` (should redirect to `/pdf/merge-pdf`), `/tool/sign-pdf` (should render stub).

If any check fails, **stop and fix before proceeding.** Don't build new tools on a broken foundation.

---

## 🏗️ Phase 10 — Shared foundation (1 week) ⟵ BLOCKS everything after

### 10.1 ToolService protocol + Result type (½ day)
- [ ] Write failing test `apps/proofmark-pdf/tests/test_tool_service_protocol.py` asserting imports work + shape
- [ ] Create `apps/proofmark-pdf/proofmark_pdf/tool_services/__init__.py`
- [ ] Define `ToolService` Protocol with `slug`, `describe()`, `validate()`, `run()`
- [ ] Define `ToolMeta` dataclass
- [ ] Define `Result = Union[Ok, Err]` (`Ok` carries payload; `Err` carries `code`, `reason`, optional `**ctx`)
- [ ] `mypy --strict` clean on the new file
- [ ] Commit: `feat(foundation): ToolService protocol + Result type`

### 10.2 Shared test fixtures (½ day)
- [ ] Create `apps/proofmark-pdf/tests/fixtures/` directory
- [ ] Add `tiny.pdf` (1 page, text only)
- [ ] Add `multipage.pdf` (10 pages, mixed content)
- [ ] Add `password.pdf` (password = "test")
- [ ] Add `scanned.pdf` (no text layer, images only)
- [ ] Add `broken.pdf` (corrupt header)
- [ ] Add `form.pdf` (AcroForm with named fields)
- [ ] Create `conftest.py` exposing each as a pytest fixture
- [ ] Write `test_fixtures_sanity.py` asserting each opens and has expected properties
- [ ] Commit: `feat(foundation): shared PDF test fixtures`

### 10.3 Feature flag module (½ day)
- [ ] Write failing test `test_feature_flags.py`: `is_enabled("merge-pdf")` returns True by default, False when env is `"false"`/`"0"`/`"off"`
- [ ] Implement `apps/proofmark-pdf/proofmark_pdf/feature_flags.py`
- [ ] Duplicate (lightweight copy) into `proofmark-studio/proofmark_studio/feature_flags.py`
- [ ] Document every tool slug → flag name mapping in `docs/feature-flags.md`
- [ ] Commit: `feat(foundation): feature-flag module`

### 10.4 Structured-return + error taxonomy (½ day)
- [ ] Write failing test `test_errors.py` for each error code's JSON shape
- [ ] Create `common/result.py` (copied per-repo since no shared package yet)
- [ ] Create `common/errors.py` with `ErrorCode` enum: `INVALID_PDF`, `PDF_PASSWORD_REQUIRED`, `PDF_PASSWORD_WRONG`, `PDF_TOO_LARGE`, `INVALID_PAGE_RANGE`, `OCR_UNAVAILABLE`, `CONVERT_FAILED`, `LLM_UNAVAILABLE`, `RATE_LIMITED`, `TOOL_DISABLED`
- [ ] Each code has `user_message` + `mitigation_hint` attributes
- [ ] Commit: `feat(foundation): Result type + error taxonomy`

### 10.5 /api/tools merges runtime flags (½ day)
- [ ] Write failing test `test_api_tools_respects_flags.py`: set `TOOL_MERGE_PDF_ENABLED=false`, hit `/api/tools`, assert `tools["merge-pdf"].status == "planned"`
- [ ] Update `proofmark_studio/hub_app.py`: `/api/tools` handler reads feature flags and downgrades status
- [ ] Update `static/hub/src/app.jsx` or `tools.jsx`: show "paused" micro-badge on tiles whose status was flag-downgraded
- [ ] Smoke: flip merge-pdf flag → hub tile becomes "paused" → flip back → reverts
- [ ] Commit: `feat(hub): /api/tools respects feature flags`

### 10.6 Refactor existing 8 live tools to ToolService (2 days)
- [ ] merge-pdf → `tool_services/merge_pdf.py`, tests still green. Commit: `refactor(merge-pdf): migrate to ToolService`
- [ ] split-pdf → `tool_services/split_pdf.py`. Commit.
- [ ] extract-pdf-pages → `tool_services/extract_pdf_pages.py`. Commit.
- [ ] text-inspection → `tool_services/text_inspection.py` (in text-cleaner). Commit.
- [ ] inspect-hidden → `tool_services/inspect_hidden.py`. Commit.
- [ ] normalize-whitespace → `tool_services/normalize_whitespace.py`. Commit.
- [ ] review-typography → `tool_services/review_typography.py`. Commit.
- [ ] export-cleanup-report → `tool_services/export_cleanup_report.py`. Commit.

### 10.7 Generic contract test (½ day)
- [ ] Write `apps/proofmark-pdf/tests/test_tool_contract.py` that iterates all registered tools and asserts `ToolService` conformance
- [ ] Same for text-cleaner
- [ ] Verify CI fails if a new tool doesn't conform (intentionally break and re-fix)
- [ ] Commit: `test(foundation): generic tool-contract test`

### 10.8 Observability baseline (½ day)
- [ ] Add `[tool:<slug>]` log helper in `common/logging.py`
- [ ] Every `ToolService.run()` emits start + end log with `{inputs, context, strategy, outcome, durationMs}`
- [ ] Smoke: run merge-pdf → see 2 structured log lines
- [ ] Commit: `feat(foundation): per-tool observability baseline`

### 10.9 Docs + phase review (½ day)
- [ ] Update `docs/adding-a-tool.md` with ToolService + flag steps
- [ ] Write `docs/observability.md`
- [ ] Tag milestone: `git tag phase-10-complete && git push --tags`

### Phase 10 exit gate
- [ ] All 8 live tools use `ToolService`
- [ ] Adding a tool = touches ≤3 files (service, test, registry) + 1 env-var doc line
- [ ] `TOOL_MERGE_PDF_ENABLED=false` instantly demotes the tile
- [ ] Test count up from 173 → ~190

---

## 🧰 Phase 11 — Organize family (1 week)

### 11.1 compress-pdf (2 days)
- [ ] 11.1.1 Failing tests: compression ratio ≥ 20%, lossy/lossless toggle, protected → error
- [ ] 11.1.2 Service: pypdf content-stream compression + Pillow image downsample
- [ ] 11.1.3 API `POST /api/compress-pdf` + UI `/compress-pdf` with drag-drop + lossy radio
- [ ] 11.1.4 Promote in `tool_registry.py` (status=live, path=`/compress-pdf`). Smoke 3 real PDFs. Commit: `feat(compress-pdf): live`

### 11.2 rotate-pdf (1 day)
- [ ] 11.2.1 Failing tests: 90/180/270, per-page vs all-pages, rotation attribute check
- [ ] 11.2.2 Service + API + UI (small tool, one commit OK)
- [ ] 11.2.3 Promote + smoke. Commit: `feat(rotate-pdf): live`

### 11.3 delete-pdf-pages (1 day)
- [ ] 11.3.1 Failing tests: single page, range `3-7`, comma `1,4,9`, out-of-bounds → `INVALID_PAGE_RANGE`
- [ ] 11.3.2 Service + API + UI with range parser
- [ ] 11.3.3 Promote. Commit: `feat(delete-pdf-pages): live`

### 11.4 number-pages (1 day)
- [ ] 11.4.1 Failing tests: footer positions, `Page {n} of {total}` format, roman numerals, start-at-N
- [ ] 11.4.2 Service: pypdf + reportlab overlay
- [ ] 11.4.3 UI options panel + promote. Commit

### 11.5 organize-pdf — promote from beta (1 day)
- [ ] 11.5.1 Audit current beta impl; write missing tests (drag-reorder determinism, preview correctness)
- [ ] 11.5.2 Polish + wire through `ToolService`
- [ ] 11.5.3 Promote. Commit: `feat(organize-pdf): promoted to live`

### 11.6 Phase review + redeploy (½ day)
- [ ] All three test suites green; ≥195 total tests
- [ ] Deploy proofmark-pdf to Vercel
- [ ] Hit each new tool via prod hub URL
- [ ] Tag: `git tag phase-11-complete && git push --tags`

### Phase 11 exit gate
- [ ] 13 live tools total
- [ ] Every new tool has `TOOL_<SLUG>_ENABLED` flag tested

---

## 📤 Phase 12 — Convert-from-PDF (2 weeks)

### 12.1 Shared extraction module (2 days)
- [ ] 12.1.1 Failing test `test_extraction.py` with golden outputs per fixture
- [ ] 12.1.2 `proofmark_pdf/extraction.py` with `extract_pages(bytes) → list[Page]`
- [ ] 12.1.3 Integration test: all 5 downstream tools emit consistent content from same input
- [ ] Commit: `feat(extraction): shared page-extraction pipeline`

### 12.2 pdf-to-text (1 day)
- [ ] 12.2.1 Tests: encoding cases, special chars, multi-page concat
- [ ] 12.2.2 Service + API + UI
- [ ] 12.2.3 Promote. Commit

### 12.3 pdf-to-jpg — promote from beta (1 day)
- [ ] 12.3.1 Audit beta; tests for DPI, quality, multi-page → zip
- [ ] 12.3.2 Align with ToolService + extraction
- [ ] 12.3.3 Promote. Commit

### 12.4 pdf-to-png (½ day)
- [ ] 12.4.1 Tests
- [ ] 12.4.2 Service + API + UI (shares jpg path)
- [ ] Commit

### 12.5 pdf-to-markdown (2 days)
- [ ] 12.5.1 Tests: heading detection, lists, links, table → md-table
- [ ] 12.5.2 Service: pypdf + heuristics, new `markdown_conversion.py`
- [ ] 12.5.3 UI + promote

### 12.6 pdf-to-html (2 days)
- [ ] 12.6.1 Tests: structured output, CSS preservation, links
- [ ] 12.6.2 Service: pdfminer.six → structured HTML emit
- [ ] 12.6.3 UI + promote

### 12.7 Phase review (½ day)
- [ ] 5 new live; extraction shared; `test_extraction_pipeline.py` consistency check
- [ ] Tag: `phase-12-complete`

### Phase 12 exit gate
- [ ] 18 live tools, tests ≥210

---

## 📥 Phase 13 — Convert-to-PDF (2 weeks; Office tools stay beta on Vercel)

### 13.1 Shared converter module (1 day)
- [ ] 13.1.1 Tests with fixture inputs per source type
- [ ] 13.1.2 `proofmark_pdf/converters.py`: `convert(bytes, source_type) → pdf_bytes`
- [ ] 13.1.3 Tmpfile lifecycle + cleanup-on-error guaranteed
- [ ] Commit

### 13.2 jpg-to-pdf (½ day)
- [ ] Tests: single, multi-image, aspect, orientation
- [ ] Service + API + UI (Pillow + pypdf). Promote. Commit

### 13.3 markdown-to-pdf (1 day)
- [ ] Tests: headings, lists, code blocks, YAML front-matter
- [ ] Service: markdown-it + weasyprint
- [ ] UI + promote

### 13.4 html-to-pdf (1 day)
- [ ] Tests: inline/external CSS, images, page breaks
- [ ] Service: weasyprint
- [ ] UI + promote

### 13.5 pdf-ocr (2 days)
- [ ] Tests: scanned fixture → searchable text layer
- [ ] Service: ocrmypdf wrapper, multi-language
- [ ] Runtime warning if tesseract missing
- [ ] UI + promote

### 13.6 word-to-pdf (beta — 1 day)
- [ ] Tests (skip on Vercel where LO missing)
- [ ] Service: LibreOffice subprocess
- [ ] UI banner "requires self-host"; status stays `beta`
- [ ] Route returns `CONVERT_UNAVAILABLE` when `soffice` missing

### 13.7 excel-to-pdf + ppt-to-pdf (beta — 1 day)
- [ ] Same pattern as 13.6; both stay `beta`

### 13.8 Phase review (½ day)
- [ ] 4 live (jpg, md, html, ocr) + 3 beta
- [ ] Tag: `phase-13-complete`

### Phase 13 exit gate
- [ ] 22 live, tests ≥225
- [ ] Office beta tiles have explicit "self-host" messaging

---

## 🎨 Phase 14 — View & Edit (3 weeks)

### 14.1 PDF.js editor shell (2 days)
- [ ] Scaffold `apps/proofmark-pdf/proofmark_pdf/static/editor/` — React 18 + PDF.js, no build step
- [ ] Render PDF with thumbnails + zoom
- [ ] Hook: load PDF from `/api/pdf-load?id=...`

### 14.2 pdf-reader (2 days)
- [ ] Tests: render correctness (canvas pixel sampling or DOM-based)
- [ ] Features: zoom, fit-width, page-jump, search, TOC
- [ ] UI page + promote

### 14.3 pdf-annotator — promote from beta (3 days)
- [ ] Audit beta; tests for highlight, sticky note, rect tool
- [ ] Implement missing tool modes using PDF.js annotation layer
- [ ] Persist as real PDF annotations via pypdf
- [ ] UI polish + promote

### 14.4 crop-pdf (1 day)
- [ ] Tests: crop box → output page dimensions match
- [ ] Service (pypdf `crop_box`) + interactive canvas in UI
- [ ] Promote

### 14.5 watermark-pdf (1 day)
- [ ] Tests: text overlay visible on every page, rotate correctly
- [ ] Service: pypdf + reportlab overlay
- [ ] UI: text input + image upload + opacity/rotate

### 14.6 redact-pdf (2 days) ⚠️ DANGER ZONE
- [ ] Tests: search matches → black boxes **AND** underlying text actually removed (read-back with pypdf should NOT find redacted text)
- [ ] Service: pypdf content-stream rewrite; drop text operators within box regions
- [ ] UI: prominent "cannot be undone" warning + preview + explicit "I understand" checkbox

### 14.7 pdf-form-filler (2 days)
- [ ] Tests: AcroForm parse, field fill, flatten
- [ ] Service: pypdf form handling
- [ ] UI: auto-generate form fields from schema

### 14.8 edit-pdf — defer as beta (½ day)
- [ ] Document as beta with "inline editing requires desktop app" stub messaging
- [ ] Commit as explicit beta with roadmap note

### 14.9 Phase review (½ day)
- [ ] 6 live (reader, annotator, crop, watermark, redact, form-filler). edit-pdf beta
- [ ] Tag: `phase-14-complete`

### Phase 14 exit gate
- [ ] 28 live, tests ≥250
- [ ] Redact "irreversible" warning flow tested

---

## 🔐 Phase 15 — Sign & Secure (2 weeks)

### 15.1 unlock-pdf (1 day)
- [ ] Tests: protected fixture → unlocked; wrong password → `PDF_PASSWORD_WRONG`
- [ ] Service: pypdf decrypt
- [ ] UI + promote

### 15.2 protect-pdf (1 day)
- [ ] Tests: encrypt + permission flags (print, copy, modify); AES-256
- [ ] Service: pypdf encrypt with `PermissionsFlag`
- [ ] UI: password + permission checkboxes + promote

### 15.3 flatten-pdf (1 day)
- [ ] Tests: flatten annotations + form fields; opens in any PDF reader
- [ ] Service + UI + promote

### 15.4 sign-pdf — visual mode (2 days)
- [ ] Tests: signature image overlay at page/coordinate
- [ ] Service: drawing (data URL) or typed name → rendered → pypdf overlay
- [ ] UI: canvas drawing pad + placement preview + promote

### 15.5 sign-pdf — digital mode (beta — 2 days)
- [ ] Tests: pyHanko sign + verify
- [ ] Service: pyHanko; requires user cert
- [ ] UI: upload cert, verify, stays beta

### 15.6 request-signatures — defer as beta (½ day)
- [ ] Stub messaging + roadmap note

### 15.7 Phase review (½ day)
- [ ] 4 live + 2 beta; tag `phase-15-complete`

### Phase 15 exit gate
- [ ] 32 live, tests ≥270

---

## 🤖 Phase 16 — AI family (3 weeks)

### 16.1 LLM service layer (2 days)
- [ ] Tests: Anthropic SDK wrapper, prompt-cache hit/miss tracking
- [ ] `proofmark_pdf/llm.py`: `complete(prompt, cache_key)` with prompt caching
- [ ] Rate-limit middleware: per-IP + per-day
- [ ] Commit

### 16.2 ai-pdf-summarizer — promote from beta (2 days)
- [ ] Tests: summary length correlates; factual accuracy sampled vs golden
- [ ] Service: extract → Claude with `prompts/summarize_v1.md`
- [ ] UI: summary-length selector + promote

### 16.3 chat-with-pdf — promote from beta (4 days)
- [ ] Tests: retrieval quality (top-k relevant chunks for known questions)
- [ ] RAG: extract → chunk (with overlap) → embed → FAISS (in-memory)
- [ ] Chat loop: question → retrieve → Claude → stream
- [ ] UI: chat pane + citation chips that jump to source page. Promote

### 16.4 ai-pdf-assistant — promote from beta (2 days)
- [ ] Tests: multi-turn memory, tool-use (rerun, cite)
- [ ] Service: wrapper over chat-with-pdf with tool-use definitions
- [ ] UI: assistant pane + promote

### 16.5 translate-pdf (3 days)
- [ ] Tests: extract → translate → layout-preserved reinsert
- [ ] Service: batch-translate text runs via Claude → reinsert via pypdf
- [ ] UI: language picker + promote

### 16.6 Cost + observability (1 day)
- [ ] `/admin/llm-cost` dashboard with daily spend per tool
- [ ] Threshold alert (Slack webhook or email)

### 16.7 Phase review (½ day)
- [ ] 4 AI tools live (for users with `ANTHROPIC_API_KEY`); tag `phase-16-complete`

### Phase 16 exit gate
- [ ] 36 live, tests ≥295
- [ ] Prompt-cache hit-rate ≥50% on same-document repeated questions

---

## 🗂️ Phase 17 — Workflow family (4 weeks; biggest infra leap)

### 17.1 Database setup (2 days)
- [ ] Pick: Supabase (Postgres + auth bundled) — recommended
- [ ] Schema: `projects`, `project_files`, `review_tasks`, `delivery_manifests`, `standards_rules` (UUIDs + `created_at`/`updated_at`)
- [ ] SQLAlchemy models
- [ ] Alembic migrations
- [ ] docker-compose for local Postgres

### 17.2 Auth (2 days)
- [ ] Supabase auth in hub only
- [ ] Login page + session cookie
- [ ] JWT middleware for workflow endpoints
- [ ] Tests

### 17.3 project-intake (2 days)
- [ ] Tests: create project, upload files, list projects
- [ ] Service + API
- [ ] UI: project list + detail + upload; promote

### 17.4 review-queue (3 days)
- [ ] Tests: task create, assign, state transitions
- [ ] Service: review_tasks CRUD
- [ ] UI: Kanban (drag-drop)
- [ ] Promote

### 17.5 delivery-center (3 days)
- [ ] Tests: package outputs, manifest, email delivery
- [ ] Service: zip + S3-compatible upload + notification
- [ ] UI + promote

### 17.6 standards-library (2 days)
- [ ] Tests: rule CRUD, apply rule to doc
- [ ] Service + UI: rule editor. Promote

### 17.7 publishing-hub (3 days)
- [ ] Tests: export to PDF / static site / S3
- [ ] Service: adapter pattern (PDF, static-site, S3 exporters)
- [ ] UI + promote

### 17.8 Phase review (1 day)
- [ ] 5 live behind login. End-to-end: intake → review → delivery → publishing
- [ ] DB backups scheduled
- [ ] Tag `phase-17-complete`

### Phase 17 exit gate
- [ ] 41 live, tests ≥330
- [ ] Demo project flows full lifecycle

---

## ✨ Phase 18 — Polish + monetization (2 weeks)

### 18.1 Stripe plans (2 days)
- [ ] Free (5/day), Pro ($9/mo, 500/day), Team ($29/mo, 5k/day) defined in Stripe
- [ ] Checkout flow per plan
- [ ] Webhook handling for subscription state

### 18.2 Usage tracking + rate limits (2 days)
- [ ] Per-user counter table
- [ ] Middleware reads plan + counter, enforces limits
- [ ] Tests

### 18.3 Dashboard (2 days)
- [ ] `/dashboard`: ops remaining, history, billing portal link
- [ ] Usage charts (recharts or D3)
- [ ] Tests + deploy

### 18.4 Error pages (1 day)
- [x] Pretty 404/500 with hub chrome
- [x] Tests

### 18.5 OG images (1 day)
- [ ] Dynamic `/og/<slug>.png` renders tool-specific social card
- [ ] Test in Twitter/LinkedIn validators

### 18.6 Sitemap + SEO (1 day)
- [x] Auto-regenerate sitemap from live tools
- [x] `meta description` per tool page
- [ ] Submit to Google Search Console (manual, post-deploy)

### 18.7 About + changelog (1 day)
- [x] `/about` + `/changelog` (markdown-driven)

### 18.8 Keyboard shortcuts cheat-sheet (½ day)
- [x] `?` opens modal listing shortcuts

### 18.10 Live-only catalog policy (½ day) ✅
> Rule: users only ever see tiles that work end-to-end. Beta + planned
> stay in the registry for the roadmap but are hidden from every public
> surface. A single env var (`PROOFMARK_SHOW_ALL_TILES=true`) restores
> the full catalog for local dev and plan review.

- [x] `feature_flags.show_all_tiles()` + `is_displayed(slug, entry)` helpers
- [x] `/api/tools` adds `display: bool` per entry + `display_counts` block (backwards-compatible with the Phase 10.5 `counts` contract)
- [x] `/tool/{slug}` returns 404 for non-live tiles in live-only mode; flag-off on a live tile still renders the paused stub so bookmarked links explain themselves
- [x] `/sitemap.xml` only lists displayed tools
- [x] SPA: sync marks `t.hidden` from server response; `__pmVisible()` helper filters every render surface (hero counts, popular strip, grouped catalog, group chips, pinned sidebar, pinned view, workflow view, command palette)
- [x] Docs: `docs/feature-flags.md` gains a _Catalog display mode_ section with env-var table + behaviour matrix
- [x] Tests: 11 new assertions covering defaults, roadmap mode, per-tool flag interaction, SPA filter surface

### 18.9 Phase review (½ day)
- [ ] Sign up → upgrade Pro → run 50 ops → see dashboard → cancel → works
- [ ] Tag `phase-18-complete`

### Phase 18 exit gate
- [ ] Paying users subscribe end-to-end
- [ ] Every live tool has a dynamic OG image

---

## 🌐 Phase 19 — Custom domain cutover (1 active day + DNS propagation)

### 19.1 Buy `proofmarkstudio.com` (minutes)
- [ ] Register at preferred registrar

### 19.2 Attach to Vercel (minutes)
- [ ] Dashboard → proofmark-studio project → Settings → Domains
- [ ] Add `proofmarkstudio.com` and `www.proofmarkstudio.com`
- [ ] Apply DNS instructions at registrar

### 19.3 Wait for SSL (15 min – 2 h)
- [ ] Vercel auto-provisions Let's Encrypt
- [ ] Confirm `https://proofmarkstudio.com` loads

### 19.4 301 redirects from old URLs (½ day)
- [ ] `pdf.sabbir.ca` → `proofmarkstudio.com/pdf/`
- [ ] `proofmark.sabbir.ca` → `proofmarkstudio.com/text/`
- [ ] Test with curl

### 19.5 Full smoke (½ day)
- [ ] Every live tool via new domain
- [ ] Upload + process + download full flow
- [ ] Share link; second user confirms usability

### 19.6 Launch (½ day)
- [ ] Social post, dev.to, Hacker News "Show HN", newsletter
- [ ] Update LinkedIn + personal site
- [ ] Tag: `release: v1.0 launch`

### Phase 19 exit gate
- [ ] `proofmarkstudio.com` is primary
- [ ] Old URLs 301
- [ ] First real user signs up

---

## 🔗 Phase 20 — Tool Chaining (advanced, post-launch v1.1 — 3–4 weeks)

> **Why last:** 49 standalone tools first. Chaining is a power-user feature that
> multiplies value only once the individual tools are proven. Shipping it
> pre-launch dilutes focus; shipping it post-launch when we have real users
> lets actual feedback drive which chains to templatize.

**User story:** "Upload PDF → compress to 50% → add watermark 'DRAFT' → protect with password → download." All in one flow, in one interface.

### 20.1 Design + API contract (3 days)
- [ ] 20.1.1 RFC doc `docs/tool-chaining-rfc.md` covering: chain shape (ordered list of steps), step contract (in→out), shared context (file handles, options), error mode (fail-fast vs best-effort), UI paradigm (node-graph vs step-list)
- [ ] 20.1.2 Decide: start with **linear step-list** (simpler, covers 80% of cases), defer branching/conditionals to v1.2
- [ ] 20.1.3 Define `ChainStep` schema: `{ slug, options }`. Decide which tools are **chainable** — flag `chainable: bool` in `ToolMeta`
- [ ] 20.1.4 Chain JSON schema:
      ```json
      {
        "name": "PDF Prep",
        "steps": [
          { "slug": "compress-pdf", "options": { "mode": "lossy" } },
          { "slug": "watermark-pdf", "options": { "text": "DRAFT" } },
          { "slug": "protect-pdf", "options": { "password": "<user-input>" } }
        ]
      }
      ```
- [ ] 20.1.5 Audit all 41 live tools → mark chainable. Tools that take non-PDF inputs (convert-TO-PDF) are "chain heads"; tools that output non-PDF (convert-FROM-PDF) are "chain tails"; most others are pure PDF→PDF
- [ ] Commit: `docs(chaining): RFC + chainability audit`

### 20.2 Chain executor — server-side (5 days)
- [ ] 20.2.1 Failing tests: 2-step chain, 5-step chain, step failure → chain fails with partial progress, cancellation mid-chain
- [ ] 20.2.2 `proofmark_pdf/chain_executor.py`: `execute_chain(chain, initial_file) -> ChainResult` — runs steps in sequence, passing output of N to input of N+1
- [ ] 20.2.3 Each step runs through its existing `ToolService.run()` — no tool code changes needed
- [ ] 20.2.4 Intermediate artifacts stored in tmpdir, cleaned up after final output
- [ ] 20.2.5 `POST /api/chain/execute` accepts chain JSON + initial file; returns final file (or streams progress via Server-Sent Events for long chains)
- [ ] 20.2.6 Telemetry: `[chain:<name>]` log per step with `{step_index, step_slug, durationMs, outcome}`
- [ ] 20.2.7 Commit per checkpoint: `feat(chain): executor`, `feat(chain): /api/chain/execute`, `feat(chain): SSE progress`

### 20.3 Chain builder UI (5 days)
- [ ] 20.3.1 New hub route `/chain` — linear step-list composer in the React app
- [ ] 20.3.2 "Add step" dropdown populated from `/api/tools?chainable=true`
- [ ] 20.3.3 Per-step options pane (reuses each tool's existing options schema)
- [ ] 20.3.4 Drag-to-reorder
- [ ] 20.3.5 Input validation: warn if a step's output type doesn't match next step's input type (e.g. can't put jpg-to-pdf after protect-pdf — protect outputs a protected PDF, jpg-to-pdf input is an image)
- [ ] 20.3.6 Execute button → file upload → live progress per step → download result
- [ ] 20.3.7 Tests (Playwright or hand-test)
- [ ] Commit

### 20.4 Chain templates (2 days)
- [ ] 20.4.1 Predefined chains in `proofmark_studio/chain_templates.py`:
      - "PDF Prep" (compress + watermark + protect)
      - "Scan to Searchable" (pdf-ocr + compress + extract-text alongside)
      - "Publish Ready" (compress + watermark + number-pages + flatten + protect)
      - "Redact & Deliver" (redact + flatten + protect + compress)
- [ ] 20.4.2 Template picker in UI — one click loads the chain, user tweaks options, runs
- [ ] Commit

### 20.5 Custom chain persistence (2 days)
- [ ] 20.5.1 Requires Phase 17 (DB + auth). Table: `user_chains (id, user_id, name, steps_json, created_at, updated_at)`
- [ ] 20.5.2 Save/load/delete user chains via REST
- [ ] 20.5.3 UI: "My chains" list; save-current-chain button
- [ ] Commit

### 20.6 Launch chaining feature (1 day)
- [ ] 20.6.1 Announcement post (v1.1 release) with a demo video
- [ ] 20.6.2 Tag `release: v1.1 chaining`
- [ ] 20.6.3 Hub tile strip: "Try a chain →" above the tool catalog, rotating featured templates
- [ ] 20.6.4 Update landing page copy + SEO meta

### Phase 20 exit gate
- [ ] 5+ predefined chain templates ship
- [ ] Users can build/save/run custom chains
- [ ] Every chainable tool honors a strict PDF→PDF contract with predictable behavior
- [ ] Chain executor has a kill switch: `CHAIN_EXECUTOR_ENABLED=false` → `/chain` page shows "temporarily unavailable"

**Deferred to v1.2+ (branches, conditions, AI orchestration):**
- Conditional branching ("if page count > 100 then compress-aggressive else compress-normal")
- Parallel fan-out ("extract pages → OCR each → recombine")
- AI-driven chain suggestion ("you're about to merge scanned PDFs — chain OCR before merge?")
- Scheduled/triggered chains (cron — "compress all PDFs in dropbox folder X nightly")

---

## 📋 Per-tool checklist (copy for each new tool)

- [ ] Registry entry added (status starts `planned`)
- [ ] Test file with: empty input, password, too-large, happy-path, regression
- [ ] Service file implementing `ToolService`
- [ ] API route `POST /api/<slug>`
- [ ] UI route `GET /<slug>` with drag-drop + options
- [ ] Feature flag `TOOL_<SLUG>_ENABLED` documented
- [ ] Telemetry `[tool:<slug>]` log with structured context
- [ ] Promoted to `live` after 3-document manual smoke
- [ ] Commit: `feat(<slug>): <one-line-why>`
- [ ] Hub tile shows "Live" pill, click works end-to-end

---

## 🔁 Cross-cutting reminders

- **Commit often.** Every sub-phase = at least one commit.
- **Tests never drop.** Baseline is 173; each phase end ≥ baseline of its start.
- **Kill-switch every tool.** `TOOL_<SLUG>_ENABLED=false` reverts to stub in ≤60s.
- **Structured returns.** `{ ok, reason?, signal?, ...payload }` — not bare booleans.
- **Observability.** Every decision point logs `[tag] message` with JSON context.
- **WHY comments only.** Code explains what; comments explain why.
- **No Co-Authored-By lines in commits.**

## 📚 References

- Full plan (per-sub-phase acceptance criteria): `C:\Users\sabbir\.claude\plans\proofmark-studio-tool-buildout.md`
- Deploy playbook: `docs/deployment.md`
- Architecture: `docs/architecture.md`
- Art spec: `docs/art-background.md`
- Adding a tool: `docs/adding-a-tool.md`
- Previous session plan: `C:\Users\sabbir\.claude\plans\c-users-sabbir-downloads-proofmark-stud-abstract-moon.md`
