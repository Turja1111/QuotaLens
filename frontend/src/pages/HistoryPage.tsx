import { useState } from 'react'
import { useUsageHistory, useUsageSummary } from '../hooks/useUsageQuery'
import { UsageChart } from '../components/UsageChart'
import { ModelTable } from '../components/ModelTable'
import { BarChart3, LineChart, PieChart, DollarSign, SlidersHorizontal } from 'lucide-react'

export function HistoryPage() {
  const [days, setDays] = useState<number>(30)
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [accountFilter, setAccountFilter] = useState<string>('')
  
  // Tab states for charts
  const [activeChartTab, setActiveChartTab] = useState<'tokens' | 'models' | 'share' | 'cost'>('tokens')

  // Fetch summary data for charts
  const { data: summaryData, isLoading: isSummaryLoading } = useUsageSummary({
    source: sourceFilter || undefined,
    account_id: accountFilter || undefined,
    days: days,
  })

  // Fetch raw records for table
  const { data: rawRecordsData, isLoading: isRecordsLoading } = useUsageHistory({
    source: sourceFilter || undefined,
    account_id: accountFilter || undefined,
  })

  // ── Data Formatting for Charts ─────────────────────────────────────────
  const rawSummary = summaryData?.summary || []

  // 1. Line/Area Chart — Daily Token Totals (input, output, cache grouped by day)
  const dailyTokensMap: Record<string, { day: string; input_tokens: number; output_tokens: number; cache_tokens: number }> = {}
  rawSummary.forEach((item) => {
    const d = item.day
    if (!dailyTokensMap[d]) {
      dailyTokensMap[d] = { day: d, input_tokens: 0, output_tokens: 0, cache_tokens: 0 }
    }
    dailyTokensMap[d].input_tokens += item.input_tokens
    dailyTokensMap[d].output_tokens += item.output_tokens
    dailyTokensMap[d].cache_tokens += item.cache_tokens
  })
  const dailyTokensData = Object.values(dailyTokensMap).sort((a, b) => a.day.localeCompare(b.day))

  // 2. Bar Chart — Per-model breakdown (stacked bar per day)
  const dailyModelsMap: Record<string, any> = {}
  rawSummary.forEach((item) => {
    const d = item.day
    const model = item.model_label
    const tokens = item.input_tokens + item.output_tokens
    
    if (!dailyModelsMap[d]) {
      dailyModelsMap[d] = { day: d, total_tokens: 0 }
    }
    dailyModelsMap[d][model] = (dailyModelsMap[d][model] || 0) + tokens
    dailyModelsMap[d].total_tokens += tokens
  })
  const dailyModelsData = Object.values(dailyModelsMap).sort((a, b) => a.day.localeCompare(b.day))

  // 3. Donut Chart — Token share across all models today or overall
  const modelShareMap: Record<string, number> = {}
  let totalOverallTokens = 0
  rawSummary.forEach((item) => {
    const model = item.model_label
    const tokens = item.input_tokens + item.output_tokens
    modelShareMap[model] = (modelShareMap[model] || 0) + tokens
    totalOverallTokens += tokens
  })
  const modelShareData = Object.entries(modelShareMap).map(([name, value]) => ({
    name,
    value,
    percentage: totalOverallTokens > 0 ? Math.round((value / totalOverallTokens) * 100) : 0,
  })).sort((a, b) => b.value - a.value)

  // 4. Cost Chart — USD spend over time (accumulated per day)
  const dailyCostMap: Record<string, { day: string; cost: number }> = {}
  rawSummary.forEach((item) => {
    const d = item.day
    const cost = item.cost_usd || 0
    if (!dailyCostMap[d]) {
      dailyCostMap[d] = { day: d, cost: 0 }
    }
    dailyCostMap[d].cost += cost
  })
  const dailyCostData = Object.values(dailyCostMap).sort((a, b) => a.day.localeCompare(b.day))

  const isLoading = isSummaryLoading || isRecordsLoading

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
      {/* Page Header */}
      <div className="page-header">
        <h1>Usage History & Analytics</h1>
        <p>Analyze model queries, token shares and cumulative cost logs</p>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ display: 'flex', gap: 'var(--space-md)', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          <SlidersHorizontal size={16} /> Filters:
        </div>

        <select
          className="form-control"
          style={{ width: '160px' }}
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
        >
          <option value="">All Sources</option>
          <option value="antigravity">Antigravity</option>
          <option value="cursor">Cursor</option>
          <option value="copilot">GitHub Copilot</option>
          <option value="gemini">Gemini API</option>
          <option value="openrouter">OpenRouter</option>
        </select>

        <input
          type="text"
          className="form-control"
          placeholder="Filter Account ID..."
          style={{ width: '200px' }}
          value={accountFilter}
          onChange={(e) => setAccountFilter(e.target.value)}
        />

        <div style={{ display: 'flex', gap: '4px', background: 'var(--bg-input)', padding: '4px', borderRadius: 'var(--radius-sm)' }}>
          <button
            type="button"
            className="btn btn-sm"
            style={{
              padding: '6px 12px',
              background: days === 30 ? 'var(--accent-primary)' : 'transparent',
              color: days === 30 ? 'white' : 'var(--text-secondary)',
            }}
            onClick={() => setDays(30)}
          >
            30 Days
          </button>
          <button
            type="button"
            className="btn btn-sm"
            style={{
              padding: '6px 12px',
              background: days === 90 ? 'var(--accent-primary)' : 'transparent',
              color: days === 90 ? 'white' : 'var(--text-secondary)',
            }}
            onClick={() => setDays(90)}
          >
            90 Days
          </button>
        </div>
      </div>

      {/* Chart Section */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
            Visual Analytics
          </h3>
          <div style={{ display: 'flex', gap: 'var(--space-xs)' }}>
            <button
              type="button"
              className={`btn btn-secondary btn-sm ${activeChartTab === 'tokens' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('tokens')}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <LineChart size={14} /> Tokens Over Time
            </button>
            <button
              type="button"
              className={`btn btn-secondary btn-sm ${activeChartTab === 'models' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('models')}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <BarChart3 size={14} /> Model Stack
            </button>
            <button
              type="button"
              className={`btn btn-secondary btn-sm ${activeChartTab === 'share' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('share')}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <PieChart size={14} /> Model Share
            </button>
            <button
              type="button"
              className={`btn btn-secondary btn-sm ${activeChartTab === 'cost' ? 'active' : ''}`}
              onClick={() => setActiveChartTab('cost')}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              <DollarSign size={14} /> USD Spend
            </button>
          </div>
        </div>

        {isLoading ? (
          <div style={{ height: '350px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Preparing charts...</span>
          </div>
        ) : (
          <div>
            {activeChartTab === 'tokens' && <UsageChart type="line" data={dailyTokensData} />}
            {activeChartTab === 'models' && <UsageChart type="bar" data={dailyModelsData} />}
            {activeChartTab === 'share' && <UsageChart type="donut" data={modelShareData} />}
            {activeChartTab === 'cost' && <UsageChart type="cost" data={dailyCostData} />}
          </div>
        )}
      </div>

      {/* Raw Data Table */}
      <div className="card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px' }}>Raw Usage Log</h3>
        {isRecordsLoading ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-xl)', color: 'var(--text-muted)' }}>
            Fetching history data...
          </div>
        ) : (
          <ModelTable records={rawRecordsData?.records || []} />
        )}
      </div>
    </div>
  )
}
