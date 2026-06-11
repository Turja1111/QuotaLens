import { Zap, Code, ShieldAlert, Cpu, Share2 } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface ToolCardProps {
  name: string
  source: 'antigravity' | 'cursor' | 'copilot' | 'gemini' | 'openrouter'
  accountLabel: string
  avgQuotaPct: number | null
  creditsText?: string | null
  nextResetText?: string | null
  onClick?: () => void
}

export function ToolCard({
  name,
  source,
  accountLabel,
  avgQuotaPct,
  creditsText,
  nextResetText,
  onClick,
}: ToolCardProps) {
  // Select icon based on source
  let Icon: LucideIcon = Code
  if (source === 'antigravity') Icon = Cpu
  if (source === 'cursor') Icon = Zap
  if (source === 'copilot') Icon = ShieldAlert
  if (source === 'openrouter') Icon = Share2

  const percent = avgQuotaPct !== null ? Math.round(avgQuotaPct * 100) : null
  
  let colorClass = 'high'
  if (percent !== null) {
    if (percent < 20) colorClass = 'low'
    else if (percent < 50) colorClass = 'mid'
  } else {
    colorClass = 'exhausted'
  }

  return (
    <div className="tool-card" onClick={onClick}>
      <div className="tool-card-header">
        <div className={`tool-card-icon ${source}`}>
          <Icon size={20} />
        </div>
        <div>
          <div className="tool-card-name">{name}</div>
          <div className="tool-card-account">{accountLabel}</div>
        </div>
      </div>

      <div className="tool-card-quota">
        <div className="quota-bar-container" style={{ marginBottom: 0 }}>
          <div className="quota-bar-header">
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {percent !== null ? 'Avg Remaining' : 'No Snapshot'}
            </span>
            {percent !== null && (
              <span className={`quota-bar-pct ${colorClass}`}>{percent}%</span>
            )}
          </div>
          {percent !== null && (
            <div className="quota-bar-track" style={{ height: '6px' }}>
              <div
                className={`quota-bar-fill ${colorClass}`}
                style={{ width: `${percent}%` }}
              />
            </div>
          )}
        </div>
      </div>

      <div className="tool-card-stats">
        <span>{creditsText || ''}</span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          {nextResetText || ''}
        </span>
      </div>
    </div>
  )
}
