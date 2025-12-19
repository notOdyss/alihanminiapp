import { useState, useEffect } from 'react'
import { useLanguage } from '../context/LanguageContext'
import './Calculator.css'

const methods = [
  { id: 'paypal', name: 'PayPal', fee: 6 },
  { id: 'bank', name: 'Bank', fee: 8.5 },
  { id: 'stripe', name: 'Stripe', fee: 7 },
]

export default function Calculator() {
  const { t } = useLanguage()
  const [selectedMethod, setSelectedMethod] = useState(methods[0])
  const [amount, setAmount] = useState('')
  const [result, setResult] = useState(null)

  const calculate = (amt, method) => {
    const saleAmount = parseFloat(amt) || 0
    if (saleAmount <= 0) {
      setResult(null)
      return
    }

    // Комиссия метода оплаты (PayPal/Bank/Stripe)
    const exchangeFee = (saleAmount * method.fee) / 100

    // Внутренняя комиссия: $5 + 6%
    const internalFee = 5 + (saleAmount * 6) / 100

    // P2P комиссия: 3%
    const p2pFee = (saleAmount * 3) / 100

    // Чистая сумма
    const total = saleAmount - exchangeFee - internalFee - p2pFee

    setResult({
      saleAmount,
      exchangeFee,
      internalFee,
      p2pFee,
      total: Math.max(0, total)
    })
  }

  // Auto-calculate when amount or method changes
  useEffect(() => {
    calculate(amount, selectedMethod)
  }, [amount, selectedMethod])

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }

  return (
    <div className="calculator-page">
      <div className="section-header">
        <h2>{t('calculatorTitle')}</h2>
        <p>{t('calculatorSubtitle')}</p>
      </div>

      <div className="calculator-card">
        <div className="method-selector">
          {methods.map((method) => (
            <button
              key={method.id}
              className={`method-btn ${selectedMethod.id === method.id ? 'active' : ''}`}
              onClick={() => setSelectedMethod(method)}
            >
              {method.name} ({method.fee}%)
            </button>
          ))}
        </div>

        <div className="input-group">
          <label>{t('saleAmount')}</label>
          <input
            type="number"
            className="calc-input"
            placeholder="0.00"
            step="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>

        {result && (
          <div className="calc-result">
            <div className="result-item">
              <span>
                {selectedMethod.id === 'paypal' ? t('paypalFee') :
                 selectedMethod.id === 'bank' ? t('bankFee') : t('stripeFee')} ({selectedMethod.fee}%)
              </span>
              <strong className="fee-amount">{formatCurrency(result.exchangeFee)}</strong>
            </div>
            <div className="result-item">
              <span>{t('internalFee')} ($5 + 6%)</span>
              <strong className="fee-amount">{formatCurrency(result.internalFee)}</strong>
            </div>
            <div className="result-item">
              <span>{t('p2pFee')} (3%)</span>
              <strong className="fee-amount">{formatCurrency(result.p2pFee)}</strong>
            </div>
            <div className="result-divider"></div>
            <div className="result-total">
              <span>{t('youReceive')}</span>
              <strong className="total-amount">{formatCurrency(result.total)}</strong>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
