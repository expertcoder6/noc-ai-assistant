"""Initial schema migration.

Revision ID: 0001_initial_schema
Revises: (none — this is the baseline)
Create Date: 2026-05-28

Creates all 7 tables as specified in the Network AI Assistant design doc:
  locations, devices, interfaces, device_metrics,
  config_changes, alerts, audit_log

Also creates read-only role and performance indexes.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── locations ────────────────────────────────────────────────────────────
    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("site_name", sa.String(100), nullable=False),
        sa.Column("site_code", sa.String(20), nullable=False, unique=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )

    # ── devices ──────────────────────────────────────────────────────────────
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("hostname", sa.String(255), nullable=False, unique=True),
        sa.Column("ip_address", postgresql.INET(), nullable=False),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("vendor", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("os_version", sa.String(100), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("status", sa.String(20), server_default="unknown"),
        sa.Column("last_seen", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_devices_device_type", "devices", ["device_type"])
    op.create_index("ix_devices_status", "devices", ["status"])
    op.create_index("ix_devices_location_id", "devices", ["location_id"])

    # ── interfaces ───────────────────────────────────────────────────────────
    op.create_table(
        "interfaces",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=True),
        sa.Column("interface_name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="down"),
        sa.Column("speed_mbps", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("packet_loss_pct", sa.Numeric(5, 2), server_default="0"),
        sa.Column("error_count", sa.Integer(), server_default="0"),
        sa.Column("utilization_pct", sa.Numeric(5, 2), server_default="0"),
        sa.Column("last_updated", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("device_id", "interface_name", name="uq_interfaces_device_ifname"),
    )
    op.create_index("ix_interfaces_device_id", "interfaces", ["device_id"])

    # ── device_metrics ───────────────────────────────────────────────────────
    op.create_table(
        "device_metrics",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=True),
        sa.Column("cpu_usage", sa.Numeric(5, 2), nullable=True),
        sa.Column("memory_usage", sa.Numeric(5, 2), nullable=True),
        sa.Column("uptime_seconds", sa.BigInteger(), nullable=True),
        sa.Column("temperature_c", sa.Numeric(5, 1), nullable=True),
        sa.Column("recorded_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_device_metrics_device_id", "device_metrics", ["device_id"])
    op.create_index("ix_device_metrics_recorded_at", "device_metrics", ["recorded_at"])

    # ── config_changes ───────────────────────────────────────────────────────
    op.create_table(
        "config_changes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=True),
        sa.Column("changed_by", sa.String(100), nullable=True),
        sa.Column("change_type", sa.String(50), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("diff_hash", sa.String(64), nullable=True),
        sa.Column("changed_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_config_changes_changed_at", "config_changes", ["changed_at"])

    # ── alerts ───────────────────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id", ondelete="CASCADE"), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("alert_type", sa.String(100), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="TRUE"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("resolved_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_is_active", "alerts", ["is_active"])

    # ── audit_log ────────────────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(100), nullable=False),
        sa.Column("user_question", sa.Text(), nullable=False),
        sa.Column("parsed_intent", postgresql.JSONB(), nullable=True),
        sa.Column("sql_executed", sa.Text(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("alerts")
    op.drop_table("config_changes")
    op.drop_table("device_metrics")
    op.drop_table("interfaces")
    op.drop_table("devices")
    op.drop_table("locations")
