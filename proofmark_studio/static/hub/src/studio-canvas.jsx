/* StudioCanvas — contemporary-art background layer.
 *
 * Marker / paint-stroke vibe: thick rounded strokes, deliberately overflowing
 * the viewport, with a subtle SVG turbulence filter that nudges edges so each
 * stroke feels hand-laid rather than CAD-perfect.
 *
 * Design discipline:
 *   - Deterministic: ELEMENTS is a fixed list. No randomness. Tweak positions here.
 *   - Hero strokes (sw 14–22) start outside the viewBox and end outside — they read
 *     as confident brush sweeps that "transcend the screen", not boxed-in shapes.
 *   - Corner-clustered fillers stay (now sw 6–14) so the centre of the screen
 *     remains quiet enough for body text to compete.
 *   - Three tones reuse existing tokens: red #ff6b8a, yellow #f0c674, blue #7cb0ff.
 *
 * Filter: feTurbulence + feDisplacementMap is applied at the <g> level (one filter
 * pass for the whole layer) which is much cheaper than per-element filters.
 */

const STUDIO_TONES = {
  r: '#ff6b8a',  // red
  y: '#f0c674',  // yellow
  b: '#7cb0ff',  // blue
};

/* ---------- Element catalog — tweak here to adjust the layout ---------- */
const STUDIO_ELEMENTS = [
  // ── HERO SWEEPS — thick brush strokes that overflow the viewport ────
  { k:'squiggle', d:'M-200,260 C300,120 800,460 1300,200 S1900,320 2000,180', tone:'r', sw:20, op:0.55 },
  { k:'squiggle', d:'M-180,920 C400,1140 1000,780 1500,1020 S1900,940 2050,1080', tone:'b', sw:18, op:0.5 },
  { k:'squiggle', d:'M820,-160 C620,300 1080,720 880,1100 S780,1280 920,1400', tone:'y', sw:16, op:0.5 },

  // ── TOP-LEFT cluster ────────────────────────────────────────────────
  { k:'squiggle', d:'M20,60 C80,20 140,100 200,60 S320,80 380,40', tone:'r', sw:11 },
  { k:'circle',   cx:70,  cy:40,  r:24, tone:'b', sw:9, dashed:true },
  { k:'circle',   cx:300, cy:180, r:16, tone:'y', sw:10 },
  { k:'triangle', cx:400, cy:120, size:24, tone:'y', sw:9, rot:15 },
  { k:'plus',     cx:360, cy:100, size:18, tone:'r', sw:8 },
  { k:'asterisk', cx:180, cy:220, size:16, tone:'b', sw:7 },
  { k:'dots',     cx:220, cy:50,  dots:[[0,0,'r'],[14,8,'b'],[-8,16,'y'],[6,-10,'r']], r:5 },

  // ── TOP-RIGHT cluster ───────────────────────────────────────────────
  { k:'squiggle', d:'M1220,150 C1280,100 1360,170 1440,110 S1540,160 1580,90', tone:'b', sw:10 },
  { k:'circle',   cx:1480, cy:50,  r:32, tone:'r', sw:11, dashed:true },
  { k:'circle',   cx:1280, cy:180, r:20, tone:'y', sw:10 },
  { k:'triangle', cx:1380, cy:220, size:34, tone:'y', sw:10, rot:-10 },
  { k:'plus',     cx:1260, cy:40,  size:22, tone:'y', sw:8 },
  { k:'asterisk', cx:1560, cy:180, size:20, tone:'r', sw:8 },

  // ── BOTTOM-LEFT cluster ─────────────────────────────────────────────
  { k:'squiggle', d:'M20,1090 C100,1050 160,1130 240,1080 S340,1120 380,1070', tone:'y', sw:11 },
  { k:'circle',   cx:60,  cy:1140, r:28, tone:'r', sw:11 },
  { k:'circle',   cx:320, cy:1000, r:16, tone:'b', sw:9, dashed:true },
  { k:'triangle', cx:180, cy:1050, size:44, tone:'b', sw:11, rot:25 },
  { k:'crescent', cx:280, cy:1170, r:28, tone:'y', sw:10 },
  { k:'asterisk', cx:100, cy:1020, size:18, tone:'y', sw:8 },
  { k:'dots',     cx:350, cy:1150, dots:[[0,0,'r'],[10,-8,'b'],[-12,6,'r']], r:5 },

  // ── BOTTOM-RIGHT cluster ────────────────────────────────────────────
  { k:'squiggle', d:'M1220,1050 C1300,1090 1380,1020 1460,1060 S1540,1030 1580,1070', tone:'r', sw:10 },
  { k:'circle',   cx:1480, cy:1160, r:24, tone:'y', sw:10, dashed:true },
  { k:'circle',   cx:1280, cy:980,  r:18, tone:'b', sw:9 },
  { k:'triangle', cx:1560, cy:1080, size:40, tone:'r', sw:11, rot:-20 },
  { k:'crescent', cx:1240, cy:1120, r:26, tone:'y', sw:10 },
  { k:'plus',     cx:1420, cy:1000, size:20, tone:'y', sw:8 },
  { k:'asterisk', cx:1380, cy:1170, size:18, tone:'b', sw:8 },

  // ── LEFT edge ribbon ────────────────────────────────────────────────
  { k:'squiggle', d:'M40,600 C80,540 40,680 120,640', tone:'b', sw:9 },
  { k:'asterisk', cx:120, cy:450, size:16, tone:'y', sw:7 },
  { k:'dots',     cx:60,  cy:500, dots:[[0,0,'b'],[10,10,'y'],[-6,18,'b']], r:5 },

  // ── RIGHT edge ribbon ───────────────────────────────────────────────
  { k:'squiggle', d:'M1500,550 C1550,470 1580,580 1560,480', tone:'y', sw:9 },
  { k:'asterisk', cx:1560, cy:400, size:16, tone:'r', sw:7 },
  { k:'dots',     cx:1500, cy:800, dots:[[0,0,'r'],[-12,-8,'y'],[8,12,'b'],[18,2,'r']], r:5 },

  // ── CENTER (whisper-quiet — 3 elements max) ─────────────────────────
  { k:'crescent', cx:800,  cy:600, r:22, tone:'y', sw:8 },
  { k:'plus',     cx:600,  cy:320, size:14, tone:'b', sw:6 },
  { k:'asterisk', cx:1000, cy:880, size:14, tone:'r', sw:7 },

  // ── WAVE BARS (sine ribbons hugging the top + bottom edges) ─────────
  { k:'wave', y:28,   tone:'b', sw:10, amp:14, period:200 },
  { k:'wave', y:1182, tone:'r', sw:10, amp:14, period:240 },
];

