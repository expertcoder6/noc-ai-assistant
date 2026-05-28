import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .session import AsyncSessionLocal, engine
from .models import (
    locations,
    devices,
    interfaces,
    device_metrics,
    alerts,
    config_changes,
    audit_log,
    metadata,
)

# Helper constants
LOCATIONS_DATA = [
    {"site_name": "Dallas Office", "site_code": "DAL01", "address": "Dallas, TX"},
    {"site_name": "New York DC", "site_code": "NYC01", "address": "New York, NY"},
    {"site_name": "Chicago Hub", "site_code": "CHI01", "address": "Chicago, IL"},
    {"site_name": "LA Office", "site_code": "LAX01", "address": "Los Angeles, CA"},
]

DEVICE_TEMPLATES = {
    "router": [
        "dal-rtr-core-01",
        "dal-rtr-edge-01",
        "nyc-rtr-core-01",
        "nyc-rtr-edge-01",
        "chi-rtr-01",
        "chi-rtr-02",
        "lax-rtr-01",
        "lax-rtr-02",
    ],
    "switch": [
        # 5 per location, naming pattern will be generated later
    ],
    "firewall": ["dal-fw-01", "dal-fw-02", "nyc-fw-01", "nyc-fw-02", "chi-fw-01", "chi-fw-02", "lax-fw-01", "lax-fw-02"],
    "ap": [
        "dal-ap-floor1-01",
        "dal-ap-floor2-01",
        "nyc-ap-floor1-01",
        "nyc-ap-floor2-01",
        "chi-ap-floor1-01",
        "chi-ap-floor2-01",
        "lax-ap-floor1-01",
        "lax-ap-floor2-01",
        "dal-ap-floor3-01",
        "lax-ap-02",
    ],
    "load_balancer": ["dal-lb-01", "nyc-lb-01", "chi-lb-01", "lax-lb-01"],
}

STATUS_DISTRIBUTION = {
    "up": 40,
    "down": 6,
    "degraded": 4,
}

# Map specific device hostnames to forced statuses
FORCED_DEVICE_STATUS = {
    "dal-rtr-edge-01": "down",
    "nyc-rtr-edge-01": "down",
    "chi-sw-access-03": "down",
    "lax-fw-01": "down",
    "dal-sw-dist-02": "degraded",
    "nyc-sw-dist-01": "degraded",
}

INTERFACE_TYPES = ["GigabitEthernet0/0", "GigabitEthernet0/1", "Management0", "Loopback0"]

async def clear_tables(session: AsyncSession):
    # Delete in reverse FK order
    for table in [alerts, config_changes, device_metrics, interfaces, devices, locations]:
        await session.execute(delete(table))
    await session.commit()

async def seed_locations(session: AsyncSession):
    await session.execute(insert(locations), LOCATIONS_DATA)
    await session.commit()
    # Retrieve generated IDs
    result = await session.execute(select(locations.c.id, locations.c.site_code))
    return {row.site_code: row.id for row in result.fetchall()}

async def seed_devices(session: AsyncSession, location_ids: dict):
    device_rows = []
    # Routers
    for hostname in DEVICE_TEMPLATES["router"]:
        loc_code = hostname.split("-")[0].upper() + "01"  # e.g., DAL -> DAL01
        location_id = location_ids.get(loc_code)
        device_rows.append({
            "hostname": hostname,
            "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "device_type": "router",
            "location_id": location_id,
            "status": FORCED_DEVICE_STATUS.get(hostname, "up"),
            "last_seen": datetime.now(timezone.utc) if FORCED_DEVICE_STATUS.get(hostname, "up") == "up" else datetime.now(timezone.utc) - timedelta(hours=random.randint(1,4)),
        })
    # Switches: 5 per location
    for loc_code in ["DAL", "NYC", "CHI", "LAX"]:
        site_code = loc_code + "01"
        for i in range(1, 6):
            hostname = f"{loc_code.lower()}-sw-dist-{i:02d}"
            device_rows.append({
                "hostname": hostname,
                "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                "device_type": "switch",
                "location_id": location_ids[site_code],
                "status": FORCED_DEVICE_STATUS.get(hostname, "up"),
                "last_seen": datetime.now(timezone.utc) if FORCED_DEVICE_STATUS.get(hostname, "up") == "up" else datetime.now(timezone.utc) - timedelta(hours=random.randint(1,4)),
            })
    # Firewalls
    for hostname in DEVICE_TEMPLATES["firewall"]:
        loc_code = hostname.split("-")[0].upper() + "01"
        device_rows.append({
            "hostname": hostname,
            "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "device_type": "firewall",
            "location_id": location_ids.get(loc_code),
            "status": FORCED_DEVICE_STATUS.get(hostname, "up"),
            "last_seen": datetime.now(timezone.utc) if FORCED_DEVICE_STATUS.get(hostname, "up") == "up" else datetime.now(timezone.utc) - timedelta(hours=random.randint(1,4)),
        })
    # Access Points
    for hostname in DEVICE_TEMPLATES["ap"]:
        loc_code = hostname.split("-")[0].upper() + "01"
        device_rows.append({
            "hostname": hostname,
            "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "device_type": "ap",
            "location_id": location_ids.get(loc_code),
            "status": "up",
            "last_seen": datetime.now(timezone.utc),
        })
    # Load balancers
    for hostname in DEVICE_TEMPLATES["load_balancer"]:
        loc_code = hostname.split("-")[0].upper() + "01"
        device_rows.append({
            "hostname": hostname,
            "ip_address": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
            "device_type": "load_balancer",
            "location_id": location_ids.get(loc_code),
            "status": "up",
            "last_seen": datetime.now(timezone.utc),
        })
    await session.execute(insert(devices), device_rows)
    await session.commit()
    # Return mapping hostname -> id
    result = await session.execute(select(devices.c.id, devices.c.hostname))
    return {row.hostname: row.id for row in result.fetchall()}

