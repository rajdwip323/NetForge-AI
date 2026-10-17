
from datetime import datetime


KNOWN_FAULT_EVENTS = {
    "interface_down": "high",
    "device_down": "high",
    "link_down": "high",
    "connectivity_lost": "high",
}

VALID_SEVERITIES = {"low", "medium", "high", "critical"}


def detect_network_faults(target, collected_evidence):
    """
    Detect potential network faults from collected troubleshooting evidence.

    This function performs rule-based fault detection only.
    It does not determine root cause or modify network devices.
    """

    timestamp = datetime.utcnow().isoformat()

    def failure(message):
        return {
            "success": False,
            "target": target,
            "faults": [],
            "fault_count": 0,
            "timestamp": timestamp,
            "error": message,
        }

    if not isinstance(target, str) or not target.strip():
        return failure("Troubleshooting target cannot be empty")

    target = target.strip()

    if not isinstance(collected_evidence, dict):
        return failure("Collected evidence must be a dictionary")

    if collected_evidence.get("success") is not True:
        return failure("Collected evidence is not successful")

    evidence_items = collected_evidence.get("evidence")

    if not isinstance(evidence_items, list):
        return failure("Collected evidence must contain an evidence list")

    if collected_evidence.get("target") != target:
        return failure("Target does not match collected evidence target")

    detected = {}

    def add_fault(fault_type, severity, strength, item):
        if fault_type not in detected:
            detected[fault_type] = {
                "fault_type": fault_type,
                "severity": severity,
                "detection_strength": strength,
                "evidence": [],
            }

        fault = detected[fault_type]

        if severity in VALID_SEVERITIES:
            priority = {"low": 1, "medium": 2, "high": 3, "critical": 4}

            if priority[severity] > priority[fault["severity"]]:
                fault["severity"] = severity

        if strength == "high":
            fault["detection_strength"] = "high"

        fault["evidence"].append(item)

    for item in evidence_items:
        if not isinstance(item, dict):
            return failure("Each evidence item must be a dictionary")

        if item.get("target") != target:
            continue

        event_type = item.get("type")

        if event_type in KNOWN_FAULT_EVENTS:
            severity = str(item.get("severity", "high")).lower()

            if severity not in VALID_SEVERITIES:
                severity = "high"

            add_fault(
                fault_type=event_type,
                severity=severity,
                strength="high",
                item=item,
            )

        elif event_type == "verification_result":
            expected = item.get("expected")
            actual = item.get("actual")

            if expected is None or actual is None:
                continue

            if str(expected).strip().lower() != str(actual).strip().lower():
                add_fault(
                    fault_type="verification_mismatch",
                    severity="medium",
                    strength="medium",
                    item=item,
                )

    return {
        "success": True,
        "target": target,
        "faults": list(detected.values()),
        "fault_count": len(detected),
        "timestamp": timestamp,
        "error": None,
    }
