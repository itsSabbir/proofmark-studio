/* StudioCanvas — contemporary-art background layer.
 *
 * Replaces the old grid. Scatters hand-drawn-style squiggles, outlined shapes,
 * asterisks, crescents, dot clusters, and edge wave ribbons across the viewport.
 *
 * Design discipline:
 *   - Deterministic: ELEMENTS is a fixed list. No randomness. Tweak positions here.
 *   - Corner-clustered: most density at TL/TR/BL/BR + edge ribbons; center viewport
 *     is nearly empty so body text never competes with art.
 *   - Low opacity (set in CSS via --art-opacity) so it reads as texture, not content.
 *   - Three tones reuse existing tokens: red #ff6b8a, yellow #f0c674, blue #7cb0ff.
 *
 * ViewBox is 1600x1200 with preserveAspectRatio="xMidYMid slice" so the SVG fills
 * any window size. Elements positioned in viewBox coordinates.
 */

const STUDIO_TONES = {
  r: '#ff6b8a',  // red
  y: '#f0c674',  // yellow
  b: '#7cb0ff',  // blue
};

/* ---------- Element catalog — tweak here to adjust the layout ---------- */
const STUDIO_ELEMENTS = [
  // ── TOP-LEFT cluster ────────────────────────────────────────────────
  { k:'squiggle', d:'M20,60 C80,20 140,100 200,60 S320,80 380,40', tone:'r', sw:1.8 },
  { k:'circle',   cx:70,  cy:40,  r:22, tone:'b', dashed:true },
  { k:'circle',   cx:300, cy:180, r:14, tone:'y' },
  { k:'triangle', cx:400, cy:120, size:20, tone:'y', rot:15 },
  { k:'plus',     cx:360, cy:100, size:14, tone:'r' },
  { k:'asterisk', cx:180, cy:220, size:12, tone:'b' },
  { k:'dots',     cx:220, cy:50,  dots:[[0,0,'r'],[10,6,'b'],[-6,12,'y'],[4,-8,'r']] },

  // ── TOP-RIGHT cluster ───────────────────────────────────────────────
  { k:'squiggle', d:'M1220,150 C1280,100 1360,170 1440,110 S1540,160 1580,90', tone:'b', sw:1.6 },
  { k:'circle',   cx:1480, cy:50,  r:30, tone:'r', dashed:true },
  { k:'circle',   cx:1280, cy:180, r:18, tone:'y' },
  { k:'triangle', cx:1380, cy:220, size:30, tone:'y', rot:-10 },
  { k:'plus',     cx:1260, cy:40,  size:18, tone:'y' },
  { k:'asterisk', cx:1560, cy:180, size:16, tone:'r' },

  // ── BOTTOM-LEFT cluster ─────────────────────────────────────────────
  { k:'squiggle', d:'M20,1090 C100,1050 160,1130 240,1080 S340,1120 380,1070', tone:'y', sw:1.8 },
  { k:'circle',   cx:60,  cy:1140, r:26, tone:'r' },
  { k:'circle',   cx:320, cy:1000, r:14, tone:'b', dashed:true },
  { k:'triangle', cx:180, cy:1050, size:40, tone:'b', rot:25 },
  { k:'crescent', cx:280, cy:1170, r:24, tone:'y' },
  { k:'asterisk', cx:100, cy:1020, size:14, tone:'y' },
  { k:'dots',     cx:350, cy:1150, dots:[[0,0,'r'],[8,-6,'b'],[-10,4,'r']] },

  // ── BOTTOM-RIGHT cluster ────────────────────────────────────────────
  { k:'squiggle', d:'M1220,1050 C1300,1090 1380,1020 1460,1060 S1540,1030 1580,1070', tone:'r', sw:1.6 },
  { k:'circle',   cx:1480, cy:1160, r:22, tone:'y', dashed:true },
  { k:'circle',   cx:1280, cy:980,  r:16, tone:'b' },
  { k:'triangle', cx:1560, cy:1080, size:36, tone:'r', rot:-20 },
  { k:'crescent', cx:1240, cy:1120, r:22, tone:'y' },
  { k:'plus',     cx:1420, cy:1000, size:16, tone:'y' },
  { k:'asterisk', cx:1380, cy:1170, size:14, tone:'b' },

  // ── LEFT edge ribbon (y 300-900) ────────────────────────────────────
  { k:'squiggle', d:'M40,600 C80,540 40,680 120,640', tone:'b', sw:1.4 },
  { k:'asterisk', cx:120, cy:450, size:12, tone:'y' },
  { k:'dots',     cx:60,  cy:500, dots:[[0,0,'b'],[8,8,'y'],[-4,14,'b']] },

  // ── RIGHT edge ribbon (y 300-900) ───────────────────────────────────
  { k:'squiggle', d:'M1500,550 C1550,470 1580,580 1560,480', tone:'y', sw:1.4 },
  { k:'asterisk', cx:1560, cy:400, size:12, tone:'r' },
  { k:'dots',     cx:1500, cy:800, dots:[[0,0,'r'],[-10,-6,'y'],[6,10,'b'],[14,0,'r']] },

  // ── CENTER (whisper-quiet — 3 elements max) ─────────────────────────
  { k:'crescent', cx:800,  cy:600, r:18, tone:'y' },
  { k:'plus',     cx:600,  cy:320, size:10, tone:'b' },
  { k:'asterisk', cx:1000, cy:880, size:10, tone:'r' },

  // ── WAVE BARS (horizontal sines at top + bottom edges) ──────────────
  { k:'wave', y:28,   tone:'b', sw:1.2, amp:10, period:160 },
  { k:'wave', y:1182, tone:'r', sw:1.2, amp:10, period:200 },
];

