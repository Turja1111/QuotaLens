import { useState } from 'react'
import {
  useAccounts,
  useAccountMutations,
  useGeminiLimits,
  useGeminiLimitsMutation,
  useDbStats,
  useDataMutations,
} from '../hooks/useUsageQuery'
import {
  UserCheck,
  Settings,
  Database,
  Shield,
  Play,
  Trash2,
  Download,
  ExternalLink,
  Plus,
} from 'lucide-react'

type SettingsTab = 'accounts' | 'gemini' | 'data' | 'admin'

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('accounts')

  // Accounts Queries & Mutations
  const { data: accountsData, isLoading: isAccountsLoading } = useAccounts()
  const { create: createAccount, remove: removeAccount, testConnection } = useAccountMutations()

  // Accounts Form State
  const [showAddAccount, setShowAddAccount] = useState(false)
  const [accId, setAccId] = useState('')
  const [accLabel, setAccLabel] = useState('')
  const [accEmail, setAccEmail] = useState('')
  const [accSource, setAccSource] = useState('antigravity')
  const [accSlot, setAccSlot] = useState('')

  // Connection testing states
  const [testResults, setTestResults] = useState<Record<string, { ok: boolean; message: string }>>({})
  const [testingId, setTestingId] = useState<string | null>(null)

  // Gemini Limits Queries & Mutations
  const { data: geminiData, isLoading: isGeminiLoading } = useGeminiLimits()
  const updateGeminiLimit = useGeminiLimitsMutation()
  const [editingLimitModel, setEditingLimitModel] = useState<string | null>(null)
  const [limitRpm, setLimitRpm] = useState(0)
  const [limitTpm, setLimitTpm] = useState(0)
  const [limitRpd, setLimitRpd] = useState(0)

  // Data Queries & Mutations
  const { data: dbStats, isLoading: isStatsLoading, refetch: refetchStats } = useDbStats()
  const { purge: purgeData } = useDataMutations()
  const [purgeDays, setPurgeDays] = useState(30)
  const [purgeMessage, setPurgeMessage] = useState('')

  const accounts = accountsData?.accounts || []
  const geminiLimits = geminiData?.configs || []

  // ── Handlers ───────────────────────────────────────────────────────────
  const handleAddAccountSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!accId || !accLabel) return
    
    createAccount.mutate(
      {
        id: accId,
        label: accLabel,
        email: accEmail || null,
        source: accSource,
        gmail_slot: accSlot || null,
      },
      {
        onSuccess: () => {
          setShowAddAccount(false)
          setAccId('')
          setAccLabel('')
          setAccEmail('')
          setAccSlot('')
        },
      }
    )
  }

  const handleTestConnection = (id: string) => {
    setTestingId(id)
    testConnection.mutate(id, {
      onSuccess: (data) => {
        setTestResults((prev) => ({ ...prev, [id]: data }))
        setTestingId(null)
      },
      onError: (err) => {
        setTestResults((prev) => ({ ...prev, [id]: { ok: false, message: err.message || 'Network error' } }))
        setTestingId(null)
      },
    })
  }

  const handleEditLimitClick = (config: any) => {
    setEditingLimitModel(config.model_id)
    setLimitRpm(config.rpm)
    setLimitTpm(config.tpm)
    setLimitRpd(config.rpd)
  }

  const handleSaveLimit = (model_id: string) => {
    updateGeminiLimit.mutate(
      {
        model_id,
        data: { rpm: limitRpm, tpm: limitTpm, rpd: limitRpd },
      },
      {
        onSuccess: () => {
          setEditingLimitModel(null)
        },
      }
    )
  }

  const handlePurge = () => {
    if (!window.confirm(`Are you sure you want to purge data older than ${purgeDays} days?`)) return
    purgeData.mutate(purgeDays, {
      onSuccess: (res) => {
        setPurgeMessage(res.message)
        refetchStats()
        setTimeout(() => setPurgeMessage(''), 4000)
      },
    })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
      {/* Page Header */}
      <div className="page-header">
        <h1>System Settings</h1>
        <p>Manage API integrations, rate thresholds, backups and database operations</p>
      </div>

      {/* Settings Navigation Tabs */}
      <div className="account-tabs">
        <button
          type="button"
          className={`account-tab ${activeTab === 'accounts' ? 'active' : ''}`}
          onClick={() => setActiveTab('accounts')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <UserCheck size={14} /> Accounts
        </button>
        <button
          type="button"
          className={`account-tab ${activeTab === 'gemini' ? 'active' : ''}`}
          onClick={() => setActiveTab('gemini')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <Settings size={14} /> Gemini Limits
        </button>
        <button
          type="button"
          className={`account-tab ${activeTab === 'data' ? 'active' : ''}`}
          onClick={() => setActiveTab('data')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <Database size={14} /> Data Manager
        </button>
        <button
          type="button"
          className={`account-tab ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
          style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
        >
          <Shield size={14} /> SQL Admin
        </button>
      </div>

      {/* ── TAB 1: ACCOUNTS MANAGER ── */}
      {activeTab === 'accounts' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Registered Connection Accounts</h3>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={() => setShowAddAccount(!showAddAccount)}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <Plus size={14} /> Add Account
            </button>
          </div>

          {showAddAccount && (
            <form className="card" onSubmit={handleAddAccountSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600 }}>Register New Connection</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-md)' }}>
                <div className="form-group">
                  <label className="form-label">Unique Account ID *</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. gmail1_gemini"
                    value={accId}
                    onChange={(e) => setAccId(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Readable Label *</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. Gmail 1 Gemini Key"
                    value={accLabel}
                    onChange={(e) => setAccLabel(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Email Address (Optional)</label>
                  <input
                    type="email"
                    className="form-control"
                    placeholder="e.g. user@gmail.com"
                    value={accEmail}
                    onChange={(e) => setAccEmail(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Source Provider</label>
                  <select className="form-control" value={accSource} onChange={(e) => setAccSource(e.target.value)}>
                    <option value="antigravity">Antigravity</option>
                    <option value="cursor">Cursor</option>
                    <option value="copilot">GitHub Copilot</option>
                    <option value="gemini">Gemini API</option>
                    <option value="openrouter">OpenRouter</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Gmail Slot Mapping</label>
                  <select className="form-control" value={accSlot} onChange={(e) => setAccSlot(e.target.value)}>
                    <option value="">None (Single Account)</option>
                    <option value="gmail1">Gmail Slot 1</option>
                    <option value="gmail2">Gmail Slot 2</option>
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 'var(--space-md)', justifyContent: 'end' }}>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowAddAccount(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary btn-sm" disabled={createAccount.isPending}>
                  {createAccount.isPending ? 'Registering...' : 'Register'}
                </button>
              </div>
            </form>
          )}

          {isAccountsLoading ? (
            <div className="card" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading account registry...</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {accounts.map((acc) => (
                <div
                  key={acc.id}
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
                  <div>
                    <h4 style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {acc.label}
                      <span className={`source-badge ${acc.source}`}>{acc.source}</span>
                    </h4>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      ID: <span className="mono">{acc.id}</span> | Email: {acc.email || 'N/A'} | Slot:{' '}
                      {acc.gmail_slot || 'None'}
                    </p>
                    {testResults[acc.id] && (
                      <p
                        style={{
                          fontSize: '0.75rem',
                          color: testResults[acc.id].ok ? 'var(--color-success)' : 'var(--color-danger)',
                          marginTop: '4px',
                          fontWeight: 500,
                        }}
                      >
                        Connection Test: {testResults[acc.id].ok ? '✓ Passed' : '✗ Failed'} ({testResults[acc.id].message})
                      </p>
                    )}
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      disabled={testingId === acc.id}
                      onClick={() => handleTestConnection(acc.id)}
                      style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
                    >
                      <Play size={12} /> {testingId === acc.id ? 'Testing...' : 'Test Connection'}
                    </button>
                    <button
                      type="button"
                      className="btn btn-danger btn-sm"
                      onClick={() => {
                        if (window.confirm('Delete this account integration?')) {
                          removeAccount.mutate(acc.id)
                        }
                      }}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── TAB 2: GEMINI API CONFIGS ── */}
      {activeTab === 'gemini' && (
        <div className="card">
          <h3 style={{ fontSize: '1rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '16px' }}>
            Gemini Free Tier API Rate Limits
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: 1.5 }}>
            Customize your local fallback rates for the Gemini Free Key API. These values are used to compute remaining percentages and progress bars on the VS Code panel page.
          </p>

          {isGeminiLoading ? (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading limit configurations...</div>
          ) : (
            <div className="data-table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Model Label</th>
                    <th>Model ID</th>
                    <th>RPM (Reqs/Min)</th>
                    <th>TPM (Tokens/Min)</th>
                    <th>RPD (Reqs/Day)</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {geminiLimits.map((cfg) => (
                    <tr key={cfg.model_id}>
                      <td style={{ fontWeight: 500 }}>{cfg.model_label}</td>
                      <td className="mono" style={{ fontSize: '0.75rem' }}>{cfg.model_id}</td>
                      <td>
                        {editingLimitModel === cfg.model_id ? (
                          <input
                            type="number"
                            className="form-control"
                            style={{ width: '80px', padding: '4px' }}
                            value={limitRpm}
                            onChange={(e) => setLimitRpm(parseInt(e.target.value))}
                          />
                        ) : (
                          cfg.rpm
                        )}
                      </td>
                      <td>
                        {editingLimitModel === cfg.model_id ? (
                          <input
                            type="number"
                            className="form-control"
                            style={{ width: '100px', padding: '4px' }}
                            value={limitTpm}
                            onChange={(e) => setLimitTpm(parseInt(e.target.value))}
                          />
                        ) : (
                          cfg.tpm.toLocaleString()
                        )}
                      </td>
                      <td>
                        {editingLimitModel === cfg.model_id ? (
                          <input
                            type="number"
                            className="form-control"
                            style={{ width: '80px', padding: '4px' }}
                            value={limitRpd}
                            onChange={(e) => setLimitRpd(parseInt(e.target.value))}
                          />
                        ) : (
                          cfg.rpd.toLocaleString()
                        )}
                      </td>
                      <td>
                        {editingLimitModel === cfg.model_id ? (
                          <div style={{ display: 'flex', gap: '4px' }}>
                            <button
                              type="button"
                              className="btn btn-primary btn-sm"
                              style={{ padding: '4px 8px' }}
                              onClick={() => handleSaveLimit(cfg.model_id)}
                            >
                              Save
                            </button>
                            <button
                              type="button"
                              className="btn btn-secondary btn-sm"
                              style={{ padding: '4px 8px' }}
                              onClick={() => setEditingLimitModel(null)}
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            style={{ padding: '4px 8px' }}
                            onClick={() => handleEditLimitClick(cfg)}
                          >
                            Edit
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── TAB 3: DATA MANAGER ── */}
      {activeTab === 'data' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          {/* DB Statistics */}
          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '16px' }}>
              Database Record Statistics
            </h3>
            {isStatsLoading ? (
              <div style={{ color: 'var(--text-muted)' }}>Calculating stats...</div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--space-md)' }}>
                <div style={{ padding: '12px', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {dbStats?.usage_records || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Usage Records</div>
                </div>
                <div style={{ padding: '12px', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {dbStats?.quota_snapshots || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Quota Snapshots</div>
                </div>
                <div style={{ padding: '12px', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {dbStats?.accounts || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Connected Accounts</div>
                </div>
                <div style={{ padding: '12px', background: 'var(--bg-card)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {dbStats?.alert_rules || 0}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>Alert Rules</div>
                </div>
              </div>
            )}
          </div>

          {/* Backup and Purge */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
              Maintenance Tools
            </h3>
            
            {/* Backup */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: '1px solid var(--border-subtle)' }}>
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600 }}>Backup Settings & Records</h4>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Export all accounts, alert rules, gemini limits, and token usage history logs into a single backup JSON.
                </p>
              </div>
              <a href="http://localhost:8000/api/v1/data/export" download className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Download size={14} /> Export Backup
              </a>
            </div>

            {/* Purge */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 600 }}>Purge Stale Records</h4>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Clear logs and snapshots older than a specified duration to optimize storage sizes.
                </p>
              </div>
              
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Older than</span>
                <input
                  type="number"
                  className="form-control"
                  style={{ width: '70px', padding: '6px' }}
                  value={purgeDays}
                  onChange={(e) => setPurgeDays(parseInt(e.target.value))}
                  min="1"
                />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>days</span>
                <button type="button" className="btn btn-danger btn-sm" onClick={handlePurge}>
                  Purge Data
                </button>
              </div>
            </div>

            {purgeMessage && (
              <div className="badge success" style={{ padding: '8px 12px', textTransform: 'none', fontWeight: 'normal', marginTop: 'var(--space-sm)' }}>
                {purgeMessage}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB 4: SQL ADMIN LINK ── */}
      {activeTab === 'admin' && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', alignItems: 'center', textAlign: 'center', padding: 'var(--space-2xl)' }}>
          <Shield size={48} className="text-accent" />
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginTop: '12px' }}>sqladmin Control Console</h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '8px', maxWidth: '400px', lineHeight: 1.5 }}>
              Use the built-in sqladmin dashboard to directly read, create, update, or prune all PostgreSQL rows across all 5 database models with full visual interfaces.
            </p>
          </div>
          <a
            href="http://localhost:8000/admin"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: 'var(--space-md)' }}
          >
            Open SQL Admin Console <ExternalLink size={16} />
          </a>
        </div>
      )}
    </div>
  )
}
