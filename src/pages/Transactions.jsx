import { useData } from '../context/DataContext'
import './Transactions.css'

export default function Transactions() {
  const { transactions, stats, loading } = useData()

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
        <h2>📊 Транзакции</h2>
        <p>История ваших последних транзакций</p>
      </div>

      <div className="stats-overview">
        <div className="stat-card">
          <span className="stat-label">Общая сумма</span>
          <span className="stat-value">{formatCurrency(stats.totalSum)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Транзакций</span>
          <span className="stat-value">{stats.totalChecks}</span>
        </div>
      </div>

      <div className="date-range">
        <div className="date-item">
          <span>Начало</span>
          <strong>{formatDate(startOfMonth)}</strong>
        </div>
        <div className="date-item">
          <span>Конец</span>
          <strong>{formatDate(endOfMonth)}</strong>
        </div>
      </div>

      <div className="vip-progress">
        <div className="progress-header">
          <span>Порог VIP ({formatCurrency(vipThreshold)})</span>
          <span>{formatCurrency(stats.totalSum)} / {formatCurrency(vipThreshold)}</span>
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      <div className="transactions-list">
        {transactions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>Пока нет транзакций</p>
            <span>Ваши транзакции появятся здесь</span>
          </div>
        ) : (
          transactions.map((tx) => (
            <div key={tx.id} className="transaction-item">
              <div className="tx-icon">
                {tx.payment_method === 'PayPal' ? '💳' :
                 tx.payment_method === 'Stripe' ? '💳' : '💰'}
              </div>
              <div className="tx-details">
                <strong>{tx.payment_method}</strong>
                <span>{formatDate(tx.created_at)}</span>
              </div>
              <div className="tx-amount">
                <strong>{formatCurrency(tx.amount)}</strong>
                <span className={`tx-status status-${tx.status}`}>
                  {tx.status === 'completed' ? 'Завершено' :
                   tx.status === 'pending' ? 'В обработке' : 'Отменено'}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
