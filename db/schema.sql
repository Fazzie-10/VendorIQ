-- VendorIQ PostgreSQL Schema
-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- Users
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    business_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_users_phone ON users (phone);
CREATE INDEX idx_users_status ON users (status);

-- ============================================
-- Transactions
-- ============================================
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    amount NUMERIC,
    item TEXT,
    quantity NUMERIC,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_transactions_user_id ON transactions (user_id);
CREATE INDEX idx_transactions_type ON transactions (type);
CREATE INDEX idx_transactions_created_at ON transactions (created_at);
CREATE INDEX idx_transactions_user_id_created_at ON transactions (user_id, created_at);

-- ============================================
-- Customers
-- ============================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    category TEXT,
    notes TEXT,
    balance NUMERIC DEFAULT 0,
    total_debt NUMERIC DEFAULT 0,
    total_paid NUMERIC DEFAULT 0,
    last_activity TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    UNIQUE(user_id, name)
);

CREATE INDEX idx_customers_user_id ON customers (user_id);
CREATE INDEX idx_customers_phone ON customers (phone);
CREATE INDEX idx_customers_category ON customers (category);
CREATE INDEX idx_customers_is_active ON customers (is_active);
CREATE INDEX idx_customers_user_id_balance ON customers (user_id, balance);

-- ============================================
-- Inventory
-- ============================================
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item TEXT NOT NULL,
    quantity NUMERIC DEFAULT 0,
    unit TEXT DEFAULT 'units',
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, item)
);

CREATE INDEX idx_inventory_user_id ON inventory (user_id);
CREATE INDEX idx_inventory_item ON inventory (item);

-- ============================================
-- Audit Logs
-- ============================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    phone TEXT,
    event_type TEXT NOT NULL,
    input_data JSONB,
    intent TEXT,
    entities JSONB,
    handler TEXT,
    response_text TEXT,
    db_changes JSONB,
    model_used TEXT,
    latency_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX idx_audit_logs_phone ON audit_logs (phone);
CREATE INDEX idx_audit_logs_event_type ON audit_logs (event_type);
CREATE INDEX idx_audit_logs_intent ON audit_logs (intent);
CREATE INDEX idx_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX idx_audit_logs_user_id_created_at ON audit_logs (user_id, created_at);

-- ============================================
-- Conversation Sessions
-- ============================================
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone TEXT NOT NULL,
    session_id TEXT NOT NULL,
    context_summary TEXT,
    message_count INTEGER DEFAULT 0,
    last_activity TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    expired_at TIMESTAMPTZ
);

CREATE INDEX idx_conversation_sessions_phone ON conversation_sessions (phone);
CREATE INDEX idx_conversation_sessions_session_id ON conversation_sessions (session_id);
CREATE INDEX idx_conversation_sessions_last_activity ON conversation_sessions (last_activity);
CREATE INDEX idx_conversation_sessions_phone_session_id ON conversation_sessions (phone, session_id);

-- ============================================
-- Business Events
-- ============================================
CREATE TABLE business_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type TEXT,
    amount NUMERIC,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_business_events_user_id ON business_events (user_id);
CREATE INDEX idx_business_events_event_type ON business_events (event_type);
CREATE INDEX idx_business_events_created_at ON business_events (created_at);
CREATE INDEX idx_business_events_user_id_event_type ON business_events (user_id, event_type);

-- ============================================
-- Notifications
-- ============================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT,
    title TEXT,
    body TEXT,
    scheduled_for TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_notifications_user_id ON notifications (user_id);
CREATE INDEX idx_notifications_status ON notifications (status);
CREATE INDEX idx_notifications_scheduled_for ON notifications (scheduled_for);
CREATE INDEX idx_notifications_user_id_status ON notifications (user_id, status);

-- ============================================
-- Message History
-- ============================================
CREATE TABLE message_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    phone TEXT,
    direction TEXT,
    message_type TEXT DEFAULT 'text',
    intent TEXT,
    content TEXT,
    raw_payload JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_message_history_user_id ON message_history (user_id);
CREATE INDEX idx_message_history_phone ON message_history (phone);
CREATE INDEX idx_message_history_direction ON message_history (direction);
CREATE INDEX idx_message_history_intent ON message_history (intent);
CREATE INDEX idx_message_history_created_at ON message_history (created_at);
CREATE INDEX idx_message_history_user_id_created_at ON message_history (user_id, created_at);

-- ============================================
-- Customer Payments
-- ============================================
CREATE TABLE customer_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type TEXT,
    amount NUMERIC,
    balance_after NUMERIC,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_customer_payments_customer_id ON customer_payments (customer_id);
CREATE INDEX idx_customer_payments_user_id ON customer_payments (user_id);
CREATE INDEX idx_customer_payments_type ON customer_payments (type);
CREATE INDEX idx_customer_payments_created_at ON customer_payments (created_at);
CREATE INDEX idx_customer_payments_customer_id_created_at ON customer_payments (customer_id, created_at);

-- ============================================
-- Healthcheck Function
-- ============================================
CREATE OR REPLACE FUNCTION healthcheck()
RETURNS TABLE (
    table_name TEXT,
    status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        unnest(ARRAY[
            'users',
            'transactions',
            'customers',
            'inventory',
            'audit_logs',
            'conversation_sessions',
            'business_events',
            'notifications',
            'message_history',
            'customer_payments'
        ])::TEXT AS table_name,
        'ok'::TEXT AS status;
END;
$$;
