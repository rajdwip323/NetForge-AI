from .monitoring_result import (
    monitoring_success,
    monitoring_error,
    is_monitoring_successful
)


def monitor_metric(target, metric, value):
    """
    Create a standardized monitoring result for a metric.
    """

    if not target:
        return monitoring_error(
            target,
            metric,
            "Monitoring target cannot be empty"
        )

    if not metric:
        return monitoring_error(
            target,
            metric,
            "Monitoring metric cannot be empty"
        )

    return monitoring_success(
        target,
        metric,
        value
    )


def validate_monitoring_result(result):
    """
    Validate the basic structure of a monitoring result.
    """

    if not isinstance(result, dict):
        return False

    required_keys = [
        "success",
        "target",
        "metric",
        "value",
        "timestamp",
        "error"
    ]

    for key in required_keys:
        if key not in result:
            return False

    return True