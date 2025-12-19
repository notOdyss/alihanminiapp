import { useState, useEffect } from 'react'
import { useData } from '../context/DataContext'
import './More.css'

const admins = [
  { username: 'thxfortheslapali', initials: 'TF' },
  { username: 'herr_leutenant', initials: 'HL' },
]

export default function More() {
  const { createReferralCode: createCode, getReferralCode } = useData()
  const [referralCode, setReferralCode] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadReferralCode = async () => {
      const code = await getReferralCode()
      setReferralCode(code)
      setLoading(false)
    }

    loadReferralCode()
  }, [])

  const handleCreateReferralCode = async () => {
    const code = await createCode()
    if (code) {
      setReferralCode(code)
    }
  }

  const copyReferralCode = () => {
    if (referralCode) {
      navigator.clipboard.writeText(referralCode)
    }
  }

  return (
    <div className="more-page">
      <div className="section-header">
        <h2>⚙️ Еще</h2>
        <p>Дополнительные опции</p>
      </div>

      <div className="admin-contacts">
        <h3>Связаться с админами</h3>
        <p>Свяжитесь с нашей командой для получения поддержки и помощи</p>

        <div className="contact-cards">
          {admins.map((admin) => (
            <a
              key={admin.username}
              href={`https://t.me/${admin.username}`}
              className="contact-card"
              target="_blank"
              rel="noopener noreferrer"
            >
              <div className="contact-avatar">
                <span>{admin.initials}</span>
              </div>
              <div className="contact-info">
                <strong>@{admin.username}</strong>
                <span className="admin-badge">Admin</span>
              </div>
              <svg className="contact-arrow" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7 4l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </a>
          ))}
        </div>

        <p className="contact-hint">Нажмите на карточку администратора, чтобы начать чат в Telegram</p>
      </div>

      <div className="referral-section">
        <h3>Реферальная программа</h3>

        {referralCode ? (
          <div className="referral-card active">
            <div className="referral-info">
              <span className="ref-label">Ваш реферальный код:</span>
              <div className="ref-code-display">
                <code>{referralCode}</code>
                <button className="copy-btn" onClick={copyReferralCode}>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M7 7V4a2 2 0 012-2h7a2 2 0 012 2v7a2 2 0 01-2 2h-3M4 9a2 2 0 012-2h7a2 2 0 012 2v7a2 2 0 01-2 2H6a2 2 0 01-2-2V9z" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  Копировать
                </button>
              </div>
            </div>
            <div className="ref-stats">
              <div className="ref-stat">
                <span>Переходов</span>
                <strong>0</strong>
              </div>
              <div className="ref-stat">
                <span>Регистраций</span>
                <strong>0</strong>
              </div>
            </div>
          </div>
        ) : (
          <div className="referral-card">
            <div className="referral-info">
              <span>У вас пока нет реферального кода</span>
              <p>Создайте код и приглашайте друзей, чтобы получать бонусы</p>
            </div>
            <button className="referral-btn" onClick={handleCreateReferralCode}>
              Создать реферальный код
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
