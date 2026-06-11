import { AlertTriangle, Info, X } from 'lucide-react'
import { useState } from 'react'

interface AlertBannerProps {
  message: string
  type?: 'warning' | 'info' | 'critical'
  onClose?: () => void
}

export function AlertBanner({ message, type = 'warning', onClose }: AlertBannerProps) {
  const [visible, setVisible] = useState(true)

  if (!visible) return null

  let typeClass = 'warning'
  let Icon = AlertTriangle
  if (type === 'info') {
    typeClass = 'info'
    Icon = Info
  } else if (type === 'critical') {
    typeClass = 'danger'
    Icon = AlertTriangle
  }

  const handleClose = () => {
    setVisible(false)
    if (onClose) onClose()
  }

  return (
    <div
      className={`badge ${typeClass}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
        padding: '12px 16px',
        borderRadius: 'var(--radius-md)',
        fontSize: '0.85rem',
        textTransform: 'none',
        fontWeight: 'normal',
        letterSpacing: 'normal',
        marginBottom: 'var(--space-md)',
        boxShadow: 'var(--shadow-sm)',
        border: '1px solid currentColor',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Icon size={18} style={{ flexShrink: 0 }} />
        <span>{message}</span>
      </div>
      <button
        type="button"
        onClick={handleClose}
        style={{
          background: 'transparent',
          border: 'none',
          color: 'inherit',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          padding: 0,
        }}
      >
        <X size={16} />
      </button>
    </div>
  )
}
