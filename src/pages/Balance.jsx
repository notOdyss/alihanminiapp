import { useData } from '../context/DataContext'
import { useTelegram } from '../context/TelegramContext'
import { useLanguage } from '../context/LanguageContext'
import './Balance.css'

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
        <h2>{t('balanceTitle')}</h2>
        <p>{t('balanceSubtitle')}</p>
      </div>

      <div className="balance-total">
        <span>{t('totalBalance')}</span>
        <h1>{formatCurrency(balance.total)}</h1>
      </div>

      <div className="balance-cards">
        <div className="balance-card">
          <div className="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
              <line x1="1" y1="10" x2="23" y2="10"/>
            </svg>
          </div>
          <span>{t('paypalBalance')}</span>
          <strong>{formatCurrency(balance.paypal)}</strong>
        </div>
        <div className="balance-card">
          <div className="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="1" y="4" width="22" height="16" rx="2" ry="2"/>
              <line x1="1" y1="10" x2="23" y2="10"/>
            </svg>
          </div>
          <span>{t('stripeBalance')}</span>
          <strong>{formatCurrency(balance.stripe)}</strong>
        </div>
      </div>

      <div className="withdrawal-card">
        <div className="withdrawal-header">
          <div className="card-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="1" x2="12" y2="13"/>
              <path d="M12 13l-4-4m4 4l4-4"/>
              <path d="M4 16v3a2 2 0 002 2h12a2 2 0 002-2v-3"/>
            </svg>
          </div>
          <span>{t('withdrawalPaypal')}</span>
        </div>
        <strong className="withdrawal-amount">{formatCurrency(balance.withdrawal)}</strong>
      </div>

      <div className="account-info">
        <p>{t('balanceInfo')}</p>
        <div className="account-tag">
          {t('account')}: <strong>{user?.username ? `@${user.username}` : `ID: ${user?.id}`}</strong>
        </div>
      </div>
    </div>
  )
}