/* ---------- Element renderers ---------- */

const StudioSquiggle = ({ d, tone, sw }) => (
  <path d={d} stroke={STUDIO_TONES[tone]} strokeWidth={sw} fill="none" strokeLinecap="round" />
);

const StudioCircle = ({ cx, cy, r, tone, dashed }) => (
  <circle cx={cx} cy={cy} r={r} stroke={STUDIO_TONES[tone]} strokeWidth="1.5" fill="none"
    strokeDasharray={dashed ? '4 6' : undefined} />
);

const StudioTriangle = ({ cx, cy, size, tone, rot = 0 }) => {
  const h = size * Math.sqrt(3) / 2;
  const pts = `${cx},${cy-h*0.66} ${cx-size/2},${cy+h*0.33} ${cx+size/2},${cy+h*0.33}`;
  return <polygon points={pts} stroke={STUDIO_TONES[tone]} strokeWidth="1.4" fill="none"
    transform={`rotate(${rot} ${cx} ${cy})`} strokeLinejoin="round" />;
};

const StudioAsterisk = ({ cx, cy, size, tone }) => (
  <g stroke={STUDIO_TONES[tone]} strokeWidth="1.4" strokeLinecap="round">
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} />
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} transform={`rotate(60 ${cx} ${cy})`} />
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} transform={`rotate(120 ${cx} ${cy})`} />
  </g>
);

const StudioPlus = ({ cx, cy, size, tone }) => (
  <g stroke={STUDIO_TONES[tone]} strokeWidth="1.5" strokeLinecap="round">
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} />
    <line x1={cx} y1={cy-size/2} x2={cx} y2={cy+size/2} />
  </g>
);

const StudioCrescent = ({ cx, cy, r, tone }) => {
  // Outer arc then inner arc offset, forming a crescent outline
  const d = `M${cx-r},${cy} A${r},${r} 0 0,1 ${cx+r},${cy} A${r*0.75},${r*0.6} 0 0,0 ${cx-r},${cy} Z`;
  return <path d={d} stroke={STUDIO_TONES[tone]} strokeWidth="1.4" fill="none" strokeLinejoin="round" />;
};

const StudioDots = ({ cx, cy, dots }) => (
  <g>
    {dots.map(([dx, dy, tone], i) => (
      <circle key={i} cx={cx+dx} cy={cy+dy} r={2.2} fill={STUDIO_TONES[tone]} />
    ))}
  </g>
);

const StudioWave = ({ y, tone, sw, amp, period }) => {
  // Build a sine-like cubic-Bézier path across the full 1600 viewBox width.
  let d = `M0,${y}`;
  for (let x = 0; x < 1600; x += period) {
    d += ` C${x + period/4},${y - amp} ${x + 3*period/4},${y + amp} ${x + period},${y}`;
  }
  return <path d={d} stroke={STUDIO_TONES[tone]} strokeWidth={sw} fill="none" opacity="0.55" />;
};

/* ---------- Kind → renderer dispatch ---------- */
const STUDIO_RENDERERS = {
  squiggle: StudioSquiggle,
  circle:   StudioCircle,
  triangle: StudioTriangle,
  asterisk: StudioAsterisk,
  plus:     StudioPlus,
  crescent: StudioCrescent,
  dots:     StudioDots,
  wave:     StudioWave,
};

/* ---------- Main component ---------- */
const StudioCanvas = () => (
  <svg viewBox="0 0 1600 1200" preserveAspectRatio="xMidYMid slice"
    xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    {STUDIO_ELEMENTS.map((el, i) => {
      const R = STUDIO_RENDERERS[el.k];
      return R ? <R key={i} {...el} /> : null;
    })}
  </svg>
);

/* ---------- Mount into its own root (separate from the React app) ---------- */
const __studioCanvasRoot = document.getElementById('studio-canvas-root');
if (__studioCanvasRoot) {
  ReactDOM.createRoot(__studioCanvasRoot).render(<StudioCanvas />);
}

window.StudioCanvas = StudioCanvas;
