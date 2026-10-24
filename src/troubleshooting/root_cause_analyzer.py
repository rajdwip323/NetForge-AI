from datetime import datetime


def analyze_root_cause(target, collected_evidence, detected_faults):
    """
    Analyze possible root causes using explicit diagnostic evidence.

    Fault symptoms alone are not treated as confirmed root causes.
    This function does not modify network devices.
    """

    timestamp = datetime.utcnow().isoformat()

    def failure(message):
        return {
            "success": False,
            "target": target,
            "status": "error",
            "root_cause": None,
            "candidates": [],
            "supporting_evidence": [],
            "confidence": "none",
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

    evidence_items = collected_evidence.get("evidence")

    if not isinstance(evidence_items, list):
        return failure("Collected evidence must contain an evidence list")

    if not isinstance(detected_faults, dict):
        return failure("Detected faults must be a dictionary")

    if detected_faults.get("success") is not True:
        return failure("Fault detection result is not successful")

    if detected_faults.get("target") != target:
        return failure("Target does not match detected faults target")

    faults = detected_faults.get("faults")

    if not isinstance(faults, list):
        return failure("Detected faults must contain a faults list")

    for item in evidence_items:
        if not isinstance(item, dict):
            return failure("Each evidence item must be a dictionary")

    for fault in faults:
        if not isinstance(fault, dict):
            return failure("Each detected fault must be a dictionary")

    candidates = {}

    # Only accept diagnostic evidence explicitly linked to a detected fault.
    detected_fault_types = {
        fault.get("fault_type")
        for fault in faults
        if isinstance(fault.get("fault_type"), str)
    }

    for item in evidence_items:
        if item.get("target") != target:
            continue

        if str(item.get("source", "")).strip().lower() != "diagnostic":
            continue

        related_fault_type = item.get("related_fault_type")
        if related_fault_type not in detected_fault_types:
            continue

        candidate = item.get("cause_candidate")

        if not isinstance(candidate, str) or not candidate.strip():
            candidate = item.get("root_cause_candidate")

        if not isinstance(candidate, str) or not candidate.strip():
            continue

        candidate = candidate.strip()

        if candidate not in candidates:
            candidates[candidate] = []

        candidates[candidate].append(item)

    candidate_results = [
        {
            "cause": cause,
            "supporting_evidence": supporting_evidence,
        }
        for cause, supporting_evidence in candidates.items()
    ]

    # Faults and diagnostic evidence are both required for a possible cause.
    if not faults or len(candidate_results) != 1:
        result_status = "inconclusive"
        root_cause = None
        supporting_evidence = []
        confidence = "none"
        candidate_results = candidate_results if faults else []

    else:
        result_status = "possible"
        root_cause = candidate_results[0]["cause"]
        supporting_evidence = candidate_results[0]["supporting_evidence"]
        confidence = "low"

    return {
        "success": True,
        "target": target,
        "status": result_status,
        "root_cause": root_cause,
        "candidates": candidate_results,
        "supporting_evidence": supporting_evidence,
        "confidence": confidence,
        "timestamp": timestamp,
        "error": None,
    }
