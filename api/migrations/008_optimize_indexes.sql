-- Optimize indexes for case-insensitive username lookups and sorting

-- 1. Index for Check Access / Total Earnings (WHERE LOWER(username) AND withdrawal_received)
CREATE INDEX IF NOT EXISTS idx_transactions_lower_user_withdrawal 
ON sheet_transactions (LOWER(client_username), withdrawal_received);

-- 2. Index for Transaction List (WHERE LOWER(username) ORDER BY date)
CREATE INDEX IF NOT EXISTS idx_transactions_lower_user_date 
ON sheet_transactions (LOWER(client_username), transaction_date DESC);

-- 3. Index for Buyer Lookup (Exact match usually, but email might be mixed case)
CREATE INDEX IF NOT EXISTS idx_transactions_buyer_email
ON sheet_transactions (buyer_email);
