"""Unit tests for intent validation and Pydantic filter models.

These tests are pure and require no LLM or database connection.
Run with: pytest backend/tests/test_intent_validation.py -v
"""
import pytest
from pydantic import ValidationError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.query.intent_validator import (
    ParsedIntent,
    DeviceStatusFilters,
    DeviceInventoryFilters,
    InterfaceMetricsFilters,
    DeviceMetricsFilters,
    ConfigChangesFilters,
    ActiveAlertsFilters,
    AlertSummaryFilters,
    DeviceUptimeFilters,
)


# ─── ParsedIntent: Unknown / Invalid Intent ────────────────────────────────────

class TestParsedIntentRejection:
    def test_rejects_unknown_intent(self):
        """An intent not in the whitelist must be rejected."""
        with pytest.raises((ValueError, ValidationError)):
            ParsedIntent(intent="hack_database", filters={})

    def test_rejects_drop_table_intent(self):
        with pytest.raises((ValueError, ValidationError)):
            ParsedIntent(intent="drop_table", filters={})

    def test_rejects_empty_intent(self):
        with pytest.raises((ValueError, ValidationError)):
            ParsedIntent(intent="", filters={})

    def test_accepts_all_valid_intents(self):
        valid_intents = [
            ("device_status", {}),
            ("device_inventory", {"device_type": "router"}),
            ("interface_metrics", {"metric": "packet_loss", "operator": "gt", "threshold": 5.0}),
            ("device_metrics", {"metric": "cpu", "operator": "gt", "threshold": 80.0}),
            ("config_changes", {}),
            ("active_alerts", {}),
            ("alert_summary", {}),
            ("device_uptime", {}),
            ("out_of_scope", {}),
        ]
        for intent_name, filters in valid_intents:
            p = ParsedIntent(intent=intent_name, filters=filters)
            assert p.intent == intent_name


# ─── DeviceStatusFilters ───────────────────────────────────────────────────────

