import { useState } from 'react'
import { useData } from '../context/DataContext'
import './Statistics.css'

export default function Statistics() {
  const { stats, loading } = useData()
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
        <h2>📈 Статистика</h2>
        <p>Обзор ваших транзакций</p>
      </div>

      <div className="stats-tabs">
        <button
          className={`stats-tab-btn ${activeTab === 'my' ? 'active' : ''}`}
          onClick={() => setActiveTab('my')}
        >
          Моя статистика
        </button>
        <button
          className={`stats-tab-btn ${activeTab === 'buyer' ? 'active' : ''}`}
          onClick={() => setActiveTab('buyer')}
        >
          Статистика покупателя
        </button>
      </div>

      {activeTab === 'my' ? (
        <div className="stats-grid">
          <div className="stat-box">
            <div className="stat-icon">💰</div>
            <strong className="stat-number">{formatCurrency(stats.avgCheck)}</strong>
            <span className="stat-title">Средний чек</span>
            <p className="stat-description">Общая $ сумма чеков / общее количество чеков</p>
          </div>

          <div className="stat-box">
            <div className="stat-icon">📊</div>
            <strong className="stat-number">{stats.totalChecks}</strong>
            <span className="stat-title">Всего чеков</span>
            <p className="stat-description">Общее количество обработанных чеков</p>
          </div>

          <div className="stat-box">
            <div className="stat-icon">💵</div>
            <strong className="stat-number">{formatCurrency(stats.totalSum)}</strong>
            <span className="stat-title">Общая сумма</span>
            <p className="stat-description">Совокупный доход за весь период</p>
          </div>

          <div className="stat-box">
            <div className="stat-icon">📅</div>
            <strong className="stat-number">{Math.round(stats.avgChecksMonth)}</strong>
            <span className="stat-title">Среднее количество чеков в месяц</span>
            <p className="stat-description">Усредненная активность за месяц</p>
          </div>

          <div className="stat-box">
            <div className="stat-icon">💸</div>
            <strong className="stat-number">{formatCurrency(stats.avgSumMonth)}</strong>
            <span className="stat-title">Средняя сумма в месяц</span>
            <p className="stat-description">Средний доход за месячный период</p>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <p>Статистика покупателя пока недоступна</p>
          <span>Данные появятся после первых покупок</span>
        </div>
      )}
    </div>
  )
}
