# Observability

**Rule** (from CLAUDE.md): if a decision can produce a wrong-looking outcome,
it must log the decision. Every `ToolService.run()` wrapped with
`instrument_all()` emits two events per call — a start, and an end carrying
the outcome.

## Log shape

### Human-readable (stdlib `logging`)

```
[tool:merge-pdf] start
[tool:merge-pdf] end outcome=ok duration_ms=12.4
```

- Tag format: `[tool:<slug>]`, lowercase, ≤ 12-char slug.
- Logger name: `proofmark_pdf.tool` (pdf-side) and `text_cleaner.tool` (text-side).

### Structured JSON sidecar (stderr)

```json
{
  "tag": "[tool:merge-pdf]",
  "slug": "merge-pdf",
  "phase": "start",
  "outcome": "started",
  "duration_ms": 0,
  "inputs": {"pdfs": {"kind": "list[bytes]", "n": 2, "sizes": [12345, 67890]}},
  "context": {}
}
{
  "tag": "[tool:merge-pdf]",
  "slug": "merge-pdf",
  "phase": "end",
  "outcome": "ok",
  "duration_ms": 12.4,
  "inputs": {"pdfs": {"kind": "list[bytes]", "n": 2, "sizes": [12345, 67890]}},
  "context": {"data_keys": ["input_count", "pdf_bytes"]}
}
```

## Outcomes

| Outcome | Meaning |
|---|---|
| `ok` | `Ok` returned, payload under `context.data_keys` |
| `err:<CODE>` | `Err(code=CODE)` returned; `context` carries the `Err.context` |
| `raise:<ExcName>` | `run()` raised — should never happen in a well-behaved service |
| `started` | Only on the start event |

## Privacy

Raw `bytes` / `bytearray` payloads are redacted to `<bytes:N>` / list-of-sizes
before logging — file contents never hit the log pipeline. Scalar options
(page ranges, chunk sizes, mode names) pass through.

## Grep/jq triage

```bash
# All errors today:
grep '"outcome":"err:' .runtime/*.stderr.log | jq 'select(.slug=="merge-pdf")'

# Slowest calls per tool:
grep '"phase":"end"' .runtime/*.stderr.log \
  | jq -s 'group_by(.slug) | map({slug: .[0].slug, p95: (map(.duration_ms) | sort | .[(length*0.95|floor)])})'
```

## Consumption

Right now: stderr. Future phases (18+) plug a collector in front without
touching tool code — the emit function is the only place that knows the
transport. Consumers ignore unknown keys, so adding fields to the payload is
non-breaking.
