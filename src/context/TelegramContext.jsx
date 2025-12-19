import { createContext, useContext, useEffect, useState } from 'react'

const TelegramContext = createContext(null)

export const TelegramProvider = ({ children }) => {
  const [tg, setTg] = useState(null)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const telegram = window.Telegram?.WebApp
    if (telegram) {
      setTg(telegram)
      setUser(telegram.initDataUnsafe?.user || null)
    }
  }, [])

  return (
    <TelegramContext.Provider value={{ tg, user }}>
      {children}
    </TelegramContext.Provider>
  )
}

export const useTelegram = () => {
  const context = useContext(TelegramContext)
  if (!context) {
    throw new Error('useTelegram must be used within TelegramProvider')
  }
  return context
}
