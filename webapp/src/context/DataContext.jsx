import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react'
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

  // Ref to track if we've already fetched to avoid double-fetch
  const hasFetched = useRef(false)

  const addLog = useCallback((msg) => {
    console.log(msg)
    setDebugLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 10))
  }, [])

  // Wait for Telegram to be ready before fetching
  useEffect(() => {
    // Only fetch once when tg is ready
    if (hasFetched.current) return

    // 1. Ideal case: We have initData
    if (tg?.initData) {
      addLog(`Telegram ready, fetching data...`)
      hasFetched.current = true
      fetchData(tg.initData)
    }
    // 2. Telegram SDK loaded but no initData yet - Just wait, don't trigger fetch
    else if (tg && !tg.initData) {
      addLog(`Telegram SDK loaded, waiting for initData...`)
    }
    // 3. tg is null - Still loading SDK script - Wait
    else {
      addLog(`Waiting for Telegram SDK...`)
    }
  }, [tg, user])

  // Timeout to ensure we don't wait forever
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!hasFetched.current) {
        if (tg?.initData) {
          // It appeared just now?
          hasFetched.current = true
          fetchData(tg.initData)
        } else {
          // Timeout reached and still no initData. 
          // Likely running in browser or Telegram failed to inject data.
          addLog(`Timeout: No initData found.`)
          // We do NOT fetch here to avoid 401. We just stop loading.
          setLoading(false)
        }
      }
    }, 3000) // Wait 3 seconds

    return () => clearTimeout(timeout)
  }, [tg])

  const fetchData = async (initData) => {
    addLog(`Fetching data... User: ${user?.username || 'unknown'}`)

    // Start 5-second minimum timer BEFORE any API calls
    const loadStartTime = Date.now()
    const MIN_LOAD_TIME = 1000

    // Build headers once and reuse - avoid stale closure issues
    const headers = {
      'ngrok-skip-browser-warning': 'true',
      'Content-Type': 'application/json'
    }

    if (initData) {
      headers['X-Telegram-Init-Data'] = initData
      addLog(`Using initData: ${initData.substring(0, 30)}...`)
    } else {
      addLog(`WARNING: No initData available!`)
    }

    try {
      // Parallel Fetching - headers object is passed by reference to all
      const [balanceRes, statsRes, txsRes] = await Promise.all([
        fetch(`${API_URL}/balance`, { headers }),
        fetch(`${API_URL}/statistics`, { headers }),
        fetch(`${API_URL}/transactions?limit=50`, { headers }),
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
      // Ensure minimum 5-second load time even if API fails
      const elapsed = Date.now() - loadStartTime
      const remainingTime = MIN_LOAD_TIME - elapsed

      if (remainingTime > 0) {
        await new Promise(resolve => setTimeout(resolve, remainingTime))
      }

      setLoading(false)
    }
  }

  const value = {
    transactions,
    balance,
    stats,
    loading,
    debugLogs,
    refreshData: () => fetchData(tg?.initData || null),
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
