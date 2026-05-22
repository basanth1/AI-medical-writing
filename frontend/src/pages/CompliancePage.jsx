import Topbar from '../components/layout/Topbar.jsx'
import CompliancePanel from '../components/compliance/CompliancePanel.jsx'
import { ShieldCheck } from 'lucide-react'
import { useAppStore } from '../store/appStore'

export default function CompliancePage() {
  const { generationResult, complianceReport } = useAppStore()
   // Debug log
   const report = complianceReport ?? generationResult?.compliance_report
    console.log('Compliance Report:', report)
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
      <Topbar title="Compliance Report" subtitle="ICH E6/E3, FDA, EMA regulatory validation" />
      <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>
        {!generationResult ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
            <ShieldCheck size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
            <p style={{ fontSize: 14 }}>Generate a document first to see its compliance report.</p>
          </div>
        ) : (
          <div style={{ maxWidth: 760, margin: '0 auto' }}>
            <CompliancePanel report={report} />
          </div>
        )}
      </div>
    </div>
  )
}
