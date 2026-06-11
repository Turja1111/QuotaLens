import { useState, useEffect } from 'react'

export interface QuotaSnapshot {
  id: string
  account_id: string
  source: string
  model_id: string
  model_label: string
  snapshot_at: string
  quota_remaining_pct: number | null
  is_exhausted: boolean
  reset_at: string | null
  reset_cadence: string | null
  requests_used: number | null
  requests_total: number | null
  credits_used: string | null
  credits_total: string | null
}

export function useQuotaStream() {
  const [snapshots, setSnapshots] = useState<QuotaSnapshot[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimeout: number | null = null

    function connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host === 'localhost:5173' ? 'localhost:8000' : window.location.host
      const url = `${protocol}//${host}/ws/quota`

      ws = new WebSocket(url)

      ws.onopen = () => {
        setIsConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data && data.error) {
            setError(data.error)
          } else if (Array.isArray(data)) {
            setSnapshots(data)
          }
        } catch (err: any) {
          console.error('Failed to parse WebSocket message:', err)
        }
      }

      ws.onerror = (err) => {
        console.error('WebSocket error:', err)
        setError('WebSocket connection error')
      }

      ws.onclose = () => {
        setIsConnected(false)
        // Reconnect after 3 seconds
        reconnectTimeout = window.setTimeout(() => {
          connect()
        }, 3000)
      }
    }

    connect()

    return () => {
      if (ws) {
        ws.close()
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
    }
  }, [])

  return { snapshots, isConnected, error }
}
