import { useState, useCallback, memo } from 'react'
import { useForm } from 'react-hook-form'
import {
  ChevronRight, Plus, X, Target, Users,
  Calendar, Building2, Hash, FlaskConical,
} from 'lucide-react'
import { Button, Input, Select, Textarea, Card } from '../ui/index.jsx'
import {
  DOC_TYPES, PHASES, DESIGNS, INDICATIONS,
  REVIEWER_ROLES, MODEL_TIERS, RAG_TOP_K_OPTIONS,
} from '../../data/constants.js'

// ─── Stable input style (defined once outside, never recreated) ───────────────
const dynInputStyle = {
  flex: 1,
  background: 'var(--bg-elevated)',
  border: '1px solid var(--border-soft)',
  borderRadius: 'var(--radius-md)',
  padding: '7px 10px',
  fontSize: 12,
  color: 'var(--text-primary)',
  outline: 'none',
  fontFamily: 'var(--font-body)',
  transition: 'border-color 0.15s',
  minWidth: 0,
}

// ─── DynItem: single controlled input row ────────────────────────────────────
// Defined OUTSIDE the form component so it never gets a new reference on render.
// Uses a stable key (index) — focus is preserved because the node is never
// unmounted between keystrokes.
const DynItem = memo(function DynItem({ value, index, onChange, onRemove, placeholder, showRemove }) {
  return (
    <div style={{ display: 'flex', gap: 6, marginBottom: 6 }}>
      <input
        value={value}
        onChange={e => onChange(index, e.target.value)}
        placeholder={`${placeholder} ${index + 1}`}
        style={dynInputStyle}
        onFocus={e  => { e.target.style.borderColor = 'var(--accent)' }}
        onBlur={e   => { e.target.style.borderColor = 'var(--border-soft)' }}
      />
      {showRemove && (
        <button
          type="button"
          onClick={() => onRemove(index)}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: 'var(--text-muted)', padding: 4, flexShrink: 0,
            display: 'flex', alignItems: 'center',
          }}
        >
          <X size={13} />
        </button>
      )}
    </div>
  )
})

// ─── DynList: list of DynItem rows + Add button ───────────────────────────────
// Also defined outside the form component.
const DynList = memo(function DynList({ items, placeholder, onChangeItem, onRemoveItem, onAdd }) {
  return (
    <div style={{ marginTop: 6 }}>
      {items.map((val, i) => (
        <DynItem
          key={i}
          index={i}
          value={val}
          placeholder={placeholder}
          onChange={onChangeItem}
          onRemove={onRemoveItem}
          showRemove={items.length > 1}
        />
      ))}
      <button
        type="button"
        onClick={onAdd}
        style={{
          fontSize: 11, color: 'var(--accent)', background: 'none',
          border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: 4,
          marginTop: 2,
        }}
      >
        <Plus size={11} /> Add
      </button>
    </div>
  )
})

