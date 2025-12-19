import { useState } from 'react'
import { useData } from '../context/DataContext'
import { useLanguage } from '../context/LanguageContext'
import './Transactions.css'

export default function Transactions() {
  const { transactions, stats, loading } = useData()
  const { t } = useLanguage()
  const [filter, setFilter] = useState('all')

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return '—'
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(date)
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0)
  }

  // Calculate progress towards VIP
  const vipThreshold = 2000
  const progress = Math.min((stats.totalSum / vipThreshold) * 100, 100)

  // Current month dates
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)

  // Filter transactions
  const filteredTransactions = filter === 'all'
    ? transactions
    : transactions.filter(tx => tx.status === filter)

  if (loading) {
    return (
      <div className="transactions-page">
        <div className="section-header">
          <div className="skeleton skeleton-title"></div>
          <div className="skeleton skeleton-text" style={{ width: '50%' }}></div>
        </div>
        <div className="skeleton-stats">
          <div className="skeleton skeleton-stat-card"></div>
          <div className="skeleton skeleton-stat-card"></div>
        </div>
        {[1, 2, 3, 4, 5].map(i => (
          <div key={i} className="skeleton skeleton-tx"></div>
        ))}
      </div>
    )
  }

  return (
    <div className="transactions-page">
      <div className="section-header">
        <h2>{t('transactionsTitle')}</h2>
        <p>{t('transactionsSubtitle')}</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-overview">
        <div className="stat-card">
          <span className="stat-label">{t('totalAmount')}</span>
          <span className="stat-value">{formatCurrency(stats.totalSum)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">{t('totalTransactions')}</span>
          <span className="stat-value">{stats.totalChecks}</span>
        </div>
      </div>

      {/* Date Range */}
      <div className="date-range">
        <div className="date-item">
          <span>{t('startDate')}</span>
          <strong>{formatDate(startOfMonth)}</strong>
        </div>
        <div className="date-item">
          <span>{t('endDate')}</span>
          <strong>{formatDate(endOfMonth)}</strong>
        </div>
      </div>

      {/* VIP Progress - Premium Design */}
      <div className={`vip-progress ${progress >= 100 ? 'vip-unlocked' : ''}`}>
        <div className="vip-crown-badge">
          <span className="crown-emoji">👑</span>
          <span className="crown-percent">{Math.round(progress)}%</span>
        </div>
        <div className="vip-content">
          <div className="vip-title">
            <span>{progress >= 100 ? 'VIP Status Unlocked!' : t('vipThreshold')}</span>
            <strong>{formatCurrency(stats.totalSum)} / {formatCurrency(vipThreshold)}</strong>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}>
              <div className="progress-glow"></div>
            </div>
          </div>
          {progress < 100 && (
            <span className="vip-hint">
              {formatCurrency(vipThreshold - stats.totalSum)} left to unlock VIP
            </span>
          )}
        </div>
      </div>

      {/* Transactions List */}
      <div className="transactions-list">
        {filteredTransactions.length === 0 ? (
          <div className="empty-state">
            <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3>{t('noTransactions')}</h3>
            <p>{t('transactionsAppear')}</p>
          </div>
        ) : (
          filteredTransactions.map((tx, index) => (
            <div
              key={tx.id}
              className="transaction-item"
              style={{ animationDelay: `${Math.min(index * 0.05, 0.5)}s` }}
            >
              <div className="tx-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  {tx.payment_method?.toLowerCase().includes('paypal') ? (
                    <path d="M7 15l-2 5h3l1-3h2c2 0 4-2 4-4s-2-4-4-4H6l-1 6" />
                  ) : tx.payment_method?.toLowerCase().includes('stripe') ? (
                    <>
                      <rect x="1" y="4" width="22" height="16" rx="2" />
                      <line x1="1" y1="10" x2="23" y2="10" />
                    </>
                  ) : (
                    <>
                      <circle cx="12" cy="12" r="10" />
                      <path d="M12 6v6l4 2" />
                    </>
                  )}
                </svg>
              </div>
              <div className="tx-details">
                <strong>{tx.payment_method || 'Payment'}</strong>
                <span>{formatDate(tx.created_at)}</span>
              </div>
              <div className="tx-amount">
                <strong>{formatCurrency(tx.amount)}</strong>
                <span className={`tx-status status-${tx.status}`}>
                  {tx.status === 'completed' ? t('completed') :
                    tx.status === 'pending' ? t('pending') : t('cancelled')}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
