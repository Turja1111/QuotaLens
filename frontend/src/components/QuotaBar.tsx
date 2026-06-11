import { useEffect, useState } from 'react'

interface QuotaBarProps {
  label: string
  pct: number | null // value between 0 and 1
  isExhausted: boolean
  resetAt: string | null
  requestsUsed?: number | null
  requestsTotal?: number | null
  creditsUsed?: string | null
  creditsTotal?: string | null
}

export function QuotaBar({
  label,
  pct,
  isExhausted,
  resetAt,
  requestsUsed,
  requestsTotal,
  creditsUsed,
  creditsTotal,
}: QuotaBarProps) {
  const [timeLeft, setTimeLeft] = useState<string>('')

  // Calculate real-time countdown
  useEffect(() => {
    if (!resetAt) {
      setTimeLeft('')
      return
    }

    function updateTimer() {
      const now = new Date().getTime()
      const target = new Date(resetAt!).getTime()
      const diff = target - now

      if (diff <= 0) {
        setTimeLeft('Refreshed')
        return
      }

      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((diff % (1000 * 60)) / 1000)

      if (hours > 0) {
        setTimeLeft(`Refreshes in ${hours}h ${minutes}m`)
      } else if (minutes > 0) {
        setTimeLeft(`Refreshes in ${minutes}m ${seconds}s`)
      } else {
        setTimeLeft(`Refreshes in ${seconds}s`)
      }
    }

    updateTimer()
    const interval = setInterval(updateTimer, 1000)
    return () => clearInterval(interval)
  }, [resetAt])

  // Determine percentage and color class
  const percent = pct !== null ? Math.round(pct * 100) : null
  
  let colorClass = 'high'
  if (isExhausted || (percent !== null && percent === 0)) {
    colorClass = 'exhausted'
  } else if (percent !== null) {
    if (percent < 20) {
      colorClass = 'low'
    } else if (percent < 50) {
      colorClass = 'mid'
    }
  }

  // Display detail string e.g. "412 / 500 requests" or "$2.50 / $10.00 credits"
  let detailText = ''
  if (requestsUsed !== undefined && requestsUsed !== null && requestsTotal) {
    detailText = `${requestsUsed} / ${requestsTotal} reqs`
  } else if (creditsUsed && creditsTotal) {
    detailText = `$${parseFloat(creditsUsed).toFixed(2)} / $${parseFloat(creditsTotal).toFixed(2)}`
  }

  return (
    <div className="quota-bar-container">
      <div className="quota-bar-header">
        <span className="quota-bar-label">{label}</span>
        <div className="quota-bar-stats">
          {detailText && <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{detailText}</span>}
          {percent !== null && <span className={`quota-bar-pct ${colorClass}`}>{percent}%</span>}
          {timeLeft && <span className="quota-bar-timer">{timeLeft}</span>}
        </div>
      </div>
      <div className="quota-bar-track">
        <div
          className={`quota-bar-fill ${colorClass}`}
          style={{ width: `${percent !== null ? Math.max(0, Math.min(100, percent)) : 0}%` }}
        />
      </div>
    </div>
  )
}
