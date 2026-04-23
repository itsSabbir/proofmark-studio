# Adding a tool to the catalog

Two files, same slug. That's it.

## Recipe

### 1. `proofmark_studio/tool_registry.py`

Add an entry under the right group:

```python
"my-new-tool": _t(
    "My New Tool",                       # title (shown in tile + drawer + stub)
    "One-line description of the tool.", # desc
    "organize",                          # group: organize | convert-from | convert-to | edit | sign | proof | ai | workflow
    "planned",                           # status: live | beta | planned
    "proofmark-pdf",                     # parent: proofmark-pdf | text-cleaner | None
    "/my-new-tool",                      # path (only used when status='live')
),
```

Status semantics:
- `live` — hub redirects to `parent_base + path`. The parent app must implement that path.
- `beta` — stub page with "Beta" badge + "Open [Parent Tool]" button.
- `planned` — stub page with "Planned" badge.

URL is computed automatically from `PROOFMARK_PDF_BASE` / `PROOFMARK_TEXT_BASE` env vars — local dev gets `http://127.0.0.1:8010/my-new-tool`, Vercel prod gets `/pdf/my-new-tool` (relative, same-origin via rewrite).

### 2. `proofmark_studio/static/hub/src/tools.jsx`

Add a matching tile:

```js
{ slug:'my-new-tool', title:'My New Tool', group:'organize', cat:'organize',
  status:'planned', icon:'merge',
  desc:'One-line description of the tool.' },
```

Must-match fields: `slug`, `title`, `group`, `status`, `desc`. Other fields are display-only:
- `cat` — category tab (`organize` | `convert` | `edit` | `sign` | `proof` | `ai` | `workflow`)
- `icon` — illustration key (see `illust.jsx` for available names: `merge`, `split`, `docx`, `sig`, `aa`, `ai`, etc.)
- `popular: true` — promotes to the "Popular right now" strip
- `pin: true` — shows in sidebar's pinned list

### 3. That's it.

No build step. Refresh the hub at `http://127.0.0.1:8020/` and your tile appears. Click it → drawer opens → "Open preview" → lands on the stub page (or redirects to live parent if status=live).

## Promoting a tool from `planned` → `beta` → `live`

- **planned → beta**: flip `status` in both files. Stub page still renders; pill reads "Beta".
- **beta → live**: flip `status` + ensure `path` in `tool_registry.py` points at a real route in the parent app.

No code gymnastics — the catalog redraws, the router routes.

## Adding a new group / category

Rare. If you need a new top-level bucket (e.g. "Analytics"):

1. Add to `GROUPS` dict in `tool_registry.py` with a `label` and `tone` (hex).
2. Add matching entry to `GROUPS` array in `tools.jsx` with a `pastel` background hex.
3. Add matching entry to `CATEGORIES` in `tools.jsx` if you want a filter chip for it.

## Adding a new parent app (beyond PDF and Text Inspection)

Bigger change. Touch points:

1. **New sibling folder** at `tools/proofmark-<name>/` — FastAPI app, own port.
2. **`tool_registry.py`**:
   - Add helper `_<name>(path)` that builds URLs.
   - Add to `PARENT_URLS` and `PARENT_LABELS`.
3. **`hub_app.py`**: add `/go/<name>` redirect route.
4. **`scripts/launch-all.ps1`**: add entry to `$APPS` array.
5. **New env var**: `PROOFMARK_<NAME>_BASE` with localhost default.
6. **Phase 9 (prod)**: add Vercel project + rewrite rule in `vercel.json`.

## Checklist before committing a new tool

- [ ] Entry in `tool_registry.py` with correct status
- [ ] Matching tile in `tools.jsx` with same slug
- [ ] Test it in the hub: tile renders? Drawer opens? Click "Open" routes correctly?
- [ ] If live: parent app actually serves the path
- [ ] `pytest` green in hub + parent sibling
