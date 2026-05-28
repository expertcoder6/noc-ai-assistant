from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Literal, Dict

# Filter models
class DeviceStatusFilters(BaseModel):
    device_type: Literal['router', 'switch', 'firewall', 'ap', 'load_balancer'] | None = None
    status: Literal['up', 'down', 'degraded'] | None = None
    location_code: Literal['DAL01', 'NYC01', 'CHI01', 'LAX01'] | None = None

class DeviceInventoryFilters(BaseModel):
    device_type: Literal['router', 'switch', 'firewall', 'ap', 'load_balancer'] | None = None
    vendor: str | None = None
    location_code: Literal['DAL01', 'NYC01', 'CHI01', 'LAX01'] | None = None

    @model_validator(mode='after')
    def check_at_least_one(cls, values):
        if not values.device_type and not values.vendor and not values.location_code:
            raise ValueError('At least one of device_type, vendor, or location_code must be provided')
        return values

class InterfaceMetricsFilters(BaseModel):
    metric: Literal['packet_loss', 'errors', 'utilization']
    operator: Literal['gt', 'lt', 'eq', 'gte', 'lte']
    threshold: float = Field(ge=0, le=100)
    device_hostname: str | None = None

class DeviceMetricsFilters(BaseModel):
    metric: Literal['cpu', 'memory', 'temperature']
    operator: Literal['gt', 'lt', 'eq', 'gte', 'lte']
    threshold: float = Field(ge=0, le=100)
    location_code: Literal['DAL01', 'NYC01', 'CHI01', 'LAX01'] | None = None

class ConfigChangesFilters(BaseModel):
    changed_by: str | None = None
    since_hours: int | None = Field(default=24, ge=1, le=168)
    device_hostname: str | None = None

class ActiveAlertsFilters(BaseModel):
    severity: Literal['critical', 'warning', 'info'] | None = None
    is_active: bool = True

class AlertSummaryFilters(BaseModel):
    pass

class DeviceUptimeFilters(BaseModel):
    device_hostname: str | None = None
    device_type: Literal['router', 'switch', 'firewall', 'ap', 'load_balancer'] | None = None
    location_code: Literal['DAL01', 'NYC01', 'CHI01', 'LAX01'] | None = None

class OutOfScopeFilters(BaseModel):
    pass

INTENT_TO_FILTER_MODEL = {
    "device_status": DeviceStatusFilters,
    "device_inventory": DeviceInventoryFilters,
    "interface_metrics": InterfaceMetricsFilters,
    "device_metrics": DeviceMetricsFilters,
    "config_changes": ConfigChangesFilters,
    "active_alerts": ActiveAlertsFilters,
    "alert_summary": AlertSummaryFilters,
    "device_uptime": DeviceUptimeFilters,
    "out_of_scope": OutOfScopeFilters,
}

class ParsedIntent(BaseModel):
    intent: str
    filters: Dict
    response_hint: Literal['list', 'summary', 'single'] = 'list'
    validated_filters: dict | None = None

    @model_validator(mode='after')
    def validate_intent_and_filters(cls, values):
        intent = values.intent
        if intent not in INTENT_TO_FILTER_MODEL:
            raise ValueError(f"Unknown intent: {intent}")
        filter_model = INTENT_TO_FILTER_MODEL[intent]
        # this will raise ValidationError if filters are invalid
        values.validated_filters = filter_model(**values.filters)
        return values
