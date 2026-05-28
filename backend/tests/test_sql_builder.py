"""Unit tests for the SQL query builder.

These tests verify that build_query() produces correctly parameterized SQL
for each intent. No database or LLM connection is required.
Run with: pytest backend/tests/test_sql_builder.py -v
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.query.sql_builder import build_query, ALLOWED_OPERATORS
from app.query.intent_validator import (
    DeviceStatusFilters,
    DeviceInventoryFilters,
    InterfaceMetricsFilters,
    DeviceMetricsFilters,
    ConfigChangesFilters,
    ActiveAlertsFilters,
    AlertSummaryFilters,
    DeviceUptimeFilters,
    OutOfScopeFilters,
)


# ─── device_status ─────────────────────────────────────────────────────────────

class TestDeviceStatusSQL:
    def test_builds_parameterized_sql(self):
        """Core doc requirement: SQL must use :param style, never string concat."""
        f = DeviceStatusFilters(device_type="router", status="down")
        sql, params = build_query("device_status", f)
        assert ":device_type" in sql
        assert ":status" in sql
        assert params["device_type"] == "router"
        assert params["status"] == "down"

    def test_no_sql_injection_in_params(self):
        """Parameter values must be bound, not interpolated into the SQL string."""
        f = DeviceStatusFilters(device_type="router", status="down")
        sql, params = build_query("device_status", f)
        assert "router" not in sql   # value must be in params dict, not the SQL string
        assert "down" not in sql

    def test_no_filters_returns_valid_sql(self):
        f = DeviceStatusFilters()
        sql, params = build_query("device_status", f)
        assert "SELECT" in sql
        assert "devices" in sql
        assert params == {}

    def test_with_location_code(self):
        f = DeviceStatusFilters(location_code="DAL01")
        sql, params = build_query("device_status", f)
        # location_code is applied via optional filter clause
        assert "location_code" in params or "DAL01" in str(params)

    def test_no_leftover_placeholders(self):
        """Unfilled template placeholders like {device_type_filter} must be cleaned up."""
        f = DeviceStatusFilters()
        sql, params = build_query("device_status", f)
        assert "{" not in sql
        assert "}" not in sql

    def test_query_includes_join_to_locations(self):
        f = DeviceStatusFilters()
        sql, _ = build_query("device_status", f)
        assert "locations" in sql.lower() or "LEFT JOIN" in sql


# ─── device_inventory ──────────────────────────────────────────────────────────

class TestDeviceInventorySQL:
    def test_builds_with_device_type(self):
        f = DeviceInventoryFilters(device_type="switch")
        sql, params = build_query("device_inventory", f)
        assert ":device_type" in sql
        assert params["device_type"] == "switch"

    def test_builds_with_vendor(self):
        f = DeviceInventoryFilters(vendor="Cisco")
        sql, params = build_query("device_inventory", f)
        assert ":vendor" in sql
        assert params["vendor"] == "Cisco"

    def test_builds_with_location_only(self):
        f = DeviceInventoryFilters(location_code="NYC01")
        sql, params = build_query("device_inventory", f)
        assert "NYC01" in str(params)

    def test_no_leftover_placeholders(self):
        f = DeviceInventoryFilters(vendor="Juniper")
        sql, _ = build_query("device_inventory", f)
        assert "{" not in sql


# ─── interface_metrics ─────────────────────────────────────────────────────────

class TestInterfaceMetricsSQL:
    def test_packet_loss_gt(self):
        f = InterfaceMetricsFilters(metric="packet_loss", operator="gt", threshold=5.0)
        sql, params = build_query("interface_metrics", f)
        assert "packet_loss_pct" in sql
        assert ">" in sql
        assert ":threshold" in sql
        assert params["threshold"] == 5.0

    def test_errors_lt(self):
        f = InterfaceMetricsFilters(metric="errors", operator="lt", threshold=50.0)
        sql, params = build_query("interface_metrics", f)
        assert "error_count" in sql
        assert "<" in sql

    def test_utilization_gte(self):
        f = InterfaceMetricsFilters(metric="utilization", operator="gte", threshold=80.0)
        sql, params = build_query("interface_metrics", f)
        assert "utilization_pct" in sql
        assert ">=" in sql

    def test_operator_is_whitelisted_symbol(self):
        """Operators must be substituted from whitelist — never raw user input."""
        f = InterfaceMetricsFilters(metric="packet_loss", operator="gt", threshold=5.0)
        sql, _ = build_query("interface_metrics", f)
        # The string "gt" must not appear in the SQL — only its symbol ">"
        assert " gt " not in sql.lower()
        assert ">" in sql

    def test_with_device_hostname_filter(self):
        f = InterfaceMetricsFilters(metric="utilization", operator="gt", threshold=80.0, device_hostname="dal-rtr-01")
        sql, params = build_query("interface_metrics", f)
        assert ":device_hostname" in sql
        assert params["device_hostname"] == "dal-rtr-01"

    def test_without_hostname_no_leftover_placeholder(self):
        f = InterfaceMetricsFilters(metric="utilization", operator="gt", threshold=80.0)
        sql, params = build_query("interface_metrics", f)
        assert "{device_hostname_filter}" not in sql
        assert "device_hostname" not in params


# ─── device_metrics ────────────────────────────────────────────────────────────

class TestDeviceMetricsSQL:
    def test_cpu_gt_80(self):
        f = DeviceMetricsFilters(metric="cpu", operator="gt", threshold=80.0)
        sql, params = build_query("device_metrics", f)
        assert "cpu_usage" in sql
        assert ">" in sql
        assert params["threshold"] == 80.0

    def test_memory_lte(self):
        f = DeviceMetricsFilters(metric="memory", operator="lte", threshold=90.0)
        sql, params = build_query("device_metrics", f)
        assert "memory_usage" in sql
        assert "<=" in sql

    def test_temperature_metric(self):
        f = DeviceMetricsFilters(metric="temperature", operator="gt", threshold=60.0)
        sql, _ = build_query("device_metrics", f)
        assert "temperature_c" in sql

    def test_with_location_filter(self):
        f = DeviceMetricsFilters(metric="cpu", operator="gt", threshold=80.0, location_code="CHI01")
        sql, params = build_query("device_metrics", f)
        assert "location_code" in params
        assert params["location_code"] == "CHI01"


# ─── config_changes ────────────────────────────────────────────────────────────

class TestConfigChangesSQL:
    def test_returns_valid_sql(self):
        f = ConfigChangesFilters()
        sql, params = build_query("config_changes", f)
        assert "SELECT" in sql
        assert "config_changes" in sql

    def test_default_since_hours_is_24(self):
        f = ConfigChangesFilters()
        _, params = build_query("config_changes", f)
        assert params["since_hours"] == 24

    def test_custom_since_hours(self):
        f = ConfigChangesFilters(since_hours=48)
        _, params = build_query("config_changes", f)
        assert params["since_hours"] == 48

    def test_changed_by_param_bound(self):
        f = ConfigChangesFilters(changed_by="jsmith")
        _, params = build_query("config_changes", f)
        assert params["changed_by"] == "jsmith"


# ─── active_alerts ─────────────────────────────────────────────────────────────

class TestActiveAlertsSQL:
    def test_critical_alerts(self):
        f = ActiveAlertsFilters(severity="critical", is_active=True)
        sql, params = build_query("active_alerts", f)
        assert "SELECT" in sql
        assert params["severity"] == "critical"
        assert params["is_active"] is True

    def test_is_active_defaults_true(self):
        f = ActiveAlertsFilters()
        _, params = build_query("active_alerts", f)
        assert params["is_active"] is True


# ─── alert_summary ─────────────────────────────────────────────────────────────

class TestAlertSummarySQL:
    def test_returns_groupby_query(self):
        sql, params = build_query("alert_summary", AlertSummaryFilters())
        assert "GROUP BY" in sql.upper()
        assert params == {}

    def test_has_severity_column(self):
        sql, _ = build_query("alert_summary", AlertSummaryFilters())
        assert "severity" in sql


# ─── device_uptime ─────────────────────────────────────────────────────────────

class TestDeviceUptimeSQL:
    def test_returns_valid_sql(self):
        f = DeviceUptimeFilters()
        sql, params = build_query("device_uptime", f)
        assert "SELECT" in sql
        assert "uptime_seconds" in sql

    def test_with_hostname(self):
        f = DeviceUptimeFilters(device_hostname="dal-rtr-core-01")
        _, params = build_query("device_uptime", f)
        assert params["device_hostname"] == "dal-rtr-core-01"

    def test_null_params_are_none(self):
        f = DeviceUptimeFilters()
        _, params = build_query("device_uptime", f)
        assert params["device_hostname"] is None
        assert params["device_type"] is None
        assert params["location_code"] is None


# ─── out_of_scope ──────────────────────────────────────────────────────────────

class TestOutOfScopeSQL:
    def test_returns_empty_sql_and_params(self):
        sql, params = build_query("out_of_scope", OutOfScopeFilters())
        assert sql == ""
        assert params == {}


# ─── Unknown intent ────────────────────────────────────────────────────────────

class TestUnknownIntent:
    def test_raises_value_error(self):
        with pytest.raises(ValueError):
            build_query("steal_data", DeviceStatusFilters())


# ─── ALLOWED_OPERATORS whitelist ───────────────────────────────────────────────

class TestAllowedOperators:
    def test_all_operators_map_to_sql_symbols(self):
        expected = {"gt": ">", "lt": "<", "eq": "=", "gte": ">=", "lte": "<="}
        assert ALLOWED_OPERATORS == expected
