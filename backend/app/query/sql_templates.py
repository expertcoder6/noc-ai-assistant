# SQL template strings for the various intents.
# All placeholders use SQLAlchemy text style (:param_name).
# Operators for metrics are substituted in the builder, not parametrized.

DEVICE_STATUS_SQL = """
SELECT d.hostname, d.ip_address, d.device_type, d.status, d.last_seen,
       d.vendor, l.site_name AS location
FROM devices d
LEFT JOIN locations l ON d.location_id = l.id
WHERE 1=1
{device_type_filter}
{status_filter}
{location_filter}
ORDER BY d.status, d.hostname
LIMIT 100
"""

DEVICE_INVENTORY_SQL = """
SELECT d.hostname, d.ip_address, d.device_type, d.vendor, d.model, d.os_version,
       l.site_name AS location
FROM devices d
LEFT JOIN locations l ON d.location_id = l.id
WHERE 1=1
{device_type_filter}
{vendor_filter}
{location_filter}
ORDER BY d.hostname
LIMIT 100
"""

INTERFACE_METRICS_SQL = """
SELECT i.interface_name, d.hostname AS device_hostname, i.{metric_column} AS metric_value,
       i.status
FROM interfaces i
JOIN devices d ON i.device_id = d.id
WHERE i.{metric_column} {operator} :threshold
{device_hostname_filter}
ORDER BY metric_value DESC
LIMIT 100
"""

DEVICE_METRICS_SQL = """
WITH latest AS (
    SELECT DISTINCT ON (device_id) *
    FROM device_metrics
    ORDER BY device_id, recorded_at DESC
)
SELECT d.hostname, d.device_type, l.site_name AS location,
       latest.{metric_column} AS metric_value,
       latest.recorded_at
FROM latest
JOIN devices d ON latest.device_id = d.id
LEFT JOIN locations l ON d.location_id = l.id
WHERE latest.{metric_column} {operator} :threshold
{location_filter}
ORDER BY metric_value DESC
LIMIT 100
"""

CONFIG_CHANGES_SQL = """
SELECT c.changed_at, d.hostname AS device_hostname, c.changed_by, c.change_type, c.summary
FROM config_changes c
JOIN devices d ON c.device_id = d.id
WHERE (CAST(:changed_by AS VARCHAR) IS NULL OR c.changed_by = :changed_by)
  AND c.changed_at > NOW() - (CAST(:since_hours AS integer) * INTERVAL '1 hour')
  AND (CAST(:device_hostname AS VARCHAR) IS NULL OR d.hostname = :device_hostname)
ORDER BY c.changed_at DESC
LIMIT 50
"""

ACTIVE_ALERTS_SQL = """
SELECT a.severity, a.is_active, a.alert_type, a.message, d.hostname AS device_hostname,
       a.created_at
FROM alerts a
JOIN devices d ON a.device_id = d.id
WHERE (CAST(:severity AS VARCHAR) IS NULL OR a.severity = :severity)
  AND a.is_active = :is_active
ORDER BY a.created_at DESC
LIMIT 100
"""

ALERT_SUMMARY_SQL = """
SELECT severity,
       COUNT(*) AS count,
       SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS active_count
FROM alerts
GROUP BY severity
ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END
"""

DEVICE_UPTIME_SQL = """
WITH latest AS (
    SELECT DISTINCT ON (device_id) *
    FROM device_metrics
    ORDER BY device_id, recorded_at DESC
)
SELECT d.hostname, d.device_type, l.site_name AS location,
       latest.uptime_seconds,
       (latest.uptime_seconds/86400)::int AS uptime_days,
       latest.cpu_usage, latest.memory_usage, latest.recorded_at
FROM latest
JOIN devices d ON latest.device_id = d.id
LEFT JOIN locations l ON d.location_id = l.id
WHERE (CAST(:device_hostname AS VARCHAR) IS NULL OR d.hostname = :device_hostname)
  AND (CAST(:device_type AS VARCHAR) IS NULL OR d.device_type = :device_type)
  AND (CAST(:location_code AS VARCHAR) IS NULL OR l.site_code = :location_code)
ORDER BY latest.recorded_at DESC
LIMIT 100
"""

