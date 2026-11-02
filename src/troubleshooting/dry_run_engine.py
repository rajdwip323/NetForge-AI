
from datetime import datetime, timezone


SUPPORTED_FAULT_TYPES = {
    "interface_down",
    "device_down",
    "link_down",
    "connectivity_lost",
    "verification_mismatch",
}


def _valid_text(value):
    return isinstance(value, str) and bool(value.strip())


def _error_result(target, message):
    return {
        "success": False,
        "status": "error",
        "target": target,
        "preview": None,
        "pre_checks": [],
        "proposed_actions": [],
        "expected_result": [],
        "post_checks": [],
        "impact": {},
        "risk": "unknown",
        "executed": False,
        "limitations": [
            "This is a read-only diagnostic preview.",
            "No device commands were executed.",
            "No device configuration was changed.",
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": message,
    }


def _validate_recommendations(target, recommended_fix):

    if not isinstance(recommended_fix, dict):
        return None, "recommended_fix must be a dictionary."

    if recommended_fix.get("success") is not True:
        return None, "Recommended fix result is not successful."

    if recommended_fix.get("target") != target:
        return None, "Recommended fix target mismatch."

    if recommended_fix.get("status") != "diagnostic_recommendations_available":
        return None, "Diagnostic recommendations are not available."

    recommendations = recommended_fix.get("recommendations")
    evidence = recommended_fix.get("supporting_evidence")

    if not isinstance(recommendations, list) or not recommendations:
        return None, "Recommendations must be a non-empty list."

    if not isinstance(evidence, list) or not evidence:
        return None, "Supporting evidence must be a non-empty list."

    for item in evidence:

        if not isinstance(item, dict):
            return None, "Supporting evidence contains an invalid item."

        if item.get("target") != target:
            return None, "Supporting evidence target mismatch."

    for recommendation in recommendations:

        if not isinstance(recommendation, dict):
            return None, "Recommendation contains an invalid item."

        fault_type = recommendation.get("fault_type")
        action = recommendation.get("action")

        if not isinstance(fault_type, str):
            return None, "Recommendation fault type must be a string."

        if fault_type not in SUPPORTED_FAULT_TYPES:
            return None, "Unsupported recommendation fault type."

        if recommendation.get("type") != "diagnostic":
            return None, "Only diagnostic recommendations are allowed."

        if not _valid_text(action):
            return None, "Recommendation action must be non-empty."

        if recommendation.get("confidence") != "low":
            return None, "Unsupported recommendation confidence."

        matching_evidence = []

        for item in evidence:

            if fault_type == "verification_mismatch":
                matches = (
                    item.get("type") == "verification_result"
                    and item.get("expected") != item.get("actual")
                )
            else:
                matches = item.get("type") == fault_type

            if matches:
                matching_evidence.append(item)

        if not matching_evidence:
            return None, (
                "Recommendation has no matching supporting evidence: "
                + fault_type
            )

    return {
        "recommendations": recommendations,
        "supporting_evidence": evidence,
    }, None


def _validate_impact(target, impact_result):

    if not isinstance(impact_result, dict):
        return None, "impact_result must be a dictionary."

    if impact_result.get("success") is not True:
        return None, "Impact analysis result is not successful."

    if impact_result.get("target") != target:
        return None, "Impact analysis target mismatch."

    status = impact_result.get("status")

    if not isinstance(status, str):
        return None, "Impact status must be a string."

    if status not in ("inconclusive", "potential_impact_identified"):
        return None, "Unsupported impact status."

    if impact_result.get("impact_severity") != "unknown":
        return None, "Impact severity must remain unknown."

    affected_targets = impact_result.get("affected_targets")
    supporting_evidence = impact_result.get("supporting_evidence")

    if not isinstance(affected_targets, list):
        return None, "affected_targets must be a list."

    if not isinstance(supporting_evidence, list):
        return None, "Impact supporting_evidence must be a list."

    normalized_targets = []

    for affected in affected_targets:

        if not _valid_text(affected):
            return None, "Affected targets must contain non-empty strings."

        dependent = affected.strip()

        if dependent == target:
            return None, "Target cannot be listed as its own affected target."

        normalized_targets.append(dependent)

    if len(set(normalized_targets)) != len(normalized_targets):
        return None, "Duplicate affected targets are not allowed."

    if status == "inconclusive":

        if normalized_targets or supporting_evidence:
            return None, "Inconclusive impact cannot contain affected targets."

        if impact_result.get("confidence") != "none":
            return None, "Inconclusive impact confidence must be none."

    else:

        if not normalized_targets or not supporting_evidence:
            return None, "Identified impact requires dependency evidence."

        evidence_targets = set()

        for item in supporting_evidence:

            if not isinstance(item, dict):
                return None, "Invalid dependency evidence item."

            required_fields = (
                "source",
                "target",
                "depends_on",
                "dependency_type",
                "relationship",
            )

            for field in required_fields:

                if not _valid_text(item.get(field)):
                    return None, "Dependency evidence has missing fields."

            if item["source"] != "dependency":
                return None, "Unsupported dependency evidence source."

            if item["relationship"] != "depends_on":
                return None, "Unsupported dependency relationship."

            if item["depends_on"].strip() != target:
                return None, "Dependency evidence target mismatch."

            dependent = item["target"].strip()

            if dependent == target:
                return None, "Self-dependency is not allowed."

            evidence_targets.add(dependent)

        if evidence_targets != set(normalized_targets):
            return None, "Impact targets do not match dependency evidence."

        if impact_result.get("confidence") != "low":
            return None, "Identified impact confidence must be low."

    return {
        "status": status,
        "impact_severity": "unknown",
        "affected_targets": normalized_targets,
        "supporting_evidence": supporting_evidence.copy(),
        "confidence": impact_result.get("confidence"),
    }, None


def run_dry_run(target, recommended_fix, impact_result):
    """Prepare a read-only diagnostic preview without device execution."""

    if not _valid_text(target):
        return _error_result("", "Target must be a non-empty string.")

    target = target.strip()

    recommendation_data, error = _validate_recommendations(
        target,
        recommended_fix,
    )

    if error:
        return _error_result(target, error)

    impact_data, error = _validate_impact(
        target,
        impact_result,
    )

    if error:
        return _error_result(target, error)

    recommendations = recommendation_data["recommendations"]

    proposed_actions = []

    for item in recommendations:

        proposed_actions.append({
            "fault_type": item["fault_type"],
            "type": "diagnostic",
            "action": item["action"],
            "confidence": item["confidence"],
        })

    return {
        "success": True,
        "status": "preview_ready",
        "target": target,
        "preview": {
            "type": "read_only_diagnostic",
            "summary": "Diagnostic preview prepared.",
        },
        "pre_checks": [
            "Review the supplied supporting evidence.",
            "Confirm the target and relevant interface.",
            "Review each diagnostic recommendation.",
        ],
        "proposed_actions": proposed_actions,
        "expected_result": [
            "Diagnostic observations may help identify the current issue.",
            "Additional evidence may be required.",
            "No recovery or configuration change is guaranteed.",
        ],
        "post_checks": [
            "Review diagnostic observations when independently collected.",
            "Determine whether additional evidence is required.",
            "Reassess the issue before any future approved action.",
        ],
        "impact": impact_data,
        "risk": "unknown",
        "executed": False,
        "limitations": [
            "This preview is advisory and read-only.",
            "No device commands are generated or executed.",
            "No device configuration is changed.",
            "Evidence has not been independently re-collected.",
            "Root cause is not independently confirmed.",
            "Impact severity remains unknown.",
            "Risk remains unknown because independent risk evidence is unavailable.",
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": None,
    }