async def seed_interfaces(session: AsyncSession, device_id_map: dict):
    interface_rows = []
    for hostname, dev_id in device_id_map.items():
        iface_count = random.randint(2, len(INTERFACE_TYPES))
        selected_ifaces = random.sample(INTERFACE_TYPES, iface_count)
        for iface_name in selected_ifaces:
            status = "down" if random.random() < 0.1 else "up"
            packet_loss = 0
            if random.random() < 0.05:
                packet_loss = round(random.uniform(3, 15), 2)
            utilization = round(random.uniform(5, 95), 2)
            interface_rows.append({
                "device_id": dev_id,
                "interface_name": iface_name,
                "status": status,
                "speed_mbps": random.choice([100, 1000, 10000]),
                "description": f"{iface_name} on {hostname}",
                "ip_address": f"192.168.{random.randint(0,255)}.{random.randint(1,254)}",
                "packet_loss_pct": packet_loss,
                "error_count": random.randint(0, 10),
                "utilization_pct": utilization,
                "last_updated": datetime.now(timezone.utc),
            })
    await session.execute(insert(interfaces), interface_rows)
    await session.commit()

async def seed_device_metrics(session: AsyncSession, device_id_map: dict):
    metrics_rows = []
    for hostname, dev_id in device_id_map.items():
        # Determine if device is up/down for uptime logic
        dev_status = None
        # fetch status quickly
        result = await session.execute(select(devices.c.status).where(devices.c.id == dev_id))
        dev_status = result.scalar_one()
        uptime = 0
        if dev_status == "up":
            days = random.randint(1, 365)
            uptime = days * 24 * 3600
        metrics_rows.append({
            "device_id": dev_id,
            "cpu_usage": round(random.uniform(5, 95), 2),
            "memory_usage": round(random.uniform(20, 90), 2),
            "uptime_seconds": uptime,
            "temperature_c": round(random.uniform(30, 80), 1),
            "recorded_at": datetime.now(timezone.utc),
        })
    await session.execute(insert(device_metrics), metrics_rows)
    await session.commit()

async def seed_alerts(session: AsyncSession, device_id_map: dict):
    alerts_rows = []
    # Generate 25 alerts with distribution
    severities = ["critical"] * 8 + ["warning"] * 12 + ["info"] * 5
    random.shuffle(severities)
    device_ids = list(device_id_map.values())
    for i, severity in enumerate(severities, 1):
        dev_id = random.choice(device_ids)
        is_active = True if i <= 20 else False
        alerts_rows.append({
            "device_id": dev_id,
            "severity": severity,
            "alert_type": f"{severity}_test_{i}",
            "message": f"Generated {severity} alert #{i}",
            "is_active": is_active,
            "created_at": datetime.now(timezone.utc),
            "resolved_at": None if is_active else datetime.now(timezone.utc) - timedelta(days=random.randint(1, 5)),
        })
    await session.execute(insert(alerts), alerts_rows)
    await session.commit()

async def seed_config_changes(session: AsyncSession, device_id_map: dict):
    users = ["jsmith", "mjohnson", "arogers", "bwilliams"]
    types = ["acl_update", "routing_change", "vlan_config", "interface_update"]
    changes = []
    for _ in range(15):
        dev_id = random.choice(list(device_id_map.values()))
        changed_by = random.choice(users)
        change_type = random.choice(types)
        changes.append({
            "device_id": dev_id,
            "changed_by": changed_by,
            "change_type": change_type,
            "summary": f"{change_type} performed by {changed_by}",
            "diff_hash": f"{random.getrandbits(256):064x}",
            "changed_at": datetime.now(timezone.utc) - timedelta(days=random.randint(0, 6)),
        })
    await session.execute(insert(config_changes), changes)
    await session.commit()

async def main():
    async with AsyncSessionLocal() as session:
        await clear_tables(session)
        location_ids = await seed_locations(session)
        device_id_map = await seed_devices(session, location_ids)
        await seed_interfaces(session, device_id_map)
        await seed_device_metrics(session, device_id_map)
        await seed_alerts(session, device_id_map)
        await seed_config_changes(session, device_id_map)
        # audit_log left empty on purpose

if __name__ == "__main__":
    asyncio.run(main())
