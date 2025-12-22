import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useData } from '../context/DataContext'
import LoadingScreen from './LoadingScreen'
import './Layout.css'

const NavIcon = ({ id }) => {
  const icons = {
    transactions: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="12" y1="1" x2="12" y2="23" />
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
      </svg>
    ),
    calculator: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="4" y="2" width="16" height="20" rx="2" />
        <line x1="8" y1="6" x2="16" y2="6" />
        <line x1="16" y1="14" x2="16" y2="14" />
        <line x1="8" y1="14" x2="8" y2="14" />
        <line x1="12" y1="14" x2="12" y2="14" />
        <line x1="16" y1="18" x2="16" y2="18" />
        <line x1="8" y1="18" x2="8" y2="18" />
        <line x1="12" y1="18" x2="12" y2="18" />
      </svg>
    ),
    balance: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
        <line x1="1" y1="10" x2="23" y2="10" />
      </svg>
    ),
    statistics: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10" />
        <line x1="12" y1="20" x2="12" y2="4" />
      </svg>
    ),
    referral: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="8.5" cy="7" r="4" />
        <line x1="20" y1="8" x2="20" y2="14" />
        <line x1="23" y1="11" x2="17" y2="11" />
      </svg>
    ),
    more: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="1" />
        <circle cx="19" cy="12" r="1" />
        <circle cx="5" cy="12" r="1" />
      </svg>
    ),
  }

  return icons[id] || null
}

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  const { loading } = useData()

  if (loading) {
    return <LoadingScreen />
  }

  const tabs = [
    { id: 'transactions', path: '/transactions' },
    { id: 'calculator', path: '/calculator' },
    { id: 'balance', path: '/balance' },
    { id: 'statistics', path: '/statistics' },
    { id: 'more', path: '/more' },
  ]

  return (
    <div className="layout">
      <main className="layout-content">
        <Outlet />
      </main>

      <nav className="bottom-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-item ${location.pathname === tab.path ? 'active' : ''}`}
            onClick={() => navigate(tab.path)}
          >
            <span className="nav-icon">
              <NavIcon id={tab.id} />
            </span>
            <span className="nav-label">{t(tab.id)}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
