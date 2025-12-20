# Настройка Google Sheets API

## Шаг 1: Создание Service Account в Google Cloud

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Перейдите в **APIs & Services** → **Library**
4. Найдите и включите **Google Sheets API**
5. Перейдите в **APIs & Services** → **Credentials**
6. Нажмите **Create Credentials** → **Service Account**
7. Заполните:
   - Service account name: `alihanbot-sheets-sync`
   - Service account ID: (автоматически)
   - Description: `Service account for syncing Google Sheets with PostgreSQL`
8. Нажмите **Create and Continue**
9. Role: выберите **Editor** (или можно оставить без роли)
10. Нажмите **Done**

## Шаг 2: Создание ключа для Service Account

1. Найдите созданный Service Account в списке
2. Нажмите на него
3. Перейдите на вкладку **Keys**
4. Нажмите **Add Key** → **Create new key**
5. Выберите **JSON**
6. Скачайте файл (например, `alihanbot-service-account.json`)
7. **ВАЖНО:** Сохраните этот файл в безопасном месте!

## Шаг 3: Предоставление доступа к таблицам

1. Откройте скачанный JSON файл
2. Найдите поле `"client_email"` (например, `alihanbot-sheets-sync@project-id.iam.gserviceaccount.com`)
3. Скопируйте этот email
4. Откройте вашу Google Таблицу с данными
5. Нажмите **Share** (Поделиться)
6. Вставьте скопированный email
7. Выберите роль **Viewer** (или **Editor** если нужна запись)
8. Снимите галочку **Notify people** (не отправлять уведомление)
9. Нажмите **Share**

## Шаг 4: Получение ID таблиц

URL Google Таблицы выглядит так:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=SHEET_ID
```

Где:
- `SPREADSHEET_ID` - ID всей таблицы (основной ID)
- `SHEET_ID` - ID конкретного листа внутри таблицы

**Пример:**
```
https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit#gid=0
```
- SPREADSHEET_ID: `1a2b3c4d5e6f7g8h9i0j`
- SHEET_ID: `0` (первый лист)

Скопируйте SPREADSHEET_ID для ваших таблиц:
1. Таблица с транзакциями
2. Таблица с балансами (PayPal/Stripe/Вывод)

## Шаг 5: Настройка в проекте

1. Поместите скачанный JSON файл в папку `/Users/notodyss/Desktop/alihanbot/credentials/`
2. Переименуйте в `google-sheets-credentials.json`
3. Добавьте в `.env` файл:
```env
# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials/google-sheets-credentials.json
TRANSACTIONS_SPREADSHEET_ID=your_transactions_spreadsheet_id
BALANCES_SPREADSHEET_ID=your_balances_spreadsheet_id
SYNC_INTERVAL_MINUTES=5
```

## Структура ваших таблиц

### Таблица транзакций
Листы:
- Лист "Транзакции" с колонками:
  - Клиент (tg username)
  - День, Месяц, Год
  - ID платежа
  - Сумма платежа
  - Платежная система
  - Реквизиты покупателя
  - Платеж получен (посредники)
  - Тип реквизитов
  - Реквизиты клиента
  - Комиссия Ali для клиента
  - Комиссия P2P
  - Комиссия PayPal
  - Комиссия PayPal на вывод
  - Сумма вывода клиенту
  - Клиент получил вывод?
  - Комментарий

### Таблица балансов
Листы:
- "PayPal" с колонками: Клиент @, PayPal $, Комментарий 1, 2, 3
- "Stripe" с колонками: Клиент @, Stripe $, Дата, Рек Покуп, Коммент 1
- "PayPal Вывод" с колонками: Клиент @, PayPal Вывод $, Комментарий 1, 2, 3

## Что дальше?

После настройки запустите:
```bash
cd /Users/notodyss/Desktop/alihanbot
python3 sheets_sync/test_connection.py
```

Это проверит подключение к Google Sheets.
