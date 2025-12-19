import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useLanguage } from '../context/LanguageContext'
import './Layout.css'

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useLanguage()

  const tabs = [
    { id: 'transactions', icon: '📊', path: '/transactions' },
    { id: 'calculator', icon: '🧮', path: '/calculator' },
    { id: 'balance', icon: '💰', path: '/balance' },
    { id: 'statistics', icon: '📈', path: '/statistics' },
    { id: 'more', icon: '⚙️', path: '/more' },
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
            <span className="nav-icon">{tab.icon}</span>
            {t(tab.id)}
          </button>
        ))}
      </nav>
    </div>
  )
}
