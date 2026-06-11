import { useState } from 'react'
import { useAlerts, useAlertMutations, useAccounts } from '../hooks/useUsageQuery'
import { Plus, Trash2, Bell, Play, ToggleLeft, ToggleRight } from 'lucide-react'
import axios from 'axios'

export function AlertsPage() {
  const { data: alertsData, isLoading: isAlertsLoading } = useAlerts()
  const { data: accountsData } = useAccounts()
  const { create, update, remove } = useAlertMutations()

  // Form states
  const [showForm, setShowForm] = useState(false)
  const [label, setLabel] = useState('')
  const [source, setSource] = useState('')
  const [accountId, setAccountId] = useState('')
  const [modelId, setModelId] = useState('')
  const [thresholdPct, setThresholdPct] = useState(75)
  const [channel, setChannel] = useState('desktop')
  const [webhookUrl, setWebhookUrl] = useState('')
  const [cooldownMinutes, setCooldownMinutes] = useState(60)

  // Testing states
  const [testStatus, setTestStatus] = useState<Record<string, 'idle' | 'testing' | 'success' | 'error'>>({})

  const accounts = accountsData?.accounts || []
  const alerts = alertsData?.alerts || []

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (!label) return

    create.mutate(
      {
        label,
        source: source || null,
        account_id: accountId || null,
        model_id: modelId || null,
        threshold_pct: thresholdPct / 100,
        channel,
        webhook_url: webhookUrl || null,
        cooldown_minutes: cooldownMinutes,
      },
      {
        onSuccess: () => {
          setShowForm(false)
          setLabel('')
          setSource('')
          setAccountId('')
          setModelId('')
          setThresholdPct(75)
          setChannel('desktop')
          setWebhookUrl('')
          setCooldownMinutes(60)
        },
      }
    )
  }

  const handleToggleActive = (id: string, currentlyActive: boolean) => {
    update.mutate({ id, data: { is_active: !currentlyActive } })
  }

  const handleTestAlert = async (id: string) => {
    setTestStatus((prev) => ({ ...prev, [id]: 'testing' }))
    try {
      await axios.post(`http://localhost:8000/api/v1/alerts/${id}/test`)
      setTestStatus((prev) => ({ ...prev, [id]: 'success' }))
      setTimeout(() => {
        setTestStatus((prev) => ({ ...prev, [id]: 'idle' }))
      }, 3000)
    } catch (err) {
      console.error(err)
      setTestStatus((prev) => ({ ...prev, [id]: 'error' }))
      setTimeout(() => {
        setTestStatus((prev) => ({ ...prev, [id]: 'idle' }))
      }, 3000)
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
      {/* Page Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Alert Rules & Channels</h1>
          <p>Configure notifications for when token credits or model usage approaches limits</p>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
          style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
        >
          <Plus size={16} /> New Alert Rule
        </button>
      </div>

      {/* Creation Form */}
      {showForm && (
        <form className="card" onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Create New Alert Rule</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-md)' }}>
            <div className="form-group">
              <label className="form-label">Rule Label *</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g. Cursor 90% Limit"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Data Source (Optional)</label>
              <select className="form-control" value={source} onChange={(e) => setSource(e.target.value)}>
                <option value="">Any Source</option>
                <option value="antigravity">Antigravity</option>
                <option value="cursor">Cursor</option>
                <option value="copilot">Copilot</option>
                <option value="gemini">Gemini API</option>
                <option value="openrouter">OpenRouter</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Account (Optional)</label>
              <select className="form-control" value={accountId} onChange={(e) => setAccountId(e.target.value)}>
                <option value="">Any Account</option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Model ID (Optional)</label>
              <input
                type="text"
                className="form-control"
                placeholder="e.g. gemini-3.5-flash"
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Threshold Percentage ({thresholdPct}%)</label>
              <input
                type="range"
                min="10"
                max="100"
                step="5"
                value={thresholdPct}
                onChange={(e) => setThresholdPct(parseInt(e.target.value))}
                style={{ width: '100%', marginTop: '12px' }}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Cooldown Minutes</label>
              <input
                type="number"
                className="form-control"
                value={cooldownMinutes}
                onChange={(e) => setCooldownMinutes(parseInt(e.target.value))}
                min="5"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Channel</label>
              <select className="form-control" value={channel} onChange={(e) => setChannel(e.target.value)}>
                <option value="desktop">Desktop Notification</option>
                <option value="webhook">Slack/Discord Webhook</option>
              </select>
            </div>

            {channel === 'webhook' && (
              <div className="form-group" style={{ gridColumn: 'span 2' }}>
                <label className="form-label">Webhook URL *</label>
                <input
                  type="url"
                  className="form-control"
                  placeholder="https://hooks.slack.com/services/..."
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  required
                />
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-md)', justifyContent: 'end', marginTop: 'var(--space-sm)' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={create.isPending}>
              {create.isPending ? 'Saving...' : 'Create Rule'}
            </button>
          </div>
        </form>
      )}

      {/* Rules List */}
      <div className="card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px' }}>Active Alert Rules</h3>

        {isAlertsLoading ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-lg)', color: 'var(--text-muted)' }}>
            Loading alert definitions...
          </div>
        ) : alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)' }}>
            No alert rules defined. Create one to be notified when thresholds are breached.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            {alerts.map((alert) => (
              <div
                key={alert.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: 'var(--space-md)',
                  background: 'var(--bg-card)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-color)',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'start', gap: '12px' }}>
                  <Bell size={20} className="text-accent" style={{ marginTop: '2px' }} />
                  <div>
                    <h4 style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {alert.label}
                      <span className="badge info" style={{ padding: '1px 6px', fontSize: '0.65rem' }}>
                        {alert.channel}
                      </span>
                    </h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      Trigger: {alert.source ? `[${alert.source}]` : 'Any source'}{' '}
                      {alert.model_id ? `(${alert.model_id})` : ''} at &gt;= {alert.threshold_pct * 100}%{' '}
                      | Cooldown: {alert.cooldown_minutes}m
                    </p>
                    {alert.last_fired_at && (
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        Last triggered: {new Date(alert.last_fired_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                  {/* Toggle active */}
                  <button
                    type="button"
                    style={{ background: 'transparent', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', color: alert.is_active ? 'var(--color-success)' : 'var(--text-muted)' }}
                    onClick={() => handleToggleActive(alert.id, alert.is_active)}
                  >
                    {alert.is_active ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
                  </button>

                  {/* Test button */}
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    disabled={testStatus[alert.id] === 'testing'}
                    onClick={() => handleTestAlert(alert.id)}
                    style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <Play size={12} />
                    {testStatus[alert.id] === 'testing'
                      ? 'Firing...'
                      : testStatus[alert.id] === 'success'
                      ? 'Fired ✓'
                      : testStatus[alert.id] === 'error'
                      ? 'Failed ✗'
                      : 'Test Alert'}
                  </button>

                  {/* Delete button */}
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => remove.mutate(alert.id)}
                    style={{ padding: '8px' }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
