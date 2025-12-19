import { useData } from '../context/DataContext'
import { useTelegram } from '../context/TelegramContext'
import './Balance.css'

export default function Balance() {
  const { balance, loading } = useData()
  const { user } = useTelegram()

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0)
  }

  if (loading) {
    return (
      <div className="page-loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="balance-page">
      <div className="section-header">
        <h2>💰 Баланс</h2>
        <p>Ваш текущий баланс</p>
      </div>

      <div className="balance-total">
        <span>Общий доступный баланс</span>
        <h1>{formatCurrency(balance.total)}</h1>
      </div>

      <div className="balance-cards">
        <div className="balance-card">
          <div className="card-icon">💳</div>
          <span>Баланс PayPal</span>
          <strong>{formatCurrency(balance.paypal)}</strong>
        </div>
        <div className="balance-card">
          <div className="card-icon">💳</div>
          <span>Баланс Stripe</span>
          <strong>{formatCurrency(balance.stripe)}</strong>
        </div>
      </div>

      <div className="withdrawal-card">
        <div className="withdrawal-header">
          <div className="card-icon">💸</div>
          <span>Вывод PayPal</span>
        </div>
        <strong className="withdrawal-amount">{formatCurrency(balance.withdrawal)}</strong>
      </div>

      <div className="account-info">
        <p>Информация о балансе обновляется из данных вашего аккаунта.</p>
        <div className="account-tag">
          Аккаунт: <strong>{user?.username ? `@${user.username}` : `ID: ${user?.id}`}</strong>
        </div>
      </div>
    </div>
  )
}
