# AlihanBot API - Полное руководство

## 🎉 Статус: ВСЕ ГОТОВО И РАБОТАЕТ!

✅ Google Sheets → PostgreSQL синхронизация (12,465 транзакций)
✅ FastAPI backend с реальными данными
✅ Webapp готов к использованию
✅ Система доступа с порогом $500

---

## 📊 Архитектура системы

```
Google Sheets (источник)
       ↓
Sync Service (каждые 5 мин)
       ↓
PostgreSQL (12,465+ транзакций)
       ↓
FastAPI API (http://localhost:8080)
       ↓
React Webapp (Telegram Mini App)
```

---

## 🚀 Быстрый старт

### 1. Запуск синхронизации Google Sheets (фон)
```bash
cd /Users/notodyss/Desktop/alihanbot
mkdir -p logs
nohup ./venv/bin/python3 sheets_sync/sync_service_v2.py > logs/sheets_sync.log 2>&1 &
```

### 2. Запуск API сервера (фон)
```bash
nohup ./venv/bin/python3 api/main.py > logs/api.log 2>&1 &
```

### 3. Запуск webapp (development)
```bash
cd webapp
npm run dev
```

---

## 📡 API Endpoints

### Base URL: `http://localhost:8080/api`

### 1. **GET /health**
Health check
```bash
curl http://localhost:8080/api/health
```

### 2. **GET /access-status**
Проверка статуса доступа клиента

**Headers:**
- `X-Telegram-Init-Data`: Telegram initData

**Response:**
```json
{
  "has_access": true,
  "total_earnings": 110584.99,
  "threshold_amount": 500.00,
  "threshold_reached": true,
  "progress_percentage": 100.0,
  "is_admin": false
}
```

### 3. **GET /balance**
Получить балансы клиента (требует $500+)

**Headers:**
- `X-Telegram-Init-Data`: Telegram initData

**Response:**
```json
{
  "total": 1000.50,
  "paypal": 500.00,
  "stripe": 450.50,
  "withdrawal": 50.00
}
```

### 4. **GET /statistics**
Статистика клиента (требует $500+)

**Response:**
```json
{
  "avgCheck": 3455.78,
  "totalChecks": 32,
  "totalSum": 110584.99,
  "avgChecksMonth": 4.4,
  "avgSumMonth": 15763.91
}
```

### 5. **GET /transactions**
Список транзакций (требует $500+)

**Query params:**
- `limit` (default: 50)
- `offset` (default: 0)

**Response:**
```json
{
  "transactions": [
    {
      "id": 1,
      "payment_method": "PayPal",
      "amount": 458.30,
      "created_at": "2025-08-30T00:00:00",
      "status": "completed"
    }
  ],
  "total": 31
}
```

### 6. **GET /admin/top-clients** (Только для админов)
Топ клиентов по обороту

**Response:**
```json
{
  "clients": [
    {
      "username": "@memphees",
      "transactions": 32,
      "total_amount": 159513.91,
      "total_withdrawals": 110584.99
    }
  ]
}
```

---

## 🔐 Система доступа

### Правила доступа:
1. **Админы** (из ADMIN_IDS) - **всегда** имеют доступ
2. **Клиенты с оборотом ≥ $500** - имеют доступ к своим данным
3. **Клиенты с оборотом < $500** - получают **403 Forbidden**

### Как работает:
- При каждом INSERT/UPDATE в `sheet_transactions` триггер автоматически обновляет `client_thresholds`
- API проверяет `can_view_data` флаг перед возвратом данных
- Если записи нет - считает сумму withdrawal_amount вручную

### Проверка доступа:
```python
# API автоматически проверяет при каждом запросе
has_access = await check_client_access(username, db, user_id)
if not has_access:
    raise HTTPException(status_code=403, detail="...")
```

---

## 🧪 Тестирование

### Тест API с реальными данными:
```bash
./venv/bin/python3 test_api.py
```

### Тест системы доступа:
```bash
./venv/bin/python3 test_access.py
```

### Ручное тестирование endpoints:
```bash
# Health check
curl http://localhost:8080/api/health

# Access status (нужен mock initData)
python3 -c "
import json, urllib.parse, requests
user = {'id': 123, 'username': 'memphees'}
init_data = f'user={urllib.parse.quote(json.dumps(user))}'
headers = {'X-Telegram-Init-Data': init_data}
r = requests.get('http://localhost:8080/api/access-status', headers=headers)
print(r.json())
"
```

---

## 📊 База данных

