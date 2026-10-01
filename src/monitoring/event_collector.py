from datetime import datetime


def create_network_event(
    target,
    event_type,
    severity,
    message
):
    """
    Create a standardized network event.
    """

    if not target:
        return {
            "success": False,
            "target": target,
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error": "Event target cannot be empty"
        }

    if not event_type:
        return {
            "success": False,
            "target": target,
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error": "Event type cannot be empty"
        }

    return {
        "success": True,
        "target": target,
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "error": None
    }