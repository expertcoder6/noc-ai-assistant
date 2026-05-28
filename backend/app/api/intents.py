from fastapi import APIRouter, Depends
from ..auth.middleware import get_current_user

router = APIRouter()

INTENTS_DATA = [
    {
        "name": "device_status",
        "description": "Check if devices (routers, switches, firewalls, etc.) are up or down.",
        "example_questions": [
            "Which routers are down?",
            "Is the dal-fw-01 firewall up?",
            "Show me degraded switches"
        ]
    },
    {
        "name": "device_inventory",
        "description": "List devices by type, vendor, or location.",
        "example_questions": [
            "List all switches in Dallas",
            "Show all Cisco devices",
            "What devices are in NYC?"
        ]
    },
    {
        "name": "interface_metrics",
        "description": "Monitor interface health, including packet loss, errors, and utilization.",
        "example_questions": [
            "Show interfaces with packet loss above 5%",
            "Are there any interfaces with errors?",
            "List highly utilized interfaces on lax-rtr-01"
        ]
    },
    {
        "name": "device_metrics",
        "description": "Check device CPU, memory usage, or temperature.",
        "example_questions": [
            "Show devices with CPU usage over 80%",
            "List switches with high memory utilization",
            "What is the temperature of routers in CHI01?"
        ]
    },
    {
        "name": "config_changes",
        "description": "Track configuration changes made to network devices.",
        "example_questions": [
            "Who changed configs today?",
            "Show recent config changes on dal-rtr-core-01",
            "What configuration changes happened in the last 24 hours?"
        ]
    },
    {
        "name": "active_alerts",
        "description": "List critical, warning, or informational alerts.",
        "example_questions": [
            "Show critical alerts",
            "Are there any warning alerts active?",
            "List all active alerts"
        ]
    },
    {
        "name": "alert_summary",
        "description": "Get a count of alerts grouped by severity.",
        "example_questions": [
            "Give me a summary of alerts",
            "What is the alert count by severity?"
        ]
    },
    {
        "name": "device_uptime",
        "description": "Check the uptime of network devices.",
        "example_questions": [
            "What is the uptime of dal-rtr-edge-01?",
            "Show device uptimes in Chicago",
            "List routers with low uptime"
        ]
    }
]

@router.get("/intents")
async def list_intents(current_user: dict = Depends(get_current_user)):
    """Return the catalog of intents that the assistant can understand."""
    return {"intents": INTENTS_DATA}

