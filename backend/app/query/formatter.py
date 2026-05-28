from typing import List, Dict, Any
from datetime import datetime

def format_deterministic_response(rows: List[Dict[str, Any]], intent: str) -> str:
    """Format query database rows deterministically into highly structured markdown answers.
    
    This replaces the second LLM formatting call, dropping response latency significantly.
    """
    if not rows:
        return "No results found matching your query."
        
    count = len(rows)
    lines = []
    
    if intent == "device_status":
        down_degraded = [r for r in rows if r.get("status", "").lower() in ["down", "degraded"]]
        if down_degraded:
            lines.append(f"### Alert: {len(down_degraded)} out of {count} monitored devices require attention:")
            for r in rows:
                status_emoji = "🔴" if r.get("status") == "down" else "🟡" if r.get("status") == "degraded" else "🟢"
                lines.append(
                    f"* {status_emoji} **{r.get('hostname')}** ({r.get('ip_address')}) — "
                    f"Status: **{r.get('status')}**, Location: {r.get('location') or 'Unknown'}"
                )
        else:
            lines.append(f"🟢 **All {count} devices are fully operational.**")
            for r in rows:
                lines.append(f"* **{r.get('hostname')}** ({r.get('ip_address')}) — Location: {r.get('location') or 'Unknown'}")
                
    elif intent == "device_inventory":
        lines.append(f"📋 **Inventory Catalog ({count} active devices matched):**")
        for r in rows:
            lines.append(
                f"* **{r.get('hostname')}** — Type: *{r.get('device_type')}*, Vendor: {r.get('vendor') or 'Standard'}, "
                f"IP: `{r.get('ip_address')}`, Site: {r.get('location') or 'Unknown'}"
            )
            
    elif intent == "interface_metrics":
        lines.append(f"📊 **Interface Metrics & Telemetry ({count} interfaces):**")
        for r in rows:
            warn = "⚠️ " if (r.get("packet_loss_pct", 0) > 2 or r.get("error_count", 0) > 0) else "✔️ "
            lines.append(
                f"* {warn}**{r.get('hostname')}** // `{r.get('interface_name')}` — "
                f"Utilization: **{r.get('utilization_pct')}%**, Packet Loss: **{r.get('packet_loss_pct')}%**, "
                f"Errors: **{r.get('error_count')}**, Speed: {r.get('speed_mbps')} Mbps"
            )
            
    elif intent == "device_metrics":
        lines.append(f"⚡ **Device System Performance ({count} nodes):**")
        for r in rows:
            cpu = r.get("cpu_usage", 0)
            mem = r.get("memory_usage", 0)
            status_indicator = "🔴 " if cpu > 80 or mem > 85 else "🟢 "
            
            # Format uptime nicely
            uptime_sec = r.get("uptime_seconds", 0)
            uptime_str = f"{uptime_sec // 86400} days" if uptime_sec >= 86400 else f"{uptime_sec // 3600} hours"
            
            lines.append(
                f"* {status_indicator}**{r.get('hostname')}** — "
                f"CPU: **{cpu}%**, Memory: **{mem}%**, "
                f"Temp: **{r.get('temperature_c')}°C**, Uptime: {uptime_str}"
            )
            
    elif intent == "config_changes":
        lines.append(f"⚙️ **Operator Configuration Audit Log ({count} modifications):**")
        for r in rows:
            # Parse changed_at date
            dt = r.get("changed_at")
            if isinstance(dt, datetime):
                dt_str = dt.strftime("%Y-%m-%d %H:%M UTC")
            else:
                dt_str = str(dt)
                
            lines.append(
                f"* **{r.get('hostname')}** — Action: `{r.get('change_type')}` by **{r.get('changed_by')}** "
                f"(*{r.get('summary')}*) at {dt_str}"
            )
            
    elif intent == "active_alerts":
        lines.append(f"🚨 **Active Operational Alerts ({count} warnings trigger):**")
        for r in rows:
            sev_emoji = "🔴 [CRITICAL]" if r.get("severity") == "critical" else "🟡 [WARNING]" if r.get("severity") == "warning" else "🔵 [INFO]"
            lines.append(
                f"* {sev_emoji} **{r.get('hostname')}** — `{r.get('alert_type')}`: "
                f"\"{r.get('message')}\""
            )
            
    elif intent == "alert_summary":
        lines.append("📈 **NOC Incident Distribution Summary:**")
        for r in rows:
            lines.append(f"* Severity **{r.get('severity').upper()}**: **{r.get('alert_count')}** active tickets")
            
    elif intent == "device_uptime":
        lines.append(f"⏱️ **Device Service Uptime Stats ({count} nodes):**")
        for r in rows:
            uptime_sec = r.get("uptime_seconds", 0)
            days = uptime_sec / 86400.0
            status_indicator = "🔴 " if uptime_sec == 0 else "🟢 "
            lines.append(
                f"* {status_indicator}**{r.get('hostname')}** ({r.get('device_type')}) — "
                f"Uptime: **{days:.2f} days**"
            )
            
    else:
        # Fallback raw list
        lines.append(f"📝 Raw query results ({count} matches):")
        for r in rows:
            lines.append(f"* {str(r)}")
            
    return "\n".join(lines)
