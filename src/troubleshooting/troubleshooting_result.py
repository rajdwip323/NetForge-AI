from datetime import datetime


def create_troubleshooting_result(
    target,
    problem,
    severity="medium",
    fault=None,
    evidence=None,
    root_cause=None,
    impact=None,
    recommendation=None,
):
    """
    Create a standardized troubleshooting result.
    """

    if not target:
        return {
            "success": False,
            "target": target,
            "problem": problem,
            "severity": severity,
            "fault": fault,
            "evidence": evidence or [],
            "root_cause": root_cause,
            "impact": impact,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Troubleshooting target cannot be empty",
        }

    if not problem:
        return {
            "success": False,
            "target": target,
            "problem": problem,
            "severity": severity,
            "fault": fault,
            "evidence": evidence or [],
            "root_cause": root_cause,
            "impact": impact,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Troubleshooting problem cannot be empty",
        }

    return {
        "success": True,
        "target": target,
        "problem": problem,
        "severity": severity,
        "fault": fault,
        "evidence": evidence or [],
        "root_cause": root_cause,
        "impact": impact,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow().isoformat(),
        "error": None,
    }


def validate_troubleshooting_result(result):
    """
    Validate the basic structure of a troubleshooting result.
    """

    required_fields = [
        "success",
        "target",
        "problem",
        "severity",
        "fault",
        "evidence",
        "root_cause",
        "impact",
        "recommendation",
        "timestamp",
        "error",
    ]

    if not isinstance(result, dict):
        return False

    for field in required_fields:
        if field not in result:
            return False

    if not result["target"]:
        return False

    if not result["problem"]:
        return False

    if not isinstance(result["evidence"], list):
        return False

    return True