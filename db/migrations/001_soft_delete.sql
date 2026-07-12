ALTER TABLE transactions ADD COLUMN IF NOT EXISTS deleted boolean DEFAULT false;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS deleted_at timestamp with time zone;
CREATE INDEX IF NOT EXISTS idx_transactions_deleted ON transactions (deleted);
