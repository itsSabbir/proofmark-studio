/* ProofMark Studio — main app: tile-led, grouped, SmallPDF-ish */

const { useState, useEffect, useMemo, useRef, useCallback } = React;

/* ---------- Shortcuts cheat-sheet ----------
 * `?` opens this modal; it lists every keyboard binding the hub registers
 * so users don't have to guess. Kept alongside the palette because they
 * share a similar chrome shape. */
const SHORTCUTS = [
  { combo: ['Cmd+K', 'Ctrl+K'],  label: 'Open command palette' },
  { combo: ['?'],                label: 'Open this cheat-sheet' },
  { combo: ['H'],                label: 'Go to Home' },
  { combo: ['G'],                label: 'Go to All tools' },
  { combo: ['R'],                label: 'Go to Recent' },
  { combo: ['P'],                label: 'Go to Pinned' },
  { combo: ['W'],                label: 'Go to Workflow' },
  { combo: ['M'],                label: 'Go to Platform map' },
  { combo: ['Esc'],              label: 'Close dialogs / drawers' },
];

const ShortcutsModal = ({ open, onClose }) => {
  useEffect(() => {
    if (!open) return;
    const h = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div onClick={onClose} style={{
      position:'fixed', inset:0, zIndex:110,
      background:'color-mix(in oklab, var(--bg-inset) 60%, transparent)',
      backdropFilter:'blur(6px)',
      display:'flex', alignItems:'flex-start', justifyContent:'center',
      paddingTop:'12vh', animation:'fadeInUp .14s ease',
    }}>
      <div onClick={e => e.stopPropagation()} role="dialog" aria-label="Keyboard shortcuts" style={{
        width:'min(540px, 92vw)', borderRadius:16,
        background:'var(--bg-elev)', border:'1px solid var(--border-strong)',
        boxShadow:'var(--shadow-lg)', overflow:'hidden',
      }}>
        <div style={{ display:'flex', alignItems:'center', gap:10, padding:'14px 18px', borderBottom:'1px solid var(--border)' }}>
          <span style={{ fontSize:10.5, fontFamily:'var(--font-mono)', color:'var(--text-dim)', textTransform:'uppercase', letterSpacing:'.1em', fontWeight:600 }}>Keyboard shortcuts</span>
          <Kbd style={{ marginLeft:'auto' }}>Esc</Kbd>
        </div>
        <div style={{ padding:'8px 0' }}>
          {SHORTCUTS.map((s, i) => (
            <div key={i} style={{ display:'flex', alignItems:'center', gap:12, padding:'10px 18px', borderBottom: i === SHORTCUTS.length-1 ? 0 : '1px solid var(--border)' }}>
              <div style={{ display:'flex', gap:6 }}>
                {s.combo.map((c, j) => <Kbd key={j}>{c}</Kbd>)}
              </div>
              <span style={{ marginLeft:'auto', fontSize:13, color:'var(--text-muted)' }}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/* ---------- Command Palette ---------- */
const CommandPalette = ({ open, onClose, onRun }) => {
  const [q, setQ] = useState('');
  const [idx, setIdx] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open) { setQ(''); setIdx(0); setTimeout(() => inputRef.current?.focus(), 20); }
  }, [open]);

  const results = useMemo(() => {
    const tools = window.PM_TOOLS;
    const term = q.trim().toLowerCase();
    if (!term) {
      return [
        { group:'Popular',   items: tools.filter(t => t.popular).slice(0,6) },
        { group:'Pinned',    items: tools.filter(t => t.pin).slice(0,4) },
      ];
    }
    const hits = tools.filter(t =>
      t.title.toLowerCase().includes(term) ||
      t.desc.toLowerCase().includes(term) ||
      t.cat.includes(term) ||
      t.slug.includes(term)
    );
    return [{ group:`${hits.length} result${hits.length===1?'':'s'}`, items: hits.slice(0, 14) }];
  }, [q]);

  const flat = results.flatMap(g => g.items);

  useEffect(() => {
    if (!open) return;
    const h = (e) => {
      if (e.key === 'Escape') onClose();
      else if (e.key === 'ArrowDown') { e.preventDefault(); setIdx(i => Math.min(i+1, flat.length-1)); }
      else if (e.key === 'ArrowUp')   { e.preventDefault(); setIdx(i => Math.max(i-1, 0)); }
      else if (e.key === 'Enter')     { e.preventDefault(); const t = flat[idx]; if (t) { onRun(t); onClose(); } }
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open, flat, idx, onClose, onRun]);

  if (!open) return null;
  let running = -1;
  return (
    <div onClick={onClose} style={{
      position:'fixed', inset:0, zIndex:100,
      background:'color-mix(in oklab, var(--bg-inset) 60%, transparent)',
      backdropFilter:'blur(6px)',
      display:'flex', alignItems:'flex-start', justifyContent:'center',
      paddingTop:'14vh', animation:'fadeInUp .14s ease',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        width:'min(640px, 92vw)', borderRadius:16,
        background:'var(--bg-elev)', border:'1px solid var(--border-strong)',
        boxShadow:'var(--shadow-lg)', overflow:'hidden',
      }}>
        <div style={{ display:'flex', alignItems:'center', gap:10, padding:'14px 16px', borderBottom:'1px solid var(--border)' }}>
          <Glyph name="search" size={16}/>
          <input ref={inputRef} value={q} onChange={e=>{setQ(e.target.value); setIdx(0);}}
            placeholder="Search 50+ tools, workflows…"
            style={{ flex:1, border:0, outline:0, background:'transparent', color:'var(--text)', fontSize:15, fontFamily:'inherit' }}/>
          <Kbd>Esc</Kbd>
        </div>
        <div style={{ maxHeight:'52vh', overflowY:'auto', padding:'8px' }}>
          {results.map((g, gi) => (
            <div key={gi} style={{ marginBottom:8 }}>
              <div style={{ padding:'8px 12px 6px', fontSize:10, color:'var(--text-dim)', textTransform:'uppercase', letterSpacing:'.1em', fontWeight:600, fontFamily:'var(--font-mono)' }}>{g.group}</div>
              {g.items.length === 0 && <div style={{ padding:'14px 12px', color:'var(--text-muted)', fontSize:13 }}>No matches.</div>}
              {g.items.map(t => {
                running++;
                const sel = running === idx;
                const myIdx = running;
                const grp = window.PM_GROUPS.find(x=>x.id===t.group);
                return (
                  <button key={t.slug} onClick={() => { onRun(t); onClose(); }} onMouseEnter={() => setIdx(myIdx)} style={{
                    display:'flex', alignItems:'center', gap:12,
                    width:'100%', padding:'9px 12px', borderRadius:9,
                    background: sel ? 'var(--bg-elev-2)' : 'transparent',
                    border:'1px solid ' + (sel ? 'var(--border)' : 'transparent'),
                    color:'var(--text)', cursor:'pointer', textAlign:'left',
                  }}>
                    <div style={{ width:36, height:36, borderRadius:8, display:'grid', placeItems:'center', background:`color-mix(in oklab, ${grp?.tone||'#7cb0ff'} 14%, transparent)`, border:`1px solid color-mix(in oklab, ${grp?.tone||'#7cb0ff'} 30%, transparent)`, flexShrink:0 }}>
                      <Illust name={t.icon} tone={grp?.tone||'#7cb0ff'} size={24}/>
                    </div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ fontSize:13.5, fontWeight:500 }}>{t.title}</div>
                      <div style={{ fontSize:11.5, color:'var(--text-muted)', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{t.desc}</div>
                    </div>
                    <StatusPill status={t.status} paused={t.paused}/>
                    <Glyph name="arrow" size={14}/>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:14, padding:'10px 14px', borderTop:'1px solid var(--border)', background:'var(--bg-elev-2)', fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)' }}>
          <span style={{ display:'flex', alignItems:'center', gap:6 }}><Kbd>↑</Kbd><Kbd>↓</Kbd> navigate</span>
          <span style={{ display:'flex', alignItems:'center', gap:6 }}><Kbd>↵</Kbd> open</span>
          <span style={{ display:'flex', alignItems:'center', gap:6 }}><Kbd>Esc</Kbd> close</span>
          <span style={{ marginLeft:'auto' }}>ProofMark Studio · v0.3.4</span>
        </div>
      </div>
    </div>
  );
};

/* ---------- Tool drawer ---------- */
const ToolDrawer = ({ tool, onClose }) => {
  if (!tool) return null;
  const grp = window.PM_GROUPS.find(g => g.id === tool.group);
  const tone = grp?.tone || '#7cb0ff';
  return (
    <div onClick={onClose} style={{
      position:'fixed', inset:0, zIndex:90,
      background:'color-mix(in oklab, var(--bg-inset) 50%, transparent)',
      backdropFilter:'blur(4px)', display:'flex', justifyContent:'flex-end',
      animation:'fadeInUp .14s ease',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        width:'min(520px, 94vw)', height:'100%',
        background:'var(--bg-elev)', borderLeft:'1px solid var(--border-strong)',
        boxShadow:'var(--shadow-lg)', display:'flex', flexDirection:'column',
      }}>
        <div style={{
          padding:'24px 20px 18px', borderBottom:'1px solid var(--border)',
          background:`linear-gradient(180deg, color-mix(in oklab, ${tone} 10%, var(--bg-elev)) 0%, var(--bg-elev) 100%)`,
        }}>
          <div style={{ display:'flex', alignItems:'center', gap:12, marginBottom:16 }}>
            <StatusPill status={tool.status} size="md" paused={tool.paused}/>
            <span style={{ fontSize:11, fontFamily:'var(--font-mono)', color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'.08em' }}>{grp?.label}</span>
            <button onClick={onClose} style={{ marginLeft:'auto', padding:7, borderRadius:7, background:'transparent', border:'1px solid var(--border)', color:'var(--text-muted)', cursor:'pointer', display:'grid', placeItems:'center' }}>
              <Glyph name="x" size={14}/>
            </button>
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:16 }}>
            <div style={{ width:72, height:72, borderRadius:14, background:`color-mix(in oklab, ${tone} 16%, transparent)`, border:`1px solid color-mix(in oklab, ${tone} 32%, transparent)`, display:'grid', placeItems:'center' }}>
              <Illust name={tool.icon} tone={tone} size={48}/>
            </div>
            <div>
              <div style={{ fontSize:22, fontWeight:600, letterSpacing:'-.015em' }}>{tool.title}</div>
              <div style={{ fontSize:12, color:'var(--text-muted)', fontFamily:'var(--font-mono)', marginTop:4 }}>/tools/{tool.slug}</div>
            </div>
          </div>
        </div>
        <div style={{ padding:'20px', overflowY:'auto', flex:1 }}>
          <p style={{ fontSize:14, lineHeight:1.6, color:'var(--text)', margin:'0 0 22px' }}>{tool.desc}</p>

          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, marginBottom:22 }}>
            {[
              { label:'Avg. run time',  value:'1.2s' },
              { label:'Max file size',  value:'512 MB' },
              { label:'Docs processed', value:'14.2k' },
              { label:'Last updated',   value:'Apr 16' },
            ].map(m => (
              <div key={m.label} style={{ padding:'12px 14px', borderRadius:10, background:'var(--bg-elev-2)', border:'1px solid var(--border)' }}>
                <div style={{ fontSize:10.5, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'.06em', fontFamily:'var(--font-mono)' }}>{m.label}</div>
                <div style={{ fontSize:20, fontWeight:500, marginTop:4, fontFamily:'var(--font-serif)' }}>{m.value}</div>
              </div>
            ))}
          </div>

          <div style={{ marginBottom:10, fontSize:11, color:'var(--text-dim)', textTransform:'uppercase', letterSpacing:'.08em', fontWeight:600, fontFamily:'var(--font-mono)' }}>How it works</div>
          <ol style={{ margin:0, paddingLeft:0, listStyle:'none', display:'flex', flexDirection:'column', gap:10 }}>
            {['Drop your files into the workspace','Configure options (preserved between runs)','Download or forward the result'].map((s,i)=>(
              <li key={i} style={{ display:'flex', alignItems:'flex-start', gap:12, fontSize:13, color:'var(--text-muted)', lineHeight:1.5 }}>
                <div style={{ flexShrink:0, width:22, height:22, borderRadius:999, background:`color-mix(in oklab, ${tone} 18%, transparent)`, color:tone, display:'grid', placeItems:'center', fontSize:11, fontWeight:700, fontFamily:'var(--font-mono)' }}>{i+1}</div>
                <div>{s}</div>
              </li>
            ))}
          </ol>
        </div>
        <div style={{ display:'flex', gap:10, padding:'14px 20px', borderTop:'1px solid var(--border)' }}>
          <button
            onClick={() => { window.location.href = '/tool/' + tool.slug; }}
            style={{ flex:1, padding:'11px 14px', borderRadius:10, background:tone, color:'#0a0a0b', border:0, fontSize:13, fontWeight:600, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
            <Glyph name="bolt" size={14}/>
            {tool.status === 'live' ? 'Open tool' : 'Open preview'}
          </button>
          <button style={{ padding:'11px 14px', borderRadius:10, background:'var(--bg-elev-2)', color:'var(--text)', border:'1px solid var(--border)', fontSize:13, cursor:'pointer', display:'flex', alignItems:'center', gap:8 }}>
            <Glyph name="star" size={14}/>Pin
          </button>
        </div>
      </div>
    </div>
  );
};

/* ---------- Big icon tile (SmallPDF-style) ---------- */
const ToolTile = ({ tool, onOpen }) => {
  const grp = window.PM_GROUPS.find(g => g.id === tool.group);
  const tone = grp?.tone || '#7cb0ff';
  const [hover, setHover] = useState(false);
  return (
    <button onClick={() => onOpen(tool)}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        position:'relative',
        display:'flex', flexDirection:'column', alignItems:'flex-start',
        textAlign:'left', padding:'20px 18px 16px',
        borderRadius:16,
        background: hover
          ? `linear-gradient(180deg, color-mix(in oklab, ${tone} 9%, var(--bg-elev)) 0%, var(--bg-elev) 100%)`
          : 'var(--bg-elev)',
        border:'1px solid ' + (hover ? `color-mix(in oklab, ${tone} 45%, var(--border))` : 'var(--border)'),
        color:'var(--text)', cursor:'pointer',
        transition:'background .15s, border-color .15s, transform .15s',
        transform: hover ? 'translateY(-2px)' : 'none',
        minHeight: 168,
      }}
    >
      {tool.popular && (
        <span style={{
          position:'absolute', top:10, right:10,
          fontSize:9.5, fontWeight:700, letterSpacing:'.08em', textTransform:'uppercase', fontFamily:'var(--font-mono)',
          padding:'3px 7px', borderRadius:999, color:tone,
          background:`color-mix(in oklab, ${tone} 14%, transparent)`,
          border:`1px solid color-mix(in oklab, ${tone} 30%, transparent)`,
        }}>Popular</span>
      )}
      <div style={{
        width:56, height:56, borderRadius:13,
        background:`color-mix(in oklab, ${tone} 14%, transparent)`,
        border:`1px solid color-mix(in oklab, ${tone} 26%, transparent)`,
        display:'grid', placeItems:'center', marginBottom:14,
        transition:'transform .2s ease',
        transform: hover ? 'scale(1.06) rotate(-2deg)' : 'none',
      }}>
        <Illust name={tool.icon} tone={tone} size={36}/>
      </div>
      <div style={{ fontSize:15, fontWeight:600, letterSpacing:'-.01em', marginBottom:4 }}>{tool.title}</div>
      <div style={{ fontSize:12.5, color:'var(--text-muted)', lineHeight:1.5, display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical', overflow:'hidden' }}>{tool.desc}</div>
      <div style={{ marginTop:'auto', paddingTop:10, display:'flex', alignItems:'center', justifyContent:'space-between', width:'100%' }}>
        <StatusPill status={tool.status} paused={tool.paused}/>
        <div style={{ width:26, height:26, borderRadius:999, background: hover ? tone : 'var(--bg-inset)', color: hover ? '#0a0a0b' : 'var(--text-muted)', display:'grid', placeItems:'center', transition:'background .15s, color .15s' }}>
          <Glyph name="arrow" size={13}/>
        </div>
      </div>
    </button>
  );
};

/* ---------- Group section header ---------- */
const GroupHeader = ({ group, count, onViewAll }) => (
  <div style={{ display:'flex', alignItems:'flex-end', gap:16, marginBottom:16 }}>
    <div style={{
      width:44, height:44, borderRadius:11,
      background:`color-mix(in oklab, ${group.tone} 16%, transparent)`,
      border:`1px solid color-mix(in oklab, ${group.tone} 30%, transparent)`,
      display:'grid', placeItems:'center', flexShrink:0,
    }}>
      <span style={{ width:16, height:16, borderRadius:4, background:group.tone, display:'block' }}/>
    </div>
    <div style={{ flex:1 }}>
      <div style={{ display:'flex', alignItems:'center', gap:10 }}>
        <div style={{ fontSize:11, fontFamily:'var(--font-mono)', color:'var(--text-dim)', textTransform:'uppercase', letterSpacing:'.1em', fontWeight:700 }}>{String(count).padStart(2,'0')} tools</div>
        <span style={{ width:4, height:4, borderRadius:99, background:'var(--text-dim)' }}/>
        <div style={{ fontSize:11, fontFamily:'var(--font-mono)', color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:'.08em' }}>{group.id}</div>
      </div>
      <h3 style={{
        fontFamily:'var(--font-serif)', fontWeight:400,
        fontSize:28, lineHeight:1.05, letterSpacing:'-.02em',
        margin:'4px 0 2px',
      }}>{group.label}</h3>
      <div style={{ fontSize:13, color:'var(--text-muted)', maxWidth:'56ch' }}>{group.desc}</div>
    </div>
  </div>
);

/* ---------- Hero: visual-first ---------- */
const HeroPanel = ({ onOpenPalette }) => {
  const liveCount = window.PM_TOOLS.filter(t=>t.status==='live').length;
  const total = window.PM_TOOLS.length;
  const planned = window.PM_TOOLS.filter(t=>t.status==='planned').length;
  const beta = window.PM_TOOLS.filter(t=>t.status==='beta').length;

  // The flying mini-tile cluster behind the hero copy
  const stack = [
    { ic:'merge', tone:'#ff7a45', x: 62, y: 6,  r:-8 },
    { ic:'docx',  tone:'#7cb0ff', x: 72, y: 44, r:5 },
    { ic:'sig',   tone:'#ff6b8a', x: 86, y: 18, r:10 },
    { ic:'aa',    tone:'#62e0d9', x: 54, y: 42, r:-4 },
    { ic:'ai',    tone:'#f0c674', x: 80, y: 64, r:-6 },
  ];

  return (
    <div style={{
      padding:'32px 32px 28px',
      borderRadius:20, border:'1px solid var(--border)',
      background:
        'radial-gradient(1000px 360px at 88% -40%, var(--accent-glow), transparent 60%),' +
        'linear-gradient(180deg, var(--bg-elev) 0%, var(--bg-elev-2) 100%)',
      position:'relative', overflow:'hidden', minHeight: 340,
    }}>
      {/* Floating tiles cluster */}
      <div style={{ position:'absolute', inset:0, pointerEvents:'none' }}>
        {stack.map((s,i) => (
          <div key={i} style={{
            position:'absolute', left:`${s.x}%`, top:`${s.y}%`,
            transform:`rotate(${s.r}deg)`,
            width:78, height:78, borderRadius:16,
            background:`color-mix(in oklab, ${s.tone} 12%, var(--bg-elev))`,
            border:`1px solid color-mix(in oklab, ${s.tone} 34%, transparent)`,
            display:'grid', placeItems:'center',
            boxShadow: `0 14px 30px color-mix(in oklab, ${s.tone} 18%, transparent), var(--shadow-md)`,
          }}>
            <Illust name={s.ic} tone={s.tone} size={44}/>
          </div>
        ))}
      </div>

      <div style={{ position:'absolute', top:20, right:24, display:'flex', alignItems:'center', gap:8, fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em' }}>
        <span style={{ width:6, height:6, borderRadius:99, background:'var(--live)', animation:'pulseDot 2.2s infinite' }}/>
        Workspace · online
      </div>

      <div style={{ position:'relative', zIndex:2, maxWidth:'56%' }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.1em', fontWeight:600 }}>
          <Glyph name="dot" size={8}/> ProofMark Studio · Working hub
        </div>
        <h1 style={{
          fontFamily:'var(--font-serif)', fontWeight:400,
          fontSize:'clamp(38px, 5vw, 60px)', lineHeight:1.02,
          letterSpacing:'-.02em', margin:'14px 0 10px',
        }}>
          Every PDF tool<br/>
          you need, <em style={{ fontStyle:'italic', color:'var(--accent)' }}>in one studio</em>.
        </h1>
        <p style={{ fontSize:14.5, lineHeight:1.6, color:'var(--text-muted)', margin:'0 0 22px', maxWidth:'46ch' }}>
          Merge, split, convert, sign, compress, and proofread. Fifty plus tools, organized like a real workspace — private, keyboard-first, built for document craft.
        </p>
        <div style={{ display:'flex', gap:10, flexWrap:'wrap' }}>
          <button onClick={onOpenPalette} style={{ display:'flex', alignItems:'center', gap:8, padding:'11px 16px', borderRadius:11, background:'var(--accent)', color:'var(--accent-ink)', border:0, fontSize:13, fontWeight:600, cursor:'pointer' }}>
            <Glyph name="search" size={14}/> Find a tool <kbd style={{ fontFamily:'var(--font-mono)', fontSize:10.5, padding:'1px 5px', borderRadius:4, background:'color-mix(in oklab, var(--accent-ink) 14%, transparent)', marginLeft:6 }}>⌘K</kbd>
          </button>
          <button style={{ display:'flex', alignItems:'center', gap:8, padding:'11px 16px', borderRadius:11, background:'var(--bg-elev-2)', color:'var(--text)', border:'1px solid var(--border)', fontSize:13, cursor:'pointer' }}>
            <Glyph name="plus" size={14}/> New project
          </button>
        </div>
      </div>

      <div style={{ position:'relative', zIndex:2, display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:14, marginTop:26, paddingTop:22, borderTop:'1px solid var(--border)' }}>
        {[
          { k: liveCount, l:'Live now',       dot:'var(--live)' },
          { k: beta,      l:'In beta',        dot:'var(--beta)' },
          { k: planned,   l:'Planned lanes',  dot:'var(--planned)' },
          { k: '99.98%',  l:'Uptime · 30d',   dot:null },
        ].map((m,i)=>(
          <div key={i}>
            <div style={{ display:'flex', alignItems:'baseline', gap:8 }}>
              <div style={{ fontFamily:'var(--font-serif)', fontSize:32, lineHeight:1, fontWeight:400, letterSpacing:'-.02em' }}>{m.k}</div>
              {m.dot && <span style={{ width:6, height:6, borderRadius:99, background:m.dot }}/>}
            </div>
            <div style={{ fontSize:11, color:'var(--text-muted)', marginTop:6, fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.06em' }}>{m.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ---------- Popular strip ---------- */
const PopularStrip = ({ onOpen }) => {
  const pops = window.PM_TOOLS.filter(t => t.popular);
  return (
    <div>
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:14 }}>
        <Glyph name="star" size={15}/>
        <div style={{ fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.1em', fontWeight:600 }}>Popular right now</div>
        <div style={{ flex:1, height:1, background:'var(--border)' }}/>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:`repeat(${Math.min(pops.length, 8)}, 1fr)`, gap:12 }}>
        {pops.map(t => <ToolTile key={t.slug} tool={t} onOpen={onOpen}/>)}
      </div>
    </div>
  );
};

/* ---------- Grouped catalog ---------- */
const GroupedCatalog = ({ onOpen, activeGroup, onSetGroup }) => {
  const groups = activeGroup === 'all' ? window.PM_GROUPS : window.PM_GROUPS.filter(g => g.id === activeGroup);
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:40 }}>
      {groups.map(g => {
        const items = window.PM_TOOLS.filter(t => t.group === g.id);
        return (
          <section key={g.id} id={`g-${g.id}`}>
            <GroupHeader group={g} count={items.length}/>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(210px, 1fr))', gap:12 }}>
              {items.map(t => <ToolTile key={t.slug} tool={t} onOpen={onOpen}/>)}
            </div>
          </section>
        );
      })}
    </div>
  );
};

/* ---------- Group chips with colored dots ---------- */
const GroupChips = ({ active, onSelect }) => (
  <div style={{
    display:'flex', gap:8, flexWrap:'wrap', padding:'12px 0 20px',
    borderBottom:'1px solid var(--border)', marginBottom:30,
    position:'sticky', top:54, zIndex:10,
    background:'color-mix(in oklab, var(--bg) 94%, transparent)',
    backdropFilter:'blur(10px)',
  }}>
    <button onClick={() => onSelect('all')} style={{
      display:'flex', alignItems:'center', gap:8, padding:'7px 12px', borderRadius:999,
      background: active === 'all' ? 'var(--text)' : 'var(--bg-elev)',
      color:    active === 'all' ? 'var(--bg)'   : 'var(--text-muted)',
      border:'1px solid ' + (active==='all' ? 'var(--text)' : 'var(--border)'),
      fontSize:12.5, fontWeight:500, cursor:'pointer',
    }}>All <span style={{ fontFamily:'var(--font-mono)', fontSize:10.5, padding:'1px 6px', borderRadius:999, background: active==='all' ? 'color-mix(in oklab, var(--bg) 30%, transparent)' : 'var(--bg-inset)' }}>{window.PM_TOOLS.length}</span></button>
    {window.PM_GROUPS.map(g => {
      const isActive = active === g.id;
      const count = window.PM_TOOLS.filter(t => t.group === g.id).length;
      return (
        <button key={g.id} onClick={() => onSelect(g.id)} style={{
          display:'flex', alignItems:'center', gap:8, padding:'7px 12px', borderRadius:999,
          background: isActive ? `color-mix(in oklab, ${g.tone} 16%, transparent)` : 'var(--bg-elev)',
          color: isActive ? g.tone : 'var(--text-muted)',
          border:'1px solid ' + (isActive ? `color-mix(in oklab, ${g.tone} 40%, transparent)` : 'var(--border)'),
          fontSize:12.5, fontWeight:500, cursor:'pointer',
        }}>
          <span style={{ width:8, height:8, borderRadius:3, background:g.tone }}/>
          {g.label}
          <span style={{ fontFamily:'var(--font-mono)', fontSize:10.5, color: isActive ? g.tone : 'var(--text-dim)' }}>{count}</span>
        </button>
      );
    })}
  </div>
);

/* ---------- Recent activity ---------- */
const RecentStream = () => (
  <div style={{ padding:'22px 24px', borderRadius:16, background:'var(--bg-elev)', border:'1px solid var(--border)' }}>
    <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:16 }}>
      <Glyph name="clock" size={15}/>
      <div style={{ fontSize:13.5, fontWeight:600 }}>Recent activity</div>
      <span style={{ fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em' }}>Today · You + 2</span>
    </div>
    <div style={{ display:'flex', flexDirection:'column' }}>
      {window.PM_RECENT.map((r, i) => {
        const tool = window.PM_TOOLS.find(t => t.slug === r.kind);
        const grp = tool && window.PM_GROUPS.find(g => g.id === tool.group);
        const tone = grp?.tone || '#7cb0ff';
        return (
          <div key={r.id} style={{
            display:'flex', alignItems:'center', gap:14, padding:'12px 0',
            borderTop: i===0 ? 'none' : '1px solid var(--border)',
          }}>
            <div style={{ width:34, height:34, borderRadius:9, background:`color-mix(in oklab, ${tone} 14%, transparent)`, border:`1px solid color-mix(in oklab, ${tone} 28%, transparent)`, display:'grid', placeItems:'center', flexShrink:0 }}>
              <Illust name={tool?.icon || 'merge'} tone={tone} size={20}/>
            </div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ fontSize:13, fontWeight:500 }}>{r.label}</div>
              <div style={{ fontSize:11.5, color:'var(--text-muted)', fontFamily:'var(--font-mono)', marginTop:2 }}>{r.meta}</div>
            </div>
            <div style={{ fontSize:11.5, color:'var(--text-muted)', textAlign:'right' }}>
              <div>{r.when}</div>
              <div style={{ color:'var(--text-dim)', fontSize:10.5, fontFamily:'var(--font-mono)' }}>{r.by}</div>
            </div>
          </div>
        );
      })}
    </div>
  </div>
);

/* ---------- Throughput ---------- */
const Throughput = () => {
  const data = [8,12,9,14,18,16,22,19,24,28,26,32,30,35,33,40,38,44,47,43,49,52];
  const max = Math.max(...data);
  const w = 100, h = 40;
  const pts = data.map((v,i) => [(i/(data.length-1))*w, h - (v/max)*h]).map(p=>p.join(',')).join(' ');
  return (
    <div style={{ padding:'20px 22px', borderRadius:16, background:'var(--bg-elev)', border:'1px solid var(--border)', display:'flex', flexDirection:'column', gap:14 }}>
      <div style={{ display:'flex', alignItems:'center', gap:10 }}>
        <Glyph name="bolt" size={15}/>
        <div style={{ fontSize:13.5, fontWeight:600 }}>Throughput</div>
        <span style={{ fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em' }}>22d</span>
      </div>
      <div style={{ display:'flex', alignItems:'baseline', gap:10 }}>
        <div style={{ fontFamily:'var(--font-serif)', fontSize:38, fontWeight:400, lineHeight:1, letterSpacing:'-.02em' }}>14,283</div>
        <div style={{ fontSize:12, color:'var(--live)', fontFamily:'var(--font-mono)' }}>+38.2%</div>
      </div>
      <svg viewBox={`0 0 ${w} ${h+4}`} style={{ width:'100%', height:70 }}>
        <defs>
          <linearGradient id="sparkG" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity=".35"/>
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0"/>
          </linearGradient>
        </defs>
        <polygon points={`0,${h} ${pts} ${w},${h}`} fill="url(#sparkG)"/>
        <polyline points={pts} fill="none" stroke="var(--accent)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
      <div style={{ fontSize:11.5, color:'var(--text-muted)' }}>Docs processed across your workspace.</div>
    </div>
  );
};

/* ---------- Platform map ---------- */
const PlatformMap = () => {
  const spokes = window.PM_SPOKES;
  return (
    <div style={{ padding:'24px', borderRadius:16, background:'var(--bg-elev)', border:'1px solid var(--border)' }}>
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:18 }}>
        <Glyph name="layers" size={15}/>
        <div style={{ fontSize:13.5, fontWeight:600 }}>Platform map</div>
        <span style={{ fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em' }}>6 lanes</span>
      </div>
      <div style={{ display:'flex', flexDirection:'column', gap:2 }}>
        {spokes.map((s, i) => (
          <div key={s.id} style={{ display:'grid', gridTemplateColumns:'16px 1fr auto', alignItems:'center', gap:14, padding:'12px 4px', borderTop: i===0 ? 'none' : '1px solid var(--border)' }}>
            <span style={{ fontFamily:'var(--font-mono)', fontSize:10, color:'var(--text-dim)', letterSpacing:'.06em' }}>{String(i+1).padStart(2,'0')}</span>
            <div>
              <div style={{ fontSize:13, fontWeight:500 }}>{s.title}</div>
              <div style={{ fontSize:11.5, color:'var(--text-muted)', marginTop:2 }}>{s.desc}</div>
            </div>
            <StatusPill status={s.status}/>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ---------- Tweaks panel ---------- */
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "dark",
  "density": "comfortable",
  "accent": "#7cb0ff"
}/*EDITMODE-END*/;

const TweaksPanel = ({ open, values, onChange, onClose }) => {
  if (!open) return null;
  const opt = (current, choices, onPick, label) => (
    <div style={{ marginBottom:18 }}>
      <div style={{ fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em', fontWeight:600, marginBottom:8 }}>{label}</div>
      <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
        {choices.map(c => (
          <button key={c.v} onClick={() => onPick(c.v)} style={{
            padding:'7px 11px', borderRadius:8,
            background: current === c.v ? 'var(--text)' : 'var(--bg-elev-2)',
            color:    current === c.v ? 'var(--bg)' : 'var(--text)',
            border:'1px solid ' + (current === c.v ? 'var(--text)' : 'var(--border)'),
            fontSize:12, fontWeight:500, cursor:'pointer',
          }}>{c.l}</button>
        ))}
      </div>
    </div>
  );
  const accents = ['#7cb0ff','#5ee59b','#ffb366','#ff6b8a','#a57cff','#1e4fd6'];
  return (
    <div style={{ position:'fixed', right:20, bottom:20, zIndex:80, width:280, padding:18, borderRadius:14, background:'var(--bg-elev)', border:'1px solid var(--border-strong)', boxShadow:'var(--shadow-lg)' }}>
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:14 }}>
        <div style={{ fontSize:13, fontWeight:600 }}>Tweaks</div>
        <span style={{ fontSize:10.5, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em' }}>Live</span>
        <button onClick={onClose} style={{ marginLeft:'auto', padding:5, border:'1px solid var(--border)', borderRadius:6, background:'transparent', color:'var(--text-muted)', cursor:'pointer', display:'grid', placeItems:'center' }}>
          <Glyph name="x" size={12}/>
        </button>
      </div>
      {opt(values.theme, [{ v:'dark', l:'Console (dark)' }, { v:'light', l:'Editorial (light)' }], v => onChange({ theme: v }), 'Theme')}
      {opt(values.density, [{ v:'comfortable', l:'Comfortable' }, { v:'compact', l:'Compact' }], v => onChange({ density: v }), 'Density')}
      <div style={{ marginBottom:4 }}>
        <div style={{ fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em', fontWeight:600, marginBottom:8 }}>Accent</div>
        <div style={{ display:'flex', gap:8 }}>
          {accents.map(a => (
            <button key={a} onClick={() => onChange({ accent: a })} style={{ width:26, height:26, borderRadius:999, background:a, border:'2px solid ' + (values.accent === a ? 'var(--text)' : 'transparent'), cursor:'pointer' }}/>
          ))}
        </div>
      </div>
    </div>
  );
};

/* ---------- Main App ---------- */
const App = () => {
  const [view, setView] = useState('home');
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const [tweaksOpen, setTweaksOpen] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);
  const [group, setGroup] = useState('all');
  const [tweaks, setTweaks] = useState(() => {
    try { return { ...TWEAK_DEFAULTS, ...JSON.parse(localStorage.getItem('pm_tweaks')||'{}') }; }
    catch { return TWEAK_DEFAULTS; }
  });

  useEffect(() => {
    document.body.dataset.theme = tweaks.theme;
    document.body.style.setProperty('--accent', tweaks.accent);
    document.body.style.setProperty('--accent-glow', tweaks.accent + '22');
    try { localStorage.setItem('pm_tweaks', JSON.stringify(tweaks)); } catch {}
  }, [tweaks]);

  useEffect(() => {
    const handler = (e) => {
      if (!e.data || typeof e.data !== 'object') return;
      if (e.data.type === '__activate_edit_mode')   setTweaksOpen(true);
      if (e.data.type === '__deactivate_edit_mode') setTweaksOpen(false);
    };
    window.addEventListener('message', handler);
    window.parent.postMessage({ type:'__edit_mode_available' }, '*');
    return () => window.removeEventListener('message', handler);
  }, []);

  const updateTweak = (patch) => {
    setTweaks(prev => ({ ...prev, ...patch }));
    window.parent.postMessage({ type:'__edit_mode_set_keys', edits: patch }, '*');
  };

  useEffect(() => {
    const h = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); setPaletteOpen(true); return; }
      if (document.activeElement?.tagName === 'INPUT') return;
      if (paletteOpen) return;
      if (e.key === '?') { e.preventDefault(); setShortcutsOpen(v => !v); return; }
      if (shortcutsOpen) return;
      if (e.key === 'g' || e.key === 'G') setView('tools');
      if (e.key === 'h' || e.key === 'H') setView('home');
      if (e.key === 'r' || e.key === 'R') setView('recent');
      if (e.key === 'p' || e.key === 'P') setView('pinned');
      if (e.key === 'w' || e.key === 'W') setView('workflow');
      if (e.key === 'm' || e.key === 'M') setView('map');
    };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [paletteOpen, shortcutsOpen]);

  const onRun = (tool) => setSelectedTool(tool);

  const breadcrumb = (() => {
    if (view === 'home') return ['Workspace', 'Home'];
    if (view === 'tools') return ['Workspace', 'All tools', group === 'all' ? 'All' : (window.PM_GROUPS.find(g=>g.id===group)?.label || 'All')];
    if (view === 'recent') return ['Workspace', 'Recent'];
    if (view === 'pinned') return ['Workspace', 'Pinned'];
    if (view === 'workflow') return ['Workspace', 'Workflow'];
    if (view === 'map') return ['Workspace', 'Platform map'];
    return ['Workspace'];
  })();

  return (
    <div style={{ display:'flex', minHeight:'100vh' }}>
      <Sidebar active={view} onSelect={(v) => {
        if (v.startsWith('tool:')) {
          const slug = v.slice(5);
          const tool = window.PM_TOOLS.find(t => t.slug === slug);
          if (tool) setSelectedTool(tool);
        } else setView(v);
      }} onOpenPalette={() => setPaletteOpen(true)} density={tweaks.density}/>

      <main style={{ flex:1, minWidth:0 }}>
        <Topbar onOpenPalette={() => setPaletteOpen(true)} onOpenTweaks={() => setTweaksOpen(true)} breadcrumb={breadcrumb}/>

        <div style={{ padding:'28px clamp(20px, 3vw, 36px) 60px', maxWidth:1440, margin:'0 auto' }}>
          {view === 'home' && (
            <div style={{ display:'flex', flexDirection:'column', gap:36 }}>
              <HeroPanel onOpenPalette={() => setPaletteOpen(true)}/>
              <PopularStrip onOpen={onRun}/>
              <GroupedCatalog onOpen={onRun} activeGroup={'all'} onSetGroup={()=>{}}/>
              <div style={{ display:'grid', gridTemplateColumns:'3fr 2fr 2fr', gap:22 }}>
                <RecentStream/>
                <Throughput/>
                <PlatformMap/>
              </div>
            </div>
          )}

          {view === 'tools' && (
            <div>
              <div style={{ marginBottom:10 }}>
                <div style={{ fontSize:11, color:'var(--text-muted)', fontFamily:'var(--font-mono)', textTransform:'uppercase', letterSpacing:'.08em', fontWeight:600 }}>Catalog</div>
                <h2 style={{ fontFamily:'var(--font-serif)', fontWeight:400, fontSize:44, lineHeight:1, letterSpacing:'-.02em', margin:'10px 0 6px' }}>
                  All tools <span style={{ color:'var(--text-dim)' }}>· {window.PM_TOOLS.length}</span>
                </h2>
                <p style={{ fontSize:13.5, color:'var(--text-muted)', margin:'0 0 6px' }}>Click a category to filter, or scroll through grouped sections below.</p>
              </div>
              <GroupChips active={group} onSelect={setGroup}/>
              <GroupedCatalog onOpen={onRun} activeGroup={group} onSetGroup={setGroup}/>
            </div>
          )}

          {view === 'recent' && (<div><h2 style={{ fontFamily:'var(--font-serif)', fontWeight:400, fontSize:44, letterSpacing:'-.02em', margin:'0 0 22px' }}>Recent activity</h2><RecentStream/></div>)}
          {view === 'pinned' && (
            <div>
              <h2 style={{ fontFamily:'var(--font-serif)', fontWeight:400, fontSize:44, letterSpacing:'-.02em', margin:'0 0 22px' }}>Pinned tools</h2>
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(210px, 1fr))', gap:12 }}>
                {window.PM_TOOLS.filter(t=>t.pin).map(t => <ToolTile key={t.slug} tool={t} onOpen={onRun}/>)}
              </div>
            </div>
          )}
          {view === 'workflow' && (
            <div>
              <h2 style={{ fontFamily:'var(--font-serif)', fontWeight:400, fontSize:44, letterSpacing:'-.02em', margin:'0 0 22px' }}>Workflow</h2>
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(210px, 1fr))', gap:12 }}>
                {window.PM_TOOLS.filter(t=>t.cat==='workflow').map(t => <ToolTile key={t.slug} tool={t} onOpen={onRun}/>)}
              </div>
            </div>
          )}
          {view === 'map' && (<div><h2 style={{ fontFamily:'var(--font-serif)', fontWeight:400, fontSize:44, letterSpacing:'-.02em', margin:'0 0 22px' }}>Platform map</h2><PlatformMap/></div>)}
          {view === 'settings' && (<div><h2 style={{ fontFamily:'var(--font-serif)', fontWeight:400, fontSize:44, letterSpacing:'-.02em', margin:'0 0 22px' }}>Settings</h2><div style={{ padding:22, borderRadius:14, background:'var(--bg-elev)', border:'1px solid var(--border)', color:'var(--text-muted)', fontSize:13.5 }}>Use the Tweaks panel (bottom-right) to adjust theme, density, and accent.</div></div>)}
        </div>
      </main>

      <CommandPalette open={paletteOpen} onClose={() => setPaletteOpen(false)} onRun={onRun}/>
      <ShortcutsModal open={shortcutsOpen} onClose={() => setShortcutsOpen(false)}/>
      <ToolDrawer tool={selectedTool} onClose={() => setSelectedTool(null)}/>
      <TweaksPanel open={tweaksOpen} values={tweaks} onChange={updateTweak} onClose={() => setTweaksOpen(false)}/>
    </div>
  );
};

/* ---------- Backend registry sync ----------
 * Hub serves /api/tools as source of truth for { status, url } per slug.
 * We merge that into the React catalog (window.PM_TOOLS) BEFORE first render
 * so status pills + drawer targets reflect whatever the backend currently says.
 * Falls back to hardcoded values after a 600ms timeout so offline dev still works. */
const __pmSyncFromBackend = async () => {
  try {
    const res = await fetch('/api/tools', { cache: 'no-store' });
    if (!res.ok) return;
    const payload = await res.json();
    const serverTools = payload.tools || {};
    window.PM_TOOLS.forEach(t => {
      const s = serverTools[t.slug];
      if (!s) return;
      if (s.status) t.status = s.status;
      if (s.url)    t.url    = s.url;  // drawer keeps this for potential deep-link
      // Flag-downgraded live tools carry `paused: true` so the pill can show it.
      if (s.paused) t.paused = true;
    });
  } catch (err) {
    console.warn('[registry] sync failed, using hardcoded catalog', err);
  }
};

const __pmMount = () => {
  ReactDOM.createRoot(document.getElementById('root')).render(<App/>);
};

Promise.race([
  __pmSyncFromBackend(),
  new Promise(resolve => setTimeout(resolve, 600)),
]).then(__pmMount);
