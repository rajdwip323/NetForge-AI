"""
NETFORGE-AI Verification Report

Phase 5.7:
Aggregates individual verification results
into one standardized verification report.

This module is vendor-independent.
"""


def create_verification_report(results):
    """
    Create an aggregated verification report.

    Parameters:
        results : list or tuple of verification result dictionaries

    Returns:
        {
            "overall_success": True/False,
            "overall_verified": True/False,
            "total": int,
            "passed": int,
            "failed": int,
            "errors": int,
            "results": [...]
        }
    """

    # Validate result collection
    if not isinstance(results, (list, tuple)):
        return {
            "overall_success": False,
            "overall_verified": False,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "results": [],
            "error": "Verification results must be a list or tuple"
        }

    normalized_results = []
    passed = 0
    failed = 0
    errors = 0

    for index, result in enumerate(results):

        # Validate individual result
        if not isinstance(result, dict):
            errors += 1

            normalized_results.append({
                "success": False,
                "verified": False,
                "target": f"Result {index + 1}",
                "expected": None,
                "actual": None,
                "error": "Invalid verification result"
            })

            continue

        normalized_results.append(result)

        success = result.get("success") is True
        verified = result.get("verified") is True

        if success and verified:
            passed += 1

        elif success and not verified:
            failed += 1

        else:
            errors += 1

    total = len(normalized_results)

    overall_success = (
        errors == 0
    )

    overall_verified = (
        total > 0
        and passed == total
    )

    return {
        "overall_success": overall_success,
        "overall_verified": overall_verified,
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "results": normalized_results
    }


def is_report_successful(report):
    """
    Return True only when the verification report
    completed successfully and every verification passed.
    """

    if not isinstance(report, dict):
        return False

    return (
        report.get("overall_success") is True
        and report.get("overall_verified") is True
    )