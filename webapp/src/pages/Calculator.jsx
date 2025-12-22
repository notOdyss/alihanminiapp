import { useState, useEffect } from 'react'
import { useLanguage } from '../context/LanguageContext'
import { useToast } from '../context/ToastContext'
import { useTelegram } from '../context/TelegramContext' // Added for tg.initData
import Modal from '../components/ui/Modal'
import './Calculator.css'

const methods = [
  {
    id: 'paypal',
    name: 'PayPal',
    fee: 6,
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M19.333 11.23C19.866 9.47 19.982 7.545 18.736 6.008C17.5 4.484 15.362 3.961 12.984 3.961H7.817C6.985 3.961 6.273 4.545 6.136 5.366L4.053 17.866C4.008 18.136 4.218 18.375 4.492 18.375H8.381C9.079 18.375 9.683 17.892 9.814 17.207L10.518 12.983C10.65 12.192 11.332 11.608 12.135 11.608H12.915C15.424 11.608 18.261 15.013 19.333 11.23Z" fill="currentColor" />
      </svg>
    ),
    color: '#003087'
  },
  {
    id: 'bank',
    name: 'Bank',
    fee: 8.5,
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="5" width="20" height="14" rx="2" />
        <line x1="2" y1="10" x2="22" y2="10" />
      </svg>
    ),
    color: '#10B981'
  },
  {
    id: 'stripe',
    name: 'Stripe',
    fee: 7,
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="8" y1="13" x2="16" y2="13"></line>
        <line x1="8" y1="17" x2="16" y2="17"></line>
        <polyline points="10 9 9 9 8 9"></polyline>
      </svg>
    ),
    color: '#635BFF'
  },
]

