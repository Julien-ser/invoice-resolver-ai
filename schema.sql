-- =====================================================
-- INVOICE RESOLVER AI - Database Schema
-- PostgreSQL 13+
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    invoice_limit INTEGER NOT NULL DEFAULT 5,
    timezone VARCHAR(50) DEFAULT 'UTC',
    email_notifications_enabled BOOLEAN DEFAULT true,
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- Indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);
CREATE INDEX idx_users_created_at ON users(created_at);

-- =====================================================
-- PAYMENT CONNECTIONS TABLE
-- =====================================================
CREATE TABLE payment_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('stripe', 'paypal', 'plaid')),
    connection_name VARCHAR(255),
    credentials_encrypted TEXT NOT NULL,
    external_account_id VARCHAR(500),
    external_user_id VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for payment_connections
CREATE INDEX idx_payment_connections_user_id ON payment_connections(user_id);
CREATE INDEX idx_payment_connections_provider ON payment_connections(provider);
CREATE INDEX idx_payment_connections_is_active ON payment_connections(is_active);

-- Unique constraint: user can have one active connection per provider
CREATE UNIQUE INDEX uniq_user_provider_active ON payment_connections(user_id, provider) WHERE is_active = true;

-- =====================================================
-- INVOICES TABLE
-- =====================================================
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invoice_number VARCHAR(255),
    client_name VARCHAR(500) NOT NULL,
    client_email VARCHAR(500),
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(50) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'disputed', 'canceled')),
    due_date DATE NOT NULL,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    paid_date TIMESTAMPTZ,
    stripe_payment_intent_id VARCHAR(500),
    stripe_invoice_id VARCHAR(500),
    paypal_txn_id VARCHAR(500),
    paypal_invoice_id VARCHAR(500),
    plaid_account_id VARCHAR(500),
    plaid_transaction_id VARCHAR(500),
    description TEXT,
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for invoices
CREATE INDEX idx_invoices_user_id ON invoices(user_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_due_date ON invoices(due_date);
CREATE INDEX idx_invoices_created_at ON invoices(created_at);
CREATE INDEX idx_invoices_stripe_payment_intent ON invoices(stripe_payment_intent_id) WHERE stripe_payment_intent_id IS NOT NULL;
CREATE INDEX idx_invoices_paypal_txn ON invoices(paypal_txn_id) WHERE paypal_txn_id IS NOT NULL;
CREATE INDEX idx_invoices_metadata ON invoices USING GIN(metadata);

-- Composite indexes for common queries
CREATE INDEX idx_invoices_user_status ON invoices(user_id, status);
CREATE INDEX idx_invoices_user_due_date ON invoices(user_id, due_date);

-- =====================================================
-- TEMPLATES TABLE
-- =====================================================
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    is_system BOOLEAN DEFAULT false,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('follow_up_3_day', 'follow_up_7_day', 'follow_up_14_day', 'dispute_letter', 'small_claims_form', 'custom')),
    subject VARCHAR(1000) NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT,
    variables JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for templates
CREATE INDEX idx_templates_user_id ON templates(user_id);
CREATE INDEX idx_templates_type ON templates(type);
CREATE INDEX idx_templates_is_system ON templates(is_system);
CREATE INDEX idx_templates_created_at ON templates(created_at);

-- =====================================================
-- CAMPAIGNS TABLE
-- =====================================================
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE RESTRICT,
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    ab_test_variant VARCHAR(50),
    scheduled_send_at TIMESTAMPTZ NOT NULL,
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    opened_count INTEGER DEFAULT 0,
    clicked_at TIMESTAMPTZ,
    paid_after_send BOOLEAN DEFAULT false,
    paid_amount DECIMAL(12,2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for campaigns
CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_template_id ON campaigns(template_id);
CREATE INDEX idx_campaigns_invoice_id ON campaigns(invoice_id);
CREATE INDEX idx_campaigns_sent_at ON campaigns(sent_at);
CREATE INDEX idx_campaigns_opened_at ON campaigns(opened_at);
CREATE INDEX idx_campaigns_ab_test_variant ON campaigns(ab_test_variant);

-- =====================================================
-- A/B TESTS TABLE
-- =====================================================
CREATE TABLE ab_tests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    test_type VARCHAR(50) NOT NULL CHECK (test_type IN ('template', 'timing', 'subject_line')),
    variants JSONB NOT NULL DEFAULT '[]', -- Array of variant IDs/names
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for ab_tests
CREATE INDEX idx_ab_tests_user_id ON ab_tests(user_id);
CREATE INDEX idx_ab_tests_is_active ON ab_tests(is_active);
CREATE INDEX idx_ab_tests_test_type ON ab_tests(test_type);

-- =====================================================
-- EMAIL EVENTS TABLE (for tracking opens, clicks, bounces)
-- =====================================================
CREATE TABLE email_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained')),
    event_data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for email_events
CREATE INDEX idx_email_events_campaign_id ON email_events(campaign_id);
CREATE INDEX idx_email_events_event_type ON email_events(event_type);
CREATE INDEX idx_email_events_occurred_at ON email_events(occurred_at);

-- =====================================================
-- SYSTEM AUDIT LOG TABLE
-- =====================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for audit_logs
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- =====================================================
-- WEBHOOK EVENTS TABLE (for idempotency and debugging)
-- =====================================================
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('stripe', 'paypal', 'plaid')),
    event_id VARCHAR(500) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    signature_verified BOOLEAN DEFAULT false,
    processing_status VARCHAR(50) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processed', 'failed')),
    processing_error TEXT,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for webhook_events
