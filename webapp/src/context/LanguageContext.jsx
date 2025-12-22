import { createContext, useContext, useState, useEffect } from 'react'

const LanguageContext = createContext(null)

const translations = {
  ru: {
    // Navigation
    transactions: 'Транзакции',
    calculator: 'Калькулятор',
    balance: 'Баланс',
    statistics: 'Статистика',
    more: 'Еще',

    // Transactions Page
    transactionsTitle: 'Транзакции',
    transactionsSubtitle: 'История ваших последних транзакций',
    totalAmount: 'Общая сумма',
    totalTransactions: 'Транзакций',
    startDate: 'Начало',
    endDate: 'Конец',
    vipThreshold: 'Порог VIP',
    noTransactions: 'Пока нет транзакций',
    transactionsAppear: 'Ваши транзакции появятся здесь',
    completed: 'Завершено',
    pending: 'В обработке',
    cancelled: 'Отменено',

    // Calculator Page
    calculatorTitle: 'Калькулятор комиссий',
    calculatorSubtitle: 'Рассчитайте комиссии в обоих направлениях',
    saleAmount: 'Введите сумму продажи ($)',
    paypalFee: 'Комиссия PayPal',
    bankFee: 'Комиссия Банка',
    stripeFee: 'Комиссия Stripe',
    internalFee: 'Внутренняя комиссия',
    p2pFee: 'P2P комиссия',
    youReceive: 'Вы получите',
    netAmount: 'Чистая сумма',

    // Balance Page
    balanceTitle: 'Баланс',
    balanceSubtitle: 'Ваш текущий баланс',
    totalBalance: 'Общий доступный баланс',
    paypalBalance: 'Баланс PayPal',
    stripeBalance: 'Баланс Stripe',
    withdrawalPaypal: 'Вывод PayPal',
    balanceInfo: 'Информация о балансе обновляется из данных вашего аккаунта.',
    account: 'Аккаунт',

    // Statistics Page
    statisticsTitle: 'Статистика',
    statisticsSubtitle: 'Обзор ваших транзакций',
    myStats: 'Моя статистика',
    buyerStats: 'Статистика покупателя',
    avgCheck: 'Средний чек',
    avgCheckDesc: 'Общая $ сумма чеков / общее количество чеков',
    totalChecks: 'Всего чеков',
    totalChecksDesc: 'Общее количество обработанных чеков',
    totalSum: 'Общая сумма',
    totalSumDesc: 'Совокупный доход за весь период',
    avgChecksMonth: 'Среднее количество чеков в месяц',
    avgChecksMonthDesc: 'Усредненная активность за месяц',
    avgSumMonth: 'Средняя сумма в месяц',
    avgSumMonthDesc: 'Средний доход за месячный период',
    buyerStatsUnavailable: 'Статистика покупателя пока недоступна',
    buyerStatsAppear: 'Данные появятся после первых покупок',

    // More Page
    moreTitle: 'Еще',
    moreSubtitle: 'Дополнительные опции',
    contactAdmins: 'Связаться с админами',
    contactDesc: 'Свяжитесь с нашей командой для получения поддержки и помощи',
    admin: 'Admin',
    clickToChat: 'Нажмите на карточку администратора, чтобы начать чат в Telegram',
    referralProgram: 'Реферальная программа',
    yourReferralCode: 'Ваш реферальный код:',
    copy: 'Копировать',
    clicks: 'Переходов',
    registrations: 'Регистраций',
    noReferralCode: 'У вас пока нет реферального кода',
    createCodeDesc: 'Создайте код и приглашайте друзей, чтобы получать бонусы',
    createReferralCode: 'Создать реферальный код',
    language: 'Язык',
    vipStatus: 'VIP Статус',
    vipProgress: 'Прогресс к VIP',
    spent: 'потрачено',
    unlockVip: 'До VIP статуса',
    referralCodeCreated: 'Реферальный код создан!',
    linkCopied: 'Ссылка скопирована!',

    // Buyer Lookup
    enterEmail: 'Введите email покупателя',
    lookup: 'Найти',
    buyerFound: 'Покупатель найден',
    buyerNotFound: 'Покупатель не найден',
    firstSeen: 'Первая покупка',
    lastSeen: 'Последняя покупка',
    uniquePartners: 'Уникальных партнеров',
    premiumFeature: 'Премиум функция',
    premiumFeatureDesc: 'Для доступа нужен оборот >$1000 за 30 дней.',

    // Loading
    loading: 'Загрузка...',
  },
  en: {
    // Navigation
    transactions: 'Transactions',
    calculator: 'Calculator',
    balance: 'Balance',
    statistics: 'Statistics',
    more: 'More',

    // Transactions Page
    transactionsTitle: 'Transactions',
    transactionsSubtitle: 'History of your recent transactions',
    totalAmount: 'Total Amount',
    totalTransactions: 'Transactions',
    startDate: 'Start',
    endDate: 'End',
    vipThreshold: 'VIP Threshold',
    noTransactions: 'No transactions yet',
    transactionsAppear: 'Your transactions will appear here',
    completed: 'Completed',
    pending: 'Pending',
    cancelled: 'Cancelled',

    // Calculator Page
    calculatorTitle: 'Fee Calculator',
    calculatorSubtitle: 'Calculate fees in both directions',
    saleAmount: 'Enter sale amount ($)',
    paypalFee: 'PayPal Fee',
    bankFee: 'Bank Fee',
    stripeFee: 'Stripe Fee',
    internalFee: 'Internal Fee',
    p2pFee: 'P2P Fee',
    youReceive: 'You Receive',
    netAmount: 'Net Amount',

    // Balance Page
    balanceTitle: 'Balance',
    balanceSubtitle: 'Your current balance',
    totalBalance: 'Total Available Balance',
    paypalBalance: 'PayPal Balance',
    stripeBalance: 'Stripe Balance',
    withdrawalPaypal: 'PayPal Withdrawal',
    balanceInfo: 'Balance information is updated from your account data.',
    account: 'Account',

    // Statistics Page
    statisticsTitle: 'Statistics',
    statisticsSubtitle: 'Overview of your transactions',
    myStats: 'My Statistics',
    buyerStats: 'Buyer Statistics',
    avgCheck: 'Average Check',
    avgCheckDesc: 'Total $ amount / total number of checks',
    totalChecks: 'Total Checks',
    totalChecksDesc: 'Total number of processed checks',
    totalSum: 'Total Amount',
    totalSumDesc: 'Cumulative income for the entire period',
    avgChecksMonth: 'Average Checks per Month',
    avgChecksMonthDesc: 'Average activity per month',
    avgSumMonth: 'Average Amount per Month',
    avgSumMonthDesc: 'Average income per monthly period',
    buyerStatsUnavailable: 'Buyer statistics not yet available',
    buyerStatsAppear: 'Data will appear after first purchases',

    // More Page
    moreTitle: 'More',
    moreSubtitle: 'Additional options',
    contactAdmins: 'Contact Admins',
    contactDesc: 'Contact our team for support and assistance',
    admin: 'Admin',
    clickToChat: 'Click on admin card to start chat in Telegram',
    referralProgram: 'Referral Program',
    yourReferralCode: 'Your referral code:',
    copy: 'Copy',
    clicks: 'Clicks',
    registrations: 'Registrations',
    noReferralCode: 'You don\'t have a referral code yet',
    createCodeDesc: 'Create a code and invite friends to get bonuses',
    createReferralCode: 'Create Referral Code',
    language: 'Language',
    vipStatus: 'VIP Status',
    vipProgress: 'VIP Progress',
    spent: 'spent',
    unlockVip: 'Until VIP status',
    referralCodeCreated: 'Referral code created!',
    linkCopied: 'Link copied!',

    // Buyer Lookup
    enterEmail: 'Enter buyer email',
    lookup: 'Lookup',
    buyerFound: 'Buyer Found',
    buyerNotFound: 'Buyer not found',
    firstSeen: 'First seen',
    lastSeen: 'Last seen',
    uniquePartners: 'Unique partners',
    premiumFeature: 'Premium Feature',
    premiumFeatureDesc: 'You need >$1000 volume in the last 30 days to use this feature.',

    // Loading
    loading: 'Loading...',
  }
}

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem('language')
    return saved || 'ru'
  })

  useEffect(() => {
    localStorage.setItem('language', language)
  }, [language])

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'ru' ? 'en' : 'ru')
  }

  const t = (key) => {
    return translations[language][key] || key
  }

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider')
  }
  return context
}
