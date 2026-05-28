from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Numeric,
    BigInteger,
    JSON,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.schema import MetaData

# Central metadata object for all tables
metadata = MetaData()

# Locations table
locations = Table(
    "locations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("site_name", String(100), nullable=False),
    Column("site_code", String(20), nullable=False, unique=True),
    Column("address", Text),
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
)

# Devices table
devices = Table(
    "devices",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("hostname", String(255), nullable=False, unique=True),
    Column("ip_address", INET, nullable=False),
    Column(
        "device_type",
        String(50),
        nullable=False,
        server_default=text("'router'")
    ),
    Column("vendor", String(100)),
    Column("model", String(100)),
    Column("os_version", String(100)),
    Column("serial_number", String(100)),
    Column("location_id", Integer, ForeignKey("locations.id")),
    Column(
        "status",
        String(20),
        nullable=False,
        server_default=text("'unknown'")
    ),
    Column("last_seen", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
    Column("updated_at", DateTime(timezone=True), server_default=text("NOW()")),
    CheckConstraint(
        "device_type IN ('router','switch','firewall','ap','load_balancer')",
        name="ck_devices_device_type",
    ),
    CheckConstraint(
        "status IN ('up','down','degraded','unknown')",
        name="ck_devices_status",
    ),
    Index("idx_devices_device_type", "device_type"),
    Index("idx_devices_status", "status"),
    Index("idx_devices_location_id", "location_id"),
)

# Interfaces table
interfaces = Table(
    "interfaces",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("device_id", Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
    Column("interface_name", String(100), nullable=False),
    Column(
        "status",
        String(20),
        nullable=False,
        server_default=text("'down'")
    ),
    Column("speed_mbps", Integer),
    Column("description", Text),
    Column("ip_address", INET),
    Column("packet_loss_pct", Numeric(5, 2), server_default=text("0")),
    Column("error_count", Integer, server_default=text("0")),
    Column("utilization_pct", Numeric(5, 2), server_default=text("0")),
    Column("last_updated", DateTime(timezone=True), server_default=text("NOW()")),
    UniqueConstraint("device_id", "interface_name", name="uq_interfaces_device_interface"),
)

# Device metrics table
device_metrics = Table(
    "device_metrics",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("device_id", Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
    Column("cpu_usage", Numeric(5, 2)),
    Column("memory_usage", Numeric(5, 2)),
    Column("uptime_seconds", BigInteger),
    Column("temperature_c", Numeric(5, 1)),
    Column("recorded_at", DateTime(timezone=True), server_default=text("NOW()")),
    Index("idx_device_metrics_recorded_at", "recorded_at"),
)

# Config changes table
config_changes = Table(
    "config_changes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("device_id", Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
    Column("changed_by", String(100), nullable=False),
    Column("change_type", String(50)),
    Column("summary", Text),
    Column("diff_hash", String(64)),
    Column("changed_at", DateTime(timezone=True), server_default=text("NOW()")),
    Index("idx_config_changes_changed_at", "changed_at"),
)

# Alerts table
alerts = Table(
    "alerts",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("device_id", Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False),
    Column(
        "severity",
        String(20),
        nullable=False,
    ),
    Column("alert_type", String(100)),
    Column("message", Text),
    Column("is_active", Boolean, server_default=text("TRUE")),
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
    Column("resolved_at", DateTime(timezone=True)),
    CheckConstraint(
        "severity IN ('critical','warning','info')",
        name="ck_alerts_severity",
    ),
    Index("idx_alerts_severity", "severity"),
    Index("idx_alerts_is_active", "is_active"),
)

# Audit log table
audit_log = Table(
    "audit_log",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", String(100), nullable=False),
    Column("user_question", Text, nullable=False),
    Column("parsed_intent", JSON),
    Column("sql_executed", Text),
    Column("row_count", Integer),
    Column("latency_ms", Integer),
    Column("error_message", Text),
    Column("created_at", DateTime(timezone=True), server_default=text("NOW()")),
    Index("idx_audit_log_user_id", "user_id"),
    Index("idx_audit_log_created_at", "created_at"),
)


def get_metadata():
    """Return the shared MetaData object containing all table definitions."""
    return metadata
