import { useState } from 'react'
import { useQuotaStream } from '../hooks/useQuotaStream'
import { QuotaBar } from '../components/QuotaBar'
import { useImportCursorCsv } from '../hooks/useUsageQuery'
import { Upload, FileText, CheckCircle, AlertCircle, Info } from 'lucide-react'

export function CursorPage() {
  const { snapshots: wsSnapshots } = useQuotaStream()
  const importCsvMutation = useImportCursorCsv()
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)

  // Filter snapshots for Cursor
  const cursorSnaps = wsSnapshots.filter((s) => s.source === 'cursor')

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.name.endsWith('.csv')) {
        setSelectedFile(file)
      } else {
        alert('Please select a valid CSV file')
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const handleImport = () => {
    if (!selectedFile) return
    importCsvMutation.mutate(selectedFile, {
      onSuccess: () => {
        setSelectedFile(null)
      },
    })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      {/* Page Header */}
      <div className="page-header">
        <h1>Cursor IDE Quota & CSV Upload</h1>
        <p>Monitor your Cursor Pro plan cycle and manually import usage statistics</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 'var(--space-lg)' }}>
        {/* Left Column — Quota Snapshots */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', marginBottom: '16px' }}>
              Cursor Plan Status
            </h3>
            {cursorSnaps.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No active Cursor accounts configured. Add your API credential in Settings to track live remaining tokens.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
                {cursorSnaps.map((s) => (
                  <QuotaBar
                    key={s.id}
                    label={s.model_label}
                    pct={s.quota_remaining_pct}
                    isExhausted={s.is_exhausted}
                    resetAt={s.reset_at}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="card" style={{ display: 'flex', alignItems: 'start', gap: '12px' }}>
            <Info size={20} className="text-accent" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '4px' }}>CSV Import Information</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                Cursor Individual Pro accounts do not have an official REST API for reading historic usage stats. To view your token count trends, export the CSV log from <code>cursor.com/dashboard</code> and drop it into the loader on the right.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column — CSV Upload Form */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Import Cursor Usage CSV</h3>

          {/* Drag & Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragActive ? 'var(--accent-primary)' : 'var(--glass-border)'}`,
              borderRadius: 'var(--radius-md)',
              padding: 'var(--space-xl)',
              textAlign: 'center',
              cursor: 'pointer',
              background: dragActive ? 'rgba(124, 58, 237, 0.05)' : 'var(--bg-input)',
              transition: 'all var(--transition-fast)',
              position: 'relative',
            }}
          >
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                opacity: 0,
                cursor: 'pointer',
              }}
            />
            
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
              <Upload size={32} style={{ color: 'var(--text-secondary)' }} />
              {selectedFile ? (
                <div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <FileText size={16} /> {selectedFile.name}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              ) : (
                <div>
                  <p style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                    Drag & Drop your Cursor CSV file here
                  </p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    or click to browse local files
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Import Button */}
          {selectedFile && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleImport}
              disabled={importCsvMutation.isPending}
              style={{ width: '100%' }}
            >
              {importCsvMutation.isPending ? 'Importing logs...' : 'Parse and Import CSV'}
            </button>
          )}

          {/* Results State */}
          {importCsvMutation.isSuccess && (
            <div className="badge success" style={{ display: 'flex', gap: '8px', padding: '10px 14px', textTransform: 'none', fontWeight: 'normal', width: '100%', border: '1px solid currentColor' }}>
              <CheckCircle size={18} style={{ flexShrink: 0 }} />
              <div>
                <strong>Import Successful!</strong>
                <div style={{ fontSize: '0.75rem', marginTop: '2px' }}>
                  {importCsvMutation.data?.message}
                </div>
              </div>
            </div>
          )}

          {importCsvMutation.isError && (
            <div className="badge danger" style={{ display: 'flex', gap: '8px', padding: '10px 14px', textTransform: 'none', fontWeight: 'normal', width: '100%', border: '1px solid currentColor' }}>
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <div>
                <strong>Import Failed</strong>
                <div style={{ fontSize: '0.75rem', marginTop: '2px' }}>
                  {importCsvMutation.error.message || 'Check CSV formatting and try again.'}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
