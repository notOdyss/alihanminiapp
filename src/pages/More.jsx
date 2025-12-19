import { useState, useEffect } from 'react'
import { useData } from '../context/DataContext'
import { useLanguage } from '../context/LanguageContext'
import './More.css'

const admins = [
  { username: 'thxfortheslapali', initials: 'TF' },
  { username: 'herr_leutenant', initials: 'HL' },
]

export default function More() {
  const { createReferralCode: createCode, getReferralCode } = useData()
  const { t, language, toggleLanguage } = useLanguage()
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
        <h2>{t('moreTitle')}</h2>
        <p>{t('moreSubtitle')}</p>
      </div>

      <div className="language-section">
        <h3>{t('language')}</h3>
        <div className="language-switcher">
          <button
            className={`lang-btn ${language === 'en' ? 'active' : ''}`}
            onClick={() => language !== 'en' && toggleLanguage()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            <span>English</span>
          </button>
          <button
            className={`lang-btn ${language === 'ru' ? 'active' : ''}`}
            onClick={() => language !== 'ru' && toggleLanguage()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
            <span>Русский</span>
          </button>
        </div>
      </div>

      <div className="admin-contacts">
        <h3>{t('contactAdmins')}</h3>
        <p>{t('contactDesc')}</p>

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
                <span className="admin-badge">{t('admin')}</span>
              </div>
              <svg className="contact-arrow" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7 4l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </a>
          ))}
        </div>

        <p className="contact-hint">{t('clickToChat')}</p>
      </div>

      <div className="referral-section">
        <h3>{t('referralProgram')}</h3>

        {referralCode ? (
          <div className="referral-card active">
            <div className="referral-info">
              <span className="ref-label">{t('yourReferralCode')}</span>
              <div className="ref-code-display">
                <code>{referralCode}</code>
                <button className="copy-btn" onClick={copyReferralCode}>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M7 7V4a2 2 0 012-2h7a2 2 0 012 2v7a2 2 0 01-2 2h-3M4 9a2 2 0 012-2h7a2 2 0 012 2v7a2 2 0 01-2 2H6a2 2 0 01-2-2V9z" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  {t('copy')}
                </button>
              </div>
            </div>
            <div className="ref-stats">
              <div className="ref-stat">
                <span>{t('clicks')}</span>
                <strong>0</strong>
              </div>
              <div className="ref-stat">
                <span>{t('registrations')}</span>
                <strong>0</strong>
              </div>
            </div>
          </div>
        ) : (
          <div className="referral-card">
            <div className="referral-info">
              <span>{t('noReferralCode')}</span>
              <p>{t('createCodeDesc')}</p>
            </div>
            <button className="referral-btn" onClick={handleCreateReferralCode}>
              {t('createReferralCode')}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
