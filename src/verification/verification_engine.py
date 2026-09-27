"""
NETFORGE-AI Verification Engine

Phase 5.1:
Common foundation for network verification results.

This module is vendor-independent.

It does NOT:
- connect to devices
- execute commands
- parse vendor-specific CLI output

It only provides a common verification result structure.
"""


def create_verification_result(
    success,
    verified,
    target,
    expected=None,
    actual=None,
    error=None
):
    """
    Create a standardized verification result.

    Parameters:
        success  : Whether the verification operation itself succeeded.
        verified : Whether actual state matches expected state.
        target   : What is being verified.
        expected : Expected state/value.
        actual   : Actual state/value.
        error    : Error or mismatch message.

    Returns:
        Standardized verification result dictionary.
    """

    return {
        "success": bool(success),
        "verified": bool(verified),
        "target": target,
        "expected": expected,
        "actual": actual,
        "error": error
    }


def verification_passed(
    target,
    expected=None,
    actual=None
):
    """
    Create a successful verification result.
    """

    return create_verification_result(
        success=True,
        verified=True,
        target=target,
        expected=expected,
        actual=actual,
        error=None
    )


def verification_failed(
    target,
    expected=None,
    actual=None,
    error="Verification failed"
):
    """
    Create a verification result where the device
    responded successfully but the expected state
    was not verified.
    """

    return create_verification_result(
        success=True,
        verified=False,
        target=target,
        expected=expected,
        actual=actual,
        error=error
    )


def verification_error(
    target,
    error,
    expected=None,
    actual=None
):
    """
    Create a verification result for an operational
    or processing failure.

    Examples:
        command execution failure
        parser failure
        invalid input
    """

    return create_verification_result(
        success=False,
        verified=False,
        target=target,
        expected=expected,
        actual=actual,
        error=error
    )


def is_verification_successful(result):
    """
    Return True only when both the verification
    operation succeeded and the expected state
    was verified.
    """

    if not isinstance(result, dict):
        return False

    return (
        result.get("success") is True
        and result.get("verified") is True
    )