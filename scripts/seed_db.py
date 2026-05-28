#!/usr/bin/env python3
"""Standalone database seeder script.

Run from the project root:
    python scripts/seed_db.py

This seeds the PostgreSQL database with mock network data:
- 4 locations (DAL01, NYC01, CHI01, LAX01)
- ~50 devices (routers, switches, firewalls, APs, load balancers)
- ~200+ interfaces with port metrics
- Device CPU/memory/uptime snapshots
- Config change audit records
- Active and resolved alerts
"""
import sys
import os
import asyncio

# Add project root to path so backend modules are importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from backend.app.db.seed import seed_database

if __name__ == "__main__":
    print("🌱 Starting database seed...")
    asyncio.run(seed_database())
    print("✅ Database seeded successfully.")
