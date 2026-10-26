from datetime import datetime


def analyze_impact(
    target,
    collected_evidence,
    detected_faults,
    root_cause_result,
    dependency_evidence=None,
):
    """Assess potential impact using explicit evidence only."""

    timestamp = datetime.now().astimezone().isoformat()

    def failure(message):
        return {
            "success": False,
            "target": target,
            "status": "error",
            "impact_severity": "unknown",
            "affected_targets": [],
            "supporting_evidence": [],
            "confidence": "none",
            "limitations": [],
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
    if collected_evidence.get("target") != target:
        return failure("Target does not match collected evidence target")

    evidence = collected_evidence.get("evidence")
    if not isinstance(evidence, list):
        return failure("Collected evidence must contain an evidence list")
    if any(not isinstance(item, dict) for item in evidence):
        return failure("Each evidence item must be a dictionary")

    if not isinstance(detected_faults, dict):
        return failure("Detected faults must be a dictionary")
    if detected_faults.get("success") is not True:
        return failure("Fault detection result is not successful")
    if detected_faults.get("target") != target:
        return failure("Target does not match detected faults target")

    faults = detected_faults.get("faults")
    if not isinstance(faults, list):
        return failure("Detected faults must contain a faults list")
    if any(not isinstance(item, dict) for item in faults):
        return failure("Each detected fault must be a dictionary")

    if not isinstance(root_cause_result, dict):
        return failure("Root cause result must be a dictionary")
    if root_cause_result.get("success") is not True:
        return failure("Root cause analysis result is not successful")
    if root_cause_result.get("target") != target:
        return failure("Target does not match root cause result")
    if root_cause_result.get("status") not in {
        "possible", "inconclusive"
    }:
        return failure("Root cause result has an unsupported status")

    if dependency_evidence is None:
        dependency_evidence = []
    if not isinstance(dependency_evidence, (list, tuple)):
        return failure("Dependency evidence must be a list or tuple")

    required = (
        "source", "target", "depends_on",
        "dependency_type", "relationship",
    )

    for item in dependency_evidence:
        if not isinstance(item, dict):
            return failure(
                "Each dependency evidence item must be a dictionary"
            )
        if not all(field in item for field in required):
            return failure(
                "Dependency evidence is missing required fields"
            )
        if item.get("source") != "dependency":
            return failure(
                "Dependency evidence source must be 'dependency'"
            )

        for field in (
            "target", "depends_on",
            "dependency_type", "relationship",
        ):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                return failure(
                    f"Dependency field '{field}' must be a non-empty string"
                )

        if item["relationship"] != "depends_on":
            return failure(
                "Dependency relationship must be 'depends_on'"
            )

    limitations = [
        "Dependency relationships alone cannot establish impact severity.",
        "No topology discovery or device configuration changes are performed.",
    ]

    if root_cause_result["status"] == "possible":
        limitations.append(
            "Root cause is a candidate, not a confirmed cause."
        )

    result = {
        "success": True,
        "target": target,
        "status": "inconclusive",
        "impact_severity": "unknown",
        "affected_targets": [],
        "supporting_evidence": [],
        "confidence": "none",
        "limitations": limitations,
        "timestamp": timestamp,
        "error": None,
    }

    if not faults:
        result["limitations"].append(
            "No detected fault was provided; no potential impact was inferred."
        )
        return result

    matched = [
        item for item in dependency_evidence
        if item["depends_on"].strip() == target
        and item["target"].strip() != target
    ]

    if matched:
        result["status"] = "potential_impact_identified"
        result["affected_targets"] = sorted({
            item["target"].strip() for item in matched
        })
        result["supporting_evidence"] = matched
        result["confidence"] = "low"
    else:
        result["limitations"].append(
            "No explicit dependency evidence identifies a dependent target."
        )

    return result
