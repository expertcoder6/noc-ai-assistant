# 📋 Network AI Assistant - Implementation Plan

This document details the original and completed implementation design for the Network Operations Center (NOC) AI Operations Assistant.

---

## 🛠️ Goals & Vision

### What We Are Building
An internal chat interface designed specifically for network operations teams. Instead of logging into monitoring tools, querying complex databases, or raising helpdesk tickets, users can type natural language questions (e.g., *"Which routers are down?"* or *"Who changed configuration today?"*) and receive clean, human-readable answers compiled from real-time database schemas.

### Why We Are Building It
Traditional troubleshooting is slow and relies on tribal knowledge or manual dashboard-diving:
1. **Slow Triage:** NOC operators must manually check separate device and port metrics dashboards.
2. **Access Barriers:** Queries require direct database read-only SQL knowledge.
3. **Queue Wait Times:** Simple telemetry lookups must wait on engineer tickets.
This tool automates extraction and formatting to deliver safe network details in **under 3 seconds**.

---

## 📦 Scope & Whitelisted Intents (V1 MVP)

To enforce strict security and prevent SQL hallucinations, the system relies on an **Intent Whitelist** with strict Pydantic parsing. Only the following 9 intents are permitted:

| Intent Key | Purpose / Description | Allowed Filter Variables |
| :--- | :--- | :--- |
| `device_status` | Status tracking (`up`, `down`, `degraded`) | `device_type`, `status`, `location_code` |
| `device_inventory` | Device inventory listings | `device_type`, `vendor`, `location_code` (at least one required) |
| `interface_metrics` | Interface health checking (loss, errors) | `metric`, `operator`, `threshold`, `device_hostname` |
| `device_metrics` | CPU, Memory, and Temperature trends | `metric`, `operator`, `threshold`, `location_code` |
| `config_changes` | Log auditing for device modifications | `changed_by`, `since_hours`, `device_hostname` |
| `active_alerts` | Active network alerts and alarms | `severity`, `is_active` (default True) |
| `alert_summary` | Summary and counting of active alerts | *(None)* |
| `device_uptime` | System uptime durations | `device_hostname`, `device_type`, `location_code` |
| `out_of_scope` | Catch-all for non-network questions | *(None)* |

---

## ⚡ Key Architectural Rules

1. **The LLM Never Writes SQL:** 
   - Eliminates prompt injection vectors that attempt database modifications (`DROP TABLE`, `DELETE`, etc.).
   - Guarantees 100% database query correctness (no column or table hallucinations).
   - Allows exact debugging since all executed queries are pre-written, parameterized templates.
2. **Read-Only Database connection:**
   - The FastAPI backend accesses the core network tables through a strictly read-only PostgreSQL role.
3. **Structured Intent Extraction:**
   - Gemini is only used to translate natural language into structured JSON filters (`Call 1`).
4. **Fast Local Formatters (Zero-LLM Call 2):**
   - Pure Python formats raw records to Markdown in **<1ms**, eliminating the expensive and slow Call 2 formatting step.
