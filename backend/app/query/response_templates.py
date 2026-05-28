from typing import List, Dict, Any

def format_uptime(seconds: Any) -> str:
    """Format seconds into the standard NOC format: Xd Xh Xm."""
    if seconds is None:
        return "0d 0h 0m"
    try:
        total_seconds = int(float(seconds))
    except (ValueError, TypeError):
        return "0d 0h 0m"
    
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"

def format_response(intent: str, rows: List[Dict[str, Any]], filters: Dict[str, Any]) -> str:
    """Format PostgreSQL database results deterministically into plain English answers."""
    # 1. Handle out of scope intent
    if intent == "out_of_scope":
        return "I can only answer questions about network devices, interfaces, alerts, config changes, and metrics."
        
    # 2. Handle empty results
    if not rows:
        return "No results found for your query. Try adjusting your filters."

    n = len(rows)
    lines = []

    if intent == "device_status":
        device_type = filters.get("device_type") or "device"
        status = filters.get("status") or "any"
        lines.append(f"Found {n} {device_type}(s) with status '{status}':")
        for r in rows:
            hostname = r.get("hostname") or "Unknown"
            ip = r.get("ip_address") or "N/A"
            site = r.get("location") or r.get("site_name") or "N/A"
            last_seen = str(r.get("last_seen"))[:16] if r.get("last_seen") else "N/A"
            lines.append(f"* {hostname} ({ip}) | Site: {site} | Last Seen: {last_seen}")

    elif intent == "device_inventory":
        device_type = filters.get("device_type") or "any"
        location = filters.get("location_code") or "any"
        lines.append(f"Device inventory ({device_type} | {location}) — {n} device(s):")
        for r in rows:
            hostname = r.get("hostname") or "Unknown"
            vendor = r.get("vendor") or "N/A"
            model = r.get("model") or "N/A"
            os_ver = r.get("os_version") or "N/A"
            status = r.get("status") or "unknown"
            site = r.get("location") or r.get("site_name") or "N/A"
            lines.append(f"* {hostname} | Vendor: {vendor} | Model: {model} | OS: {os_ver} | Status: {status} | Site: {site}")

    elif intent == "interface_metrics":
        metric = filters.get("metric") or "metric"
        threshold = filters.get("threshold") or 0
        operator = filters.get("operator") or "gt"
        op_word = "above" if operator in ["gt", "gte"] else "below"
        lines.append(f"Found {n} interface(s) with {metric} {op_word} {threshold}%:")
        for r in rows:
            name = f"{r.get('device_hostname') or r.get('hostname') or 'Unknown'}/{r.get('interface_name') or 'unknown'}"
            loss = r.get("packet_loss_pct") or r.get("metric_value", 0) if metric == "packet_loss" else r.get("packet_loss_pct", 0)
            errors = r.get("error_count") or r.get("metric_value", 0) if metric == "errors" else r.get("error_count", 0)
            util = r.get("utilization_pct") or r.get("metric_value", 0) if metric == "utilization" else r.get("utilization_pct", 0)
            status = r.get("status") or "down"
            lines.append(f"* {name} | Packet Loss: {loss}% | Errors: {errors} | Utilization: {util}% | Status: {status}")

    elif intent == "device_metrics":
        metric = filters.get("metric") or "metric"
        threshold = filters.get("threshold") or 0
        lines.append(f"Found {n} device(s) with {metric} above {threshold}%:")
        for r in rows:
            hostname = r.get("hostname") or "Unknown"
            ip = r.get("ip_address") or "N/A"
            cpu = r.get("cpu_usage") or r.get("metric_value", 0) if metric == "cpu" else r.get("cpu_usage", 0)
            mem = r.get("memory_usage") or r.get("metric_value", 0) if metric == "memory" else r.get("memory_usage", 0)
            uptime = format_uptime(r.get("uptime_seconds"))
            lines.append(f"* {hostname} ({ip}) | CPU: {cpu}% | Memory: {mem}% | Uptime: {uptime}")

    elif intent == "config_changes":
        lines.append(f"Found {n} config change(s):")
        for r in rows:
            changed_at = str(r.get("changed_at"))[:16] if r.get("changed_at") else "N/A"
            hostname = r.get("device_hostname") or r.get("hostname") or "Unknown"
            change_type = r.get("change_type") or "change"
            by = r.get("changed_by") or "unknown"
            summary = r.get("summary") or "No description"
            lines.append(f"* {changed_at} - {hostname} | Type: {change_type} | By: {by} | Summary: {summary}")

    elif intent == "active_alerts":
        severity = filters.get("severity") or "any"
        lines.append(f"Found {n} active alert(s) (severity: {severity}):")
        for r in rows:
            sev_caps = str(r.get("severity", severity)).upper()
            hostname = r.get("device_hostname") or r.get("hostname") or "Unknown"
            alert_type = r.get("alert_type") or "alert"
            msg = r.get("message") or ""
            created_at = str(r.get("created_at"))[:16] if r.get("created_at") else "N/A"
            lines.append(f"* [{sev_caps}] {hostname} | Type: {alert_type} | Message: {msg} | Created At: {created_at}")

    elif intent == "alert_summary":
        lines.append("Alert summary by severity:")
        for r in rows:
            sev_caps = str(r.get("severity", "unknown")).upper()
            count = r.get("count") or r.get("alert_count") or 0
            lines.append(f"* {sev_caps}: {count} alert(s)")

    elif intent == "device_uptime":
        lines.append(f"Uptime for {n} device(s):")
        for r in rows:
            hostname = r.get("hostname") or "Unknown"
            ip = r.get("ip_address") or "N/A"
            uptime = format_uptime(r.get("uptime_seconds"))
            last_seen = str(r.get("last_seen"))[:16] if r.get("last_seen") else "N/A"
            lines.append(f"* {hostname} ({ip}) | Uptime: {uptime} | Last Seen: {last_seen}")

    else:
        # Fallback raw list
        lines.append(f"Found {n} query result(s):")
        for r in rows:
            lines.append(f"* {str(r)}")

    return "\n".join(lines)
