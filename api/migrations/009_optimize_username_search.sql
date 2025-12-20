-- Create a functional B-Tree index on LOWER(client_username) for case-insensitive exact match lookups
-- This does not require pg_trgm extension and is safe to run without superuser permissions
CREATE INDEX IF NOT EXISTS idx_transactions_lower_client_username ON sheet_transactions (LOWER(client_username));
