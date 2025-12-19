import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useTelegram } from '../context/TelegramContext'
import './Layout.css'

const tabs = [
  { id: 'transactions', label: 'Транзакции', icon: '📊', path: '/transactions' },
  { id: 'calculator', label: 'Калькулятор', icon: '🧮', path: '/calculator' },
  { id: 'balance', label: 'Баланс', icon: '💰', path: '/balance' },
  { id: 'statistics', label: 'Статистика', icon: '📈', path: '/statistics' },
  { id: 'more', label: 'Еще', icon: '⚙️', path: '/more' },
]

export default function Layout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useTelegram()

  const getInitials = () => {
    if (!user) return 'AU'
    const first = user.first_name?.[0] || ''
    const last = user.last_name?.[0] || ''
    return (first + last).toUpperCase() || 'U'
  }

  const getDisplayName = () => {
    if (!user) return 'Пользователь'
    return user.first_name || 'Пользователь'
  }

  const getUsername = () => {
    if (!user) return '@username'
    return user.username ? `@${user.username}` : `ID: ${user.id}`
  }

  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="user-info">
          <div className="user-avatar">
            <span>{getInitials()}</span>
          </div>
          <div className="user-details">
            <h3>{getDisplayName()}</h3>
            <p>{getUsername()}</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <Outlet />
      </main>

      <nav className="app-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-btn ${location.pathname === tab.path ? 'active' : ''}`}
            onClick={() => navigate(tab.path)}
          >
            <span className="nav-icon">{tab.icon}</span>
            <span className="nav-label">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  )
}
