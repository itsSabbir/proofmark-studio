# StudioCanvas — abstract art background

Replaces the old grid pattern with a hand-authored, contemporary-art layout of squiggles, outlined shapes, asterisks, crescents, and dot clusters in a red / yellow / blue palette.

**Non-goals:** animated, random, or generative. Every element is deterministic — authored once, tweakable anytime in `proofmark_studio/static/hub/src/studio-canvas.jsx`.

## Layout philosophy

**Corner-clustered + edge ribbons.** Body text lives in the middle; art lives at the edges.

```
┌──────────────────────────────────────────┐
│ ▓▓                                   ▓▓▓ │  top-left + top-right clusters
│ ▓                                     ▓  │
│                                          │
│                                          │
│   (middle viewport ≈ 3 whisper-quiet     │
│    elements max — no visual conflict     │
│    with body text)                       │
│                                          │
│                                          │
│ ▓                                     ▓  │
│ ▓▓                                   ▓▓▓ │  bottom-left + bottom-right clusters
└──────────────────────────────────────────┘
   left edge ribbon           right edge ribbon
```

Top and bottom edge also carry wave-bar sines (blue above, red below) that read as horizontal ribbons at low opacity.

## Color palette

Reuses the hub's existing tokens. No new colors introduced.

| Token | Hex       | Role                |
|-------|-----------|---------------------|
| `r`   | `#ff6b8a` | Warm red / danger   |
| `y`   | `#f0c674` | Amber yellow / beta |
| `b`   | `#7cb0ff` | Soft blue / accent  |

Opacity comes from CSS `--art-opacity`:
- Dark theme: `0.14` (subtle on near-black background)
- Light theme: `0.22` (slightly more visible on warm cream)

Set in `index.html` under `body[data-theme="dark|light"]`.

## Element catalog

Authored positions live in `STUDIO_ELEMENTS` as an array. Edit any entry to tweak the art.

| Kind       | Count | Notes                                                          |
|------------|-------|----------------------------------------------------------------|
| `squiggle` | 6     | Cubic-Bézier wavy lines. 4 cluster + 2 edge ribbon             |
| `circle`   | 8     | Outlined only. Radii 14/16/18/22/26/30. Half dashed            |
| `triangle` | 4     | Outlined equilateral. Rotated for variety                      |
| `plus`     | 4     | Two perpendicular strokes                                      |
| `asterisk` | 5     | Three lines at 0° / 60° / 120°                                 |
| `crescent` | 3     | Outer arc + inner arc                                          |
| `dots`     | 4     | Clusters of 3–5 filled dots (r=2.2)                            |
| `wave`     | 2     | Full-viewport sine ribbons at y=28 and y=1182                  |
| **Total**  | **36**|                                                                |

The viewBox is `0 0 1600 1200` with `preserveAspectRatio="xMidYMid slice"`, so the SVG fills any viewport and element coordinates are stable.

## Tweaking

**Move an element:** edit its `cx`/`cy` (or the `M x,y` in the Bézier path for squiggles) in `STUDIO_ELEMENTS`.

**Change a color:** flip the `tone` field among `'r'`, `'y'`, `'b'`.

**Add an element:** append to `STUDIO_ELEMENTS` using an existing kind's shape. Or add a new kind by:
1. Add a renderer function (e.g. `StudioSpiral`).
2. Add to `STUDIO_RENDERERS` mapping.
3. Add entries to the catalog.

**Change density:** adjust `--art-opacity` in the CSS vars. Or delete/add entries in the catalog.

**Change palette:** edit `STUDIO_TONES` at the top of `studio-canvas.jsx`.

## Why deterministic, not generative

Three reasons:
1. **Reviewability** — you see exactly what ships. Screenshot diffs tell the truth.
2. **Stability** — no surprise re-renders or layout shifts when React state changes.
3. **Accessibility** — the art is `aria-hidden` and purely decorative; deterministic positions let us verify nothing overlaps interactive content.
