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

    // Шаг 1: Комиссия платежной системы (PayPal 6%, Bank 8.5%, Stripe 7%)
    const exchangeFee = (saleAmount * method.fee) / 100
    const afterExchangeFee = saleAmount - exchangeFee

    // Шаг 2: Процентная часть внутренней комиссии (7% от исходной суммы)
    const internalFeePercent = (saleAmount * 7) / 100
    const afterInternalPercent = afterExchangeFee - internalFeePercent

    // Шаг 3: Фиксированная часть внутренней комиссии ($5)
    const internalFeeFix = 5
    const afterInternalFix = afterInternalPercent - internalFeeFix

    // Шаг 4: Комиссия P2P (3% от суммы после всех предыдущих комиссий)
    const p2pFee = (afterInternalFix * 3) / 100
    const beforeRounding = afterInternalFix - p2pFee

    // Округление: если >= 0.5 - вверх (в пользу клиента), если < 0.5 - вниз (в пользу обменника)
    const fractional = beforeRounding - Math.floor(beforeRounding)
    const total = fractional >= 0.5 ? Math.ceil(beforeRounding) : Math.floor(beforeRounding)

    // Общая внутренняя комиссия для отображения
    const internalFeeTotal = internalFeePercent + internalFeeFix

    setResult({
      saleAmount,
      exchangeFee,
      exchangeFeeName: method.name,
      exchangeFeePercent: method.fee,
      internalFeePercent,
      internalFeeFix,
      internalFeeTotal,
      p2pFee,
      beforeRounding,
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
            <div className="result-header">
              <span>Сумма продажи:</span>
              <strong>{formatCurrency(result.saleAmount)}</strong>
            </div>

            <div className="result-item">
              <span>Комиссия {result.exchangeFeeName}: {result.exchangeFeePercent}%</span>
              <strong className="fee-amount">-{formatCurrency(result.exchangeFee)}</strong>
            </div>

            <div className="result-item">
              <span>Внутренняя комиссия: $5 + 7%</span>
              <strong className="fee-amount">-{formatCurrency(result.internalFeeTotal)}</strong>
            </div>

            <div className="result-item">
              <span>Комиссия P2P: 3%</span>
              <strong className="fee-amount">-{formatCurrency(result.p2pFee)}</strong>
            </div>

            <div className="result-divider"></div>

            <div className="result-total">
              <span>Чистая сумма (Итоговая):</span>
              <strong className="total-amount">{formatCurrency(result.total)}</strong>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
