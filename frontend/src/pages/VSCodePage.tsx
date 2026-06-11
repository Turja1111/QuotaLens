import { useState } from 'react'
import { useQuotaStream } from '../hooks/useQuotaStream'
import { QuotaBar } from '../components/QuotaBar'
import { ChevronDown, ChevronUp, Shield, Cpu, Share2 } from 'lucide-react'

export function VSCodePage() {
  const { snapshots: wsSnapshots } = useQuotaStream()
  
  // Accordion toggle states
  const [copilotOpen, setCopilotOpen] = useState(true)
  const [geminiOpen, setGeminiOpen] = useState(true)
  const [openRouterOpen, setOpenRouterOpen] = useState(true)

  // 1. GitHub Copilot Data
  // Mock model list for Copilot (since Copilot REST API provides general info)
  const copilotModels = [
    { name: 'Claude 3.5 Sonnet', context: '200k', capabilities: 'Chat, Autocomplete, Agent', cost: '15.00 In / 15.00 Out / 3.00 Cache' },
    { name: 'GPT-4o', context: '128k', capabilities: 'Chat, Edit', cost: '5.00 In / 15.00 Out / 2.50 Cache' },
    { name: 'Claude Haiku 4.5', context: '8k', capabilities: 'Autocomplete, Chat', cost: '0.61 In / 2.44 Out / 0.15 Cache' },
    { name: 'GPT-5 mini', context: '16k', capabilities: 'Autocomplete, Edit', cost: '0.15 In / 0.60 Out / 0.08 Cache' },
    { name: 'MAI-Code-1-Flash', context: '4k', capabilities: 'Autocomplete', cost: '0.10 In / 0.40 Out / 0.05 Cache' },
  ]

  // ── 2. Gemini API Data ──────────────────────────────────────────────────
  const geminiSnaps = wsSnapshots.filter((s) => s.source === 'gemini')
  const geminiGmail1 = geminiSnaps.filter((s) => s.account_id.includes('gmail1'))
  const geminiGmail2 = geminiSnaps.filter((s) => s.account_id.includes('gmail2'))

  // Calculate Pacific Time Midnight Countdown
  const getPacificMidnightCountdown = () => {


    // Target midnight
    const tomorrow = new Date()
    tomorrow.setHours(24, 0, 0, 0)
    
    const diff = tomorrow.getTime() - new Date().getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    
    return `${hours}h ${minutes}m`
  }

  // ── 3. OpenRouter Data ──────────────────────────────────────────────────
  const orSnaps = wsSnapshots.filter((s) => s.source === 'openrouter')
  const orGmail1 = orSnaps.filter((s) => s.account_id.includes('gmail1'))
  const orGmail2 = orSnaps.filter((s) => s.account_id.includes('gmail2'))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      {/* Page Header */}
      <div className="page-header">
        <h1>VS Code AI Integrations</h1>
        <p>Manage limits and request totals for Copilot, Gemini API and OpenRouter extensions</p>
      </div>

      {/* ── SECTION 1: GITHUB COPILOT ── */}
      <div>
        <div className="section-header" onClick={() => setCopilotOpen(!copilotOpen)}>
          <span className="section-title">
            <Shield className="tool-card-icon copilot" style={{ width: 22, height: 22, padding: 3, borderRadius: 4 }} />
            GitHub Copilot Usage & Model Speeds
          </span>
          {copilotOpen ? <ChevronUp className="section-chevron" /> : <ChevronDown className="section-chevron" />}
        </div>

        {copilotOpen && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Name</th>
                    <th>Context Size</th>
                    <th>Supported Capabilities</th>
                    <th>Token Rates ($ / 1M tokens)</th>
                  </tr>
                </thead>
                <tbody>
                  {copilotModels.map((m) => (
                    <tr key={m.name}>
                      <td style={{ fontWeight: 600 }}>{m.name}</td>
                      <td className="mono">{m.context}</td>
                      <td>{m.capabilities}</td>
                      <td className="mono" style={{ fontSize: '0.8rem' }}>{m.cost}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              *Copilot API credits refresh monthly on GitHub subscription date. Pricing rates denote equivalent usage deduction values.
            </div>
          </div>
        )}
      </div>

      {/* ── SECTION 2: GEMINI API (FREE TIER) ── */}
      <div>
        <div className="section-header" onClick={() => setGeminiOpen(!geminiOpen)}>
          <span className="section-title">
            <Cpu className="tool-card-icon gemini" style={{ width: 22, height: 22, padding: 3, borderRadius: 4 }} />
            Gemini API (Daily Free Tier Counters)
          </span>
          {geminiOpen ? <ChevronUp className="section-chevron" /> : <ChevronDown className="section-chevron" />}
        </div>

        {geminiOpen && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 'var(--space-md)' }}>
            {/* Gmail 1 */}
            <div className="card">
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '12px', display: 'flex', justifyContent: 'between' }}>
                <span>Gmail Slot 1 — limits</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Resets in {getPacificMidnightCountdown()}</span>
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {geminiGmail1.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No configurations configured.</p>
                ) : (
                  geminiGmail1.map((s) => (
                    <QuotaBar
                      key={s.id}
                      label={s.model_label}
                      pct={s.quota_remaining_pct}
                      isExhausted={s.is_exhausted}
                      resetAt={s.reset_at}
                      requestsUsed={s.requests_used}
                      requestsTotal={s.requests_total}
                    />
                  ))
                )}
              </div>
            </div>

            {/* Gmail 2 */}
            <div className="card">
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '12px', display: 'flex', justifyContent: 'between' }}>
                <span>Gmail Slot 2 — limits</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Resets in {getPacificMidnightCountdown()}</span>
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {geminiGmail2.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No configurations configured.</p>
                ) : (
                  geminiGmail2.map((s) => (
                    <QuotaBar
                      key={s.id}
                      label={s.model_label}
                      pct={s.quota_remaining_pct}
                      isExhausted={s.is_exhausted}
                      resetAt={s.reset_at}
                      requestsUsed={s.requests_used}
                      requestsTotal={s.requests_total}
                    />
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── SECTION 3: OPENROUTER FREE TIER ── */}
      <div>
        <div className="section-header" onClick={() => setOpenRouterOpen(!openRouterOpen)}>
          <span className="section-title">
            <Share2 className="tool-card-icon openrouter" style={{ width: 22, height: 22, padding: 3, borderRadius: 4 }} />
            OpenRouter Free Accounts
          </span>
          {openRouterOpen ? <ChevronUp className="section-chevron" /> : <ChevronDown className="section-chevron" />}
        </div>

        {openRouterOpen && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 'var(--space-md)' }}>
            {/* Gmail 1 */}
            <div className="card">
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '12px' }}>
                Gmail Slot 1 — OpenRouter
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {orGmail1.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No configurations configured.</p>
                ) : (
                  orGmail1.map((s) => (
                    <QuotaBar
                      key={s.id}
                      label={s.model_label}
                      pct={s.quota_remaining_pct}
                      isExhausted={s.is_exhausted}
                      resetAt={s.reset_at}
                      requestsUsed={s.requests_used}
                      requestsTotal={s.requests_total}
                      creditsUsed={s.credits_used}
                      creditsTotal={s.credits_total}
                    />
                  ))
                )}
              </div>
            </div>

            {/* Gmail 2 */}
            <div className="card">
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '12px' }}>
                Gmail Slot 2 — OpenRouter
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {orGmail2.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No configurations configured.</p>
                ) : (
                  orGmail2.map((s) => (
                    <QuotaBar
                      key={s.id}
                      label={s.model_label}
                      pct={s.quota_remaining_pct}
                      isExhausted={s.is_exhausted}
                      resetAt={s.reset_at}
                      requestsUsed={s.requests_used}
                      requestsTotal={s.requests_total}
                      creditsUsed={s.credits_used}
                      creditsTotal={s.credits_total}
                    />
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
