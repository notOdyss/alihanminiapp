import { createContext, useContext, useState, useEffect } from 'react'
import { useTelegram } from './TelegramContext'

const DataContext = createContext(null)

const API_URL = 'http://localhost:8080/api'

export const DataProvider = ({ children }) => {
  const { tg, user } = useTelegram()
  const [transactions, setTransactions] = useState([])
  const [balance, setBalance] = useState({
    total: 0,
    paypal: 0,
    stripe: 0,
    withdrawal: 0,
  })
  const [stats, setStats] = useState({
    avgCheck: 0,
    totalChecks: 0,
    totalSum: 0,
    avgChecksMonth: 0,
    avgSumMonth: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      fetchData()
    }
  }, [user])

  const fetchData = async () => {
    if (!tg?.initData) {
      setLoading(false)
      return
    }

    try {
      const headers = {
        'X-Telegram-Init-Data': tg.initData,
      }

      const [balanceData, statsData, txsData] = await Promise.all([
        fetch(`${API_URL}/balance`, { headers }).then(r => r.json()),
        fetch(`${API_URL}/statistics`, { headers }).then(r => r.json()),
        fetch(`${API_URL}/transactions?limit=50`, { headers }).then(r => r.json())
      ])

      setBalance(balanceData)
      setStats(statsData)
      setTransactions(txsData.transactions || [])

      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch data:', error)
      setLoading(false)
    }
  }

  const createReferralCode = async () => {
    if (!tg?.initData) return null

    try {
      const headers = {
        'X-Telegram-Init-Data': tg.initData,
      }

      const response = await fetch(`${API_URL}/referral`, {
        method: 'POST',
        headers
      })
      const data = await response.json()
      return data.code
    } catch (error) {
      console.error('Error creating referral code:', error)
      return null
    }
  }

  const getReferralCode = async () => {
    if (!tg?.initData) return null

    try {
      const headers = {
        'X-Telegram-Init-Data': tg.initData,
      }

      const response = await fetch(`${API_URL}/referral`, { headers })
      const data = await response.json()
      return data.code
    } catch (error) {
      console.error('Error getting referral code:', error)
      return null
    }
  }

  const value = {
    transactions,
    balance,
    stats,
    loading,
    refreshData: fetchData,
    createReferralCode,
    getReferralCode,
  }

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  )
}

export const useData = () => {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useData must be used within DataProvider')
  }
  return context
}
