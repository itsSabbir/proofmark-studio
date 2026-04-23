/* Big colored tool illustrations — SmallPDF/iLovePDF-style tiles */

const Illust = ({ name, tone = '#7cb0ff', size = 72 }) => {
  const s = size;
  const c = tone;
  const p = (o=0.18) => `color-mix(in oklab, ${c} ${o*100}%, transparent)`;
  const doc = (x, y, w, h, color = c, fill = p(0.14)) => (
    <g>
      <rect x={x} y={y} width={w} height={h} rx="3" fill={fill} stroke={color} strokeWidth="1.8"/>
      <path d={`M${x+w-6} ${y} L${x+w} ${y+6} L${x+w-6} ${y+6} Z`} fill={color}/>
    </g>
  );

  const common = { width: s, height: s, viewBox:'0 0 64 64', xmlns:'http://www.w3.org/2000/svg' };

  switch (name) {
    case 'merge': return (
      <svg {...common}>
        {doc(8, 10, 20, 28)}
        {doc(36, 10, 20, 28)}
        <path d="M20 40 Q20 48 32 48 Q44 48 44 40" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M28 48 L32 52 L36 48" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <rect x="22" y="54" width="20" height="6" rx="2" fill={c}/>
      </svg>
    );
    case 'split': return (
      <svg {...common}>
        <rect x="22" y="4" width="20" height="22" rx="3" fill={p(0.14)} stroke={c} strokeWidth="1.8"/>
        <path d="M32 28 L32 34" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M16 34 L32 34 L48 34" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M16 34 L16 40 M48 34 L48 40" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        {doc(6, 40, 20, 20)}
        {doc(38, 40, 20, 20)}
      </svg>
    );
    case 'extract': return (
      <svg {...common}>
        <rect x="8" y="6" width="30" height="40" rx="3" fill={p(0.12)} stroke={c} strokeWidth="1.8"/>
        <path d="M14 16h18M14 22h18M14 28h12" stroke={c} strokeWidth="1.6" strokeLinecap="round"/>
        <rect x="28" y="30" width="28" height="26" rx="3" fill={tone} fillOpacity="0.16" stroke={c} strokeWidth="1.8"/>
        <path d="M34 40h16M34 46h10" stroke={c} strokeWidth="1.6" strokeLinecap="round"/>
        <path d="M22 26 L28 32 M28 32 L28 28 M28 32 L32 32" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
      </svg>
    );
    case 'grid': return (
      <svg {...common}>
        {doc(6, 6, 22, 22)}
        {doc(36, 6, 22, 22)}
        {doc(6, 36, 22, 22)}
        <rect x="36" y="36" width="22" height="22" rx="3" fill={c} fillOpacity="0.3" stroke={c} strokeWidth="1.8" strokeDasharray="3 3"/>
      </svg>
    );
    case 'compress': return (
      <svg {...common}>
        {doc(16, 10, 32, 44)}
        <path d="M10 22 L16 28 M10 22 L16 22 M10 22 L10 28" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M54 22 L48 28 M54 22 L48 22 M54 22 L54 28" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M10 42 L16 36 M10 42 L16 42 M10 42 L10 36" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M54 42 L48 36 M54 42 L48 42 M54 42 L54 36" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <text x="32" y="36" textAnchor="middle" fontFamily="Geist Mono, monospace" fontSize="9" fontWeight="700" fill={c}>ZIP</text>
      </svg>
    );
    case 'rotate': return (
      <svg {...common}>
        <g transform="rotate(12 32 32)">{doc(18, 12, 28, 36)}</g>
        <path d="M48 20 A18 18 0 1 1 16 22" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M48 14 L48 22 L40 22" fill="none" stroke={c} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    );
    case 'minus': return (
      <svg {...common}>
        {doc(18, 8, 28, 44)}
        <circle cx="46" cy="48" r="10" fill={c}/>
        <path d="M40 48 L52 48" stroke="#fff" strokeWidth="2.4" strokeLinecap="round"/>
      </svg>
    );
    // File-type tiles
    case 'docx':
    case 'xlsx':
    case 'pptx':
    case 'jpg':
    case 'png':
    case 'txt':
    case 'md':
    case 'html':
    case 'ocr': {
      const labels = { docx:'DOC', xlsx:'XLS', pptx:'PPT', jpg:'JPG', png:'PNG', txt:'TXT', md:'MD', html:'HTML', ocr:'OCR' };
      return (
        <svg {...common}>
          <rect x="10" y="6" width="32" height="44" rx="3" fill="#fff" fillOpacity="0.04" stroke={c} strokeWidth="1.8"/>
          <path d="M34 6 L42 14 L34 14 Z" fill={c}/>
          <rect x="16" y="32" width="36" height="20" rx="4" fill={c}/>
          <text x="34" y="46" textAnchor="middle" fontFamily="Geist Mono, monospace" fontSize={labels[name].length > 3 ? 8 : 10} fontWeight="800" fill="#fff">{labels[name]}</text>
          <path d="M16 18h14M16 23h10" stroke={c} strokeWidth="1.6" strokeLinecap="round"/>
        </svg>
      );
    }
    case 'pencil': return (
      <svg {...common}>
        {doc(10, 8, 32, 44)}
        <path d="M16 20h20M16 26h20M16 32h12" stroke={c} strokeWidth="1.6" strokeLinecap="round"/>
        <g transform="rotate(-25 44 44)">
          <rect x="36" y="40" width="24" height="8" rx="1" fill={c}/>
          <rect x="54" y="40" width="6" height="8" fill="#fff" fillOpacity="0.3"/>
          <path d="M60 44 L66 44" stroke={c} strokeWidth="2"/>
        </g>
      </svg>
    );
    case 'pen': return (
      <svg {...common}>
        {doc(10, 8, 32, 44)}
        <path d="M16 18h20M16 24h14" stroke={c} strokeWidth="1.6" strokeLinecap="round"/>
        <circle cx="38" cy="40" r="3" fill={c}/>
        <path d="M20 48 Q28 40 38 40" stroke={c} strokeWidth="2" fill="none" strokeLinecap="round"/>
        <rect x="14" y="46" width="10" height="3" rx="1" fill={c}/>
      </svg>
    );
    case 'book': return (
      <svg {...common}>
        <path d="M8 10 L8 50 Q18 44 32 46 Q46 44 56 50 L56 10 Q46 4 32 6 Q18 4 8 10 Z" fill={p(0.14)} stroke={c} strokeWidth="1.8"/>
        <path d="M32 6 L32 46" stroke={c} strokeWidth="1.6"/>
        <path d="M14 16 L26 14 M14 22 L26 20 M38 14 L50 16 M38 20 L50 22" stroke={c} strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    );
    case 'hash': return (
      <svg {...common}>
        {doc(10, 8, 32, 44)}
        <path d="M20 22 L18 40 M30 22 L28 40 M16 28h16M14 34h16" stroke={c} strokeWidth="1.8" strokeLinecap="round" fill="none"/>
        <circle cx="48" cy="50" r="10" fill={c}/>
        <text x="48" y="54" textAnchor="middle" fontFamily="Geist Mono, monospace" fontSize="11" fontWeight="800" fill="#fff">#</text>
      </svg>
    );
    case 'crop': return (
      <svg {...common}>
        <rect x="8" y="8" width="40" height="40" rx="2" fill={p(0.1)} stroke={c} strokeWidth="1.6" strokeDasharray="3 3"/>
        <path d="M16 4 L16 56 M4 16 L56 16" stroke={c} strokeWidth="2.2" strokeLinecap="round"/>
        <path d="M48 8 L56 8 L56 16" stroke={c} strokeWidth="2.2" strokeLinecap="round" fill="none"/>
        <path d="M8 48 L16 48 L16 56" stroke={c} strokeWidth="2.2" strokeLinecap="round" fill="none"/>
      </svg>
    );
    case 'redact': return (
      <svg {...common}>
        {doc(10, 8, 44, 48)}
        <rect x="16" y="18" width="28" height="4" fill={c}/>
        <rect x="16" y="26" width="20" height="4" fill={c}/>
        <rect x="16" y="34" width="24" height="4" fill={c}/>
        <rect x="16" y="42" width="14" height="4" fill={c}/>
      </svg>
    );
    case 'water': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <g transform="rotate(-20 32 32)" opacity="0.7">
          <text x="32" y="36" textAnchor="middle" fontFamily="Instrument Serif, serif" fontSize="14" fill={c}>DRAFT</text>
        </g>
        <path d="M14 14h8M14 50h8M42 14h8M42 50h8" stroke={c} strokeWidth="1.4" strokeLinecap="round" opacity="0.5"/>
      </svg>
    );
    case 'form': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <rect x="14" y="16" width="20" height="4" rx="1" fill={c} opacity="0.5"/>
        <rect x="14" y="24" width="36" height="6" rx="2" fill="#fff" fillOpacity="0.05" stroke={c} strokeWidth="1.4"/>
        <rect x="14" y="34" width="14" height="4" rx="1" fill={c} opacity="0.5"/>
        <rect x="14" y="42" width="36" height="6" rx="2" fill="#fff" fillOpacity="0.05" stroke={c} strokeWidth="1.4"/>
        <path d="M44 45 L46 47 L50 43" stroke={c} strokeWidth="1.8" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    );
    case 'sig': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <path d="M14 38 Q18 24 24 32 Q30 40 36 26 Q40 18 46 30" fill="none" stroke={c} strokeWidth="2.2" strokeLinecap="round"/>
        <path d="M14 46 L50 46" stroke={c} strokeWidth="1.4" strokeLinecap="round" opacity="0.5"/>
      </svg>
    );
    case 'send': return (
      <svg {...common}>
        <path d="M8 32 L56 8 L46 56 L30 40 Z" fill={p(0.18)} stroke={c} strokeWidth="2" strokeLinejoin="round"/>
        <path d="M30 40 L56 8" stroke={c} strokeWidth="2"/>
      </svg>
    );
    case 'unlock': return (
      <svg {...common}>
        {doc(10, 26, 44, 32)}
        <path d="M18 26 L18 18 A10 10 0 0 1 38 18" fill="none" stroke={c} strokeWidth="2.2" strokeLinecap="round"/>
        <circle cx="32" cy="42" r="3" fill={c}/>
      </svg>
    );
    case 'lock': return (
      <svg {...common}>
        {doc(10, 26, 44, 32)}
        <path d="M20 26 L20 18 A12 12 0 0 1 44 18 L44 26" fill="none" stroke={c} strokeWidth="2.2" strokeLinecap="round"/>
        <circle cx="32" cy="42" r="3" fill={c}/>
      </svg>
    );
    case 'layers': return (
      <svg {...common}>
        <path d="M32 6 L56 18 L32 30 L8 18 Z" fill={p(0.2)} stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
        <path d="M8 30 L32 42 L56 30" fill="none" stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
        <path d="M8 42 L32 54 L56 42" fill="none" stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
      </svg>
    );
    // Proof
    case 'aa': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <path d="M14 42 L22 20 L30 42 M16 36 L28 36" stroke={c} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
        <path d="M34 42 L42 20 L50 42 M36 36 L48 36" stroke={c} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" fill="none" opacity="0.55"/>
      </svg>
    );
    case 'zw': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <text x="32" y="40" textAnchor="middle" fontFamily="Geist Mono, monospace" fontSize="16" fontWeight="700" fill={c}>a·b</text>
        <path d="M30 20 L34 20" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <circle cx="32" cy="20" r="1.5" fill={c}/>
      </svg>
    );
    case 'space': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <path d="M14 30 L14 36 L50 36 L50 30" fill="none" stroke={c} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"/>
        <circle cx="22" cy="22" r="1.4" fill={c}/><circle cx="32" cy="22" r="1.4" fill={c}/><circle cx="42" cy="22" r="1.4" fill={c}/>
      </svg>
    );
    case 'quote': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <path d="M18 24 Q14 26 14 32 L14 40 L22 40 L22 32 L18 32 Q18 28 22 26 Z" fill={c}/>
        <path d="M38 24 Q34 26 34 32 L34 40 L42 40 L42 32 L38 32 Q38 28 42 26 Z" fill={c}/>
      </svg>
    );
    case 'report': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <rect x="14" y="40" width="4" height="8" fill={c}/>
        <rect x="22" y="30" width="4" height="18" fill={c}/>
        <rect x="30" y="34" width="4" height="14" fill={c}/>
        <rect x="38" y="22" width="4" height="26" fill={c}/>
        <rect x="46" y="28" width="4" height="20" fill={c}/>
        <path d="M14 18h30" stroke={c} strokeWidth="1.4" strokeLinecap="round" opacity="0.5"/>
      </svg>
    );
    // AI
    case 'ai': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <path d="M32 16 L36 26 L46 28 L36 30 L32 40 L28 30 L18 28 L28 26 Z" fill={c}/>
        <circle cx="44" cy="18" r="2" fill={c}/>
        <circle cx="20" cy="42" r="2" fill={c}/>
      </svg>
    );
    case 'chat': return (
      <svg {...common}>
        <rect x="6" y="12" width="40" height="28" rx="6" fill={p(0.16)} stroke={c} strokeWidth="1.8"/>
        <path d="M14 40 L14 48 L22 40" fill={p(0.16)} stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
        <circle cx="18" cy="26" r="2" fill={c}/><circle cx="26" cy="26" r="2" fill={c}/><circle cx="34" cy="26" r="2" fill={c}/>
        <rect x="40" y="28" width="20" height="22" rx="4" fill={p(0.28)} stroke={c} strokeWidth="1.6"/>
        <path d="M44 36h12M44 40h8" stroke={c} strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    );
    case 'sum': return (
      <svg {...common}>
        {doc(6, 8, 26, 48)}
        <path d="M10 16h18M10 22h18M10 28h14M10 34h18M10 40h12" stroke={c} strokeWidth="1.4" strokeLinecap="round"/>
        <path d="M36 32 L44 32" stroke={c} strokeWidth="2" strokeLinecap="round"/>
        <path d="M41 28 L44 32 L41 36" stroke={c} strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
        {doc(46, 20, 14, 24)}
        <path d="M50 28h6M50 32h4" stroke={c} strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    );
    case 'globe': return (
      <svg {...common}>
        <circle cx="32" cy="32" r="22" fill={p(0.14)} stroke={c} strokeWidth="1.8"/>
        <path d="M10 32 L54 32 M32 10 C20 22 20 42 32 54 C44 42 44 22 32 10" fill="none" stroke={c} strokeWidth="1.6"/>
        <path d="M14 22 L50 22 M14 42 L50 42" stroke={c} strokeWidth="1.4" opacity="0.6"/>
      </svg>
    );
    // Workflow
    case 'inbox': return (
      <svg {...common}>
        <path d="M10 10 L14 34 L50 34 L54 10" fill={p(0.12)} stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
        <path d="M6 34 L14 34 L18 42 L46 42 L50 34 L58 34 L58 54 L6 54 Z" fill={p(0.2)} stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
        <path d="M32 12 L32 24 M26 20 L32 26 L38 20" stroke={c} strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    );
    case 'stack': return (
      <svg {...common}>
        <rect x="8" y="10" width="48" height="10" rx="2" fill={p(0.18)} stroke={c} strokeWidth="1.6"/>
        <rect x="8" y="24" width="48" height="10" rx="2" fill={p(0.28)} stroke={c} strokeWidth="1.6"/>
        <rect x="8" y="38" width="48" height="10" rx="2" fill={c} fillOpacity="0.4" stroke={c} strokeWidth="1.6"/>
        <circle cx="48" cy="15" r="1.8" fill={c}/>
        <circle cx="48" cy="29" r="1.8" fill={c}/>
        <circle cx="48" cy="43" r="1.8" fill={c}/>
      </svg>
    );
    case 'box': return (
      <svg {...common}>
        <path d="M32 8 L56 18 L32 28 L8 18 Z" fill={p(0.18)} stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
        <path d="M8 18 L8 46 L32 56 L32 28" fill={p(0.12)} stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
        <path d="M56 18 L56 46 L32 56" fill={p(0.28)} stroke={c} strokeWidth="1.8" strokeLinejoin="round"/>
      </svg>
    );
    case 'ruler': return (
      <svg {...common}>
        <rect x="6" y="22" width="52" height="20" rx="2" fill={p(0.14)} stroke={c} strokeWidth="1.8"/>
        <path d="M14 22 L14 30 M22 22 L22 34 M30 22 L30 28 M38 22 L38 34 M46 22 L46 28 M54 22 L54 34" stroke={c} strokeWidth="1.6" strokeLinecap="round"/>
      </svg>
    );
    case 'feed': return (
      <svg {...common}>
        {doc(8, 8, 48, 48)}
        <path d="M16 48 A20 20 0 0 1 36 48" fill="none" stroke={c} strokeWidth="2.2" strokeLinecap="round"/>
        <path d="M16 40 A12 12 0 0 1 28 48" fill="none" stroke={c} strokeWidth="2.2" strokeLinecap="round"/>
        <circle cx="18" cy="48" r="2.4" fill={c}/>
      </svg>
    );
    default: return (
      <svg {...common}>
        {doc(10, 8, 44, 48)}
      </svg>
    );
  }
};

window.Illust = Illust;
