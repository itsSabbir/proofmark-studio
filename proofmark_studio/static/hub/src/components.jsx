/* ProofMark Studio — shared components */

const { useState, useEffect, useMemo, useRef, useCallback } = React;

/* ---------- Tiny monochrome Glyph (no imported icon libs) ---------- */
const Glyph = ({ name, size = 16, stroke = 1.6 }) => {
  const s = size; const sw = stroke;
  const common = {
    width: s, height: s, viewBox: '0 0 24 24', fill: 'none',
    stroke: 'currentColor', strokeWidth: sw, strokeLinecap: 'round', strokeLinejoin: 'round',
  };
  switch (name) {
    case 'search':  return <svg {...common}><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>;
    case 'cmd':     return <svg {...common}><path d="M9 6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3z"/></svg>;
    case 'spark':   return <svg {...common}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/></svg>;
    case 'arrow':   return <svg {...common}><path d="M5 12h14M13 6l6 6-6 6"/></svg>;
    case 'check':   return <svg {...common}><path d="m5 12 5 5L20 7"/></svg>;
    case 'x':       return <svg {...common}><path d="M6 6l12 12M18 6 6 18"/></svg>;
    case 'dot':     return <svg {...common}><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>;
    case 'plus':    return <svg {...common}><path d="M12 5v14M5 12h14"/></svg>;
    case 'chev':    return <svg {...common}><path d="m9 6 6 6-6 6"/></svg>;
    case 'chevD':   return <svg {...common}><path d="m6 9 6 6 6-6"/></svg>;
    case 'star':    return <svg {...common}><path d="m12 3 2.7 5.8 6.3.7-4.7 4.4 1.3 6.4L12 17.3 6.4 20.3l1.3-6.4L3 9.5l6.3-.7z"/></svg>;
    case 'pin':     return <svg {...common}><path d="M12 2v6M6 10h12l-2 4H8zM12 14v8"/></svg>;
    case 'bolt':    return <svg {...common}><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg>;
    case 'folder':  return <svg {...common}><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>;
    case 'settings':return <svg {...common}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9c.1.6.6 1 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>;
    case 'home':    return <svg {...common}><path d="m3 12 9-8 9 8"/><path d="M5 10v10h14V10"/></svg>;
    case 'grid':    return <svg {...common}><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>;
    case 'list':    return <svg {...common}><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>;
    case 'inbox':   return <svg {...common}><path d="M3 13h5l2 3h4l2-3h5"/><path d="M5 5h14l2 8v6H3v-6z"/></svg>;
    case 'clock':   return <svg {...common}><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>;
    case 'pdf':     return <svg {...common}><path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="M9 13h1.5a1.5 1.5 0 0 1 0 3H9v-3zM13 13v3M13 13h2M13 14.5h1.5M17 13v3M17 13h2"/></svg>;
    case 'text':    return <svg {...common}><path d="M4 7V5h16v2M9 5v14M15 19H9"/></svg>;
    case 'merge':   return <svg {...common}><path d="M6 3v8a4 4 0 0 0 4 4h8M18 3v8a4 4 0 0 1-4 4H6"/><path d="M4 21h16"/></svg>;
    case 'split':   return <svg {...common}><path d="M12 3v6M9 12l3-3 3 3M6 21V12M18 21V12"/></svg>;
    case 'extract': return <svg {...common}><rect x="4" y="3" width="12" height="16" rx="1.5"/><path d="M19 7v12a2 2 0 0 1-2 2H9"/></svg>;
    case 'compress':return <svg {...common}><path d="M4 9V5h4M20 9V5h-4M4 15v4h4M20 15v4h-4M9 12h6"/></svg>;
    case 'rotate': return <svg {...common}><path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 4v5h-5"/></svg>;
    case 'minus':   return <svg {...common}><path d="M5 12h14"/></svg>;
    case 'pencil':  return <svg {...common}><path d="m4 20 4-1 10-10-3-3L5 16z"/></svg>;
    case 'pen':     return <svg {...common}><path d="M4 20h4l10-10-4-4L4 16z"/><path d="M14 6l4 4"/></svg>;
    case 'book':    return <svg {...common}><path d="M4 4h7a4 4 0 0 1 4 4v12a3 3 0 0 0-3-3H4zM20 4h-7"/></svg>;
    case 'hash':    return <svg {...common}><path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/></svg>;
    case 'crop':    return <svg {...common}><path d="M6 2v16h16M2 6h16v16"/></svg>;
    case 'square':  return <svg {...common}><rect x="4" y="4" width="16" height="16" rx="1"/></svg>;
    case 'layers':  return <svg {...common}><path d="m12 3 9 5-9 5-9-5zM3 13l9 5 9-5M3 18l9 5 9-5"/></svg>;
    case 'form':    return <svg {...common}><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 9h8M8 13h5M8 17h3"/></svg>;
    case 'docx':    return <svg {...common}><path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="M9 12l1 5 1-3 1 3 1-5"/></svg>;
    case 'xlsx':    return <svg {...common}><path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="m9 13 4 4M13 13l-4 4"/></svg>;
    case 'pptx':    return <svg {...common}><path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="M10 11v6M10 11h2.5a1.5 1.5 0 0 1 0 3H10"/></svg>;
    case 'img':     return <svg {...common}><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.5"/><path d="m21 15-5-5-9 9"/></svg>;
    case 'txt':     return <svg {...common}><path d="M7 3h8l4 4v14H7z"/><path d="M15 3v4h4"/><path d="M9 13h6M9 16h6M9 10h3"/></svg>;
    case 'md':      return <svg {...common}><rect x="3" y="6" width="18" height="12" rx="1.5"/><path d="M7 15v-6l2 3 2-3v6M15 9v6M15 15l-2-2M15 15l2-2"/></svg>;
    case 'html':    return <svg {...common}><path d="m8 10-3 2 3 2M16 10l3 2-3 2M14 7l-4 10"/></svg>;
    case 'ocr':     return <svg {...common}><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M7 9v6M11 9v6M15 9v6M19 9v6"/></svg>;
    case 'sig':     return <svg {...common}><path d="M3 18c3 0 4-10 7-10s2 8 5 8 2-4 4-4"/><path d="M3 21h18"/></svg>;
    case 'send':    return <svg {...common}><path d="m21 3-9 18-2-8-8-2z"/></svg>;
    case 'unlock':  return <svg {...common}><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0"/></svg>;
    case 'lock':    return <svg {...common}><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>;
    case 'aa':      return <svg {...common}><path d="M4 20 9 6l5 14M5.8 16h6.4M14 20l4-10 4 10M15.3 17h5.4"/></svg>;
    case 'space':   return <svg {...common}><path d="M4 10v4h16v-4"/></svg>;
    case 'quote':   return <svg {...common}><path d="M6 10c0-2 1-3 3-3M6 17l3-7v7zM14 10c0-2 1-3 3-3M14 17l3-7v7z"/></svg>;
    case 'report':  return <svg {...common}><path d="M5 3h11l3 3v15H5z"/><path d="M9 9h6M9 13h6M9 17h4"/></svg>;
    case 'ai':      return <svg {...common}><path d="M12 2v4M12 18v4M4 12H2M22 12h-2M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/><circle cx="12" cy="12" r="4"/></svg>;
    case 'chat':    return <svg {...common}><path d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-6l-4 4v-4H6a2 2 0 0 1-2-2z"/></svg>;
    case 'sum':     return <svg {...common}><path d="M5 4h14L11 12l8 8H5l6-8z"/></svg>;
    case 'globe':   return <svg {...common}><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/></svg>;
    case 'stack':   return <svg {...common}><rect x="3" y="4" width="18" height="4" rx="1"/><rect x="3" y="10" width="18" height="4" rx="1"/><rect x="3" y="16" width="18" height="4" rx="1"/></svg>;
    case 'box':     return <svg {...common}><path d="m3 7 9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7M12 11v10"/></svg>;
    case 'ruler':   return <svg {...common}><rect x="3" y="8" width="18" height="8" rx="1"/><path d="M7 8v3M11 8v4M15 8v3M19 8v4"/></svg>;
    case 'feed':    return <svg {...common}><path d="M4 4a16 16 0 0 1 16 16M4 10a10 10 0 0 1 10 10M5 18a2 2 0 1 0 0 0"/></svg>;
    case 'logo':    return (
      <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
        <rect x="1" y="1" width="22" height="22" rx="6" stroke="currentColor" strokeWidth="1.4"/>
        <circle cx="12" cy="12" r="3" fill="currentColor"/>
        <circle cx="12" cy="12" r="7" stroke="currentColor" strokeWidth="1.1" strokeDasharray="1.8 2.2" opacity=".7"/>
      </svg>);
    default: return <svg {...common}><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>;
  }
};

