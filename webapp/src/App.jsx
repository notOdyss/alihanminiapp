import { useEffect, useState } from 'react'
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom'
import { TelegramProvider } from './context/TelegramContext'
import { DataProvider } from './context/DataContext'
import { LanguageProvider, useLanguage } from './context/LanguageContext'
import { ToastProvider } from './context/ToastContext'
import Layout from './components/Layout'
import Transactions from './pages/Transactions'
import Calculator from './pages/Calculator'
import Balance from './pages/Balance'
import Statistics from './pages/Statistics'
import More from './pages/More'
import LoadingScreen from './components/ui/LoadingScreen'
import './App.css'



import { useData } from './context/DataContext'

function DebugOverlay() {
  const { debugLogs, loading } = useData()
  const [expanded, setExpanded] = useState(false)

  if (!expanded) {
    return (
      <div
        onClick={() => setExpanded(true)}
        style={{
          position: 'fixed', bottom: 10, right: 10,
          background: 'rgba(0,0,0,0.8)', color: '#0f0',
          padding: '5px 10px', borderRadius: '5px', fontSize: '10px', zIndex: 9999
        }}
      >
        DEBUG {loading ? '...' : 'OK'}
      </div>
    )
  }

  return (
    <div style={{
      position: 'fixed', bottom: 0, left: 0, right: 0,
      background: 'rgba(0,0,0,0.9)', color: '#0f0',
      padding: '10px', fontSize: '10px', zIndex: 9999,
      maxHeight: '30vh', overflowY: 'auto'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
        <strong>DEBUG LOGS</strong>
        <button onClick={() => setExpanded(false)} style={{ color: '#fff' }}>CLOSE</button>
      </div>
      {debugLogs.map((log, i) => <div key={i}>{log}</div>)}
    </div>
  )
}

// Wrapper that blocks the app with LoadingScreen until data is verified
function AppContent() {
  const { loading } = useData()

  // Block access to app until data is loaded (5+ seconds minimum)
  if (loading) {
    return <LoadingScreen />
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/transactions" replace />} />
          <Route path="transactions" element={<Transactions />} />
          <Route path="calculator" element={<Calculator />} />
          <Route path="balance" element={<Balance />} />
          <Route path="statistics" element={<Statistics />} />
          <Route path="more" element={<More />} />
        </Route>
      </Routes>
      <DebugOverlay />
    </BrowserRouter>
  )
}

function App() {
  useEffect(() => {
    // Initialize Telegram WebApp
    if (window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp
      tg.ready()
      tg.expand()
      tg.enableClosingConfirmation()

      // Set header color
      tg.setHeaderColor('#6366f1')

      // Apply theme
      document.body.className = tg.colorScheme || 'light'
    }
  }, [])


  return (
    <TelegramProvider>
      <LanguageProvider>
        <ToastProvider>
          <DataProvider>
            <AppContent />
          </DataProvider>
        </ToastProvider>
      </LanguageProvider>
    </TelegramProvider>
  )
}

export default App
