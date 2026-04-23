# Deployment — Vercel (Phase 9)

Goal: `proofmarkstudio.com` serves as a **single domain** from the user's perspective. Clicks to PDF tools land on `proofmarkstudio.com/pdf/merge-pdf` (URL bar never changes), edge-proxied to the PDF Vercel project.

This is the SmallPDF pattern.

## Architecture

```
User → proofmarkstudio.com/pdf/merge-pdf
           │
           ▼  Vercel edge rewrite (invisible to user)
       proofmark-pdf.vercel.app/merge-pdf
           │
           ▼
       User sees the merge UI; URL bar still reads proofmarkstudio.com
```

Three separate Vercel projects, one from each GitHub repo:

| Repo                  | Vercel project      | Suggested domain              |
|-----------------------|---------------------|-------------------------------|
| `proofmark-studio`    | `proofmark-studio`  | **`proofmarkstudio.com`** (primary) |
| `proofmark-pdf`       | `proofmark-pdf`     | `proofmark-pdf.vercel.app` (internal) |
| `text-cleaner`        | `text-cleaner`      | `text-cleaner.vercel.app` (internal)  |

## Steps

### 1. Create the three Vercel projects

For each repo, in the Vercel dashboard:
- **New Project** → import from GitHub
- Point it at the relevant repo (`itsSabbir/proofmark-pdf`, `itsSabbir/text-remover`, `itsSabbir/proofmark-studio`)
- Accept defaults for the first two; hub gets custom env vars (see step 2)
- Deploy

Each sibling goes live at `https://<project>.vercel.app` — these are the **internal** URLs the hub will proxy to.

### 2. Configure hub env vars

On the `proofmark-studio` Vercel project:

```
PROOFMARK_PDF_BASE=""                              # empty → /pdf/ relative (rewrite handles)
PROOFMARK_TEXT_BASE=""                             # empty → /text/ relative
PROOFMARK_SITE_URL=https://sabbir.ca/              # external portfolio
```

Empty `PDF_BASE` / `TEXT_BASE` tell `tool_registry.py` to emit **same-origin relative URLs** (`/pdf/merge-pdf`). Vercel's rewrites then handle the proxy.

### 3. Custom domain

Attach `proofmarkstudio.com` to the `proofmark-studio` project (Vercel → Settings → Domains). Vercel gives you DNS instructions (A records or nameservers). Apply them at your registrar.

### 4. Update `vercel.json` rewrite targets

If your sibling Vercel project URLs differ from the defaults in `vercel.json`, edit these lines:

```json
"rewrites": [
  { "source": "/pdf/:path*",  "destination": "https://<your-pdf-url>.vercel.app/:path*" },
  { "source": "/text/:path*", "destination": "https://<your-text-url>.vercel.app/:path*" }
]
```

Commit + push → Vercel redeploys hub.

### 5. Absolute-path fix in siblings (the gotcha)

The sibling apps hardcode `fetch('/api/merge')`, `href='/'`, `<link rel='icon' href='/icon.svg'>` etc. Under a rewrite, `/api/merge` hits the **hub** origin, not the sub-app. Two workable fixes:

**Option A — `BASE_PATH` env var (recommended):**

Add a small helper at the top of each sibling's `web_app.py`:

```python
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
def u(path: str) -> str:  # "url" helper
    return f"{BASE_PATH}{path}"
```

Then replace `/api/merge` with `{u('/api/merge')}` in HTML strings, `href='/'` with `href='{u('/')}'`, etc.

Set `BASE_PATH=/pdf` on the PDF project and `BASE_PATH=/text` on the text project (Vercel env vars).

Locally (no rewrite), `BASE_PATH=""` so URLs stay the same as today.

**Option B — `<base>` tag injection (less invasive):**

Add a response middleware that injects `<base href="/pdf/">` into HTML responses:

```python
@app.middleware("http")
async def inject_base(request, call_next):
    response = await call_next(request)
    base_path = os.environ.get("BASE_PATH", "")
    if not base_path or not response.headers.get("content-type", "").startswith("text/html"):
        return response
    body = b""
    async for chunk in response.body_iterator:
        body += chunk
    body = body.replace(b"<head>", f"<head><base href='{base_path}/'>".encode(), 1)
    return Response(content=body, status_code=response.status_code, headers=dict(response.headers))
```

Browser resolves every relative URL against the `<base>`. Works for HTML but not for `fetch()` in JS (those need `BASE_PATH` injection or full URLs).

### 6. Stripe return URLs

Checkout success/cancel URLs are currently hardcoded absolute — they'd point back at the sub-app's own Vercel URL, not `proofmarkstudio.com`. Fix:

```python
# In sub-app's checkout handler:
return_url = f"{request.headers.get('origin', '')}{BASE_PATH}/donate/success"
```

Reading the origin from the incoming request means the return URL automatically lands on whatever domain the user came in through.

### 7. Smoke test end-to-end

After deploy:

1. Visit `https://proofmarkstudio.com/` → hub loads, URL bar reads proofmarkstudio.com.
2. Click "Merge PDF" → URL becomes `proofmarkstudio.com/pdf/merge-pdf`, merge tool renders.
3. Upload two test PDFs → merge → download succeeds.
4. Click "← ProofMark Studio" → back at `proofmarkstudio.com/`.
5. Click a planned tile (e.g. "Sign PDF") → stub page renders.

URL bar should never show `*.vercel.app` or `*.sabbir.ca`.

## Retiring old URLs

`pdf.sabbir.ca` / `proofmark.sabbir.ca` / etc. — three options:

- **Retire:** delete DNS records.
- **Redirect:** 301 → `proofmarkstudio.com` equivalent. Preserves SEO + old bookmarks. Set up Vercel redirects or DNS CNAME.
- **Keep as admin URL:** direct access to sub-apps bypassing the hub. Useful for ops.

## Rollback

- **Bad hub deploy:** Vercel dashboard → Promote previous deployment. Instant.
- **Bad sibling deploy:** Same, on the sibling's Vercel project. Hub unaffected.
- **DNS emergency:** Revert the `proofmarkstudio.com` CNAME / A record.

Because each project is independent, a broken release in one doesn't cascade.

## Why this architecture holds up as the catalog grows

- New tool in an existing sibling → 2-file change (registry + tiles). No deployment coordination.
- New sibling app → new Vercel project + one line in `vercel.json`. Adds a whole tool family without touching the existing sub-apps.
- Each sibling scales independently on Vercel's serverless runtime — heavy PDF work doesn't starve the text tool.
