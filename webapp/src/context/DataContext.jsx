import { createContext, useContext, useState, useEffect } from 'react'
import { useTelegram } from './TelegramContext'

const DataContext = createContext(null)

// ⚠️ HARDCODED URL FOR PRODUCTION - CHANGE IF NGROK RESTARTS
const API_URL = 'https://floy-effluvial-chaim.ngrok-free.dev/api'

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
  const [debugLogs, setDebugLogs] = useState([])

  const addLog = (msg) => {
    console.log(msg)
    setDebugLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 10))
  }

  useEffect(() => {
    // Force fetch on mount even if no user (for debug)
    fetchData()
  }, [user])

  const fetchData = async () => {
    addLog(`Fetching data... User: ${user?.username || 'unknown'}`)

    const headers = {
      'ngrok-skip-browser-warning': 'true',
      'Content-Type': 'application/json'
    }

    if (tg?.initData) {
      headers['X-Telegram-Init-Data'] = tg.initData
    }

    try {
      // Parallel Fetching
      // Force 5-second minimum load time as requested
      const minLoadTime = new Promise(resolve => setTimeout(resolve, 5000))

      const [balanceRes, statsRes, txsRes] = await Promise.all([
        fetch(`${API_URL}/balance`, { headers }),
        fetch(`${API_URL}/statistics`, { headers }),
        fetch(`${API_URL}/transactions?limit=50`, { headers }),
        minLoadTime
      ])

      // 1. Process Balance
      if (!balanceRes.ok) throw new Error(`Balance failed: ${balanceRes.status}`)
      const balanceData = await balanceRes.json()
      addLog(`Balance Loaded: $${balanceData.total}`)
      setBalance(balanceData)

      // 2. Process Stats
      if (!statsRes.ok) throw new Error(`Stats failed: ${statsRes.status}`)
      const statsData = await statsRes.json()
      setStats(statsData)

      // 3. Process Transactions
      if (!txsRes.ok) throw new Error(`Transactions failed: ${txsRes.status}`)
      const txsData = await txsRes.json()
      addLog(`Transactions: ${txsData.transactions?.length || 0}`)
      setTransactions(txsData.transactions || [])

    } catch (error) {
      addLog(`ERROR: ${error.message}`)
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const value = {
    transactions,
    balance,
    stats,
    loading,
    debugLogs,
    refreshData: fetchData,
    lookupBuyer: async (email) => {
      if (!tg?.initData) return null
      try {
        const headers = { 'X-Telegram-Init-Data': tg.initData, 'ngrok-skip-browser-warning': 'true' }
        const res = await fetch(`${API_URL}/buyer/lookup?email=${encodeURIComponent(email)}`, { headers })
        if (!res.ok) throw new Error('Failed to lookup')
        return await res.json()
      } catch (e) {
        console.error(e)
        return null
      }
    },
    checkAccessStatus: async () => {
      if (!tg?.initData) return null
      try {
        const headers = { 'X-Telegram-Init-Data': tg.initData, 'ngrok-skip-browser-warning': 'true' }
        const res = await fetch(`${API_URL}/access-status`, { headers })
        return await res.json()
      } catch (e) {
        console.error(e)
        return null
      }
    },
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
