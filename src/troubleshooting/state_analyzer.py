
from datetime import datetime


def analyze_troubleshooting_state(target, collected_evidence):
    """
    Analyze collected evidence and determine the observed network state.

    This function does not determine root cause or modify devices.
    """

    result = {
        "success": False,
        "target": target,
        "state": "unknown",
        "evidence_count": 0,
        "findings": [],
        "timestamp": datetime.utcnow().isoformat(),
        "error": None,
    }

    if not isinstance(target, str) or not target.strip():
        result["error"] = "Troubleshooting target cannot be empty"
        return result

    target = target.strip()
    result["target"] = target

    if not isinstance(collected_evidence, dict):
        result["error"] = "Collected evidence must be a dictionary"
        return result

    if collected_evidence.get("success") is not True:
        result["error"] = "Cannot analyze unsuccessful evidence collection"
        return result

    evidence = collected_evidence.get("evidence")

    if not isinstance(evidence, list):
        result["error"] = "Collected evidence must contain an evidence list"
        return result

    matching_evidence = []

    for item in evidence:
        if not isinstance(item, dict):
            result["error"] = "Evidence item must be a dictionary"
            return result

        if item.get("target") == target:
            matching_evidence.append(item)

    result["evidence_count"] = len(matching_evidence)

    if not matching_evidence:
        result["success"] = True
        result["findings"].append("No matching evidence found")
        return result

    degraded = False
    verified_healthy = False

    adverse_events = {
        "interface_down",
        "device_down",
        "link_down",
        "connectivity_lost",
    }

    for item in matching_evidence:
        source = item.get("source")

        if source == "verification":
            if item.get("success") is False or item.get("verified") is False:
                degraded = True
                result["findings"].append(
                    "Verification indicates an unsuccessful state"
                )
            elif (
                item.get("success") is True
                and item.get("verified") is True
            ):
                verified_healthy = True
                result["findings"].append(
                    "Verification confirms the expected state"
                )

        elif source == "event":
            event_type = str(item.get("event_type", item.get("type", ""))).strip().lower()
            severity = str(item.get("severity", "")).strip().lower()

            if event_type in adverse_events:
                degraded = True
                result["findings"].append(
                    f"Adverse network event detected: {event_type}"
                )
            elif severity in {"high", "critical"}:
                degraded = True
                result["findings"].append(
                    f"High-severity event detected: {event_type or 'unknown'}"
                )

        elif source == "monitoring":
            # No metric thresholds are assumed at this stage.
            result["findings"].append(
                "Monitoring evidence recorded; metric thresholds not evaluated"
            )

    if degraded:
        result["state"] = "degraded"
    elif verified_healthy:
        result["state"] = "stable"
    else:
        result["state"] = "unknown"
        result["findings"].append(
            "Evidence is insufficient to confirm a stable state"
        )

    result["success"] = True
    return result
