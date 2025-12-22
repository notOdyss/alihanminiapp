import { createContext, useContext, useEffect, useState } from 'react'

const TelegramContext = createContext(null)

export const TelegramProvider = ({ children }) => {
  const [tg, setTg] = useState(null)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const telegram = window.Telegram?.WebApp
    if (telegram) {
      telegram.ready()
      setTg(telegram)

      const tgUser = telegram.initDataUnsafe?.user
      if (tgUser) {
        setUser(tgUser)
      } else {
        // Localhost / Dev fallback
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
          console.log('Localhost detected: Using mock Telegram user')
          setUser({
            id: 12345,
            first_name: 'LocalDev',
            last_name: 'User',
            username: 'local_dev'
          })
        } else {
          setUser(null)
        }
      }
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
