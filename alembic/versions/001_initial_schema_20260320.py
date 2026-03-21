"""Initial schema creation

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-20 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all database tables."""
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column(
            "subscription_tier",
            sa.String(length=50),
            nullable=False,
            server_default="free",
        ),
        sa.Column("invoice_limit", sa.Integer, nullable=False, server_default="5"),
        sa.Column("timezone", sa.String(length=50), server_default="UTC"),
        sa.Column("email_notifications_enabled", sa.Boolean, server_default="true"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_admin", sa.Boolean, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_subscription_tier", "users", ["subscription_tier"])
    op.create_index("idx_users_created_at", "users", ["created_at"])
    op.create_check_constraint(
        "ck_users_subscription_tier",
        "users",
        "subscription_tier IN ('free', 'pro', 'enterprise')",
    )

    # Create payment_connections table
    op.create_table(
        "payment_connections",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("connection_name", sa.String(length=255), nullable=True),
        sa.Column("credentials_encrypted", sa.Text, nullable=False),
        sa.Column("external_account_id", sa.String(length=500), nullable=True),
        sa.Column("external_user_id", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_payment_connections_user_id", "payment_connections", ["user_id"]
    )
    op.create_index(
        "idx_payment_connections_provider", "payment_connections", ["provider"]
    )
    op.create_index(
        "idx_payment_connections_is_active", "payment_connections", ["is_active"]
    )
    # Partial unique index for active connections per user/provider
    op.execute(
        "CREATE UNIQUE INDEX uniq_user_provider_active ON payment_connections (user_id, provider) WHERE is_active = true"
    )
    op.create_foreign_key(
        "fk_payment_connections_user_id",
        "payment_connections",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "ck_payment_connections_provider",
        "payment_connections",
        "provider IN ('stripe', 'paypal', 'plaid')",
    )

    # Create invoices table
    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("invoice_number", sa.String(length=255), nullable=True),
        sa.Column("client_name", sa.String(length=500), nullable=False),
        sa.Column("client_email", sa.String(length=500), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "currency", sa.String(length=3), nullable=False, server_default="USD"
        ),
        sa.Column(
            "status", sa.String(length=50), nullable=False, server_default="draft"
        ),
        sa.Column("due_date", sa.Date, nullable=False),
        sa.Column(
            "issue_date",
            sa.Date,
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("paid_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stripe_payment_intent_id", sa.String(length=500), nullable=True),
        sa.Column("stripe_invoice_id", sa.String(length=500), nullable=True),
        sa.Column("paypal_txn_id", sa.String(length=500), nullable=True),
        sa.Column("paypal_invoice_id", sa.String(length=500), nullable=True),
        sa.Column("plaid_account_id", sa.String(length=500), nullable=True),
        sa.Column("plaid_transaction_id", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("extra_data", postgresql.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_invoices_user_id", "invoices", ["user_id"])
    op.create_index("idx_invoices_status", "invoices", ["status"])
    op.create_index("idx_invoices_due_date", "invoices", ["due_date"])
    op.create_index("idx_invoices_created_at", "invoices", ["created_at"])
    # Partial indexes for external IDs
    op.execute(
        "CREATE INDEX idx_invoices_stripe_payment_intent ON invoices (stripe_payment_intent_id) WHERE stripe_payment_intent_id IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX idx_invoices_paypal_txn ON invoices (paypal_txn_id) WHERE paypal_txn_id IS NOT NULL"
    )
     op.create_index(
         "idx_invoices_metadata", "invoices", ["extra_data"], postgresql_using="gin"
     )
    op.create_index("idx_invoices_user_status", "invoices", ["user_id", "status"])
    op.create_index("idx_invoices_user_due_date", "invoices", ["user_id", "due_date"])
    op.create_foreign_key(
        "fk_invoices_user_id",
        "invoices",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "ck_invoices_status",
        "invoices",
        "status IN ('draft', 'sent', 'paid', 'overdue', 'disputed', 'canceled')",
    )
    op.create_check_constraint("ck_invoices_amount", "invoices", "amount > 0")

    # Create templates table
    op.create_table(
        "templates",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("is_system", sa.Boolean, server_default="false"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("subject", sa.String(length=1000), nullable=False),
        sa.Column("body_html", sa.Text, nullable=False),
        sa.Column("body_text", sa.Text, nullable=True),
        sa.Column("variables", postgresql.JSON, server_default="[]"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_templates_user_id", "templates", ["user_id"])
    op.create_index("idx_templates_type", "templates", ["type"])
    op.create_index("idx_templates_is_system", "templates", ["is_system"])
    op.create_index("idx_templates_created_at", "templates", ["created_at"])
    op.create_foreign_key(
        "fk_templates_user_id",
        "templates",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "ck_templates_type",
        "templates",
        "type IN ('follow_up_3_day', 'follow_up_7_day', 'follow_up_14_day', "
        "'dispute_letter', 'small_claims_form', 'custom')",
    )

    # Create campaigns table
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("ab_test_variant", sa.String(length=50), nullable=True),
        sa.Column("scheduled_send_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("opened_count", sa.Integer, server_default="0"),
        sa.Column("clicked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_after_send", sa.Boolean, server_default="false"),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_campaigns_user_id", "campaigns", ["user_id"])
    op.create_index("idx_campaigns_template_id", "campaigns", ["template_id"])
    op.create_index("idx_campaigns_invoice_id", "campaigns", ["invoice_id"])
    op.create_index("idx_campaigns_sent_at", "campaigns", ["sent_at"])
    op.create_index("idx_campaigns_opened_at", "campaigns", ["opened_at"])
    op.create_index("idx_campaigns_ab_test_variant", "campaigns", ["ab_test_variant"])
    op.create_foreign_key(
        "fk_campaigns_user_id",
        "campaigns",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_campaigns_template_id",
        "campaigns",
        "templates",
        ["template_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_campaigns_invoice_id",
        "campaigns",
        "invoices",
        ["invoice_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Create ab_tests table
    op.create_table(
        "ab_tests",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("test_type", sa.String(length=50), nullable=False),
        sa.Column("variants", postgresql.JSON, server_default="{}"),
        sa.Column("metadata", postgresql.JSON, server_default="{}"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ab_tests_user_id", "ab_tests", ["user_id"])
    op.create_index("idx_ab_tests_is_active", "ab_tests", ["is_active"])
    op.create_index("idx_ab_tests_test_type", "ab_tests", ["test_type"])
    op.create_foreign_key(
        "fk_ab_tests_user_id",
        "ab_tests",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "ck_ab_tests_test_type",
        "ab_tests",
        "test_type IN ('template', 'timing', 'subject_line')",
    )

    # Create email_events table
    op.create_table(
        "email_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_data", postgresql.JSON, server_default="{}"),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_email_events_campaign_id", "email_events", ["campaign_id"])
    op.create_index("idx_email_events_event_type", "email_events", ["event_type"])
    op.create_index("idx_email_events_occurred_at", "email_events", ["occurred_at"])
    op.create_foreign_key(
        "fk_email_events_campaign_id",
        "email_events",
        "campaigns",
        ["campaign_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_check_constraint(
        "ck_email_events_event_type",
        "email_events",
        "event_type IN ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'complained')",
    )

    # Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("old_values", postgresql.JSON, nullable=True),
        sa.Column("new_values", postgresql.JSON, nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("idx_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"])
    op.create_foreign_key(
        "fk_audit_logs_user_id",
        "audit_logs",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create webhook_events table
    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("event_id", sa.String(length=500), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("payload", postgresql.JSON, nullable=False),
        sa.Column("signature_verified", sa.Boolean, server_default="false"),
        sa.Column(
            "processing_status",
            sa.String(length=50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("processing_error", sa.Text, nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_webhook_events_provider", "webhook_events", ["provider"])
    op.create_index("idx_webhook_events_event_id", "webhook_events", ["event_id"])
    op.create_index(
        "idx_webhook_events_processing_status", "webhook_events", ["processing_status"]
    )
    op.create_index("idx_webhook_events_created_at", "webhook_events", ["created_at"])
    op.create_unique_constraint(
        "uniq_provider_event_id", "webhook_events", ["provider", "event_id"]
    )
    op.create_check_constraint(
        "ck_webhook_events_processing_status",
        "webhook_events",
        "processing_status IN ('pending', 'processed', 'failed')",
    )
    op.create_check_constraint(
        "ck_webhook_events_provider",
        "webhook_events",
        "provider IN ('stripe', 'paypal', 'plaid')",
    )

    # Create system_metrics table
    op.create_table(
        "system_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("metric_name", sa.String(length=100), nullable=False),
        sa.Column("metric_value", sa.Numeric(15, 4), nullable=False),
        sa.Column("labels", postgresql.JSON, server_default="{}"),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_system_metrics_name", "system_metrics", ["metric_name"])
    op.create_index("idx_system_metrics_recorded_at", "system_metrics", ["recorded_at"])

    # Create refresh_tokens table
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("is_revoked", sa.Boolean, server_default="false"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("idx_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
    op.create_index("idx_refresh_tokens_expires_at", "refresh_tokens", ["expires_at"])
    op.create_foreign_key(
        "fk_refresh_tokens_user_id",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Create trigger function for updated_at
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )

    # Create triggers for tables with updated_at
    op.execute(
        "CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users "
        "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"
    )
    op.execute(
        "CREATE TRIGGER update_payment_connections_updated_at BEFORE UPDATE ON payment_connections "
        "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"
    )
    op.execute(
        "CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices "
        "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"
    )
    op.execute(
        "CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates "
        "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"
    )
    op.execute(
        "CREATE TRIGGER update_ab_tests_updated_at BEFORE UPDATE ON ab_tests "
        "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()"
    )

    # Create functions
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_invoice_limit(p_user_id UUID)
        RETURNS BOOLEAN AS $$
        DECLARE
            v_limit INTEGER;
            v_count INTEGER;
        BEGIN
            SELECT invoice_limit INTO v_limit FROM users WHERE id = p_user_id AND is_active = true;
            
            IF v_limit IS NULL THEN
                RETURN false;
            END IF;
            
            SELECT COUNT(*) INTO v_count FROM invoices 
            WHERE user_id = p_user_id 
            AND status NOT IN ('canceled', 'paid');
            
            RETURN v_count < v_limit;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
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
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION get_overdue_count(p_user_id UUID)
        RETURNS INTEGER AS $$
        BEGIN
            RETURN COUNT(*) FROM invoices 
            WHERE user_id = p_user_id 
            AND status IN ('overdue', 'disputed')
            AND due_date < CURRENT_DATE;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # Create views
    op.execute(
        """
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
        """
    )

    op.execute(
        """
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
        """
    )


def downgrade() -> None:
    """Drop all tables and functions."""
    # Drop views first
    op.execute("DROP VIEW IF EXISTS campaign_effectiveness")
    op.execute("DROP VIEW IF EXISTS user_invoice_summary")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS get_overdue_count(UUID)")
    op.execute("DROP FUNCTION IF EXISTS calculate_recovery_rate(UUID)")
    op.execute("DROP FUNCTION IF EXISTS check_invoice_limit(UUID)")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables in reverse order (to respect foreign keys)
    op.drop_table("refresh_tokens")
    op.drop_table("system_metrics")
    op.drop_table("webhook_events")
    op.drop_table("audit_logs")
    op.drop_table("email_events")
    op.drop_table("ab_tests")
    op.drop_table("campaigns")
    op.drop_table("templates")
    op.drop_table("invoices")
    op.drop_table("payment_connections")
    op.drop_table("users")

    # Drop extensions
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
