# 🗄️ Database Schema & Security Controls

This document details the database schema (7 tables), the raw DDL schema creation commands, relational fields, indices, and the dual-role security architecture.

---

## 🏗️ Schema Overview & Relationships

The database is built on **PostgreSQL 16** and uses a relational layout optimizing device metrics and telemetry checks:

```
  [locations]
       ▲
       │ (1-to-many)
  [devices] ◄───── (1-to-many) ─────┐
       ▲                            │
       ├───── (1-to-many) ─────┐    ├───── (1-to-many) ─────┐
       │                       │    │                       │
 [interfaces]          [device_metrics] [config_changes]    [alerts]
```

---

## 📝 Raw DDL Schema Creation SQL

```sql
-- 1. Locations Table
CREATE TABLE locations (
    id          SERIAL PRIMARY KEY,
    site_name   VARCHAR(100) NOT NULL,
    site_code   VARCHAR(20) UNIQUE NOT NULL,
    address     TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Devices Table (Asset tracking)
CREATE TABLE devices (
    id            SERIAL PRIMARY KEY,
    hostname      VARCHAR(255) UNIQUE NOT NULL,
    ip_address    INET NOT NULL,
    device_type   VARCHAR(50) NOT NULL DEFAULT 'router',
    vendor        VARCHAR(100),
    model         VARCHAR(100),
    os_version    VARCHAR(100),
    serial_number VARCHAR(100),
    location_id   INTEGER REFERENCES locations(id),
    status        VARCHAR(20) NOT NULL DEFAULT 'unknown',
    last_seen     TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT ck_devices_device_type CHECK (device_type IN ('router', 'switch', 'firewall', 'ap', 'load_balancer')),
    CONSTRAINT ck_devices_status CHECK (status IN ('up', 'down', 'degraded', 'unknown'))
);
CREATE INDEX idx_devices_device_type ON devices(device_type);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_location_id ON devices(location_id);

-- 3. Interfaces Table (Port metrics)
CREATE TABLE interfaces (
    id              SERIAL PRIMARY KEY,
    device_id       INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    interface_name  VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'down',
    speed_mbps      INTEGER,
    description     TEXT,
    ip_address      INET,
    packet_loss_pct NUMERIC(5,2) DEFAULT 0,
    error_count     INTEGER DEFAULT 0,
    utilization_pct NUMERIC(5,2) DEFAULT 0,
    last_updated    TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_interfaces_device_interface UNIQUE(device_id, interface_name)
);

-- 4. Device Metrics Table (CPU/Memory/Temperature Snapshots)
CREATE TABLE device_metrics (
    id             SERIAL PRIMARY KEY,
    device_id      INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    cpu_usage      NUMERIC(5,2),
    memory_usage   NUMERIC(5,2),
    uptime_seconds BIGINT,
    temperature_c  NUMERIC(5,1),
    recorded_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_device_metrics_recorded_at ON device_metrics(recorded_at);

-- 5. Config Changes Table (Change audit logs)
CREATE TABLE config_changes (
    id          SERIAL PRIMARY KEY,
    device_id   INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    changed_by  VARCHAR(100) NOT NULL,
    change_type VARCHAR(50),
    summary     TEXT,
    diff_hash   VARCHAR(64),
    changed_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_config_changes_changed_at ON config_changes(changed_at);

-- 6. Alerts Table (System alarms)
CREATE TABLE alerts (
    id          SERIAL PRIMARY KEY,
    device_id   INTEGER REFERENCES devices(id) ON DELETE CASCADE,
    severity    VARCHAR(20) NOT NULL,
    alert_type  VARCHAR(100),
    message     TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    CONSTRAINT ck_alerts_severity CHECK (severity IN ('critical', 'warning', 'info'))
);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_is_active ON alerts(is_active);

-- 7. Audit Log Table (NOC Activity audits)
CREATE TABLE audit_log (
    id            SERIAL PRIMARY KEY,
    user_id       VARCHAR(100) NOT NULL,
    user_question TEXT NOT NULL,
    parsed_intent JSONB,
    sql_executed  TEXT,
    row_count     INTEGER,
    latency_ms    INTEGER,
    error_message TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
```

---

## 🔒 Relational Constraints & Database Security

Enterprise database hardening is enforced through strict role isolation inside PostgreSQL:

### 1. Dual PostgreSQL Credentials Roles
The application connects to the database via two separate connection pools to prevent write escalation:
* **Read-Only Telemetry Role:**
  * Authorized exclusively for `SELECT` queries on the data tables (`locations`, `devices`, `interfaces`, `device_metrics`, `config_changes`, `alerts`).
  * Denied permissions for `INSERT`, `UPDATE`, `DELETE`, or `DDL` execution.
* **Audit-Write Role:**
  * Authorized strictly for `INSERT` queries on the `audit_log` table.
  * Denied select/update/delete capabilities on all other tables.
  * Prevents SQL injections from tampering with historical telemetry records.

### 2. Operational Indices
Indices are built on all primary foreign key and filter targets to guarantee sub-millisecond lookups:
* `idx_devices_device_type` and `idx_devices_status` optimize inventory search bounds.
* `idx_alerts_severity` and `idx_alerts_is_active` speed up the welcome screen checks.
* `idx_device_metrics_recorded_at` facilitates immediate retrieval of the most recent device telemetry snapshots.
