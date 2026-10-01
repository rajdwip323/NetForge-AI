from datetime import datetime


def create_alert_record(
    target,
    alert_type,
    severity,
    message
):
    """
    Create a new alert lifecycle record.
    """

    if not target:
        return {
            "success": False,
            "alert_id": None,
            "target": target,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "state": None,
            "created_at": None,
            "acknowledged_at": None,
            "resolved_at": None,
            "error": "Alert target cannot be empty"
        }

    if not alert_type:
        return {
            "success": False,
            "alert_id": None,
            "target": target,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "state": None,
            "created_at": None,
            "acknowledged_at": None,
            "resolved_at": None,
            "error": "Alert type cannot be empty"
        }

    return {
        "success": True,
        "alert_id": f"{target}-{alert_type}",
        "target": target,
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "state": "triggered",
        "created_at": datetime.now().isoformat(),
        "acknowledged_at": None,
        "resolved_at": None,
        "error": None
    }


def acknowledge_alert(alert):
    """
    Move an alert from triggered to acknowledged state.
    """

    if not isinstance(alert, dict):
        return {
            "success": False,
            "alert": alert,
            "error": "Alert must be a dictionary"
        }

    if alert.get("state") != "triggered":
        result = alert.copy()
        result["success"] = False
        result["error"] = (
            "Only triggered alerts can be acknowledged"
        )
        return result

    result = alert.copy()

    result["state"] = "acknowledged"
    result["acknowledged_at"] = datetime.now().isoformat()
    result["error"] = None
    result["success"] = True

    return result


def resolve_alert(alert):
    """
    Move an alert from acknowledged to resolved state.
    """

    if not isinstance(alert, dict):
        return {
            "success": False,
            "alert": alert,
            "error": "Alert must be a dictionary"
        }

    if alert.get("state") != "acknowledged":
        result = alert.copy()
        result["success"] = False
        result["error"] = (
            "Only acknowledged alerts can be resolved"
        )
        return result

    result = alert.copy()

    result["state"] = "resolved"
    result["resolved_at"] = datetime.now().isoformat()
    result["error"] = None
    result["success"] = True

    return result