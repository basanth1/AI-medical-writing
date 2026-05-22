// frontend/src/data/constants.js
// All frontend static data in one place.
// Import from here — never hardcode in components.

// ── Document types ───────────────────────────────────────────────────────────
export const DOC_TYPES = [
  { id: 'Clinical Study Protocol',   abbr: 'CSP', color: '#4a9eff', desc: 'Full study design & methodology' },
  { id: 'Informed Consent Form',     abbr: 'ICF', color: '#34c97b', desc: 'Patient-facing consent document' },
  { id: 'Clinical Study Report',     abbr: 'CSR', color: '#e8a94a', desc: 'Post-trial efficacy & safety summary' },
  { id: 'Statistical Analysis Plan', abbr: 'SAP', color: '#a78bfa', desc: 'Pre-specified statistical methods' },
  { id: 'Investigator Brochure',     abbr: 'IB',  color: '#f87171', desc: 'Pre-clinical & clinical data summary' },
]

// ── Study phases ─────────────────────────────────────────────────────────────
export const PHASES = [
  'Phase I', 'Phase Ib', 'Phase I/II', 'Phase II',
  'Phase IIb', 'Phase III', 'Phase IV',
]

// ── Study designs ─────────────────────────────────────────────────────────────
export const DESIGNS = [
  'Randomized, Controlled, Double-blind',
  'Randomized, Controlled, Open-label',
  'Single-arm, Open-label',
  'Crossover Design',
  'Adaptive Design',
  'Observational, Prospective',
  'Observational, Retrospective',
]

// ── Indications ───────────────────────────────────────────────────────────────
export const INDICATIONS = [
  'Oncology', 'Cardiology', 'Neurology', 'Endocrinology', 'Immunology',
  'Infectious Disease', 'Gastroenterology', 'Hematology', 'Rare Disease',
  'Psychiatry', 'Dermatology', 'Rheumatology', 'Respiratory', 'Nephrology',
]

// ── Reviewer roles ────────────────────────────────────────────────────────────
export const REVIEWER_ROLES = [
  'Medical Writer',
  'Principal Investigator',
  'Biostatistician',
  'Clinical Research Associate',
  'Regulatory Affairs Specialist',
  'Sponsor Representative',
]

// ── Groq model tiers ──────────────────────────────────────────────────────────
export const MODEL_TIERS = [
  { value: 'fast',    label: 'Fast (Llama 3.1 8B)',          hint: 'High volume, quick drafts' },
  { value: 'default', label: 'Default (Llama 3.3 70B)',       hint: 'General generation' },
  { value: 'medical', label: 'Medical (Llama 3.3 70B)',       hint: 'Recommended for clinical docs' },
]

// ── RAG top-k options ─────────────────────────────────────────────────────────
export const RAG_TOP_K_OPTIONS = [3, 5, 7, 10]

// ── Document ingest types ─────────────────────────────────────────────────────
export const INGEST_DOC_TYPES = [
  'historical_trial',
  'regulatory_guideline',
  'icf_template',
  'csr_template',
  'protocol_template',
]

// ── Pipeline stages (shown during generation) ─────────────────────────────────
export const PIPELINE_STAGES = [
  { label: 'FAISS Vector Retrieval',   detail: 'Searching historical clinical trial documents…' },
  { label: 'Regulatory Guidelines',     detail: 'Loading ICH E6/E3, FDA, EMA guideline context…' },
  { label: 'LLM Section Generation',   detail: 'Generating sections via Groq LLM…' },
  { label: 'RAG Enrichment Loop',      detail: 'Retrieving per-section context and improving draft…' },
  { label: 'Compliance Validation',    detail: 'Checking ICH E6/E3, FDA 21 CFR, 45 CFR 46 rules…' },
]

export const STAGE_DURATIONS = [900, 700, 500, 800, 600]  // ms per stage for animation

// ── Feedback actions ──────────────────────────────────────────────────────────
export const FEEDBACK_ACTIONS = {
  approve: { color: 'var(--success)',  bg: 'var(--success-dim)',  label: 'Approve',         border: 'rgba(52,201,123,0.3)' },
  revise:  { color: 'var(--warning)',  bg: 'var(--warning-dim)',  label: 'Needs Revision',  border: 'rgba(245,166,35,0.3)' },
  reject:  { color: 'var(--danger)',   bg: 'var(--danger-dim)',   label: 'Reject',          border: 'rgba(240,68,68,0.3)' },
}

export const FEEDBACK_SEVERITY_OPTIONS = ['minor', 'major', 'critical']

