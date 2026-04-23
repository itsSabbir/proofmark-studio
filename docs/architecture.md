# Architecture

## One sentence

Three sibling FastAPI apps, one React-based hub, connected via URL redirects — not imports.

## Why URL-based, not import-based

The sub-apps (ProofMark PDF, Text Inspection) are two large self-contained FastAPI monoliths (~280KB of HTML-in-Python combined). Mounting them into the hub process via `app.mount("/pdf", pdf_app)` would require rewriting hundreds of hardcoded absolute paths (`fetch('/api/merge')`, `href='/'`, `<link rel='icon' href='/icon.svg'>`, Stripe checkout return URLs…).

Instead: each sub-app runs as its **own FastAPI process on its own port**, and the hub sends clicks there via HTTP redirect. Sub-apps stay byte-for-byte usable standalone. Cross-cutting concerns (auth, return-to-hub, shared CSS) are added lightly via env vars and response-body injection — **additive**, not invasive.

This architecture also maps cleanly to the Phase 9 production plan (Vercel rewrites), where each sibling becomes an independent Vercel project and the hub proxies at the edge.

## Request flow: live tool

```
1. User visits proofmark-studio:8020/  (hub home)
2. Clicks "Merge PDF" tile → React drawer opens
3. Clicks "Open tool" in drawer → window.location = /tool/merge-pdf
4. Hub's FastAPI route GET /tool/merge-pdf:
     entry = TOOLS['merge-pdf']          # status=live, url=http://127.0.0.1:8010/merge-pdf
     → 307 redirect to entry['url']
5. Browser follows → proofmark-pdf:8010/merge-pdf
6. PDF sibling renders its merge UI with "← ProofMark Studio" link
   (link shown because PROOFMARK_HUB_URL env var is set by launch-all.ps1)
```

## Request flow: planned / beta tool

```
1. User clicks "Sign PDF" tile → drawer → "Open preview"
2. window.location = /tool/sign-pdf
3. Hub's route: entry.status == 'planned' → render stub HTML
4. Stub page shows:
     - Breadcrumb: ProofMark Studio / Sign & Secure / Planned
     - Title: "Sign PDF" (Instrument Serif)
     - Description from registry
     - Buttons: [Return to the hub] [Open ProofMark PDF]
```

## Components

- **Hub FastAPI** (`proofmark_studio/hub_app.py`) — thin server, ~230 LOC. Routes: `/`, `/static/*`, `/tool/{slug}`, `/api/{health,tools,studio-map,local-projects}`, `/go/*`, `/privacy`, `/terms`, `/robots.txt`, `/sitemap.xml`.
- **Tool registry** (`proofmark_studio/tool_registry.py`) — one dict per slug with `{title, desc, group, status, parent, url}`. URL is `None` for non-live tools. Bases come from env vars so local → Vercel migration is a config flip, not a code change.
- **React SPA** (`static/hub/src/*.jsx`) — hand-authored JSX served to the browser, transpiled client-side by Babel standalone. No build step required. On mount, fetches `/api/tools` and merges backend status/url into its catalog so display can't drift.
- **StudioCanvas** (`studio-canvas.jsx`) — replaces the old grid pattern with a deterministic layout of squiggles, outlined circles, triangles, asterisks, crescents, dot clusters, and wave bars in red/yellow/blue. Positions corner-clustered to avoid competing with body text. See [art-background.md](art-background.md).
- **Sub-apps** (`../proofmark-pdf/`, `../text-cleaner/`) — untouched except for: (a) port default (PDF 8010), (b) `HUB_URL` env var toggle for back-link. Tests still pass from either invocation location.

## Why React UMD + Babel standalone (no build step)

Local dev, small team, iteration speed > bundle size. Every file is editable and the browser reloads what's on disk. Moving to a build pipeline is a Phase 9+ consideration when bundle weight starts to matter.

## What's safe to change independently

- **Sub-app internals** — sub-apps don't import the hub and the hub doesn't import them. A release of the PDF tool can't break the hub and vice versa.
- **Hub UI (JSX)** — the Python server serves `.jsx` files as static assets. Edit and refresh.
- **Tool catalog** — add an entry in `tool_registry.py` + matching tile in `tools.jsx`. Nothing else.
- **Art background** — tweak any entry in `STUDIO_ELEMENTS` in `studio-canvas.jsx`.

## What requires coordinated changes

- Adding a *new sibling app* (like "proofmark-image") — needs: new port, new entry in `tool_registry.PARENT_URLS` + `PARENT_LABELS`, new section in `launch-all.ps1 $APPS`, and Vercel project for Phase 9.
- Changing the redirect contract (`/tool/{slug}` → URL) — affects both hub's router and React drawer's click handler.

## Key decisions log

1. **URL-based integration** over `.mount()` — respects sub-app autonomy; enables Vercel rewrites in prod.
2. **Sibling folders** over monorepo/submodules — simplicity. Each app's GitHub repo stays independent.
3. **Stubs for all beta** — even partially-working beta tools land on the stub + "Open parent" button. Promoting to "live" is a one-line flip in `tool_registry.py`.
4. **`PROOFMARK_HUB_URL` env var** — back-link in siblings is opt-in, so standalone launches stay clean.
5. **Deterministic art layout** — no randomness in StudioCanvas. Every element position is authored, reviewable, and tweakable.