/* ---------- Status pill ---------- */
const StatusPill = ({ status, size='sm', paused=false }) => {
  const map = {
    live:    { label:'Live',    color:'var(--live)' },
    beta:    { label:'Beta',    color:'var(--beta)' },
    planned: { label:'Planned', color:'var(--planned)' },
    paused:  { label:'Paused',  color:'var(--beta)' },
  };
  // Flag-downgraded live tools carry paused=true so the pill reads "Paused"
  // instead of collapsing silently into "Planned".
  const key = paused ? 'paused' : status;
  const s = map[key] || map.planned;
  const pad = size === 'sm' ? '2px 8px' : '4px 10px';
  return (
    <span style={{
      display:'inline-flex', alignItems:'center', gap:6,
      padding: pad, borderRadius:999,
      fontSize: size === 'sm' ? 10.5 : 11.5, fontWeight:600,
      letterSpacing:'.02em', textTransform:'uppercase',
      color:'var(--text-muted)',
      border:'1px solid var(--border)',
      background:'var(--bg-elev-2)',
      fontFamily:'var(--font-mono)',
    }}>
      <span style={{
        width:6, height:6, borderRadius:999, background:s.color,
        boxShadow: status === 'live' ? `0 0 0 0 ${s.color}` : 'none',
        animation: status === 'live' ? 'pulseDot 2.2s infinite' : 'none',
      }}/>
      {s.label}
    </span>
  );
};

