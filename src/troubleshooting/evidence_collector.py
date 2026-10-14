
from datetime import datetime

from monitoring.monitoring_engine import validate_monitoring_result


def collect_troubleshooting_evidence(
    target,
    monitoring_results=None,
    verification_report=None,
    events=None,
):
    """
    Collect existing monitoring, verification, and event data
    into one standardized troubleshooting evidence result.

    This module collects evidence only.
    It does not determine root cause or change network devices.
    """

    timestamp = datetime.now().astimezone().isoformat()

    result = {
        "success": False,
        "target": target,
        "evidence": [],
        "summary": {
            "monitoring": 0,
            "verification": 0,
            "events": 0,
        },
        "timestamp": timestamp,
        "error": None,
    }

    if not isinstance(target, str) or not target.strip():
        result["error"] = "Evidence target cannot be empty"
        return result

    target = target.strip()

    if monitoring_results is None:
        monitoring_results = []

    if events is None:
        events = []

    if not isinstance(monitoring_results, (list, tuple)):
        result["error"] = (
            "Monitoring results must be a list or tuple"
        )
        return result

    if not isinstance(events, (list, tuple)):
        result["error"] = "Events must be a list or tuple"
        return result

    if verification_report is not None:
        if not isinstance(verification_report, dict):
            result["error"] = (
                "Verification report must be a dictionary"
            )
            return result

        if not isinstance(
            verification_report.get("results"), list
        ):
            result["error"] = (
                "Verification report must contain a results list"
            )
            return result

    # Collect monitoring evidence.
    for item in monitoring_results:
        if not validate_monitoring_result(item):
            result["error"] = (
                "Invalid monitoring result encountered"
            )
            return result

        if item["target"] != target:
            continue

        result["evidence"].append({
            "source": "monitoring",
            "target": item["target"],
            "type": item["metric"],
            "value": item["value"],
            "timestamp": item["timestamp"],
            "success": item["success"],
            "error": item["error"],
        })

        result["summary"]["monitoring"] += 1

    # Collect verification evidence.
    if verification_report is not None:
        for item in verification_report["results"]:
            if not isinstance(item, dict):
                result["error"] = (
                    "Invalid verification result encountered"
                )
                return result

            required_fields = (
                "success",
                "verified",
                "target",
                "expected",
                "actual",
                "error",
            )

            if not all(
                field in item for field in required_fields
            ):
                result["error"] = (
                    "Verification result is missing required fields"
                )
                return result

            if item["target"] != target:
                continue

            result["evidence"].append({
                "source": "verification",
                "target": item["target"],
                "type": "verification_result",
                "success": item["success"],
                "verified": item["verified"],
                "expected": item["expected"],
                "actual": item["actual"],
                "error": item["error"],
            })

            result["summary"]["verification"] += 1

    # Collect network event evidence.
    for item in events:
        if not isinstance(item, dict):
            result["error"] = (
                "Invalid network event encountered"
            )
            return result

        required_fields = (
            "success",
            "target",
            "event_type",
            "severity",
            "message",
            "timestamp",
            "error",
        )

        if not all(
            field in item for field in required_fields
        ):
            result["error"] = (
                "Network event is missing required fields"
            )
            return result

        if item["target"] != target:
            continue

        result["evidence"].append({
            "source": "event",
            "target": item["target"],
            "type": item["event_type"],
            "severity": item["severity"],
            "message": item["message"],
            "timestamp": item["timestamp"],
            "success": item["success"],
            "error": item["error"],
        })

        result["summary"]["events"] += 1

    result["success"] = True
    return result