// ─── SectionHeader: collapsible accordion header ──────────────────────────────
// Outside the form component — stable reference.
const SectionHeader = memo(function SectionHeader({ id, title, icon: Icon, expanded, onToggle }) {
  return (
    <button
      type="button"
      onClick={() => onToggle(id)}
      style={{
        width: '100%', display: 'flex', alignItems: 'center',
        justifyContent: 'space-between', background: 'none',
        border: 'none', cursor: 'pointer', padding: 0, color: 'var(--text-primary)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Icon size={14} color="var(--accent)" />
        <span style={{ fontSize: 13, fontWeight: 500 }}>{title}</span>
      </div>
      <ChevronRight
        size={14}
        color="var(--text-muted)"
        style={{
          transform: expanded ? 'rotate(90deg)' : 'none',
          transition: 'transform 0.2s',
        }}
      />
    </button>
  )
})

// ─── Main form component ──────────────────────────────────────────────────────
export default function StudyMetadataForm({ onSubmit, isLoading }) {
  const [docType, setDocType]   = useState('Clinical Study Protocol')
  const [secondary, setSecondary] = useState([''])
  const [arms, setArms]           = useState(['', ''])
  const [expanded, setExpanded]   = useState({
    basic: true, design: true, endpoints: true, user: true, advanced: false,
  })

  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      indication:              'Oncology',
      phase:                   'Phase III',
      design:                  'Randomized, Controlled, Double-blind',
      primary_endpoint:        'Overall Survival (OS)',
      patient_population:      'Adults with HER2-positive metastatic breast cancer',
      investigational_product: 'TrialDrug-X 150mg',
      sponsor:                 'PharmaCo Inc.',
      therapeutic_area:        'Oncology — Breast Cancer',
      protocol_number:         'CTR-2025-ONC-003',
      sample_size:             520,
      duration_months:         48,
      reviewer_name:           '',
      reviewer_role:           'Medical Writer',
      reviewer_org:            '',
      rag_top_k:               5,
      model_tier:              'medical',
      additional_context:      '',
    },
  })

  // ── Stable callbacks — these never get a new reference unless deps change ───
  const handleToggle = useCallback((id) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }))
  }, [])

  // Secondary endpoints handlers
  const handleSecondaryChange = useCallback((index, value) => {
    setSecondary(prev => {
      const next = [...prev]
      next[index] = value
      return next
    })
  }, [])
  const handleSecondaryRemove = useCallback((index) => {
    setSecondary(prev => prev.filter((_, i) => i !== index))
  }, [])
  const handleSecondaryAdd = useCallback(() => {
    setSecondary(prev => [...prev, ''])
  }, [])

  // Treatment arms handlers
  const handleArmChange = useCallback((index, value) => {
    setArms(prev => {
      const next = [...prev]
      next[index] = value
      return next
    })
  }, [])
  const handleArmRemove = useCallback((index) => {
    setArms(prev => prev.filter((_, i) => i !== index))
  }, [])
  const handleArmAdd = useCallback(() => {
    setArms(prev => [...prev, ''])
  }, [])

  const onFormSubmit = useCallback((data) => {
    onSubmit({
      metadata: {
        ...data,
        secondary_endpoints: secondary.filter(Boolean),
        treatment_arms:      arms.filter(Boolean),
        sample_size:         Number(data.sample_size)     || null,
        duration_months:     Number(data.duration_months) || null,
      },
      document_type:            docType,
      rag_top_k:                Number(data.rag_top_k) || 5,
      model_tier:               data.model_tier,
      include_compliance_check: true,
      additional_context:       data.additional_context || null,
      reviewer: {
        name:         data.reviewer_name,
        role:         data.reviewer_role,
        organization: data.reviewer_org,
      },
    })
  }, [secondary, arms, docType, onSubmit])

  const tagStyle = (active, color) => ({
    padding: '10px 12px', borderRadius: 'var(--radius-md)',
    cursor: 'pointer', textAlign: 'left',
    border: `1.5px solid ${active ? color : 'var(--border-subtle)'}`,
    background: active ? `${color}18` : 'var(--bg-elevated)',
    transition: 'all 0.15s',
  })

  return (
    <form onSubmit={handleSubmit(onFormSubmit)}>

      {/* ── Document Type ─────────────────────────────────────────────────── */}
      <Card style={{ marginBottom: 12 }}>
        <div style={{
          fontSize: 13, fontWeight: 500, marginBottom: 12,
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <FlaskConical size={14} color="var(--accent)" />
          Document Type
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {DOC_TYPES.map(dt => (
            <button
              key={dt.id}
              type="button"
              onClick={() => setDocType(dt.id)}
              style={tagStyle(docType === dt.id, dt.color)}
            >
              <div style={{ fontSize: 11, fontWeight: 700, color: dt.color, marginBottom: 2 }}>
                {dt.abbr}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{dt.desc}</div>
            </button>
          ))}
        </div>
      </Card>

      {/* ── Study Identification ──────────────────────────────────────────── */}
      <Card style={{ marginBottom: 12 }}>
        <SectionHeader
          id="basic" title="Study Identification" icon={Hash}
          expanded={expanded.basic} onToggle={handleToggle}
        />
        {expanded.basic && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 16 }}>
            <Input label="Protocol Number"
              {...register('protocol_number')} placeholder="CTR-2025-XXX-001" />
            <Input label="Sponsor"
              {...register('sponsor')} placeholder="PharmaCo Inc." />
            <Select label="Indication *"
              {...register('indication', { required: 'Required' })}
              error={errors.indication?.message}>
              {INDICATIONS.map(i => <option key={i}>{i}</option>)}
            </Select>
            <Input label="Therapeutic Area"
              {...register('therapeutic_area')} placeholder="Oncology — Breast Cancer" />
            <Input label="Investigational Product"
              {...register('investigational_product')} placeholder="Drug Name Dose" />
            <Select label="Study Phase *"
              {...register('phase', { required: 'Required' })}
              error={errors.phase?.message}>
              {PHASES.map(p => <option key={p}>{p}</option>)}
            </Select>
          </div>
        )}
      </Card>

      {/* ── Study Design & Population ─────────────────────────────────────── */}
      <Card style={{ marginBottom: 12 }}>
        <SectionHeader
          id="design" title="Study Design & Population" icon={Users}
          expanded={expanded.design} onToggle={handleToggle}
        />
        {expanded.design && (
          <div style={{ marginTop: 16 }}>
            <Select
              label="Study Design *"
              {...register('design', { required: 'Required' })}
              error={errors.design?.message}
              
            >
              {DESIGNS.map(d => <option key={d}>{d}</option>)}
            </Select>

            <Textarea
              label="Patient Population *"
              {...register('patient_population', { required: 'Required' })}
              rows={2}
              placeholder="Adults ≥18 years with confirmed HER2-positive metastatic breast cancer…"
              error={errors.patient_population?.message}
            />

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 10 }}>
              <Input label="Sample Size (N)" type="number"
                {...register('sample_size')} placeholder="520" />
              <Input label="Duration (months)" type="number"
                {...register('duration_months')} placeholder="48" />
            </div>

            <div style={{ marginTop: 12 }}>
              <div style={{
                fontSize: 12, fontWeight: 500,
                color: 'var(--text-secondary)', marginBottom: 4,
              }}>
                Treatment Arms
              </div>
              <DynList
                items={arms}
                placeholder="Arm"
                onChangeItem={handleArmChange}
                onRemoveItem={handleArmRemove}
                onAdd={handleArmAdd}
              />
            </div>
          </div>
        )}
      </Card>

      {/* ── Endpoints & Objectives ────────────────────────────────────────── */}
      <Card style={{ marginBottom: 12 }}>
        <SectionHeader
          id="endpoints" title="Endpoints & Objectives" icon={Target}
          expanded={expanded.endpoints} onToggle={handleToggle}
        />
        {expanded.endpoints && (
          <div style={{ marginTop: 16 }}>
            <Input
              label="Primary Endpoint *"
              {...register('primary_endpoint', { required: 'Required' })}
              error={errors.primary_endpoint?.message}
              placeholder="Overall Survival (OS)"
              hint="Main efficacy endpoint pre-specified in SAP"
            />
            <div style={{ marginTop: 12 }}>
              <div style={{
                fontSize: 12, fontWeight: 500,
                color: 'var(--text-secondary)', marginBottom: 4,
              }}>
                Secondary Endpoints
              </div>
              <DynList
                items={secondary}
                placeholder="Secondary endpoint"
                onChangeItem={handleSecondaryChange}
                onRemoveItem={handleSecondaryRemove}
                onAdd={handleSecondaryAdd}
              />
            </div>
          </div>
        )}
      </Card>

      {/* ── Reviewer Identification ───────────────────────────────────────── */}
      <Card style={{ marginBottom: 12 }}>
        <SectionHeader
          id="user" title="Reviewer Identification" icon={Building2}
          expanded={expanded.user} onToggle={handleToggle}
        />
        {expanded.user && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 16 }}>
            <Input label="Your Name"
              {...register('reviewer_name')} placeholder="Dr. Jane Smith" />
            <Select label="Your Role" {...register('reviewer_role')}>
              {REVIEWER_ROLES.map(r => <option key={r}>{r}</option>)}
            </Select>
            <div style={{ gridColumn: 'span 2' }}>
              <Input label="Organization"
                {...register('reviewer_org')} placeholder="PharmaCo Inc." />
            </div>
          </div>
        )}
      </Card>

      {/* ── Advanced Options ──────────────────────────────────────────────── */}
      <Card style={{ marginBottom: 12 }}>
        <SectionHeader
          id="advanced" title="Advanced Options" icon={Calendar}
          expanded={expanded.advanced} onToggle={handleToggle}
        />
        {expanded.advanced && (
          <div style={{ marginTop: 16 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
              <Select label="Model Tier" {...register('model_tier')}>
                {MODEL_TIERS.map(m => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </Select>
              <Select label="RAG Top-K" {...register('rag_top_k')}>
                {RAG_TOP_K_OPTIONS.map(n => (
                  <option key={n} value={n}>{n} documents</option>
                ))}
              </Select>
            </div>
            <Textarea
              label="Additional Context"
              {...register('additional_context')}
              rows={3}
              placeholder="Any additional requirements, regulatory needs, or special instructions…"
            />
          </div>
        )}
      </Card>

      <Button
        type="submit"
        size="lg"
        loading={isLoading}
        style={{ width: '100%', marginTop: 4, fontSize: 14, padding: '14px' }}
        iconRight={!isLoading && <ChevronRight size={16} />}
      >
        {isLoading ? 'Generating…' : 'Generate Document'}
      </Button>
    </form>
  )
}