CREATE INDEX idx_webhook_events_provider ON webhook_events(provider);
CREATE INDEX idx_webhook_events_event_id ON webhook_events(event_id);
CREATE INDEX idx_webhook_events_processing_status ON webhook_events(processing_status);
CREATE INDEX idx_webhook_events_created_at ON webhook_events(created_at);

-- Unique constraint to prevent duplicate webhook processing
CREATE UNIQUE INDEX uniq_provider_event_id ON webhook_events(provider, event_id);

-- =====================================================
-- SYSTEM METRICS TABLE (for monitoring and analytics)
-- =====================================================
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    labels JSONB DEFAULT '{}',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for system_metrics
CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_system_metrics_recorded_at ON system_metrics(recorded_at);

-- =====================================================
-- REFRESH TOKENS TABLE (for JWT token rotation)
-- =====================================================
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for refresh_tokens
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Remove expired refresh tokens periodically (cron job)
-- CREATE INDEX idx_refresh_tokens_not_revoked ON refresh_tokens(user_id) WHERE is_revoked = false AND expires_at > NOW();

-- =====================================================
-- TRIGGER FUNCTIONS FOR UPDATED_AT
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payment_connections_updated_at BEFORE UPDATE ON payment_connections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ab_tests_updated_at BEFORE UPDATE ON ab_tests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- =====================================================

