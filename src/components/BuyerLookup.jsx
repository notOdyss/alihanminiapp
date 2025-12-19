import { useState, useEffect } from 'react'
import { useData } from '../context/DataContext'
import { useLanguage } from '../context/LanguageContext'
import './BuyerLookup.css'

export default function BuyerLookup() {
    const { lookupBuyer, checkAccessStatus } = useData()
    const { t } = useLanguage()

    const [email, setEmail] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [hasAccess, setHasAccess] = useState(null) // null = loading access status

    useEffect(() => {
        checkAccessStatus().then(status => {
            if (status) {
                setHasAccess(status.can_lookup_buyer)
            } else {
                setHasAccess(false)
            }
        })
    }, [])

    const handleLookup = async (e) => {
        e.preventDefault()
        if (!email) return

        setLoading(true)
        setError(null)
        setResult(null)

        const data = await lookupBuyer(email)

        if (data) {
            setResult(data)
        } else {
            setError(t('buyerNotFound'))
        }
        setLoading(false)
    }

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(value || 0)
    }

    const formatDate = (dateStr) => {
        if (!dateStr) return '-'
        return new Date(dateStr).toLocaleDateString()
    }

    if (hasAccess === null) {
        return <div className="spinner"></div>
    }

    if (hasAccess === false) {
        return (
            <div className="premium-lock">
                <svg className="lock-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                <h3>{t('premiumFeature')}</h3>
                <p>{t('premiumFeatureDesc')}</p>
            </div>
        )
    }

    return (
        <div className="buyer-lookup">
            <form onSubmit={handleLookup} className="lookup-form">
                <input
                    type="email"
                    placeholder={t('enterEmail')}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="lookup-input"
                    required
                />
                <button type="submit" className="lookup-btn" disabled={loading}>
                    {loading ? <div className="spinner-sm"></div> : t('lookup')}
                </button>
            </form>

            {error && <div className="lookup-error">{error}</div>}

            {result && (
                <div className="lookup-result">
                    <div className="result-header">
                        <h3>{t('buyerFound')}</h3>
                        <span className="email-tag">{result.email}</span>
                    </div>

                    <div className="stats-grid">
                        <div className="stat-box">
                            <strong className="stat-number">{formatCurrency(result.total_volume)}</strong>
                            <span className="stat-title">{t('totalSum')}</span>
                        </div>

                        <div className="stat-box">
                            <strong className="stat-number">{result.total_transactions}</strong>
                            <span className="stat-title">{t('totalTransactions')}</span>
                        </div>

                        <div className="stat-box">
                            <strong className="stat-number">{formatDate(result.first_seen)}</strong>
                            <span className="stat-title">{t('firstSeen')}</span>
                        </div>

                        <div className="stat-box">
                            <strong className="stat-number">{formatDate(result.last_seen)}</strong>
                            <span className="stat-title">{t('lastSeen')}</span>
                        </div>

                        <div className="stat-box">
                            <strong className="stat-number">{result.unique_partners}</strong>
                            <span className="stat-title">{t('uniquePartners')}</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
