-- Sync History Table
-- Tracks each sync operation for monitoring and debugging
CREATE TABLE IF NOT EXISTS sync_history (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,  -- 'transactions', 'balances_paypal', 'balances_stripe', 'withdrawals'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    rows_processed INT DEFAULT 0,
    rows_changed INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running',  -- 'running', 'completed', 'failed'
    error_message TEXT,
    duration_seconds DECIMAL(10, 2)
);

-- Index for querying recent syncs
CREATE INDEX IF NOT EXISTS idx_sync_history_started ON sync_history(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sync_history_type ON sync_history(sync_type, started_at DESC);
