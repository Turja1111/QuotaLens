import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Dashboard } from './pages/Dashboard'
import { AntigravityPage } from './pages/AntigravityPage'
import { VSCodePage } from './pages/VSCodePage'
import { CursorPage } from './pages/CursorPage'
import { HistoryPage } from './pages/HistoryPage'
import { AlertsPage } from './pages/AlertsPage'
import { SettingsPage } from './pages/SettingsPage'
import {
  Home,
  Cpu,
  Layers,
  Zap,
  History,
  Bell,
  Settings,
  ShieldCheck,
} from 'lucide-react'

// Create TanStack Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function NavigationSidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">QL</div>
          <div>
            <div className="sidebar-logo-text">QuotaLens</div>
            <div className="sidebar-logo-version">v1.0.0</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Overview</div>
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
          <Home className="nav-item-icon" />
          Dashboard
        </NavLink>

        <div className="nav-section-label">IDE Quotas</div>
        <NavLink to="/antigravity" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Cpu className="nav-item-icon" />
          Antigravity IDE
        </NavLink>
        <NavLink to="/cursor" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Zap className="nav-item-icon" />
          Cursor IDE
        </NavLink>
        <NavLink to="/vscode" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Layers className="nav-item-icon" />
          VS Code Extensions
        </NavLink>

        <div className="nav-section-label">Analytics & Rules</div>
        <NavLink to="/history" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <History className="nav-item-icon" />
          Usage History
        </NavLink>
        <NavLink to="/alerts" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Bell className="nav-item-icon" />
          Alert Rules
        </NavLink>

        <div className="nav-section-label">Configuration</div>
        <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings className="nav-item-icon" />
          Settings
        </NavLink>

        <div style={{ marginTop: 'auto', padding: 'var(--space-md) 0' }}>
          <a
            href="http://localhost:8000/admin"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-item"
            style={{ opacity: 0.8 }}
          >
            <ShieldCheck className="nav-item-icon text-accent" />
            SQL Admin Console
          </a>
        </div>
      </nav>
    </aside>
  )
}

function AppLayout() {
  return (
    <div className="app-layout">
      <NavigationSidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/antigravity" element={<AntigravityPage />} />
          <Route path="/cursor" element={<CursorPage />} />
          <Route path="/vscode" element={<VSCodePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppLayout />
      </Router>
    </QueryClientProvider>
  )
}
