# Google Sheets Sync - Руководство

## ✅ Статус
**НАСТРОЕНО И РАБОТАЕТ!**

- ✅ Google Sheets API подключен
- ✅ База данных создана
- ✅ 12,465 транзакций синхронизированы
- ✅ 30 PayPal балансов
- ✅ 30 Stripe балансов
- ✅ 26 PayPal выводов

## 📊 Что синхронизируется

### Таблицы в PostgreSQL:

1. **sheet_transactions** - все транзакции из листа "Платежи"
   - 12,465 записей
   - Данные с марта 2024 по декабрь 2025

2. **balances_paypal** - балансы клиентов PayPal
3. **balances_stripe** - балансы клиентов Stripe
4. **balances_paypal_withdrawal** - выводы PayPal
5. **client_thresholds** - пороговые значения для доступа ($500/$1000)

## 🚀 Запуск синхронизации

### Разовая синхронизация (тест):
```bash
cd /Users/notodyss/Desktop/alihanbot
./venv/bin/python3 sheets_sync/sync_service_v2.py --once
```

### Непрерывная синхронизация (каждые 5 минут):
```bash
cd /Users/notodyss/Desktop/alihanbot
./venv/bin/python3 sheets_sync/sync_service_v2.py
```

### Запуск в фоне:
```bash
cd /Users/notodyss/Desktop/alihanbot
nohup ./venv/bin/python3 sheets_sync/sync_service_v2.py > logs/sheets_sync.log 2>&1 &
```

Для остановки фонового процесса:
```bash
ps aux | grep sync_service
kill <PID>
```

## 📈 Проверка данных

### Подключение к базе:
```bash
psql postgresql://notodyss@localhost:5432/exchangebot
```

### Полезные SQL запросы:

```sql
-- Всего транзакций
SELECT COUNT(*) FROM sheet_transactions;

-- Топ-10 клиентов по обороту
SELECT
    client_username,
    COUNT(*) as transactions,
    SUM(amount_gross) as total_amount,
    SUM(withdrawal_amount) as total_withdrawals
FROM sheet_transactions
GROUP BY client_username
ORDER BY total_amount DESC
LIMIT 10;

-- Транзакции за последний месяц
SELECT
    client_username,
    transaction_date,
    amount_gross,
    payment_system
FROM sheet_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY transaction_date DESC;

-- Клиенты достигшие порога $500
SELECT
    client_username,
    total_earnings,
    threshold_amount,
    can_view_data
FROM client_thresholds
WHERE threshold_reached = TRUE
ORDER BY total_earnings DESC;

-- Балансы всех систем для клиента
SELECT
    'PayPal' as system, balance as amount
FROM balances_paypal
WHERE client_username = '@username'
UNION ALL
SELECT
    'Stripe' as system, balance
FROM balances_stripe
WHERE client_username = '@username'
UNION ALL
SELECT
    'PayPal Withdrawal' as system, withdrawal_amount
FROM balances_paypal_withdrawal
WHERE client_username = '@username';
```

## ⚙️ Настройки

Файл: `/Users/notodyss/Desktop/alihanbot/.env`

```env
# Google Sheets Sync
GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials/google-sheets-credentials.json
TRANSACTIONS_SPREADSHEET_ID=1H07GetBKwRHJ5KTRhkAg2jVrpQsYpiSocmnx1MtOFJw
BALANCES_SPREADSHEET_ID=1H07GetBKwRHJ5KTRhkAg2jVrpQsYpiSocmnx1MtOFJw
SYNC_INTERVAL_MINUTES=5  # Интервал синхронизации
```

## 🔄 Как работает синхронизация

1. **Каждые 5 минут** сервис подключается к Google Sheets
2. Читает все данные из листов "Платежи" и "Баланс"
3. Парсит данные (даты, числа, boolean)
4. Обновляет PostgreSQL с помощью UPSERT (INSERT ... ON CONFLICT UPDATE)
5. Автоматически обновляет пороговые значения клиентов

## 📝 Структура данных

### sheet_transactions
- client_username - @username клиента
- transaction_date - дата транзакции
- payment_id - ID платежа (группировка по дням)
- amount_gross - сумма платежа (грязная)
- payment_system - PayPal, Stripe, Bank, etc.
- buyer_email - email покупателя
- withdrawal_amount - сумма к выводу клиенту
- ali_commission, p2p_commission, paypal_commission - комиссии

### Триггеры и автоматика

При INSERT/UPDATE в sheet_transactions автоматически:
- Считается total_earnings для клиента
- Обновляется threshold_reached если >= $500
- Устанавливается can_view_data = true для доступа к webapp

## 🛠️ Troubleshooting

### Проблема: Синхронизация не работает
1. Проверьте Google Sheets API credentials:
   ```bash
   ./venv/bin/python3 sheets_sync/test_connection.py
   ```

2. Проверьте подключение к PostgreSQL:
   ```bash
   psql postgresql://notodyss@localhost:5432/exchangebot -c "SELECT 1;"
   ```

### Проблема: Дубликаты данных
Дубликаты невозможны благодаря UNIQUE constraint:
```sql
UNIQUE(payment_id, client_username, sheet_row_number)
```

### Проблема: Ошибки парсинга дат
Сервис поддерживает:
- Месяцы на русском (Январь, Февраль, etc.)
- Даты в формате dd.mm.yy (для Stripe)
- Года: 24 → 2024, 2024 → 2024

## 📞 Service Account Email
```
alihanbot-sheets-sync@alihanbot.iam.gserviceaccount.com
```

Этот email должен иметь **Viewer** доступ к таблице:
https://docs.google.com/spreadsheets/d/1H07GetBKwRHJ5KTRhkAg2jVrpQsYpiSocmnx1MtOFJw/

## 🔐 Безопасность

- ✅ Credentials в `.gitignore`
- ✅ Только READ доступ к Google Sheets
- ✅ Локальная база данных PostgreSQL
- ✅ Service Account без лишних прав

## 📊 Performance

- ~12,500 строк синхронизируются за ~11 секунд
- Используется batch UPSERT для скорости
- Прогресс отображается каждые 1000 строк
