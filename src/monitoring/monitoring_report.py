from datetime import datetime


def create_monitoring_report(
    target,
    metrics=None,
    events=None,
    alerts=None
):
    """
    Create a consolidated monitoring report.
    """

    if not target:
        return {
            "success": False,
            "target": target,
            "timestamp": None,
            "total_metrics": 0,
            "successful_metrics": 0,
            "failed_metrics": 0,
            "total_events": 0,
            "total_alerts": 0,
            "active_alerts": 0,
            "overall_status": "error",
            "metrics": [],
            "events": [],
            "alerts": [],
            "error": "Monitoring report target cannot be empty"
        }

    if metrics is None:
        metrics = []

    if events is None:
        events = []

    if alerts is None:
        alerts = []

    successful_metrics = sum(
        1
        for metric in metrics
        if isinstance(metric, dict)
        and metric.get("success") is True
    )

    failed_metrics = len(metrics) - successful_metrics

    active_alerts = sum(
        1
        for alert in alerts
        if isinstance(alert, dict)
        and alert.get("alert") is True
        and alert.get("state") != "resolved"
    )

    if failed_metrics > 0 or active_alerts > 0:
        overall_status = "attention_required"
    else:
        overall_status = "healthy"

    return {
        "success": True,
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "total_metrics": len(metrics),
        "successful_metrics": successful_metrics,
        "failed_metrics": failed_metrics,
        "total_events": len(events),
        "total_alerts": len(alerts),
        "active_alerts": active_alerts,
        "overall_status": overall_status,
        "metrics": metrics,
        "events": events,
        "alerts": alerts,
        "error": None
    }