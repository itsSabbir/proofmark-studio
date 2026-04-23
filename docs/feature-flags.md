# Feature flags

Every tool in the 49-tool catalog is gated by a per-tool env var. Flipping
`TOOL_<SLUG>_ENABLED=false` (or `0` / `off` / `no` / `disabled`) demotes the
tile to `"planned"` at request time — no redeploy, no code change.

## Behavior

- **Default is ON** (opt-out). Missing env var → enabled.
- **Off values** (case-insensitive, trimmed): `false`, `0`, `off`, `no`, `disabled`.
- Anything else — including empty string and `"true"` — is ON.
- The hub's `/api/tools` merges this into the registry each request; the React
  catalog downgrades the tile's status and shows a "paused" badge.

## Env var name from slug

`<slug>` → `TOOL_<slug.replace('-','_').upper()>_ENABLED`.

Examples:

| Slug | Env var |
|---|---|
| `merge-pdf` | `TOOL_MERGE_PDF_ENABLED` |
| `split-pdf` | `TOOL_SPLIT_PDF_ENABLED` |
| `extract-pdf-pages` | `TOOL_EXTRACT_PDF_PAGES_ENABLED` |
| `pdf-to-markdown` | `TOOL_PDF_TO_MARKDOWN_ENABLED` |
| `text-inspection` | `TOOL_TEXT_INSPECTION_ENABLED` |

## Full slug index (49 tools)

### Organize
- `merge-pdf` → `TOOL_MERGE_PDF_ENABLED`
- `split-pdf` → `TOOL_SPLIT_PDF_ENABLED`
- `extract-pdf-pages` → `TOOL_EXTRACT_PDF_PAGES_ENABLED`
- `organize-pdf` → `TOOL_ORGANIZE_PDF_ENABLED`
- `compress-pdf` → `TOOL_COMPRESS_PDF_ENABLED`
- `rotate-pdf` → `TOOL_ROTATE_PDF_ENABLED`
- `delete-pdf-pages` → `TOOL_DELETE_PDF_PAGES_ENABLED`

### Convert from PDF
- `pdf-to-word` → `TOOL_PDF_TO_WORD_ENABLED`
- `pdf-to-excel` → `TOOL_PDF_TO_EXCEL_ENABLED`
- `pdf-to-ppt` → `TOOL_PDF_TO_PPT_ENABLED`
- `pdf-to-jpg` → `TOOL_PDF_TO_JPG_ENABLED`
- `pdf-to-png` → `TOOL_PDF_TO_PNG_ENABLED`
- `pdf-to-text` → `TOOL_PDF_TO_TEXT_ENABLED`
- `pdf-to-markdown` → `TOOL_PDF_TO_MARKDOWN_ENABLED`
- `pdf-to-html` → `TOOL_PDF_TO_HTML_ENABLED`

### Convert to PDF
- `word-to-pdf` → `TOOL_WORD_TO_PDF_ENABLED`
- `excel-to-pdf` → `TOOL_EXCEL_TO_PDF_ENABLED`
- `ppt-to-pdf` → `TOOL_PPT_TO_PDF_ENABLED`
- `jpg-to-pdf` → `TOOL_JPG_TO_PDF_ENABLED`
- `html-to-pdf` → `TOOL_HTML_TO_PDF_ENABLED`
- `markdown-to-pdf` → `TOOL_MARKDOWN_TO_PDF_ENABLED`
- `pdf-ocr` → `TOOL_PDF_OCR_ENABLED`

### View & Edit
- `edit-pdf` → `TOOL_EDIT_PDF_ENABLED`
- `pdf-annotator` → `TOOL_PDF_ANNOTATOR_ENABLED`
- `pdf-reader` → `TOOL_PDF_READER_ENABLED`
- `number-pages` → `TOOL_NUMBER_PAGES_ENABLED`
- `crop-pdf` → `TOOL_CROP_PDF_ENABLED`
- `redact-pdf` → `TOOL_REDACT_PDF_ENABLED`
- `watermark-pdf` → `TOOL_WATERMARK_PDF_ENABLED`
- `pdf-form-filler` → `TOOL_PDF_FORM_FILLER_ENABLED`

### Sign & Secure
- `sign-pdf` → `TOOL_SIGN_PDF_ENABLED`
- `request-signatures` → `TOOL_REQUEST_SIGNATURES_ENABLED`
- `unlock-pdf` → `TOOL_UNLOCK_PDF_ENABLED`
- `protect-pdf` → `TOOL_PROTECT_PDF_ENABLED`
- `flatten-pdf` → `TOOL_FLATTEN_PDF_ENABLED`

### Proofing
- `text-inspection` → `TOOL_TEXT_INSPECTION_ENABLED`
- `inspect-hidden` → `TOOL_INSPECT_HIDDEN_ENABLED`
- `normalize-whitespace` → `TOOL_NORMALIZE_WHITESPACE_ENABLED`
- `review-typography` → `TOOL_REVIEW_TYPOGRAPHY_ENABLED`
- `export-cleanup-report` → `TOOL_EXPORT_CLEANUP_REPORT_ENABLED`

### AI
- `ai-pdf-assistant` → `TOOL_AI_PDF_ASSISTANT_ENABLED`
- `chat-with-pdf` → `TOOL_CHAT_WITH_PDF_ENABLED`
- `ai-pdf-summarizer` → `TOOL_AI_PDF_SUMMARIZER_ENABLED`
- `translate-pdf` → `TOOL_TRANSLATE_PDF_ENABLED`

### Workflow
- `project-intake` → `TOOL_PROJECT_INTAKE_ENABLED`
- `review-queue` → `TOOL_REVIEW_QUEUE_ENABLED`
- `delivery-center` → `TOOL_DELIVERY_CENTER_ENABLED`
- `standards-library` → `TOOL_STANDARDS_LIBRARY_ENABLED`
- `publishing-hub` → `TOOL_PUBLISHING_HUB_ENABLED`

## Rollback flow

Broken tool in prod:

```bash
vercel env add TOOL_<SLUG>_ENABLED false production
vercel --prod   # or toggle in dashboard
```

Tile reverts to `"paused"` on the next cache miss (≤60s). Fix forward, then
remove the env var to re-enable.
