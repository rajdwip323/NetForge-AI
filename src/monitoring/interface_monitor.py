from .monitoring_engine import monitor_metric


def monitor_interface(
    target,
    interface,
    operational_status,
    input_packets,
    output_packets,
    input_errors,
    output_errors,
    input_discards,
    output_discards
):
    """
    Create standardized monitoring results for interface metrics.
    """

    results = []

    results.append(
        monitor_metric(
            f"{target}:{interface}",
            "operational_status",
            operational_status
        )
    )

    results.append(
        monitor_metric(
            f"{target}:{interface}",
            "input_packets",
            input_packets
        )
    )

    results.append(
        monitor_metric(
            f"{target}:{interface}",
            "output_packets",
            output_packets
        )
    )

    results.append(
        monitor_metric(
            f"{target}:{interface}",
            "input_errors",
            input_errors
        )
    )

    results.append(
        monitor_metric(
            f"{target}:{interface}",
            "output_errors",
            output_errors
        )
    )

    results.append(
        monitor_metric(
            f"{target}:{interface}",
            "input_discards",
            input_discards
        )
    )

    results.append(
        monitor_metric(
            f"{target}:{interface}",
            "output_discards",
            output_discards
        )
    )

    return results