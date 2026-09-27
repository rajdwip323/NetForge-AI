"""
NETFORGE-AI Interface Verification

Phase 5.2:
Interface verification workflow.

This module is vendor-independent at the verification layer.
"""

from verification.verification_engine import (
    verification_passed,
    verification_failed,
    verification_error
)


VALID_INTERFACE_STATUSES = {
    "up",
    "down"
}


def verify_interface_state(
    interface,
    expected_description,
    expected_status,
    actual_description,
    actual_status
):
    """
    Compare expected and actual interface state.
    """

    # Validate interface
    if not isinstance(interface, str) or not interface.strip():
        return verification_error(
            target=interface,
            error="Invalid interface"
        )

    # Validate expected status
    if expected_status not in VALID_INTERFACE_STATUSES:
        return verification_error(
            target=interface,
            expected={
                "description": expected_description,
                "status": expected_status
            },
            error="Invalid expected interface status"
        )

    # Validate actual status
    if actual_status not in VALID_INTERFACE_STATUSES:
        return verification_error(
            target=interface,
            expected={
                "description": expected_description,
                "status": expected_status
            },
            actual={
                "description": actual_description,
                "status": actual_status
            },
            error="Invalid actual interface status"
        )

    # Compare expected vs actual
    description_match = (
        actual_description == expected_description
    )

    status_match = (
        actual_status == expected_status
    )

    expected = {
        "description": expected_description,
        "status": expected_status
    }

    actual = {
        "description": actual_description,
        "status": actual_status
    }

    # PASS
    if description_match and status_match:
        return verification_passed(
            target=interface,
            expected=expected,
            actual=actual
        )

    # FAIL
    return verification_failed(
        target=interface,
        expected=expected,
        actual=actual,
        error="Interface verification failed"
    )