from typing import Set, Dict

# Map roles to their whitelisted intent permissions
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {
        "device_status",
        "device_inventory",
        "interface_metrics",
        "device_metrics",
        "config_changes",
        "active_alerts",
        "alert_summary",
        "device_uptime",
        "out_of_scope"
    },
    "network_engineer": {
        "device_status",
        "device_inventory",
        "interface_metrics",
        "device_metrics",
        "config_changes",
        "device_uptime",
        "alert_summary",
        "out_of_scope"
    },
    "security_team": {
        "device_status",
        "device_inventory", # firewall inventory
        "active_alerts",
        "alert_summary",
        "out_of_scope"
    },
    "network_operator": {
        "device_status",
        "device_inventory",
        "interface_metrics",
        "device_metrics",
        "config_changes",
        "active_alerts",
        "alert_summary",
        "device_uptime",
        "out_of_scope"
    }
}

def has_permission(role: str, intent_name: str) -> bool:
    """Check if the given role has permission to run the specified intent."""
    role_normalized = role.lower()
    if role_normalized not in ROLE_PERMISSIONS:
        return False
    return intent_name in ROLE_PERMISSIONS[role_normalized]
