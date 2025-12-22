import { useState, useEffect } from 'react'
import { useData } from '../context/DataContext'
import { useLanguage } from '../context/LanguageContext'
import { useToast } from '../context/ToastContext'
import './More.css'

const admins = [
  {
    username: 'thxfortheslapali',
    name: 'Alihan',
    role: 'Founder',
    initials: 'TF',
    color: 'linear-gradient(135deg, #FF9966 0%, #FF5E62 100%)'
  },
  {
    username: 'herr_leutenant',
    name: 'Admin',
    role: 'Support',
    initials: 'HL',
    color: 'linear-gradient(135deg, #56CCF2 0%, #2F80ED 100%)'
  },
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

  const { addToast } = useToast()

  const handleCreateReferralCode = async () => {
    const code = await createCode()
    if (code) {
      setReferralCode(code)
      addToast(t('referralCodeCreated'), 'success')
    }
  }

  const copyReferralCode = () => {
    if (referralCode) {
      const link = `https://t.me/exchangeali_bot?start=${referralCode}`
      navigator.clipboard.writeText(link)
      addToast(t('linkCopied'), 'success')
    }
  }

  return (
    <div className="more-page">
      <div className="section-header">
        <h2>{t('moreTitle')}</h2>
        <p>{t('moreSubtitle')}</p>
      </div>

      <div className="glass-section language-section">
        <div className="section-title-row">
          <div className="icon-box purple">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="2" y1="12" x2="22" y2="12" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1 4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
          </div>
          <h3>{t('language')}</h3>
        </div>

        <div className="language-switcher">
          <button
            className={`lang-btn ${language === 'en' ? 'active' : ''}`}
            onClick={() => language !== 'en' && toggleLanguage()}
          >
            <span className="lang-flag">🇺🇸</span>
            <span className="lang-name">English</span>
            {language === 'en' && <div className="active-dot"></div>}
          </button>
          <button
            className={`lang-btn ${language === 'ru' ? 'active' : ''}`}
            onClick={() => language !== 'ru' && toggleLanguage()}
          >
            <span className="lang-flag">🇷🇺</span>
            <span className="lang-name">Русский</span>
            {language === 'ru' && <div className="active-dot"></div>}
          </button>
        </div>
      </div>

      <div className="glass-section contact-section">
        <div className="section-title-row">
          <div className="icon-box blue">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
          <h3>{t('contactAdmins')}</h3>
        </div>

        <div className="contact-cards">
          {admins.map((admin) => (
            <a
              key={admin.username}
              href={`https://t.me/${admin.username}`}
              className="contact-card"
              target="_blank"
              rel="noopener noreferrer"
            >
              <div className="contact-avatar" style={{ background: admin.color }}>
                <span>{admin.initials}</span>
              </div>
              <div className="contact-info">
                <div className="admin-name-row">
                  <strong>{admin.name}</strong>
                  <span className="admin-badge">{admin.role}</span>
                </div>
                <span className="admin-username">@{admin.username}</span>
              </div>
              <div className="contact-action">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                </svg>
              </div>
            </a>
          ))}
        </div>
      </div>

      <div className="glass-section referral-section">
        <div className="section-title-row">
          <div className="icon-box gold">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
              <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
            </svg>
          </div>
          <h3>{t('referralProgram')}</h3>
        </div>

        {referralCode ? (
          <div className="referral-content">
            <div className="referral-card-display">
              <div className="ref-code-box">
                <span className="ref-label">{t('yourReferralCode')}</span>
                <code className="ref-code-text">{referralCode}</code>
              </div>
              <button className="copy-btn-icon" onClick={copyReferralCode}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </button>
            </div>

            <div className="ref-stats-grid">
              <div className="ref-stat-card">
                <span className="stat-label">{t('clicks')}</span>
                <span className="stat-value">0</span>
              </div>
              <div className="ref-stat-card">
                <span className="stat-label">{t('registrations')}</span>
                <span className="stat-value">0</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="referral-empty">
            <p className="referral-desc">{t('createCodeDesc')}</p>
            <button className="create-ref-btn" onClick={handleCreateReferralCode}>
              <span>{t('createReferralCode')}</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
