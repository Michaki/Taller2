# alert_service.py
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.utils.thresholds import determine_status

# In-memory store for alert logs.
alert_logs: List[Dict[str, Any]] = []

# Dictionary to keep track of each switch's last known status.
last_switch_status: Dict[str, str] = {}

def process_switch_message(message: dict) -> Dict[str, Any]:
    """
    Analyze an incoming switch message and generate an alert if the switch's status changes.
    It compares the current status with the last known status. If a change is detected and the new
    status is "unhealthy", an alert message with switch metadata is generated.
    
    Returns:
      - A dictionary with alert information if a status change occurs.
      - An empty dictionary otherwise.
    """
    # Compute current status in "alert mode" (thresholds are strict).
    current_status = determine_status(
        message.get("bandwidth_usage", 0),
        message.get("packet_loss", 0),
        message.get("latency", 0),
        alert_mode=True
    )
    
    switch_id = message.get("switch_id")
    if not switch_id:
        return {}
    
    # Default previous status is "healthy" if not seen before.
    previous_status = last_switch_status.get(switch_id, "healthy")
    
    # If status has not changed, do nothing.
    if current_status == previous_status:
        return {}
    
    # Update the stored status.
    last_switch_status[switch_id] = current_status
    
    # Only broadcast an alert if the new status is not healthy.
    if current_status == "unhealthy":
        now = datetime.now()
        alert = {
            "switch_id": switch_id,
            "parent_switch_id": message.get("parent_switch_id"),
            "status": current_status,
            "bandwidth_usage": message.get("bandwidth_usage"),
            "packet_loss": message.get("packet_loss"),
            "latency": message.get("latency"),
            "timestamp": now.isoformat(),
            "message": f"Alert: Switch {switch_id} in group {message.get('parent_switch_id')} changed status to {current_status}."
        }
        # Deduplication logic can be added here if necessary.
        alert_logs.append(alert)
        return alert
    
    return {}

def get_alert_logs() -> List[Dict[str, Any]]:
    """Return the current alert logs."""
    return alert_logs