/* ---------- Element renderers (sw defaults if element didn't override) ---------- */

const StudioSquiggle = ({ d, tone, sw = 10, op }) => (
  <path d={d} stroke={STUDIO_TONES[tone]} strokeWidth={sw} fill="none"
    strokeLinecap="round" strokeLinejoin="round" opacity={op} />
);

const StudioCircle = ({ cx, cy, r, tone, sw = 9, dashed }) => (
  <circle cx={cx} cy={cy} r={r} stroke={STUDIO_TONES[tone]} strokeWidth={sw} fill="none"
    strokeLinecap="round" strokeDasharray={dashed ? `${sw*1.6} ${sw*2.4}` : undefined} />
);

const StudioTriangle = ({ cx, cy, size, tone, sw = 9, rot = 0 }) => {
  const h = size * Math.sqrt(3) / 2;
  const pts = `${cx},${cy-h*0.66} ${cx-size/2},${cy+h*0.33} ${cx+size/2},${cy+h*0.33}`;
  return <polygon points={pts} stroke={STUDIO_TONES[tone]} strokeWidth={sw} fill="none"
    transform={`rotate(${rot} ${cx} ${cy})`} strokeLinejoin="round" strokeLinecap="round" />;
};

const StudioAsterisk = ({ cx, cy, size, tone, sw = 7 }) => (
  <g stroke={STUDIO_TONES[tone]} strokeWidth={sw} strokeLinecap="round">
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} />
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} transform={`rotate(60 ${cx} ${cy})`} />
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} transform={`rotate(120 ${cx} ${cy})`} />
  </g>
);

const StudioPlus = ({ cx, cy, size, tone, sw = 7 }) => (
  <g stroke={STUDIO_TONES[tone]} strokeWidth={sw} strokeLinecap="round">
    <line x1={cx-size/2} y1={cy} x2={cx+size/2} y2={cy} />
    <line x1={cx} y1={cy-size/2} x2={cx} y2={cy+size/2} />
  </g>
);

const StudioCrescent = ({ cx, cy, r, tone, sw = 9 }) => {
  // Outer arc + inner offset arc — outline-only crescent
  const d = `M${cx-r},${cy} A${r},${r} 0 0,1 ${cx+r},${cy} A${r*0.75},${r*0.6} 0 0,0 ${cx-r},${cy} Z`;
  return <path d={d} stroke={STUDIO_TONES[tone]} strokeWidth={sw} fill="none"
    strokeLinejoin="round" strokeLinecap="round" />;
};

const StudioDots = ({ cx, cy, dots, r = 5 }) => (
  <g>
    {dots.map(([dx, dy, tone], i) => (
      <circle key={i} cx={cx+dx} cy={cy+dy} r={r} fill={STUDIO_TONES[tone]} />
    ))}
  </g>
);

const StudioWave = ({ y, tone, sw, amp, period }) => {
  // Sine-like cubic-Bézier path; extend slightly past viewBox so ends are clean.
  let d = `M-100,${y}`;
  for (let x = -100; x < 1700; x += period) {
    d += ` C${x + period/4},${y - amp} ${x + 3*period/4},${y + amp} ${x + period},${y}`;
  }
  return <path d={d} stroke={STUDIO_TONES[tone]} strokeWidth={sw} fill="none"
    strokeLinecap="round" opacity="0.55" />;
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
    overflow="visible" style={{ overflow: 'visible' }}
    xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <defs>
      {/* Brush-edge nudge: low-frequency noise displaces strokes by a few pixels
          so they read as hand-laid marker, not CAD vector. Fixed seed = stable
          across renders. */}
      <filter id="brush" x="-5%" y="-5%" width="110%" height="110%">
        <feTurbulence type="fractalNoise" baseFrequency="0.025" numOctaves="2" seed="7"/>
        <feDisplacementMap in="SourceGraphic" scale="5"/>
      </filter>
    </defs>
    <g filter="url(#brush)">
      {STUDIO_ELEMENTS.map((el, i) => {
        const R = STUDIO_RENDERERS[el.k];
        return R ? <R key={i} {...el} /> : null;
      })}
    </g>
  </svg>
);

/* ---------- Mount into its own root (separate from the React app) ---------- */
const __studioCanvasRoot = document.getElementById('studio-canvas-root');
if (__studioCanvasRoot) {
  ReactDOM.createRoot(__studioCanvasRoot).render(<StudioCanvas />);
}

window.StudioCanvas = StudioCanvas;
