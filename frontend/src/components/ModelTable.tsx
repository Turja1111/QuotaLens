import { useState } from 'react'
import type { UsageRecord } from '../hooks/useUsageQuery'
import { ArrowUpDown, Download } from 'lucide-react'

interface ModelTableProps {
  records: UsageRecord[]
}

type SortField = 'timestamp' | 'source' | 'model_label' | 'input_tokens' | 'output_tokens' | 'cost_usd'
type SortOrder = 'asc' | 'desc'

export function ModelTable({ records }: ModelTableProps) {
  const [sortField, setSortField] = useState<SortField>('timestamp')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [filterText, setFilterText] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 15

  // Handle Sort
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  // Filtered records
  const filtered = records.filter((r) => {
    const term = filterText.toLowerCase()
    return (
      r.model_label.toLowerCase().includes(term) ||
      r.source.toLowerCase().includes(term) ||
      r.account_id.toLowerCase().includes(term) ||
      (r.request_type && r.request_type.toLowerCase().includes(term))
    )
  })

  // Sorted records
  const sorted = [...filtered].sort((a, b) => {
    let aVal: any = a[sortField]
    let bVal: any = b[sortField]

    if (sortField === 'timestamp') {
      aVal = new Date(a.timestamp).getTime()
      bVal = new Date(b.timestamp).getTime()
    } else if (sortField === 'cost_usd') {
      aVal = a.cost_usd || 0
      bVal = b.cost_usd || 0
    }

    if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
    return 0
  })

  // Paginated records
  const totalPages = Math.ceil(sorted.length / itemsPerPage)
  const paginated = sorted.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)

  // Export to CSV helper
  const exportToCsv = () => {
    const headers = ['Timestamp', 'Source', 'Account ID', 'Model', 'Input Tokens', 'Output Tokens', 'Cached Tokens', 'Cost USD', 'Type']
    const rows = sorted.map((r) => [
      r.timestamp,
      r.source,
      r.account_id,
      r.model_label,
      r.input_tokens,
      r.output_tokens,
      r.cache_tokens,
      r.cost_usd || 0,
      r.request_type || 'N/A',
    ])

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')

    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `quotalens_export_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
      <div style={{ display: 'flex', justifyContent: 'between', gap: 'var(--space-md)', flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Filter records (model, source, account, type)..."
          className="form-control"
          style={{ flex: 1, minWidth: '240px' }}
          value={filterText}
          onChange={(e) => {
            setFilterText(e.target.value)
            setCurrentPage(1)
          }}
        />
        <button type="button" className="btn btn-secondary" onClick={exportToCsv} disabled={sorted.length === 0}>
          <Download size={16} /> Export CSV ({sorted.length} rows)
        </button>
      </div>

      <div className="data-table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('timestamp')}>
                Timestamp <ArrowUpDown size={12} style={{ marginLeft: 4 }} />
              </th>
              <th onClick={() => handleSort('source')}>
                Source <ArrowUpDown size={12} style={{ marginLeft: 4 }} />
              </th>
              <th>Account</th>
              <th onClick={() => handleSort('model_label')}>
                Model <ArrowUpDown size={12} style={{ marginLeft: 4 }} />
              </th>
              <th onClick={() => handleSort('input_tokens')}>
                Input <ArrowUpDown size={12} style={{ marginLeft: 4 }} />
              </th>
              <th onClick={() => handleSort('output_tokens')}>
                Output <ArrowUpDown size={12} style={{ marginLeft: 4 }} />
              </th>
              <th onClick={() => handleSort('cost_usd')}>
                Cost <ArrowUpDown size={12} style={{ marginLeft: 4 }} />
              </th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {paginated.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 'var(--space-xl)' }}>
                  No usage records match the current criteria
                </td>
              </tr>
            ) : (
              paginated.map((r) => (
                <tr key={r.id}>
                  <td className="mono">{new Date(r.timestamp).toLocaleString()}</td>
                  <td>
                    <span className={`source-badge ${r.source}`}>{r.source}</span>
                  </td>
                  <td style={{ fontSize: '0.8rem' }} className="mono">
                    {r.account_id}
                  </td>
                  <td style={{ fontWeight: 500 }}>{r.model_label}</td>
                  <td className="mono">{r.input_tokens.toLocaleString()}</td>
                  <td className="mono">{r.output_tokens.toLocaleString()}</td>
                  <td className="mono">
                    {r.cost_usd !== null ? `$${parseFloat(r.cost_usd.toString()).toFixed(4)}` : '-'}
                  </td>
                  <td>
                    <span style={{ textTransform: 'capitalize', fontSize: '0.75rem' }}>
                      {r.request_type || '-'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-sm)', alignItems: 'center', marginTop: 'var(--space-md)' }}>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            Prev
          </button>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