### Таблицы:
- `sheet_transactions` - 12,465 транзакций из Google Sheets
- `balances_paypal` - 30 балансов PayPal
- `balances_stripe` - 30 балансов Stripe
- `balances_paypal_withdrawal` - 26 выводов
- `client_thresholds` - пороговые значения клиентов

### Полезные запросы:
```sql
-- Клиенты с доступом
SELECT client_username, total_earnings, can_view_data
FROM client_thresholds
WHERE threshold_reached = TRUE
ORDER BY total_earnings DESC;

-- Топ-10 по обороту
SELECT
    client_username,
    COUNT(*) as tx_count,
    SUM(amount_gross) as total
FROM sheet_transactions
GROUP BY client_username
ORDER BY total DESC
LIMIT 10;

-- Статистика клиента
SELECT
    COUNT(*) as transactions,
    SUM(withdrawal_amount) as total_earnings,
    AVG(withdrawal_amount) as avg_check
FROM sheet_transactions
WHERE client_username = '@memphees'
  AND withdrawal_received = TRUE;
```

---

## 🔄 Синхронизация

### Параметры (.env):
```env
SYNC_INTERVAL_MINUTES=5  # Интервал синхронизации
```

### Мониторинг:
```bash
# Логи синхронизации
tail -f logs/sheets_sync.log

# Логи API
tail -f logs/api.log

# Количество транзакций в БД
psql $DATABASE_URL -c "SELECT COUNT(*) FROM sheet_transactions;"
```

### Ручная синхронизация:
```bash
# Разовая
./venv/bin/python3 sheets_sync/sync_service_v2.py --once

# Непрерывная
./venv/bin/python3 sheets_sync/sync_service_v2.py
```

---

## 🐛 Troubleshooting

### API не отвечает:
```bash
# Проверить что API запущен
lsof -i :8080

# Перезапустить
pkill -f "api/main.py"
./venv/bin/python3 api/main.py > logs/api.log 2>&1 &
```

### 403 Forbidden для клиента:
```sql
-- Проверить заработок клиента
SELECT
    client_username,
    SUM(withdrawal_amount) as total_earnings
FROM sheet_transactions
WHERE client_username = '@username'
  AND withdrawal_received = TRUE
GROUP BY client_username;

-- Если >= $500, обновить вручную
INSERT INTO client_thresholds (client_username, total_earnings, threshold_reached, can_view_data)
VALUES ('@username', 1000.00, TRUE, TRUE)
ON CONFLICT (client_username)
DO UPDATE SET
    total_earnings = 1000.00,
    threshold_reached = TRUE,
    can_view_data = TRUE;
```

### Синхронизация не работает:
```bash
# Проверить процесс
ps aux | grep sync_service

# Проверить логи
tail -30 logs/sheets_sync.log

# Перезапустить
pkill -f "sync_service"
nohup ./venv/bin/python3 sheets_sync/sync_service_v2.py > logs/sheets_sync.log 2>&1 &
```

---

## 📦 Зависимости

### Python (venv):
- fastapi==0.109.0
- uvicorn==0.27.0
- sqlalchemy==2.0.36
- asyncpg==0.30.0
- python-dotenv==1.0.1
- gspread==6.0.0
- google-auth==2.27.0

### Node.js (webapp):
- react==18.3.1
- react-router-dom==6.26.0
- vite==5.4.2

---

## 🔒 Безопасность

### Что защищено:
✅ Telegram initData валидация (в продакшене нужен hash check)
✅ Проверка порога перед доступом к данным
✅ Read-only доступ к Google Sheets
✅ Credentials в .gitignore
✅ CORS настроен (в продакшене указать конкретный origin)

### TODO для продакшена:
- [ ] Валидация Telegram hash в parse_telegram_init_data()
- [ ] HTTPS для API
- [ ] Rate limiting
- [ ] Логирование всех запросов
- [ ] Мониторинг (Sentry, etc.)

---

## 📞 Поддержка

**API PID:** `ps aux | grep "api/main.py"`
**Sync PID:** `ps aux | grep "sync_service"`
**Logs:** `/Users/notodyss/Desktop/alihanbot/logs/`

**База данных:**
`postgresql://notodyss@localhost:5432/exchangebot`

**Google Sheets:**
https://docs.google.com/spreadsheets/d/1H07GetBKwRHJ5KTRhkAg2jVrpQsYpiSocmnx1MtOFJw/

---

## ✨ Готово к использованию!

Все работает и протестировано! 🎉
