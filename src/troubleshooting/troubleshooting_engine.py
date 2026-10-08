from troubleshooting.troubleshooting_result import (
    create_troubleshooting_result,
    validate_troubleshooting_result,
)


def troubleshoot(
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
    Run a basic troubleshooting workflow.
    """

    result = create_troubleshooting_result(
        target=target,
        problem=problem,
        severity=severity,
        fault=fault,
        evidence=evidence,
        root_cause=root_cause,
        impact=impact,
        recommendation=recommendation,
    )

    if not validate_troubleshooting_result(result):
        result["success"] = False
        result["error"] = "Invalid troubleshooting result"

    return result