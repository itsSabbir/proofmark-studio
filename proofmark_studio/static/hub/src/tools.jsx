/* ProofMark Studio — tool catalog with color tokens + big SVG illustrations */

const CATEGORIES = [
  { id:'all',       label:'All tools',       tone:'#7cb0ff' },
  { id:'organize',  label:'Organize',        tone:'#ffb366' },
  { id:'convert',   label:'Convert',         tone:'#a57cff' },
  { id:'edit',      label:'View & Edit',     tone:'#5ee59b' },
  { id:'sign',      label:'Sign & Secure',   tone:'#ff6b8a' },
  { id:'proof',     label:'Proofing',        tone:'#7cb0ff' },
  { id:'ai',        label:'AI PDF',          tone:'#62e0d9' },
  { id:'workflow',  label:'Workflow',        tone:'#f0c674' },
];

// Grouping with colors, for the SmallPDF-style section layout
const GROUPS = [
  { id:'organize', label:'Organize PDF',        tone:'#ff7a45', pastel:'#3a1f10', desc:'Reshape documents: merge, split, reorder, compress.' },
  { id:'convert-from', label:'Convert from PDF', tone:'#a57cff', pastel:'#1f1533', desc:'Turn PDFs into Word, Excel, images, text, HTML.' },
  { id:'convert-to',   label:'Convert to PDF',   tone:'#7cb0ff', pastel:'#0f2036', desc:'Create PDFs from Word, images, HTML, markdown, OCR.' },
  { id:'edit',     label:'View & Edit',         tone:'#5ee59b', pastel:'#0f2a1c', desc:'Annotate, number, crop, redact, watermark.' },
  { id:'sign',     label:'Sign & Secure',       tone:'#ff6b8a', pastel:'#2e1018', desc:'Sign, protect, unlock, flatten documents.' },
  { id:'proof',    label:'Proofing',            tone:'#62e0d9', pastel:'#0b2a2a', desc:'Hidden characters, whitespace, typography, reports.' },
  { id:'ai',       label:'AI PDF',              tone:'#f0c674', pastel:'#2a2210', desc:'Assistants, chat, summaries, translation.' },
  { id:'workflow', label:'Workflow',            tone:'#8a96b8', pastel:'#161a24', desc:'Intake, review, delivery, standards, publishing.' },
];

