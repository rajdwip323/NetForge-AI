
from datetime import datetime


def recommend_troubleshooting_fix(
    target,
    collected_evidence,
    detected_faults,
    root_cause_result,
    impact_result,
):
    """
    Generate evidence-backed, advisory-only diagnostic recommendations.

    This function never executes commands or changes device configuration.
    """

    timestamp = datetime.now().astimezone().isoformat()

    def failure(message):
        return {
            "success": False,
            "target": target,
            "status": "error",
            "recommendations": [],
            "supporting_evidence": [],
            "confidence": "none",
            "limitations": [
                "No device commands are executed or configurations changed."
            ],
            "timestamp": timestamp,
            "error": message,
        }

    if not isinstance(target, str) or not target.strip():
        return failure("Troubleshooting target cannot be empty")

    target = target.strip()

    inputs = (
        ("Collected evidence", collected_evidence),
        ("Detected faults", detected_faults),
        ("Root cause result", root_cause_result),
        ("Impact result", impact_result),
    )

    for name, value in inputs:
        if not isinstance(value, dict):
            return failure(f"{name} must be a dictionary")

        if value.get("success") is not True:
            return failure(f"{name} is not successful")

        if value.get("target") != target:
            return failure(
                f"Target does not match {name.lower()} target"
            )

    evidence_items = collected_evidence.get("evidence")
    faults = detected_faults.get("faults")

    if not isinstance(evidence_items, list):
        return failure("Collected evidence must contain an evidence list")

    if not isinstance(faults, list):
        return failure("Detected faults must contain a faults list")

    if any(not isinstance(item, dict) for item in evidence_items):
        return failure("Each evidence item must be a dictionary")

    if any(not isinstance(item, dict) for item in faults):
        return failure("Each detected fault must be a dictionary")

    if root_cause_result.get("status") not in {
        "possible",
        "inconclusive",
    }:
        return failure("Unsupported root cause result status")

    impact_status = impact_result.get("status")

    if impact_status not in {
        "inconclusive",
        "potential_impact_identified",
    }:
        return failure("Unsupported impact result status")

    limitations = [
        "Recommendations are advisory only.",
        "No device commands or configuration changes are performed.",
        "A detected fault does not independently confirm its root cause.",
    ]

    if root_cause_result.get("status") == "inconclusive":
        limitations.append(
            "Root cause analysis is inconclusive; no specific corrective "
            "fix is inferred."
        )

    if impact_status == "inconclusive":
        limitations.append(
            "Impact analysis is inconclusive; downstream service impact "
            "remains uncertain."
        )
    else:
        limitations.append(
            "Potential affected targets were identified by impact analysis; "
            "assess service scope before any corrective action."
        )

    result = {
        "success": True,
        "target": target,
        "status": "inconclusive",
        "recommendations": [],
        "supporting_evidence": [],
        "confidence": "none",
        "limitations": limitations,
        "timestamp": timestamp,
        "error": None,
    }

    if not faults:
        limitations.append(
            "No detected fault was supplied; no recommendation was made."
        )
        return result

    diagnostic_steps = {
        "interface_down": (
            "Collect the interface administrative state, operational state, "
            "and relevant link diagnostics before considering a corrective fix."
        ),
        "device_down": (
            "Collect device reachability and availability diagnostics "
            "before determining the cause."
        ),
        "link_down": (
            "Collect link status and relevant endpoint diagnostics "
            "before determining the cause."
        ),
        "connectivity_lost": (
            "Collect end-to-end connectivity and relevant path diagnostics "
            "before determining the cause."
        ),
        "verification_mismatch": (
            "Recheck the expected and actual device state and collect "
            "additional diagnostic evidence before considering a fix."
        ),
    }

    recommendations = []
    supporting_evidence = []

    for fault in faults:
        fault_type = fault.get("fault_type")

        if not isinstance(fault_type, str) or not fault_type.strip():
            continue

        fault_type = fault_type.strip()
        fault_evidence = fault.get("evidence")

        if not isinstance(fault_evidence, list):
            continue

        valid_evidence = []

        for item in fault_evidence:
            if not isinstance(item, dict):
                continue

            if item.get("target") != target:
                continue

            if item not in evidence_items:
                continue

            evidence_type = item.get("type")

            matches_fault = evidence_type == fault_type

            if fault_type == "verification_mismatch":
                matches_fault = (
                    evidence_type == "verification_result"
                    and item.get("expected") != item.get("actual")
                )

            if matches_fault:
                valid_evidence.append(item)

        if not valid_evidence:
            continue

        step = diagnostic_steps.get(fault_type)

        if step is None:
            continue

        recommendations.append({
            "fault_type": fault_type,
            "type": "diagnostic",
            "action": step,
            "confidence": "low",
        })

        for item in valid_evidence:
            if item not in supporting_evidence:
                supporting_evidence.append(item)

    if recommendations:
        result["status"] = "diagnostic_recommendations_available"
        result["recommendations"] = recommendations
        result["supporting_evidence"] = supporting_evidence
        result["confidence"] = "low"

        limitations.append(
            "Corrective fixes are not recommended without sufficient "
            "cause-specific diagnostic evidence."
        )
    else:
        limitations.append(
            "No supported fault with matching collected evidence was found; "
            "additional diagnostics are required."
        )

    return result
