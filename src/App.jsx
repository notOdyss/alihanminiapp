import { useEffect, useState } from 'react'
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom'
import { TelegramProvider } from './context/TelegramContext'
import { DataProvider } from './context/DataContext'
import Layout from './components/Layout'
import Transactions from './pages/Transactions'
import Calculator from './pages/Calculator'
import Balance from './pages/Balance'
import Statistics from './pages/Statistics'
import More from './pages/More'
import './styles/App.css'

function App() {
  const [loading, setLoading] = useState(true)

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

    // Simulate loading
    setTimeout(() => setLoading(false), 500)
  }, [])

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Загрузка...</p>
      </div>
    )
  }

  return (
    <TelegramProvider>
      <DataProvider>
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
        </BrowserRouter>
      </DataProvider>
    </TelegramProvider>
  )
}

export default App
