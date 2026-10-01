from .monitoring_engine import monitor_metric


def monitor_device_health(
    target,
    reachability,
    cpu_usage,
    memory_usage,
    uptime
):
    """
    Create standardized monitoring results for device health metrics.
    """

    results = []

    results.append(
        monitor_metric(
            target,
            "reachability",
            reachability
        )
    )

    results.append(
        monitor_metric(
            target,
            "cpu_usage",
            cpu_usage
        )
    )

    results.append(
        monitor_metric(
            target,
            "memory_usage",
            memory_usage
        )
    )

    results.append(
        monitor_metric(
            target,
            "uptime",
            uptime
        )
    )

    return results