-- Function to check if user has exceeded invoice limit
CREATE OR REPLACE FUNCTION check_invoice_limit(p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_limit INTEGER;
    v_count INTEGER;
BEGIN
    SELECT invoice_limit INTO v_limit FROM users WHERE id = p_user_id AND is_active = true;
    
    IF v_limit IS NULL THEN
        RETURN false; -- User not found or inactive
    END IF;
    
    SELECT COUNT(*) INTO v_count FROM invoices 
    WHERE user_id = p_user_id 
    AND status NOT IN ('canceled', 'paid');
    
    RETURN v_count < v_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate recovery rate for a user
CREATE OR REPLACE FUNCTION calculate_recovery_rate(p_user_id UUID)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    v_total INTEGER;
    v_paid INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_total FROM invoices WHERE user_id = p_user_id AND status NOT IN ('draft', 'canceled');
    SELECT COUNT(*) INTO v_paid FROM invoices WHERE user_id = p_user_id AND status = 'paid';
    
    IF v_total = 0 THEN
        RETURN 0.00;
    END IF;
    
    RETURN ROUND((v_paid::DECIMAL / v_total::DECIMAL) * 100, 2);
END;
$$ LANGUAGE plpgsql;

-- Function to get overdue invoices count
CREATE OR REPLACE FUNCTION get_overdue_count(p_user_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN COUNT(*) FROM invoices 
    WHERE user_id = p_user_id 
    AND status IN ('overdue', 'disputed')
    AND due_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- User invoice summary view
CREATE OR REPLACE VIEW user_invoice_summary AS
SELECT 
    u.id as user_id,
    u.email,
    u.subscription_tier,
    COUNT(i.id) as total_invoices,
    COUNT(CASE WHEN i.status = 'paid' THEN 1 END) as paid_invoices,
    COUNT(CASE WHEN i.status = 'overdue' THEN 1 END) as overdue_invoices,
    COUNT(CASE WHEN i.status = 'disputed' THEN 1 END) as disputed_invoices,
    COALESCE(SUM(CASE WHEN i.status != 'paid' THEN i.amount ELSE 0 END), 0) as outstanding_amount,
    calculate_recovery_rate(u.id) as recovery_rate
FROM users u
LEFT JOIN invoices i ON u.id = i.user_id
GROUP BY u.id, u.email, u.subscription_tier;

-- Campaign effectiveness view
CREATE OR REPLACE VIEW campaign_effectiveness AS
SELECT 
    c.id as campaign_id,
    c.user_id,
    t.name as template_name,
    t.type as template_type,
    c.ab_test_variant,
    COUNT(DISTINCT ee.id) as total_events,
    COUNT(DISTINCT CASE WHEN ee.event_type = 'opened' THEN ee.id END) as opens,
    COUNT(DISTINCT CASE WHEN ee.event_type = 'clicked' THEN ee.id END) as clicks,
    COUNT(DISTINCT CASE WHEN c.paid_after_send = true THEN c.id END) as payments_after_send,
    COALESCE(SUM(c.paid_amount), 0) as revenue_generated
FROM campaigns c
JOIN templates t ON c.template_id = t.id
LEFT JOIN email_events ee ON c.id = ee.campaign_id
GROUP BY c.id, c.user_id, t.name, t.type, c.ab_test_variant;

-- =====================================================
-- INITIAL DATA INSERTION (System Templates)
-- =====================================================

-- Insert default system templates (will be added after user table creation)
-- These will be created by application code or a separate seed script

-- =====================================================
-- SECURITY AND ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS on user-sensitive tables
ALTER TABLE payment_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only access their own data
CREATE POLICY user_payment_connections_policy ON payment_connections
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY user_invoices_policy ON invoices
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY user_templates_policy ON templates
    FOR ALL USING (user_id IS NULL OR user_id = current_setting('app.current_user_id')::UUID);

CREATE POLICY user_campaigns_policy ON campaigns
    FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID);

-- =====================================================
-- COMMENTS ON TABLES AND COLUMNS
-- =====================================================

COMMENT ON TABLE users IS 'User accounts with subscription tiers and limits';
COMMENT ON COLUMN users.subscription_tier IS 'Subscription level: free, pro, enterprise';
COMMENT ON COLUMN users.invoice_limit IS 'Monthly invoice allowance based on tier';

COMMENT ON TABLE payment_connections IS 'Encrypted payment provider credentials and sync status';
COMMENT ON COLUMN payment_connections.credentials_encrypted IS 'Encrypted OAuth tokens/API keys using app secret';

COMMENT ON TABLE invoices IS 'Invoice records with payment status and external provider IDs';
COMMENT ON COLUMN invoices.status IS 'Current invoice status: draft, sent, paid, overdue, disputed, canceled';
COMMENT ON COLUMN invoices.stripe_payment_intent_id IS 'Stripe PaymentIntent ID for reconciliation';
COMMENT ON COLUMN invoices.paypal_txn_id IS 'PayPal transaction ID';

COMMENT ON TABLE templates IS 'Email and document templates for follow-ups and disputes';
COMMENT ON COLUMN templates.type IS 'Template category: follow_up, dispute_letter, small_claims_form';
COMMENT ON COLUMN templates.variables IS 'JSON array of template variable placeholders';

COMMENT ON TABLE campaigns IS 'Email campaign records with tracking metrics';
COMMENT ON COLUMN campaigns.ab_test_variant IS 'Variant identifier for A/B testing';
COMMENT ON COLUMN campaigns.paid_after_send IS 'Flag indicating payment received after campaign send';
COMMENT ON COLUMN campaigns.opened_count IS 'Number of times email was opened';

COMMENT ON TABLE ab_tests IS 'A/B test experiments tracking variants and results';
COMMENT ON COLUMN ab_tests.variants IS 'JSON array of variant configurations (templates, timing, etc.)';

COMMENT ON TABLE email_events IS 'Email delivery and engagement tracking events';
COMMENT ON COLUMN email_events.event_type IS 'Type: sent, delivered, opened, clicked, bounced, complained';

COMMENT ON TABLE webhook_events IS 'Persistent storage of received webhooks for audit and idempotency';
COMMENT ON COLUMN webhook_events.signature_verified IS 'Whether webhook signature passed verification';

-- =====================================================
-- FINISH
-- =====================================================

-- Grant minimal permissions (to be customized with actual roles)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES TO app_user;

COMMIT;

-- =====================================================
-- MIGRATION NOTES
-- =====================================================
-- Version: 001_initial_schema
-- Created: 2026-03-20
-- Author: OpenCode Agent
--
-- To apply:
--   psql -U postgres -d invoice_resolver < schema.sql
--
-- To rollback:
--   Drop all tables in reverse dependency order:
--   DROP TABLE IF EXISTS email_events CASCADE;
--   DROP TABLE IF EXISTS campaigns CASCADE;
--   DROP TABLE IF EXISTS ab_tests CASCADE;
--   DROP TABLE IF EXISTS templates CASCADE;
--   DROP TABLE IF EXISTS invoices CASCADE;
--   DROP TABLE IF EXISTS payment_connections CASCADE;
--   DROP TABLE IF EXISTS audit_logs CASCADE;
--   DROP TABLE IF EXISTS webhook_events CASCADE;
--   DROP TABLE IF EXISTS system_metrics CASCADE;
--   DROP TABLE IF EXISTS refresh_tokens CASCADE;
--   DROP TABLE IF EXISTS users CASCADE;
--   DROP FUNCTION IF EXISTS update_updated_at_column();
--   DROP FUNCTION IF EXISTS check_invoice_limit(UUID);
--   DROP FUNCTION IF EXISTS calculate_recovery_rate(UUID);
--   DROP FUNCTION IF EXISTS get_overdue_count(UUID);
--   DROP VIEW IF EXISTS user_invoice_summary;
--   DROP VIEW IF EXISTS campaign_effectiveness;