class TestDeviceStatusFilters:
    def test_valid_full_filters(self):
        f = DeviceStatusFilters(device_type="router", status="down", location_code="DAL01")
        assert f.device_type == "router"
        assert f.status == "down"
        assert f.location_code == "DAL01"

    def test_all_none_is_valid(self):
        f = DeviceStatusFilters()
        assert f.device_type is None
        assert f.status is None

    def test_rejects_invalid_device_type(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            DeviceStatusFilters(device_type="mainframe")

    def test_rejects_invalid_status(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            DeviceStatusFilters(status="broken")

    def test_rejects_invalid_location_code(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            DeviceStatusFilters(location_code="LON01")

    def test_all_device_types_accepted(self):
        for dt in ["router", "switch", "firewall", "ap", "load_balancer"]:
            # pyrefly: ignore [bad-argument-type]
            f = DeviceStatusFilters(device_type=dt)
            assert f.device_type == dt

    def test_all_statuses_accepted(self):
        for s in ["up", "down", "degraded"]:
            # pyrefly: ignore [bad-argument-type]
            f = DeviceStatusFilters(status=s)
            assert f.status == s


# ─── DeviceInventoryFilters ────────────────────────────────────────────────────

class TestDeviceInventoryFilters:
    def test_valid_with_device_type(self):
        f = DeviceInventoryFilters(device_type="switch")
        assert f.device_type == "switch"

    def test_valid_with_vendor(self):
        f = DeviceInventoryFilters(vendor="Cisco")
        assert f.vendor == "Cisco"

    def test_valid_with_location_code_only(self):
        """location_code alone must be sufficient — doc example: 'List devices in Dallas'."""
        f = DeviceInventoryFilters(location_code="DAL01")
        assert f.location_code == "DAL01"

    def test_valid_with_all_filters(self):
        f = DeviceInventoryFilters(device_type="router", vendor="Cisco", location_code="NYC01")
        assert f.device_type == "router"

    def test_rejects_no_filters(self):
        """At least one filter must be provided."""
        with pytest.raises(ValidationError):
            DeviceInventoryFilters()

    def test_rejects_invalid_location(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            DeviceInventoryFilters(location_code="PARIS")


# ─── InterfaceMetricsFilters ───────────────────────────────────────────────────

class TestInterfaceMetricsFilters:
    def test_valid_packet_loss(self):
        f = InterfaceMetricsFilters(metric="packet_loss", operator="gt", threshold=5.0)
        assert f.metric == "packet_loss"
        assert f.operator == "gt"
        assert f.threshold == 5.0

    def test_valid_with_device_hostname(self):
        f = InterfaceMetricsFilters(metric="errors", operator="gt", threshold=100.0, device_hostname="dal-rtr-01")
        assert f.device_hostname == "dal-rtr-01"

    def test_rejects_invalid_metric(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            InterfaceMetricsFilters(metric="bandwidth", operator="gt", threshold=5.0)

    def test_rejects_invalid_operator(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            InterfaceMetricsFilters(metric="packet_loss", operator="greater_than", threshold=5.0)

    def test_rejects_threshold_above_100(self):
        with pytest.raises(ValidationError):
            InterfaceMetricsFilters(metric="packet_loss", operator="gt", threshold=101.0)

    def test_rejects_negative_threshold(self):
        with pytest.raises(ValidationError):
            InterfaceMetricsFilters(metric="packet_loss", operator="gt", threshold=-1.0)

    def test_all_operators_accepted(self):
        for op in ["gt", "lt", "eq", "gte", "lte"]:
            # pyrefly: ignore [bad-argument-type]
            f = InterfaceMetricsFilters(metric="utilization", operator=op, threshold=50.0)
            assert f.operator == op


# ─── DeviceMetricsFilters ──────────────────────────────────────────────────────

class TestDeviceMetricsFilters:
    def test_valid_cpu_above_80(self):
        f = DeviceMetricsFilters(metric="cpu", operator="gt", threshold=80.0)
        assert f.metric == "cpu"

    def test_valid_with_location(self):
        f = DeviceMetricsFilters(metric="memory", operator="gt", threshold=70.0, location_code="CHI01")
        assert f.location_code == "CHI01"

    def test_rejects_invalid_metric(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            DeviceMetricsFilters(metric="disk", operator="gt", threshold=80.0)

    def test_all_metrics_accepted(self):
        for m in ["cpu", "memory", "temperature"]:
            # pyrefly: ignore [bad-argument-type]
            f = DeviceMetricsFilters(metric=m, operator="gt", threshold=50.0)
            assert f.metric == m


# ─── ConfigChangesFilters ──────────────────────────────────────────────────────

class TestConfigChangesFilters:
    def test_defaults(self):
        f = ConfigChangesFilters()
        assert f.since_hours == 24
        assert f.changed_by is None
        assert f.device_hostname is None

    def test_valid_full_filters(self):
        f = ConfigChangesFilters(changed_by="jsmith", since_hours=48, device_hostname="dal-rtr-01")
        assert f.changed_by == "jsmith"
        assert f.since_hours == 48

    def test_rejects_since_hours_over_168(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            ConfigChangesFilters(since_hours=200)

    def test_rejects_zero_since_hours(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            ConfigChangesFilters(since_hours=0)


# ─── ActiveAlertsFilters ───────────────────────────────────────────────────────

class TestActiveAlertsFilters:
    def test_defaults(self):
        f = ActiveAlertsFilters()
        assert f.is_active is True
        assert f.severity is None

    def test_valid_critical(self):
        f = ActiveAlertsFilters(severity="critical")
        assert f.severity == "critical"

    def test_rejects_invalid_severity(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            ActiveAlertsFilters(severity="catastrophic")

    def test_all_severities_accepted(self):
        for s in ["critical", "warning", "info"]:
            # pyrefly: ignore [bad-argument-type]
            f = ActiveAlertsFilters(severity=s)
            assert f.severity == s


# ─── DeviceUptimeFilters ───────────────────────────────────────────────────────

class TestDeviceUptimeFilters:
    def test_all_optional(self):
        f = DeviceUptimeFilters()
        assert f.device_hostname is None
        assert f.device_type is None
        assert f.location_code is None

    def test_with_hostname(self):
        f = DeviceUptimeFilters(device_hostname="dal-rtr-core-01")
        assert f.device_hostname == "dal-rtr-core-01"

    def test_rejects_invalid_device_type(self):
        with pytest.raises(ValidationError):
            # pyrefly: ignore [bad-argument-type]
            DeviceUptimeFilters(device_type="server")