// icon is a token used by the <ToolIllustration> component to render a LARGE colored mark
const TOOLS = [
  // ORGANIZE
  { slug:'merge-pdf',         title:'Merge PDF',       group:'organize',     cat:'organize', status:'live',    pin:true,  icon:'merge',    desc:'Combine multiple PDFs into a single document.', popular:true },
  { slug:'split-pdf',         title:'Split PDF',       group:'organize',     cat:'organize', status:'live',    pin:true,  icon:'split',    desc:'Split by range, fixed chunks, or every N pages.', popular:true },
  { slug:'extract-pdf-pages', title:'Extract Pages',   group:'organize',     cat:'organize', status:'live',    icon:'extract',  desc:'Pull selected pages into a new file.' },
  { slug:'organize-pdf',      title:'Organize PDF',    group:'organize',     cat:'organize', status:'live',    icon:'grid',     desc:'Resequence and reorganize page structure visually.' },
  { slug:'compress-pdf',      title:'Compress PDF',    group:'organize',     cat:'organize', status:'live',    icon:'compress', desc:'Shrink file size without losing structure.', popular:true },
  { slug:'rotate-pdf',        title:'Rotate PDF',      group:'organize',     cat:'organize', status:'live',    icon:'rotate',   desc:'Rotate pages and normalize orientation.' },
  { slug:'delete-pdf-pages',  title:'Delete Pages',    group:'organize',     cat:'organize', status:'live',    icon:'minus',    desc:'Remove unwanted pages before delivery.' },

  // CONVERT FROM PDF
  { slug:'pdf-to-word',     title:'PDF → Word',     group:'convert-from', cat:'convert',  status:'planned', icon:'docx', desc:'Editable .docx output.', popular:true },
  { slug:'pdf-to-excel',    title:'PDF → Excel',    group:'convert-from', cat:'convert',  status:'planned', icon:'xlsx', desc:'Tables and data to spreadsheets.' },
  { slug:'pdf-to-ppt',      title:'PDF → PPT',      group:'convert-from', cat:'convert',  status:'planned', icon:'pptx', desc:'Slide-ready PowerPoint output.' },
  { slug:'pdf-to-jpg',      title:'PDF → JPG',      group:'convert-from', cat:'convert',  status:'live',    icon:'jpg',  desc:'Export pages as JPG images.', popular:true },
  { slug:'pdf-to-png',      title:'PDF → PNG',      group:'convert-from', cat:'convert',  status:'live',    icon:'png',  desc:'Export pages as PNG images.' },
  { slug:'pdf-to-text',     title:'PDF → Text',     group:'convert-from', cat:'convert',  status:'live',    icon:'txt',  desc:'Extract clean text.' },
  { slug:'pdf-to-markdown', title:'PDF → Markdown', group:'convert-from', cat:'convert',  status:'live',    icon:'md',   desc:'Markdown-friendly content.' },
  { slug:'pdf-to-html',     title:'PDF → HTML',     group:'convert-from', cat:'convert',  status:'live',    icon:'html', desc:'Web-ready HTML output.' },

  // CONVERT TO PDF
  { slug:'word-to-pdf',     title:'Word → PDF',     group:'convert-to',   cat:'convert',  status:'beta',    icon:'docx', desc:'Convert .docx into clean PDF.', popular:true },
  { slug:'excel-to-pdf',    title:'Excel → PDF',    group:'convert-to',   cat:'convert',  status:'beta',    icon:'xlsx', desc:'Spreadsheets to PDF reports.' },
  { slug:'ppt-to-pdf',      title:'PPT → PDF',      group:'convert-to',   cat:'convert',  status:'beta',    icon:'pptx', desc:'Decks to PDFs.' },
  { slug:'jpg-to-pdf',      title:'JPG → PDF',      group:'convert-to',   cat:'convert',  status:'live',    icon:'jpg',  desc:'Combine JPGs into a PDF.', popular:true },
  { slug:'html-to-pdf',     title:'HTML → PDF',     group:'convert-to',   cat:'convert',  status:'live',    icon:'html', desc:'Render HTML into PDF.' },
  { slug:'markdown-to-pdf', title:'Markdown → PDF', group:'convert-to',   cat:'convert',  status:'live',    icon:'md',   desc:'Markdown to final PDF.' },
  { slug:'pdf-ocr',         title:'PDF OCR',        group:'convert-to',   cat:'convert',  status:'live',    icon:'ocr',  desc:'Make scanned PDFs searchable.' },

  // VIEW & EDIT
  { slug:'edit-pdf',        title:'Edit PDF',        group:'edit',  cat:'edit',  status:'beta',    icon:'pencil', desc:'Edit PDF content and layout inline.' },
  { slug:'pdf-annotator',   title:'Annotator',       group:'edit',  cat:'edit',  status:'beta',    icon:'pen',    desc:'Comments, highlights, and callouts.' },
  { slug:'pdf-reader',      title:'Reader',          group:'edit',  cat:'edit',  status:'beta',    icon:'book',   desc:'Focused reading experience.' },
  { slug:'number-pages',    title:'Number Pages',    group:'edit',  cat:'edit',  status:'live',    icon:'hash',   desc:'Add running page numbers.' },
  { slug:'crop-pdf',        title:'Crop PDF',        group:'edit',  cat:'edit',  status:'live',    icon:'crop',   desc:'Crop edges and reset trim.' },
  { slug:'redact-pdf',      title:'Redact PDF',      group:'edit',  cat:'edit',  status:'live',    icon:'redact', desc:'Permanently remove sensitive content.' },
  { slug:'watermark-pdf',   title:'Watermark PDF',   group:'edit',  cat:'edit',  status:'live',    icon:'water',  desc:'Brand, legal, and draft watermarks.' },
  { slug:'pdf-form-filler', title:'Form Filler',     group:'edit',  cat:'edit',  status:'live',    icon:'form',   desc:'Fill forms and flatten to PDF.' },

  // SIGN & SECURE
  { slug:'sign-pdf',           title:'Sign PDF',          group:'sign', cat:'sign', status:'planned', icon:'sig',    desc:'Add signatures cleanly.', popular:true },
  { slug:'request-signatures', title:'Request Signatures',group:'sign', cat:'sign', status:'planned', icon:'send',   desc:'Route documents for signature.' },
  { slug:'unlock-pdf',         title:'Unlock PDF',        group:'sign', cat:'sign', status:'planned', icon:'unlock', desc:'Remove access restrictions when allowed.' },
  { slug:'protect-pdf',        title:'Protect PDF',       group:'sign', cat:'sign', status:'planned', icon:'lock',   desc:'Add password and protection layers.' },
  { slug:'flatten-pdf',        title:'Flatten PDF',       group:'sign', cat:'sign', status:'planned', icon:'layers', desc:'Flatten annotations and interactive layers.' },

  // PROOF
  { slug:'text-inspection',      title:'Text Inspection',   group:'proof', cat:'proof', status:'live', pin:true, icon:'aa',     desc:'Hidden chars, normalize whitespace, typography.', popular:true },
  { slug:'inspect-hidden',       title:'Hidden Characters', group:'proof', cat:'proof', status:'live',    icon:'zw',     desc:'Zero-width, bidi, suspicious glyphs.' },
  { slug:'normalize-whitespace', title:'Normalize Space',   group:'proof', cat:'proof', status:'live',    icon:'space',  desc:'Review and normalize whitespace.' },
  { slug:'review-typography',    title:'Typography Review', group:'proof', cat:'proof', status:'live',    icon:'quote',  desc:'Check typographic replacements.' },
  { slug:'export-cleanup-report',title:'Cleanup Report',    group:'proof', cat:'proof', status:'live',    icon:'report', desc:'Export findings and choices.' },

  // AI
  { slug:'ai-pdf-assistant',  title:'AI Assistant',   group:'ai', cat:'ai', status:'beta',    icon:'ai',   desc:'Work with PDFs via a chat assistant.' },
  { slug:'chat-with-pdf',     title:'Chat with PDF',  group:'ai', cat:'ai', status:'beta',    icon:'chat', desc:'Ask questions against a document.' },
  { slug:'ai-pdf-summarizer', title:'Summarize PDF',  group:'ai', cat:'ai', status:'beta',    icon:'sum',  desc:'Executive summaries from long PDFs.' },
  { slug:'translate-pdf',     title:'Translate PDF',  group:'ai', cat:'ai', status:'planned', icon:'globe',desc:'Translate PDFs to other languages.' },

  // WORKFLOW
  { slug:'project-intake',    title:'Project Intake',    group:'workflow', cat:'workflow', status:'planned', icon:'inbox',desc:'Capture source files and project setup.' },
  { slug:'review-queue',      title:'Review Queue',      group:'workflow', cat:'workflow', status:'planned', icon:'stack',desc:'Centralize review passes and checkpoints.' },
  { slug:'delivery-center',   title:'Delivery Center',   group:'workflow', cat:'workflow', status:'planned', icon:'box',  desc:'Package final outputs and delivery.' },
  { slug:'standards-library', title:'Standards Library', group:'workflow', cat:'workflow', status:'planned', icon:'ruler',desc:'Style guides, QA rules, reusable standards.' },
  { slug:'publishing-hub',    title:'Publishing Hub',    group:'workflow', cat:'workflow', status:'planned', icon:'feed', desc:'Publishing-ready exports and distribution.' },
];

