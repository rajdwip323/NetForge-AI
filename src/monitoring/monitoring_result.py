from datetime import datetime


def monitoring_success(target, metric, value):
    return {
        "success": True,
        "target": target,
        "metric": metric,
        "value": value,
        "timestamp": datetime.now().isoformat(),
        "error": None
    }


def monitoring_error(target, metric, error):
    return {
        "success": False,
        "target": target,
        "metric": metric,
        "value": None,
        "timestamp": datetime.now().isoformat(),
        "error": error
    }


def is_monitoring_successful(result):
    return (
        isinstance(result, dict)
        and result.get("success") is True
        and result.get("error") is None
    )