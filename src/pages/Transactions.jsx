import { useData } from '../context/DataContext'
import { useLanguage } from '../context/LanguageContext'
import './Transactions.css'

export default function Transactions() {
  const { transactions, stats, loading } = useData()
  const { t } = useLanguage()

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return new Intl.DateTimeFormat('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    }).format(date)
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0)
  }

  // Calculate progress towards VIP
  const vipThreshold = 2000
  const progress = Math.min((stats.totalSum / vipThreshold) * 100, 100)

  // Calculate date range
  const now = new Date()
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)

  if (loading) {
    return (
      <div className="page-loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="transactions-page">
      <div className="section-header">
        <h2>{t('transactionsTitle')}</h2>
        <p>{t('transactionsSubtitle')}</p>
      </div>

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

      <div className="vip-progress">
        <div className="progress-header">
          <span>{t('vipThreshold')} ({formatCurrency(vipThreshold)})</span>
          <span>{formatCurrency(stats.totalSum)} / {formatCurrency(vipThreshold)}</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      <div className="transactions-list">
        {transactions.length === 0 ? (
          <div className="empty-state">
            <svg className="empty-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M9 14l-5-5m0 0l5-5m-5 5h16"/>
            </svg>
            <p>{t('noTransactions')}</p>
            <span>{t('transactionsAppear')}</span>
          </div>
        ) : (
          transactions.map((tx) => (
            <div key={tx.id} className="transaction-item">
              <div className="tx-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
                  <line x1="1" y1="10" x2="23" y2="10"/>
                </svg>
              </div>
              <div className="tx-details">
                <strong>{tx.payment_method}</strong>
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