// ── Compliance issue severity styling ─────────────────────────────────────────
export const SEVERITY_CONFIG = {
  critical: { color: 'var(--danger)',  bg: 'var(--danger-dim)',  label: 'Critical', border: 'rgba(240,68,68,0.25)' },
  warning:  { color: 'var(--warning)', bg: 'var(--warning-dim)', label: 'Warning',  border: 'rgba(245,166,35,0.25)' },
  info:     { color: 'var(--info)',    bg: 'var(--info-dim)',    label: 'Info',     border: 'rgba(74,158,255,0.25)' },
}

// ── Compliance guidelines per doc type (shown in report) ──────────────────────
export const COMPLIANCE_GUIDELINES = {
  'Clinical Study Protocol':   ['ICH E6(R2)', 'ICH E8', 'FDA 21 CFR 312', 'GCP'],
  'Informed Consent Form':     ['ICH E6', '45 CFR 46', 'FDA 21 CFR 50', 'GDPR/HIPAA'],
  'Clinical Study Report':     ['ICH E3', 'EMA Module 5'],
  'Statistical Analysis Plan': ['ICH E9', 'ICH E9(R1)', 'FDA Statistical Guidance'],
  'Investigator Brochure':     ['ICH E6 §7', 'FDA Guidance IB'],
}

// ── Analytics dimension labels ────────────────────────────────────────────────
export const QUALITY_DIMENSIONS = [
  'Medical Accuracy',
  'Regulatory Compliance',
  'Completeness',
  'Readability',
]

// ── Compliance score thresholds ───────────────────────────────────────────────
export const SCORE_THRESHOLDS = {
  good:    85,  // ≥85 → green
  medium:  70,  // 70–84 → amber
              // <70 → red
}

export function scoreColor(score) {
  if (score >= SCORE_THRESHOLDS.good)   return 'var(--success)'
  if (score >= SCORE_THRESHOLDS.medium) return 'var(--warning)'
  return 'var(--danger)'
}

// ── Badge color map (keyed by semantic name) ──────────────────────────────────
export const BADGE_COLORS = {
  default: { bg: 'var(--bg-overlay)',    color: 'var(--text-secondary)', border: 'var(--border-soft)' },
  accent:  { bg: 'var(--accent-glow)',   color: 'var(--accent-text)',    border: 'var(--accent-dim)' },
  success: { bg: 'var(--success-dim)',   color: 'var(--success)',        border: 'rgba(52,201,123,0.3)' },
  warning: { bg: 'var(--warning-dim)',   color: 'var(--warning)',        border: 'rgba(245,166,35,0.3)' },
  danger:  { bg: 'var(--danger-dim)',    color: 'var(--danger)',         border: 'rgba(240,68,68,0.3)' },
  info:    { bg: 'var(--info-dim)',      color: 'var(--info)',           border: 'rgba(74,158,255,0.3)' },
}

// ── Button variant styles (applied as inline style objects) ───────────────────
export const BUTTON_VARIANTS = {
  primary:  { background: 'var(--accent)',       color: 'var(--bg-base)',     border: 'var(--accent)' },
  ghost:    { background: 'transparent',          color: 'var(--text-secondary)', border: 'var(--border-soft)' },
  danger:   { background: 'var(--danger-dim)',    color: 'var(--danger)',      border: 'rgba(240,68,68,0.3)' },
  success:  { background: 'var(--success)',       color: '#fff',               border: 'var(--success)' },
  outline:  { background: 'transparent',          color: 'var(--accent)',      border: 'var(--accent-dim)' },
}

export const BUTTON_SIZES = {
  xs: { padding: '2px 8px',   fontSize: 11, gap: 4  },
  sm: { padding: '5px 12px',  fontSize: 12, gap: 5  },
  md: { padding: '8px 16px',  fontSize: 13, gap: 7  },
  lg: { padding: '12px 22px', fontSize: 14, gap: 8  },
}

// ── Sidebar nav items ─────────────────────────────────────────────────────────
// icon is a string key — map it in Sidebar.jsx using lucide-react
export const NAV_ITEMS = [
  { to: '/',           iconKey: 'Dna',          label: 'Generate',   end: true },
  { to: '/review',     iconKey: 'FileText',      label: 'Review' },
  { to: '/feedback',   iconKey: 'MessageSquare', label: 'Feedback' },
  { to: '/ingest',     iconKey: 'Upload',        label: 'Data Ingest' },
  { to: '/compliance', iconKey: 'ShieldCheck',   label: 'Compliance' },
  { to: '/analytics',  iconKey: 'BarChart3',     label: 'Analytics' },
  { to: '/finalized',  iconKey: 'Archive',       label: 'Documents' },   // ← NEW
  { to: '/settings',   iconKey: 'Settings',      label: 'Settings' },
]
