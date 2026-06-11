import { QuotaPanel } from '../components/QuotaPanel'
import { useQuotaStream } from '../hooks/useQuotaStream'
import { Cpu } from 'lucide-react'

export function AntigravityPage() {
  const { snapshots: wsSnapshots, isConnected } = useQuotaStream()

  // Filter snapshots for Antigravity
  const antigravitySnapshots = wsSnapshots.filter((s) => s.source === 'antigravity')

  // Group by Gmail Slots
  const gmail1Snapshots = antigravitySnapshots.filter((s) => s.account_id.includes('gmail1'))
  const gmail2Snapshots = antigravitySnapshots.filter((s) => s.account_id.includes('gmail2'))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
      {/* Page Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Antigravity Quota Panels</h1>
          <p>Real-time fill levels, ticking countdowns, and credits for both slots</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className={`badge ${isConnected ? 'success' : 'danger'}`}>
            {isConnected ? 'WebSocket Live' : 'WebSocket Reconnecting...'}
          </span>
        </div>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: 'var(--space-lg)',
        }}
      >
        <QuotaPanel
          title="Antigravity — Gmail 1"
          gmailSlot="gmail1"
          snapshots={gmail1Snapshots}
        />
        <QuotaPanel
          title="Antigravity — Gmail 2"
          gmailSlot="gmail2"
          snapshots={gmail2Snapshots}
        />
      </div>

      <div className="card" style={{ marginTop: 'var(--space-md)' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.95rem', fontWeight: 600, marginBottom: '8px' }}>
          <Cpu size={16} /> Antigravity Core Details
        </h4>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          The Antigravity engine updates its quota pool every 5 hours. If the IDE is running, QuotaLens queries the local language server directly over gRPC. If the IDE is closed, QuotaLens falls back to reading the last cached quota snapshot from the local filesystem configuration files (~/.gemini directory).
        </p>
      </div>
    </div>
  )
}
