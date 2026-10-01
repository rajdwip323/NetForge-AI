from datetime import datetime


def create_alert(
    target,
    metric,
    value,
    threshold,
    severity
):
    """
    Create a standardized alert when a metric
    exceeds the defined threshold.
    """

    if not target:
        return {
            "success": False,
            "alert": False,
            "target": target,
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "severity": severity,
            "message": None,
            "timestamp": datetime.now().isoformat(),
            "error": "Alert target cannot be empty"
        }

    if not metric:
        return {
            "success": False,
            "alert": False,
            "target": target,
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "severity": severity,
            "message": None,
            "timestamp": datetime.now().isoformat(),
            "error": "Alert metric cannot be empty"
        }

    alert_triggered = value > threshold

    return {
        "success": True,
        "alert": alert_triggered,
        "target": target,
        "metric": metric,
        "value": value,
        "threshold": threshold,
        "severity": severity,
        "message": (
            f"{metric} exceeded threshold "
            f"on {target}"
            if alert_triggered
            else None
        ),
        "timestamp": datetime.now().isoformat(),
        "error": None
    }


def create_event_alert(
    target,
    event_type,
    severity,
    message
):
    """
    Create a standardized alert from a network event.
    """

    if not target:
        return {
            "success": False,
            "alert": False,
            "target": target,
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error": "Alert target cannot be empty"
        }

    if not event_type:
        return {
            "success": False,
            "alert": False,
            "target": target,
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "error": "Alert event type cannot be empty"
        }

    return {
        "success": True,
        "alert": True,
        "target": target,
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "error": None
    }