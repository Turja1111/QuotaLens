import { QuotaBar } from './QuotaBar'
import type { QuotaSnapshot } from '../hooks/useQuotaStream'

interface QuotaPanelProps {
  title: string
  gmailSlot: 'gmail1' | 'gmail2'
  snapshots: QuotaSnapshot[]
}

export function QuotaPanel({ title, gmailSlot, snapshots }: QuotaPanelProps) {
  // Filter models vs credits
  const modelSnapshots = snapshots.filter(
    (s) => s.model_id !== 'prompt-credits' && s.model_id !== 'flow-credits'
  )
  const promptCredits = snapshots.find((s) => s.model_id === 'prompt-credits')
  const flowCredits = snapshots.find((s) => s.model_id === 'flow-credits')

  return (
    <div className="quota-panel">
      <div className="quota-panel-header">
        <h3 className="quota-panel-title">{title}</h3>
        <span className={`quota-panel-badge ${gmailSlot}`}>
          {gmailSlot === 'gmail1' ? 'Gmail Slot 1' : 'Gmail Slot 2'}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        {modelSnapshots.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', textAlign: 'center', padding: 'var(--space-md)' }}>
            No models active or snapshots found.
          </div>
        ) : (
          modelSnapshots.map((s) => (
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

      {(promptCredits || flowCredits) && (
        <div className="quota-panel-credits">
          {promptCredits && (
            <div className="credit-item">
              <span className="credit-label">{promptCredits.model_label}</span>
              <span className="credit-value">
                {promptCredits.credits_total
                  ? `${Math.round(parseFloat(promptCredits.credits_total) - parseFloat(promptCredits.credits_used || '0'))} / ${promptCredits.credits_total}`
                  : 'N/A'}
              </span>
            </div>
          )}
          {flowCredits && (
            <div className="credit-item">
              <span className="credit-label">{flowCredits.model_label}</span>
              <span className="credit-value">
                {flowCredits.credits_total
                  ? `${Math.round(parseFloat(flowCredits.credits_total) - parseFloat(flowCredits.credits_used || '0'))} / ${flowCredits.credits_total}`
                  : 'N/A'}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