const RECENT_ACTIVITY = [
  { id:1, kind:'merge-pdf',          label:'Merged 4 PDFs',              meta:'Q3-Report.pdf · 12.4 MB',   when:'just now',  by:'you' },
  { id:2, kind:'text-inspection',    label:'Cleaned 2,841 characters',   meta:'brief-v7.md · 7 issues',    when:'18 min ago',by:'you' },
  { id:3, kind:'split-pdf',          label:'Split into 6 files',         meta:'Contracts-2026.pdf',        when:'1 h ago',   by:'M. Chen' },
  { id:4, kind:'extract-pdf-pages',  label:'Extracted pages 3–11',       meta:'Onboarding.pdf',            when:'2 h ago',   by:'you' },
  { id:5, kind:'pdf-annotator',      label:'12 comments added',          meta:'legal-redline-v2.pdf',      when:'yesterday', by:'K. Park' },
  { id:6, kind:'ai-pdf-summarizer',  label:'3-page executive summary',   meta:'investor-deck.pdf',         when:'yesterday', by:'you' },
];

const SPOKES = [
  { id:'text',   title:'Text Inspection', status:'live',    desc:'Surface hidden characters, normalize text.' },
  { id:'pdf',    title:'ProofMark PDF',   status:'live',    desc:'Merge, split, reshape documents.' },
  { id:'tools',  title:'Document Suite',  status:'planned', desc:'Editing, conversion, signing, production.' },
  { id:'review', title:'Review & QA',     status:'planned', desc:'Checks, standards, review passes.' },
  { id:'site',   title:'ProofMark Site',  status:'live',    desc:'Public brand entry point.' },
  { id:'ai',     title:'AI & Automation', status:'planned', desc:'Assistants, workflow support.' },
];

window.PM_CATEGORIES = CATEGORIES;
window.PM_GROUPS = GROUPS;
window.PM_TOOLS = TOOLS;
window.PM_RECENT = RECENT_ACTIVITY;
window.PM_SPOKES = SPOKES;
