from .monitoring_engine import monitor_metric


def monitor_connectivity(
    source,
    destination,
    reachable,
    latency
):
    """
    Create standardized monitoring results
    for network reachability and connectivity.
    """

    target = f"{source}->{destination}"

    if not source:
        error = "Connectivity source cannot be empty"

        return [
            monitor_metric(
                target,
                "reachability",
                None
            ) | {"success": False, "error": error},
            monitor_metric(
                target,
                "latency",
                None
            ) | {"success": False, "error": error}
        ]

    if not destination:
        error = "Connectivity destination cannot be empty"

        return [
            monitor_metric(
                target,
                "reachability",
                None
            ) | {"success": False, "error": error},
            monitor_metric(
                target,
                "latency",
                None
            ) | {"success": False, "error": error}
        ]

    results = []

    results.append(
        monitor_metric(
            target,
            "reachability",
            reachable
        )
    )

    results.append(
        monitor_metric(
            target,
            "latency",
            latency
        )
    )

    return results