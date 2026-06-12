import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AccountTabs } from '../components/AccountTabs'
import { ToolCard } from '../components/ToolCard'
import { AlertBanner } from '../components/AlertBanner'
import { useDashboardData } from '../hooks/useUsageQuery'
import { useQuotaStream } from '../hooks/useQuotaStream'
import { RefreshCw } from 'lucide-react'

export function Dashboard() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'all' | 'gmail1' | 'gmail2'>('all')

  // Fetch API summaries
  const { data: apiData, isLoading: isApiLoading, refetch } = useDashboardData()

  // Live WebSocket snapshots
  const { snapshots: wsSnapshots, isConnected } = useQuotaStream()

  if (isApiLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <div style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>Loading QuotaLens Dashboard...</div>
      </div>
    )
  }

  const accounts = apiData?.accounts || []
  const today = apiData?.today || {}
  const todayRequests = today.requests ?? 0
  const todayInputTokens = today.input_tokens ?? 0
  const todayOutputTokens = today.output_tokens ?? 0

  // Filter accounts by active slot
  const filteredAccounts = accounts.filter((acc: any) => {
    if (activeTab === 'all') return true
    return acc.gmail_slot === activeTab
  })

  // Get active account IDs
  const activeAccountIds = new Set(filteredAccounts.map((a: any) => a.id))

  // Filter snapshots based on filtered accounts
  const filteredSnapshots = wsSnapshots.filter((s) => activeAccountIds.has(s.account_id))

  // Find exhausted quotas
  const exhaustedSnapshots = filteredSnapshots.filter((s) => s.is_exhausted)

  // Nearest Reset
  const now = new Date().getTime()
  const upcomingResets = filteredSnapshots
    .map((s) => (s.reset_at ? new Date(s.reset_at).getTime() : 0))
    .filter((time) => time > now)
  const nearestResetTime = upcomingResets.length > 0 ? Math.min(...upcomingResets) : null
  const nearestResetDate = nearestResetTime ? new Date(nearestResetTime).toLocaleTimeString() : 'N/A'

  // Helper to compute average remaining pct for a specific source
  const getSourceQuotaInfo = (source: string) => {
    const sourceSnaps = filteredSnapshots.filter((s) => s.source === source)
    if (sourceSnaps.length === 0) return { pct: null, detail: null, reset: null }

    // Average models quota
    const modelsOnly = sourceSnaps.filter((s) => s.model_id !== 'prompt-credits' && s.model_id !== 'flow-credits')
    const totalPct = modelsOnly.reduce((acc, curr) => acc + (curr.quota_remaining_pct || 0), 0)
    const avgPct = modelsOnly.length > 0 ? totalPct / modelsOnly.length : null

    // Find credits/costs
    let detail = null
    if (source === 'openrouter') {
      const credits = sourceSnaps.find((s) => s.model_id === 'openrouter-credits')
      if (credits && credits.credits_used !== null && credits.credits_total !== null) {
        detail = `$${parseFloat(credits.credits_used).toFixed(2)} / $${parseFloat(credits.credits_total).toFixed(2)}`
      }
    } else if (source === 'antigravity') {
      const prompt = sourceSnaps.find((s) => s.model_id === 'prompt-credits')
      if (prompt && prompt.credits_total !== null && prompt.credits_used !== null) {
        detail = `${Math.round(parseFloat(prompt.credits_total) - parseFloat(prompt.credits_used))} prompt credits`
      }
    }

    // Find nearest reset for this source
    const resets = sourceSnaps
      .map((s) => (s.reset_at ? new Date(s.reset_at).getTime() : 0))
      .filter((t) => t > now)
    const nextReset = resets.length > 0 ? new Date(Math.min(...resets)).toLocaleTimeString() : null

    return {
      pct: avgPct,
      detail,
      reset: nextReset ? `Reset at ${nextReset}` : null,
    }
  }

  // Define tools configuration
  const tools: Array<{
    id: 'antigravity' | 'cursor' | 'copilot' | 'gemini' | 'openrouter'
    name: string
    route: string
  }> = [
    { id: 'antigravity', name: 'Antigravity IDE', route: '/antigravity' },
    { id: 'cursor', name: 'Cursor IDE', route: '/cursor' },
    { id: 'copilot', name: 'VS Code Copilot', route: '/vscode' },
    { id: 'gemini', name: 'VS Code Gemini API', route: '/vscode' },
    { id: 'openrouter', name: 'VS Code OpenRouter', route: '/vscode' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
      {/* Page Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>QuotaLens Dashboard</h1>
          <p>Unified view of your active AI code assistant limits and token metrics</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className={`badge ${isConnected ? 'success' : 'danger'}`}>
            {isConnected ? 'Live' : 'Disconnected'}
          </span>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => refetch()}>
            <RefreshCw size={14} /> Refetch
          </button>
        </div>
      </div>

      {/* Critical Warnings */}
      {exhaustedSnapshots.map((snap) => (
        <AlertBanner
          key={snap.id}
          type="critical"
          message={`Critical Limit: Quota for ${snap.model_label} on account ${snap.account_id} has been exhausted!`}
        />
      ))}

      {/* Stats Strip */}
      <div className="stats-strip">
        <div className="stat-card purple">
          <span className="stat-label">Requests Today</span>
          <span className="stat-value">{(Number(todayRequests) || 0).toLocaleString()}</span>
          <span className="stat-detail">Across all tools & accounts</span>
        </div>
        <div className="stat-card blue">
          <span className="stat-label">Tokens Today</span>
          <span className="stat-value">
            {Math.round(((Number(todayInputTokens) || 0) + (Number(todayOutputTokens) || 0)) / 1000).toLocaleString()}k
          </span>
          <span className="stat-detail">
            {Math.round((Number(todayInputTokens) || 0) / 1000).toLocaleString()}k in / {Math.round((Number(todayOutputTokens) || 0) / 1000).toLocaleString()}k out
          </span>
        </div>
        <div className="stat-card red">
          <span className="stat-label">Exhausted Quotas</span>
          <span className="stat-value">{exhaustedSnapshots.length}</span>
          <span className="stat-detail">Require user attention</span>
        </div>
        <div className="stat-card cyan">
          <span className="stat-label">Nearest Reset</span>
          <span className="stat-value" style={{ fontSize: '1.25rem', paddingTop: '6px', paddingBottom: '6px' }}>
            {nearestResetDate}
          </span>
          <span className="stat-detail">Next automated refresh</span>
        </div>
      </div>

      {/* Account Filters */}
      <AccountTabs activeTab={activeTab} onChange={setActiveTab} />

      {/* Tools Grid */}
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: 'var(--space-md)' }}>AI Coding Tools</h2>
      <div className="tool-cards-grid">
        {tools.map((t) => {
          const info = getSourceQuotaInfo(t.id)
          // Find accounts of this source
          const sourceAccounts = filteredAccounts.filter((acc: any) => acc.source === t.id)
          const accountLabel = sourceAccounts.map((a: any) => a.label).join(', ') || 'Not configured'

          return (
            <ToolCard
              key={t.id}
              name={t.name}
              source={t.id}
              accountLabel={accountLabel}
              avgQuotaPct={info.pct}
              creditsText={info.detail}
              nextResetText={info.reset}
              onClick={() => navigate(t.route)}
            />
          )
        })}
      </div>
    </div>
  )
}
