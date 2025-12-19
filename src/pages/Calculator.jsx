import { useState } from 'react'
import './Calculator.css'

const methods = [
  { id: 'paypal', name: 'PayPal', fee: 6 },
  { id: 'bank', name: 'Bank', fee: 8.5 },
  { id: 'stripe', name: 'Stripe', fee: 7 },
]

export default function Calculator() {
  const [selectedMethod, setSelectedMethod] = useState(methods[0])
  const [amount, setAmount] = useState('')
  const [result, setResult] = useState(null)

  const calculate = () => {
    const amt = parseFloat(amount) || 0
    if (amt <= 0) {
      setResult(null)
      return
    }

    const exchangeFee = (amt * selectedMethod.fee) / 100
    const internalFee = (amt * 6) / 100 + 5
    const p2pFee = (amt * 3) / 100
    const total = amt - exchangeFee - internalFee - p2pFee

    setResult({
      exchangeFee,
      internalFee,
      p2pFee,
      total: Math.max(0, total)
    })
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value)
  }

  return (
    <div className="calculator-page">
      <div className="section-header">
        <h2>🧮 Калькулятор комиссий</h2>
        <p>Рассчитайте комиссии в обоих направлениях</p>
      </div>

      <div className="calculator-card">
        <div className="method-selector">
          {methods.map((method) => (
            <button
              key={method.id}
              className={`method-btn ${selectedMethod.id === method.id ? 'active' : ''}`}
              onClick={() => {
                setSelectedMethod(method)
                setResult(null)
              }}
            >
              {method.name} ({method.fee}%)
            </button>
          ))}
        </div>

        <div className="input-group">
          <label>Введите сумму продажи ($)</label>
          <input
            type="number"
            className="calc-input"
            placeholder="0.00"
            step="0.01"
            value={amount}
            onChange={(e) => {
              setAmount(e.target.value)
              setResult(null)
            }}
          />
        </div>

        <button className="calc-btn" onClick={calculate}>
          Рассчитать чистую сумму
        </button>

        {result && (
          <div className="calc-result">
            <div className="result-item">
              <span>Комиссия обменника ({selectedMethod.fee}%)</span>
              <strong>{formatCurrency(result.exchangeFee)}</strong>
            </div>
            <div className="result-item">
              <span>Внутренняя комиссия (6% + $5)</span>
              <strong>{formatCurrency(result.internalFee)}</strong>
            </div>
            <div className="result-item">
              <span>P2P комиссия (3%)</span>
              <strong>{formatCurrency(result.p2pFee)}</strong>
            </div>
            <div className="result-divider"></div>
            <div className="result-total">
              <span>Вы получите</span>
              <strong className="total-amount">{formatCurrency(result.total)}</strong>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
