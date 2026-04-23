# Adding a tool to the catalog

Since **Phase 10** every tool is a `ToolService` with a typed result + a feature
flag + observability. Six files in a predictable shape — the contract test
catches anything you forget.

## Recipe (post-Phase-10)

### 1. Service file — `tool_services/<slug>.py` (parent repo)

Implement the `ToolService` protocol:

```python
from typing import Any, Mapping, Optional
from proofmark_pdf import pdf_ops  # or text_cleaner for text tools
from proofmark_pdf.errors import ErrorCode, as_err
from proofmark_pdf.tool_services import Err, Ok, Result, ToolMeta


class MyNewToolService:
    slug = "my-new-tool"

    def describe(self) -> ToolMeta:
        return ToolMeta(
            slug=self.slug, title="My New Tool", group="organize",
            status="live", chainable=True,
            description="One-line description.",
        )

    def validate(self, payload: Mapping[str, Any]) -> Optional[Err]:
        if not payload.get("pdf"):
            return as_err(ErrorCode.INVALID_PDF)
        return None

    def run(self, payload: Mapping[str, Any]) -> Result:
        err = self.validate(payload)
        if err is not None:
            return err
        # ... call the pure-ops function ...
        return Ok(data={"pdf_bytes": result_bytes})
```

Structured returns — no bare booleans, no raw exceptions escaping. The web
layer maps `Err.code` onto `to_http_detail()` for a stable JSON shape.

### 2. Register it — `tool_services/registry.py`

Append an instance to `all_services()`. One line.

### 3. Tests — `tests/test_<slug>.py`

Mandatory cases from the per-tool checklist:

- Empty input → the right `ErrorCode`
- Password-protected PDF → `PDF_PASSWORD_REQUIRED` (if the tool reads PDFs)
- Oversized input → `PDF_TOO_LARGE` / `INPUT_TOO_LARGE`
- Happy path → correctness asserted on output
- One regression test per known bug class

The generic contract test (`tests/test_tool_contract.py`) already asserts
protocol conformance, describe-shape, and empty-payload-returns-Err — a new
service fails that automatically if you forget anything.

### 4. Hub catalog — `proofmark-studio/proofmark_studio/tool_registry.py`

```python
"my-new-tool": _t(
    "My New Tool",                       # title
    "One-line description.",             # desc
    "organize",                          # group
    "planned",                           # start as planned; flip to live after smoke
    "proofmark-pdf",                     # parent (None for hub-native)
    "/my-new-tool",                      # path on parent app (only used when status='live')
),
```

### 5. React tile — `static/hub/src/tools.jsx`

```js
{ slug:'my-new-tool', title:'My New Tool', group:'organize', cat:'organize',
  status:'planned', icon:'merge',
  desc:'One-line description.' },
```

### 6. Feature flag — `docs/feature-flags.md`

Add one line under the right group:

```
- `my-new-tool` → `TOOL_MY_NEW_TOOL_ENABLED`
```

No code — the flag module derives the env var from the slug automatically.

## Promotion path

- **planned → live**: flip `status` in `tool_registry.py` and `tools.jsx`;
  smoke 3 real documents; commit `feat(<slug>): live`.
- **live → paused**: set `TOOL_<SLUG>_ENABLED=false`. Tile shows "Paused" in
  ≤60s, no redeploy. Fix forward, drop the env var to re-enable.

## Observability — free

Services wrapped by `instrument_all()` emit `[tool:<slug>]` start + end logs
and a JSON sidecar on stderr with `{slug, phase, outcome, duration_ms, inputs,
context}`. See `docs/observability.md`.

## Chainability — Phase 20

If the tool's input and output are both PDFs, set `chainable=True` in
`describe()`. The chain executor (v1.1) iterates only chainable services.

Split-pdf and similar many-output tools should stay `chainable=False` until
Phase 20 defines a many-out contract.

## Checklist before committing

- [ ] `tests/test_<slug>.py` green (red first, green second)
- [ ] Registered in `tool_services/registry.py`
- [ ] Entry in `proofmark_studio/tool_registry.py` (hub)
- [ ] Tile in `static/hub/src/tools.jsx` (hub)
- [ ] Env-var listed in `docs/feature-flags.md`
- [ ] Contract test green (`tests/test_tool_contract.py`)
- [ ] Manual smoke on 3 real documents
- [ ] Commit: `feat(<slug>): <one-line-why>`
