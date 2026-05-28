"""SQL query builder for network AI assistant.

Takes a parsed intent (string) and a validated Pydantic filter model instance and
produces a concrete SQL string with placeholders and a parameters dictionary.
All operators for metric filters are safely substituted from a whitelist.
"""

from __future__ import annotations

from typing import Tuple, Dict, Any

from .sql_templates import (
    DEVICE_STATUS_SQL,
    DEVICE_INVENTORY_SQL,
    INTERFACE_METRICS_SQL,
    DEVICE_METRICS_SQL,
    CONFIG_CHANGES_SQL,
    ACTIVE_ALERTS_SQL,
    ALERT_SUMMARY_SQL,
    DEVICE_UPTIME_SQL,
)

# Allowed operator substitution mapping – never use raw user input in the SQL string.
ALLOWED_OPERATORS = {
    "gt": ">",
    "lt": "<",
    "eq": "=",
    "gte": ">=",
    "lte": "<=",
}

def _apply_optional_filter(sql: str, placeholder: str, value: Any) -> Tuple[str, Dict[str, Any]]:
    """Helper to add an optional ``AND column = :placeholder`` clause.

    Returns the possibly‑modified SQL string and a ``params`` dict containing the placeholder
    only if ``value`` is not ``None``.
    """
    if value is None:
        return sql, {}
    clause = f" AND {placeholder} = :{placeholder}"
    return sql.replace(f"{{{placeholder}_filter}}", clause), {placeholder: value}

def build_query(intent: str, filters: Any) -> Tuple[str, Dict[str, Any]]:
    """Build the final SQL string and its parameters for a given intent.

    Args:
        intent: The intent name (e.g. ``device_status``).
        filters: An instance of the validated Pydantic filter model for that intent.

    Returns:
        A tuple ``(sql, params)`` where ``sql`` is a string ready to be passed to
        ``session.execute(text(sql), params)`` and ``params`` is a dictionary of bound values.

    Raises:
        ValueError: If ``intent`` is not recognised.
    """
    # Start with empty parameter dict.
    params: Dict[str, Any] = {}

    if intent == "device_status":
        sql = DEVICE_STATUS_SQL
        sql, p = _apply_optional_filter(sql, "device_type", getattr(filters, "device_type", None))
        params.update(p)
        sql, p = _apply_optional_filter(sql, "status", getattr(filters, "status", None))
        params.update(p)
        sql, p = _apply_optional_filter(sql, "location_code", getattr(filters, "location_code", None))
        params.update(p)
        # Remove any leftover placeholders (when filter is None)
        sql = sql.replace("{device_type_filter}", "").replace("{status_filter}", "").replace("{location_filter}", "")
        return sql, params

    if intent == "device_inventory":
        sql = DEVICE_INVENTORY_SQL
        sql, p = _apply_optional_filter(sql, "device_type", getattr(filters, "device_type", None))
        params.update(p)
        sql, p = _apply_optional_filter(sql, "vendor", getattr(filters, "vendor", None))
        params.update(p)
        sql, p = _apply_optional_filter(sql, "location_code", getattr(filters, "location_code", None))
        params.update(p)
        sql = sql.replace("{device_type_filter}", "").replace("{vendor_filter}", "").replace("{location_filter}", "")
        return sql, params

    if intent == "interface_metrics":
        # Substitute the column name and operator directly – both are validated by Pydantic.
        metric_col = {
            "packet_loss": "packet_loss_pct",
            "errors": "error_count",
            "utilization": "utilization_pct",
        }[filters.metric]
        operator_sql = ALLOWED_OPERATORS[filters.operator]
        sql = INTERFACE_METRICS_SQL.replace("{metric_column}", metric_col).replace("{operator}", operator_sql)
        # Optional device hostname filter
        if filters.device_hostname:
            sql = sql.replace("{device_hostname_filter}", " AND d.hostname = :device_hostname")
            params["device_hostname"] = filters.device_hostname
        else:
            sql = sql.replace("{device_hostname_filter}", "")
        params["threshold"] = filters.threshold
        return sql, params

    if intent == "device_metrics":
        metric_col = {
            "cpu": "cpu_usage",
            "memory": "memory_usage",
            "temperature": "temperature_c",
        }[filters.metric]
        operator_sql = ALLOWED_OPERATORS[filters.operator]
        sql = DEVICE_METRICS_SQL.replace("{metric_column}", metric_col).replace("{operator}", operator_sql)
        # Optional location filter
        if filters.location_code:
            sql = sql.replace("{location_filter}", " AND l.site_code = :location_code")
            params["location_code"] = filters.location_code
        else:
            sql = sql.replace("{location_filter}", "")
        params["threshold"] = filters.threshold
        return sql, params

    if intent == "config_changes":
        sql = CONFIG_CHANGES_SQL
        params["changed_by"] = filters.changed_by
        params["since_hours"] = filters.since_hours if filters.since_hours is not None else 24
        params["device_hostname"] = filters.device_hostname
        return sql, params

    if intent == "active_alerts":
        sql = ACTIVE_ALERTS_SQL
        params["severity"] = filters.severity
        params["is_active"] = filters.is_active
        return sql, params

    if intent == "alert_summary":
        return ALERT_SUMMARY_SQL, {}

    if intent == "device_uptime":
        sql = DEVICE_UPTIME_SQL
        params["device_hostname"] = filters.device_hostname
        params["device_type"] = filters.device_type
        params["location_code"] = filters.location_code
        return sql, params


    if intent == "out_of_scope":
        # No DB access required for out_of_scope.
        return "", {}

    raise ValueError(f"Unsupported intent: {intent}")
