import { useState } from 'react'
import { useData } from '../context/DataContext'
import { useLanguage } from '../context/LanguageContext'
import './Statistics.css'

export default function Statistics() {
  const { stats, loading } = useData()
  const { t } = useLanguage()
  const [activeTab, setActiveTab] = useState('my')

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
    <div className="statistics-page">
      <div className="section-header">
        <h2>{t('statisticsTitle')}</h2>
        <p>{t('statisticsSubtitle')}</p>
      </div>

      <div className="stats-tabs">
        <button
          className={`stats-tab-btn ${activeTab === 'my' ? 'active' : ''}`}
          onClick={() => setActiveTab('my')}
        >
          {t('myStats')}
        </button>
        <button
          className={`stats-tab-btn ${activeTab === 'buyer' ? 'active' : ''}`}
          onClick={() => setActiveTab('buyer')}
        >
          {t('buyerStats')}
        </button>
      </div>

      {activeTab === 'my' ? (
        <div className="stats-grid">
          <div className="stat-box">
            <strong className="stat-number">{formatCurrency(stats.avgCheck)}</strong>
            <span className="stat-title">{t('avgCheck')}</span>
            <p className="stat-description">{t('avgCheckDesc')}</p>
          </div>

          <div className="stat-box">
            <strong className="stat-number">{stats.totalChecks}</strong>
            <span className="stat-title">{t('totalChecks')}</span>
            <p className="stat-description">{t('totalChecksDesc')}</p>
          </div>

          <div className="stat-box">
            <strong className="stat-number">{formatCurrency(stats.totalSum)}</strong>
            <span className="stat-title">{t('totalSum')}</span>
            <p className="stat-description">{t('totalSumDesc')}</p>
          </div>

          <div className="stat-box">
            <strong className="stat-number">{Math.round(stats.avgChecksMonth)}</strong>
            <span className="stat-title">{t('avgChecksMonth')}</span>
            <p className="stat-description">{t('avgChecksMonthDesc')}</p>
          </div>

          <div className="stat-box">
            <strong className="stat-number">{formatCurrency(stats.avgSumMonth)}</strong>
            <span className="stat-title">{t('avgSumMonth')}</span>
            <p className="stat-description">{t('avgSumMonthDesc')}</p>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <svg className="empty-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          <p>{t('buyerStatsUnavailable')}</p>
          <span>{t('buyerStatsAppear')}</span>
        </div>
      )}
    </div>
  )
}