/* ---------- Keyboard shortcut ---------- */
const Kbd = ({ children }) => (
  <kbd style={{
    fontFamily:'var(--font-mono)', fontSize:10.5, fontWeight:500,
    padding:'2px 6px', borderRadius:5,
    background:'var(--bg-elev-2)', border:'1px solid var(--border)',
    color:'var(--text-muted)',
    boxShadow:'0 1px 0 var(--border)',
  }}>{children}</kbd>
);

/* ---------- Sidebar ---------- */
const Sidebar = ({ active, onSelect, onOpenPalette, density }) => {
  const items = [
    { id:'home',     label:'Home',      g:'home',   kbd:'H' },
    { id:'tools',    label:'All tools', g:'grid',   kbd:'G' },
    { id:'pinned',   label:'Pinned',    g:'pin',    kbd:'P' },
  ];
  const bottom = [
    { id:'settings', label:'Settings',  g:'settings' },
  ];

  return (
    <aside style={{
      width: 232, flexShrink:0,
      borderRight:'1px solid var(--border)',
      background:'var(--bg)',
      height:'100vh', position:'sticky', top:0,
      display:'flex', flexDirection:'column',
      padding:'14px 12px',
    }}>
      {/* Brand */}
      <div style={{ display:'flex', alignItems:'center', gap:10, padding:'6px 8px 14px 8px', borderBottom:'1px solid var(--border)', marginBottom:10 }}>
        <div style={{
          width:30, height:30, borderRadius:8,
          background:'var(--accent)', color:'var(--accent-ink)',
          display:'grid', placeItems:'center',
        }}>
          <Glyph name="logo" size={18}/>
        </div>
        <div style={{ lineHeight:1.1 }}>
          <div style={{ fontWeight:600, fontSize:13.5, letterSpacing:'-.01em' }}>ProofMark</div>
          <div style={{ fontSize:10.5, color:'var(--text-muted)', fontFamily:'var(--font-mono)', letterSpacing:'.04em', textTransform:'uppercase' }}>Studio · v0.3</div>
        </div>
        <div style={{ marginLeft:'auto' }}>
          <Kbd>⌘</Kbd>
        </div>
      </div>

      {/* Search trigger */}
      <button onClick={onOpenPalette} style={{
        display:'flex', alignItems:'center', gap:10,
        width:'100%', padding:'9px 10px', marginBottom:16,
        background:'var(--bg-elev)', border:'1px solid var(--border)', borderRadius:10,
        color:'var(--text-muted)', cursor:'pointer',
        fontSize:12.5, textAlign:'left', transition:'border-color .15s',
      }}
      onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-strong)'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
      >
        <Glyph name="search" size={14}/>
        <span>Search tools…</span>
        <span style={{ marginLeft:'auto', display:'flex', gap:3 }}>
          <Kbd>⌘</Kbd><Kbd>K</Kbd>
        </span>
      </button>

      {/* Nav */}
      <nav style={{ display:'flex', flexDirection:'column', gap:1 }}>
        <div style={{ fontSize:10, letterSpacing:'.1em', textTransform:'uppercase', color:'var(--text-dim)', fontWeight:600, padding:'8px 10px 6px', fontFamily:'var(--font-mono)' }}>Workspace</div>
        {items.map(it => (
          <button key={it.id} onClick={() => onSelect(it.id)} style={{
            display:'flex', alignItems:'center', gap:10,
            width:'100%', padding:'8px 10px', borderRadius:8,
            background: active === it.id ? 'var(--bg-elev)' : 'transparent',
            border:'1px solid ' + (active === it.id ? 'var(--border)' : 'transparent'),
            color: active === it.id ? 'var(--text)' : 'var(--text-muted)',
            fontSize:13, fontWeight: active===it.id ? 500 : 400,
            cursor:'pointer', textAlign:'left', transition:'background .12s, color .12s',
          }}
          onMouseEnter={e => { if(active!==it.id){ e.currentTarget.style.color='var(--text)'; }}}
          onMouseLeave={e => { if(active!==it.id){ e.currentTarget.style.color='var(--text-muted)'; }}}
          >
            <Glyph name={it.g} size={15}/>
            <span>{it.label}</span>
            <span style={{ marginLeft:'auto' }}><Kbd>{it.kbd}</Kbd></span>
          </button>
        ))}
      </nav>

      <div style={{ marginTop:22 }}>
        <div style={{ fontSize:10, letterSpacing:'.1em', textTransform:'uppercase', color:'var(--text-dim)', fontWeight:600, padding:'8px 10px 6px', fontFamily:'var(--font-mono)' }}>Pinned tools</div>
        {__pmVisible(window.PM_TOOLS).filter(t=>t.pin).map(t => (
          <button key={t.slug} onClick={() => onSelect('tool:'+t.slug)} style={{
            display:'flex', alignItems:'center', gap:10,
            width:'100%', padding:'7px 10px', borderRadius:8,
            background:'transparent', border:'1px solid transparent',
            color:'var(--text-muted)', fontSize:12.5, cursor:'pointer', textAlign:'left',
          }}
          onMouseEnter={e => { e.currentTarget.style.background='var(--bg-elev)'; e.currentTarget.style.color='var(--text)';}}
          onMouseLeave={e => { e.currentTarget.style.background='transparent'; e.currentTarget.style.color='var(--text-muted)';}}
          >
            <Glyph name={t.icon} size={14}/>
            <span style={{ overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{t.title}</span>
            {t.status === 'live' && (
              <span style={{ marginLeft:'auto', width:6, height:6, borderRadius:99, background:'var(--live)' }}/>
            )}
          </button>
        ))}
      </div>

      <div style={{ marginTop:'auto', paddingTop:12, borderTop:'1px solid var(--border)' }}>
        {bottom.map(it => (
          <button key={it.id} onClick={() => onSelect(it.id)} style={{
            display:'flex', alignItems:'center', gap:10,
            width:'100%', padding:'8px 10px', borderRadius:8,
            background:'transparent', border:'1px solid transparent',
            color:'var(--text-muted)', fontSize:13, cursor:'pointer', textAlign:'left',
          }}>
            <Glyph name={it.g} size={15}/> {it.label}
          </button>
        ))}
        <div style={{
          display:'flex', alignItems:'center', gap:10,
          padding:'10px', marginTop:6, borderRadius:10,
          background:'var(--bg-elev)', border:'1px solid var(--border)',
        }}>
          <div style={{
            width:28, height:28, borderRadius:999,
            background:'linear-gradient(135deg, var(--accent) 0%, #a57cff 100%)',
            color:'#fff', display:'grid', placeItems:'center',
            fontSize:11, fontWeight:600,
          }}>SH</div>
          <div style={{ lineHeight:1.2, fontSize:12 }}>
            <div style={{ fontWeight:500 }}>Sabbir H.</div>
            <div style={{ color:'var(--text-muted)', fontSize:10.5, fontFamily:'var(--font-mono)' }}>Workspace · Pro</div>
          </div>
        </div>
      </div>
    </aside>
  );
};

/* ---------- Topbar ---------- */
const Topbar = ({ onOpenPalette, onOpenTweaks, breadcrumb }) => (
  <div style={{
    display:'flex', alignItems:'center', gap:14,
    padding:'14px 28px', borderBottom:'1px solid var(--border)',
    background:'color-mix(in oklab, var(--bg) 80%, transparent)',
    backdropFilter:'blur(14px)',
    position:'sticky', top:0, zIndex:20,
  }}>
    <div style={{ display:'flex', alignItems:'center', gap:10, fontSize:13, color:'var(--text-muted)' }}>
      {breadcrumb.map((b,i) => (
        <React.Fragment key={i}>
          {i>0 && <span style={{ color:'var(--text-dim)' }}>/</span>}
          <span style={{ color: i===breadcrumb.length-1 ? 'var(--text)' : 'var(--text-muted)', fontWeight: i===breadcrumb.length-1 ? 500 : 400 }}>{b}</span>
        </React.Fragment>
      ))}
    </div>
    <div style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:10 }}>
      <div style={{
        display:'flex', alignItems:'center', gap:8,
        padding:'6px 10px', borderRadius:999,
        background:'var(--bg-elev)', border:'1px solid var(--border)',
        fontSize:11.5, color:'var(--text-muted)', fontFamily:'var(--font-mono)',
      }}>
        <span style={{ width:6, height:6, borderRadius:99, background:'var(--live)', animation:'pulseDot 2.2s infinite' }}/>
        All systems operational
      </div>
      <button onClick={onOpenPalette} style={{
        display:'flex', alignItems:'center', gap:8,
        padding:'7px 11px', borderRadius:10,
        background:'var(--bg-elev)', border:'1px solid var(--border)',
        color:'var(--text-muted)', fontSize:12.5, cursor:'pointer',
      }}>
        <Glyph name="search" size={13}/>
        <span>Jump to…</span>
        <Kbd>⌘K</Kbd>
      </button>
      <button onClick={onOpenTweaks} title="Appearance" style={{
        padding:'8px', borderRadius:9,
        background:'var(--bg-elev)', border:'1px solid var(--border)',
        color:'var(--text-muted)', cursor:'pointer', display:'grid', placeItems:'center',
      }}>
        <Glyph name="spark" size={14}/>
      </button>
    </div>
  </div>
);

Object.assign(window, { Glyph, StatusPill, Kbd, Sidebar, Topbar });