export default function Calculator() {
  const { t } = useLanguage()
  const { addToast } = useToast()
  const { tg } = useTelegram()
  const [selectedMethod, setSelectedMethod] = useState(methods[0])
  const [amount, setAmount] = useState('')
  const [result, setResult] = useState(null)
  const [animationClass, setAnimationClass] = useState('')

  // Ticket State
  const [showTicketModal, setShowTicketModal] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const API_URL = import.meta.env.VITE_API_URL || 'https://floy-effluvial-chaim.ngrok-free.dev/api'

  const handleCreateTicket = async () => {
    if (!tg?.initData) {
      addToast('Please open in Telegram to create a ticket', 'error')
      return
    }

    setIsSubmitting(true)
    try {
      const response = await fetch(`${API_URL}/transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Telegram-Init-Data': tg.initData,
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          payment_method: selectedMethod.name,
          amount: parseFloat(amount),
          currency: 'USD'
        })
      })

      if (!response.ok) throw new Error('Failed to create ticket')

      addToast('Ticket created successfully!', 'success')
      setShowTicketModal(false)
    } catch (error) {
      console.error(error)
      addToast('Error creating ticket', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const calculate = (amt, method) => {
    const saleAmount = parseFloat(amt) || 0
    if (saleAmount <= 0) {
      setResult(null)
      return
    }

    // Step 1: Payment System Fee
    const exchangeFee = (saleAmount * method.fee) / 100
    const afterExchangeFee = saleAmount - exchangeFee

    // Step 2: Internal Fee %
    const internalFeePercent = (saleAmount * 7) / 100
    const afterInternalPercent = afterExchangeFee - internalFeePercent

    // Step 3: Fixed Internal Fee ($5)
    const internalFeeFix = 5
    const afterInternalFix = afterInternalPercent - internalFeeFix

    // Step 4: P2P Fee (3%)
    const p2pFee = (afterInternalFix * 3) / 100
    const beforeRounding = afterInternalFix - p2pFee

    // Rounding
    const fractional = beforeRounding - Math.floor(beforeRounding)
    const total = fractional >= 0.5 ? Math.ceil(beforeRounding) : Math.floor(beforeRounding)

    // Ensure accurate total summing for distribution
    const totalFees = exchangeFee + internalFeePercent + internalFeeFix + p2pFee
    const safeTotal = Math.max(0, total)

    // Recalculate fees slightly if total < 0 to show 0

    setResult({
      saleAmount,
      exchangeFee,
      year: new Date().getFullYear(),
      exchangeFeeName: method.name,
      exchangeFeePercent: method.fee,
      internalFeePercent,
      internalFeeFix,
      internalFeeTotal: internalFeePercent + internalFeeFix,
      p2pFee,
      beforeRounding,
      total: safeTotal,
      // For chart
      distribution: {
        net: (safeTotal / saleAmount) * 100,
        fees: (totalFees / saleAmount) * 100
      }
    })
  }

  // Auto-calculate
  useEffect(() => {
    calculate(amount, selectedMethod)
    // Trigger update animation
    setAnimationClass('pulse')
    const timer = setTimeout(() => setAnimationClass(''), 300)
    return () => clearTimeout(timer)
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
        <label className="input-label">{t('paymentMethod')}</label>
        <div className="method-selector">
          {methods.map((method) => (
            <button
              key={method.id}
              className={`method-card ${selectedMethod.id === method.id ? 'active' : ''}`}
              onClick={() => setSelectedMethod(method)}
            >
              <div className="method-icon" style={{ color: selectedMethod.id === method.id ? 'white' : method.color }}>
                {method.icon}
              </div>
              <span className="method-name">{method.name}</span>
              <span className="method-fee-badge">{method.fee}%</span>
            </button>
          ))}
        </div>

        <div className="input-group">
          <label className="input-label">{t('saleAmount')}</label>
          <div className="amount-input-wrapper">
            <span className="currency-symbol">$</span>
            <input
              type="number"
              className="calc-input"
              placeholder="0.00"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
            <div className="input-highlight"></div>
          </div>
        </div>

        {result && (
          <div className={`calc-result ${animationClass}`}>
            <div className="result-total-card">
              <span className="total-label">{t('youReceive')}</span>
              <div className="total-row-with-copy">
                <h3 className="total-value">{formatCurrency(result.total)}</h3>
                <button
                  className="copy-result-btn"
                  onClick={() => {
                    navigator.clipboard.writeText(result.total.toFixed(2));
                    addToast('Amount copied to clipboard!', 'success');
                  }}
                  title="Copy amount"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                </button>
              </div>
              <div className="payout-bar">
                <div
                  className="payout-fill"
                  style={{ width: `${Math.min(result.distribution.net, 100)}%` }}
                ></div>
              </div>
              <div className="payout-stats">
                <span>Net ~{Math.round(result.distribution.net)}%</span>
                <span>Fees ~{Math.round(result.distribution.fees)}%</span>
              </div>

              {/* CREATE TICKET BUTTON */}
              <button
                className="create-ticket-btn"
                onClick={() => setShowTicketModal(true)}
              >
                Create Exchange Ticket
              </button>
            </div>

            <div className="breakdown-list">
              <div className="breakdown-item">
                <div className="breakdown-label">
                  <span className="dot" style={{ background: selectedMethod.color }}></span>
                  {selectedMethod.name} Fee ({result.exchangeFeePercent}%)
                </div>
                <span className="breakdown-amount">-{formatCurrency(result.exchangeFee)}</span>
              </div>

              <div className="breakdown-item">
                <div className="breakdown-label">
                  <span className="dot" style={{ background: '#f5af19' }}></span>
                  Service Fee (7% + $5)
                </div>
                <span className="breakdown-amount">-{formatCurrency(result.internalFeeTotal)}</span>
              </div>

              <div className="breakdown-item">
                <div className="breakdown-label">
                  <span className="dot" style={{ background: '#f12711' }}></span>
                  P2P Gateway (3%)
                </div>
                <span className="breakdown-amount">-{formatCurrency(result.p2pFee)}</span>
              </div>
            </div>

            <div className="calc-note">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              Final amount may vary slightly due to rounding.
            </div>
          </div>
        )}
      </div>

      <Modal
        isOpen={showTicketModal}
        onClose={() => setShowTicketModal(false)}
        title="Confirm Ticket"
      >
        <div className="ticket-modal-content">
          <p>Create a ticket for <b>{formatCurrency(amount)}</b> via <b>{selectedMethod.name}</b>?</p>
          <p className="ticket-subtext">You will receive approximately <b>{result?.total ? formatCurrency(result.total) : '$0.00'}</b>.</p>

          <div className="modal-actions">
            <button
              className="modal-btn secondary"
              onClick={() => setShowTicketModal(false)}
            >
              Cancel
            </button>
            <button
              className="modal-btn primary"
              onClick={handleCreateTicket}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Confirm Ticket'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
