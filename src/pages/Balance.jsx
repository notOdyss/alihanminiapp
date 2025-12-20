import { useState, useEffect } from 'react'
import { useData } from '../context/DataContext'
import { useTelegram } from '../context/TelegramContext'
import { useLanguage } from '../context/LanguageContext'
import './Balance.css'

// Animated Number Component
function AnimatedNumber({ value, duration = 1000 }) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    let start = 0
    const end = value || 0
    const increment = end / (duration / 16)
    const timer = setInterval(() => {
      start += increment
      if (start >= end) {
        setDisplayValue(end)
        clearInterval(timer)
      } else {
        setDisplayValue(Math.floor(start))
      }
    }, 16)
    return () => clearInterval(timer)
  }, [value, duration])

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(displayValue)
}

export default function Balance() {
  const { balance, loading } = useData()
  const { user } = useTelegram()
  const { t } = useLanguage()

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0)
  }

  // Calculate percentages for visual
  const total = balance.paypal + balance.stripe + balance.withdrawal || 1
  const paypalPercent = ((balance.paypal || 0) / total) * 100
  const stripePercent = ((balance.stripe || 0) / total) * 100
  const withdrawalPercent = ((balance.withdrawal || 0) / total) * 100

  if (loading) {
    return (
      <div className="balance-page">
        <div className="section-header">
          <div className="skeleton skeleton-title"></div>
          <div className="skeleton skeleton-text" style={{ width: '60%' }}></div>
        </div>
        <div className="skeleton balance-total-skeleton"></div>
        <div className="skeleton-cards">
          <div className="skeleton skeleton-card"></div>
          <div className="skeleton skeleton-card"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="balance-page">
      <div className="section-header">
        <h2>{t('balanceTitle')}</h2>
        <p>{t('balanceSubtitle')}</p>
      </div>

      {/* Total Balance - Hero Card */}
      <div className="balance-total">
        <div className="balance-glow"></div>
        <span className="balance-label">{t('totalBalance')}</span>
        <h1 className="balance-value">
          <AnimatedNumber value={balance.total} duration={1200} />
        </h1>
        <div className="balance-indicator">
          <span className="indicator-dot"></span>
          <span>Synced just now</span>
        </div>
      </div>

      {/* Balance Distribution */}
      <div className="balance-distribution">
        <div className="distribution-bar">
          <div
            className="bar-paypal"
            style={{ width: `${paypalPercent}%` }}
          ></div>
          <div
            className="bar-stripe"
            style={{ width: `${stripePercent}%` }}
          ></div>
          <div
            className="bar-withdrawal"
            style={{ width: `${withdrawalPercent}%` }}
          ></div>
        </div>
        <div className="distribution-legend">
          <div className="legend-item">
            <span className="legend-dot paypal"></span>
            <span>PayPal</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot stripe"></span>
            <span>Stripe</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot withdrawal"></span>
            <span>Withdrawal</span>
          </div>
        </div>
      </div>

      {/* Balance Cards */}
      <div className="balance-cards">
        <div className="balance-card paypal-card">
          <div className="card-header">
            <div className="card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M7 15l-2 5h3l1-3h2c2 0 4-2 4-4s-2-4-4-4H6l-1 6" />
              </svg>
            </div>
            <span className="card-badge">Active</span>
          </div>
          <span className="card-label">{t('paypalBalance')}</span>
          <strong className="card-value">{formatCurrency(balance.paypal)}</strong>
        </div>

        <div className="balance-card stripe-card">
          <div className="card-header">
            <div className="card-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="1" y="4" width="22" height="16" rx="2" />
                <line x1="1" y1="10" x2="23" y2="10" />
              </svg>
            </div>
            <span className="card-badge">Active</span>
          </div>
          <span className="card-label">{t('stripeBalance')}</span>
          <strong className="card-value">{formatCurrency(balance.stripe)}</strong>
        </div>
      </div>

      {/* Withdrawal Card */}
      <div className="withdrawal-card">
        <div className="withdrawal-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2v10m0 0l-4-4m4 4l4-4" />
            <path d="M4 14v5a2 2 0 002 2h12a2 2 0 002-2v-5" />
          </svg>
        </div>
        <div className="withdrawal-info">
          <span>{t('withdrawalPaypal')}</span>
          <strong>{formatCurrency(balance.withdrawal)}</strong>
        </div>
        <div className="withdrawal-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14m-7-7l7 7-7 7" />
          </svg>
        </div>
      </div>

      {/* Account Info */}
      <div className="account-info">
        <div className="account-avatar">
          {user?.first_name?.charAt(0) || '?'}
        </div>
        <div className="account-details">
          <strong>{user?.first_name} {user?.last_name}</strong>
          <span>{user?.username ? `@${user.username}` : `ID: ${user?.id}`}</span>
        </div>
      </div>
    </div>
  )
}
