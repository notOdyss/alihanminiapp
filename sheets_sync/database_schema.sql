-- Схема базы данных для синхрон изации с Google Sheets

-- Таблица транзакций из Google Sheets
CREATE TABLE IF NOT EXISTS sheet_transactions (
    id SERIAL PRIMARY KEY,
    client_username VARCHAR(255),  -- Клиент (tg username)
    transaction_date DATE,  -- Собранная дата из день/месяц/год
    payment_id INTEGER,  -- ID платежа
    amount_gross DECIMAL(18, 2),  -- Сумма платежа (грязная)
    payment_system VARCHAR(100),  -- Платежная система
    buyer_email VARCHAR(255),  -- Реквизиты покупателя
    intermediary_status VARCHAR(50),  -- Платеж получен (да/не требуется/нет)
    credential_type VARCHAR(100),  -- Тип реквизитов
    client_credentials TEXT,  -- Реквизиты клиента
    ali_commission DECIMAL(18, 2),  -- Комиссия Ali для клиента
    p2p_commission DECIMAL(18, 2),  -- Комиссия P2P
    paypal_commission DECIMAL(18, 2),  -- Комиссия PayPal
    paypal_withdrawal_commission DECIMAL(18, 2),  -- Комиссия PayPal на вывод
    withdrawal_amount DECIMAL(18, 2),  -- Сумма вывода клиенту
    withdrawal_received BOOLEAN,  -- Клиент получил вывод?
    comment TEXT,  -- Комментарий
    sheet_row_number INTEGER,  -- Номер строки в Google Sheets
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(payment_id, client_username, sheet_row_number)
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_sheet_transactions_client ON sheet_transactions(client_username);
CREATE INDEX IF NOT EXISTS idx_sheet_transactions_date ON sheet_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_sheet_transactions_payment_id ON sheet_transactions(payment_id);
CREATE INDEX IF NOT EXISTS idx_sheet_transactions_payment_system ON sheet_transactions(payment_system);

-- Таблица балансов PayPal
CREATE TABLE IF NOT EXISTS balances_paypal (
    id SERIAL PRIMARY KEY,
    client_username VARCHAR(255) UNIQUE,
    balance DECIMAL(18, 2),
    comment_1 TEXT,
    comment_2 TEXT,
    comment_3 TEXT,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица балансов Stripe
CREATE TABLE IF NOT EXISTS balances_stripe (
    id SERIAL PRIMARY KEY,
    client_username VARCHAR(255) UNIQUE,
    balance DECIMAL(18, 2),
    transaction_date DATE,
    buyer_credentials TEXT,
    comment_1 TEXT,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица выводов PayPal
CREATE TABLE IF NOT EXISTS balances_paypal_withdrawal (
    id SERIAL PRIMARY KEY,
    client_username VARCHAR(255) UNIQUE,
    withdrawal_amount DECIMAL(18, 2),
    comment_1 TEXT,
    comment_2 TEXT,
    comment_3 TEXT,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для отслеживания пороговых значений клиентов
CREATE TABLE IF NOT EXISTS client_thresholds (
    id SERIAL PRIMARY KEY,
    client_username VARCHAR(255) UNIQUE,
    total_earnings DECIMAL(18, 2) DEFAULT 0,
    threshold_reached BOOLEAN DEFAULT FALSE,
    threshold_amount DECIMAL(18, 2) DEFAULT 500.00,  -- $500 или $1000
    can_view_data BOOLEAN DEFAULT FALSE,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для быстрого поиска по username
CREATE INDEX IF NOT EXISTS idx_client_thresholds_username ON client_thresholds(client_username);

-- Функция для автоматического обновления total_earnings
CREATE OR REPLACE FUNCTION update_client_total_earnings()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO client_thresholds (client_username, total_earnings, threshold_reached, can_view_data)
    VALUES (
        NEW.client_username,
        COALESCE(NEW.withdrawal_amount, 0),
        COALESCE(NEW.withdrawal_amount, 0) >= 500,
        COALESCE(NEW.withdrawal_amount, 0) >= 500
    )
    ON CONFLICT (client_username)
    DO UPDATE SET
        total_earnings = client_thresholds.total_earnings + COALESCE(NEW.withdrawal_amount, 0),
        threshold_reached = (client_thresholds.total_earnings + COALESCE(NEW.withdrawal_amount, 0)) >= client_thresholds.threshold_amount,
        can_view_data = (client_thresholds.total_earnings + COALESCE(NEW.withdrawal_amount, 0)) >= client_thresholds.threshold_amount,
        last_updated_at = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического обновления пороговых значений
DROP TRIGGER IF EXISTS trigger_update_client_earnings ON sheet_transactions;
CREATE TRIGGER trigger_update_client_earnings
AFTER INSERT OR UPDATE ON sheet_transactions
FOR EACH ROW
EXECUTE FUNCTION update_client_total_earnings();

-- Комментарии к таблицам
COMMENT ON TABLE sheet_transactions IS 'Транзакции клиентов, синхронизированные из Google Sheets';
COMMENT ON TABLE balances_paypal IS 'Балансы клиентов в PayPal';
COMMENT ON TABLE balances_stripe IS 'Балансы клиентов в Stripe';
COMMENT ON TABLE balances_paypal_withdrawal IS 'Выводы клиентов через PayPal';
COMMENT ON TABLE client_thresholds IS 'Пороговые значения для доступа клиентов к данным';
