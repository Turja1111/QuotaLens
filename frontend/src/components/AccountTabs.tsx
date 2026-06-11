interface AccountTabsProps {
  activeTab: 'all' | 'gmail1' | 'gmail2'
  onChange: (tab: 'all' | 'gmail1' | 'gmail2') => void
}

export function AccountTabs({ activeTab, onChange }: AccountTabsProps) {
  return (
    <div className="account-tabs">
      <button
        type="button"
        className={`account-tab ${activeTab === 'all' ? 'active' : ''}`}
        onClick={() => onChange('all')}
      >
        All Accounts
      </button>
      <button
        type="button"
        className={`account-tab ${activeTab === 'gmail1' ? 'active' : ''}`}
        onClick={() => onChange('gmail1')}
      >
        Gmail Slot 1
      </button>
      <button
        type="button"
        className={`account-tab ${activeTab === 'gmail2' ? 'active' : ''}`}
        onClick={() => onChange('gmail2')}
      >
        Gmail Slot 2
      </button>
    </div>
  )
}
