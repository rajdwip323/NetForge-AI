from datetime import datetime


def record_metric(
    history,
    target,
    metric,
    value
):
    """
    Record a timestamped metric value
    in historical state.
    """

    if not isinstance(history, list):
        return {
            "success": False,
            "history": history,
            "error": "History must be a list"
        }

    if not target:
        return {
            "success": False,
            "history": history,
            "error": "Historical state target cannot be empty"
        }

    if not metric:
        return {
            "success": False,
            "history": history,
            "error": "Historical state metric cannot be empty"
        }

    record = {
        "target": target,
        "metric": metric,
        "value": value,
        "timestamp": datetime.now().isoformat()
    }

    history.append(record)

    return {
        "success": True,
        "record": record,
        "history": history,
        "error": None
    }


def get_history(
    history,
    target=None,
    metric=None
):
    """
    Retrieve historical metric records.
    """

    if not isinstance(history, list):
        return {
            "success": False,
            "records": [],
            "error": "History must be a list"
        }

    records = history

    if target:
        records = [
            record
            for record in records
            if record.get("target") == target
        ]

    if metric:
        records = [
            record
            for record in records
            if record.get("metric") == metric
        ]

    return {
        "success": True,
        "records": records,
        "count": len(records),
        "error": None
    }



def analyze_trend(
    history,
    target,
    metric
):
    """
    Analyze the trend of a historical metric.
    """

    if not isinstance(history, list):
        return {
            "success": False,
            "target": target,
            "metric": metric,
            "trend": None,
            "values": [],
            "error": "History must be a list"
        }

    if not target:
        return {
            "success": False,
            "target": target,
            "metric": metric,
            "trend": None,
            "values": [],
            "error": "Trend target cannot be empty"
        }

    if not metric:
        return {
            "success": False,
            "target": target,
            "metric": metric,
            "trend": None,
            "values": [],
            "error": "Trend metric cannot be empty"
        }

    records = [
        record
        for record in history
        if record.get("target") == target
        and record.get("metric") == metric
    ]

    values = [
        record.get("value")
        for record in records
    ]

    if len(values) < 2:
        return {
            "success": False,
            "target": target,
            "metric": metric,
            "trend": None,
            "values": values,
            "error": "At least two historical values are required"
        }

    if all(
        values[index] < values[index + 1]
        for index in range(len(values) - 1)
    ):
        trend = "increasing"

    elif all(
        values[index] > values[index + 1]
        for index in range(len(values) - 1)
    ):
        trend = "decreasing"

    else:
        trend = "stable"

    return {
        "success": True,
        "target": target,
        "metric": metric,
        "trend": trend,
        "values": values,
        "error": None
    }