"""
NETFORGE-AI VLAN Verification

Phase 5.3:
VLAN verification workflow.

This module is vendor-independent at the verification layer.
"""

from verification.verification_engine import (
    verification_passed,
    verification_failed,
    verification_error
)


def verify_vlan_state(
    vlan_id,
    expected_name,
    actual_vlan_id,
    actual_name
):
    """
    Compare expected and actual VLAN state.
    """

    # Validate VLAN ID
    if not isinstance(vlan_id, int) or not 1 <= vlan_id <= 4094:
        return verification_error(
            target=vlan_id,
            error="Invalid VLAN ID"
        )

    # Validate expected VLAN name
    if not isinstance(expected_name, str) or not expected_name.strip():
        return verification_error(
            target=vlan_id,
            error="Invalid expected VLAN name"
        )

    # Validate actual VLAN ID
    if not isinstance(actual_vlan_id, int) or not 1 <= actual_vlan_id <= 4094:
        return verification_error(
            target=vlan_id,
            expected={
                "vlan_id": vlan_id,
                "name": expected_name
            },
            actual={
                "vlan_id": actual_vlan_id,
                "name": actual_name
            },
            error="Invalid actual VLAN ID"
        )

    # Validate actual VLAN name
    if not isinstance(actual_name, str) or not actual_name.strip():
        return verification_error(
            target=vlan_id,
            expected={
                "vlan_id": vlan_id,
                "name": expected_name
            },
            actual={
                "vlan_id": actual_vlan_id,
                "name": actual_name
            },
            error="Invalid actual VLAN name"
        )

    # Compare expected vs actual
    vlan_id_match = (
        actual_vlan_id == vlan_id
    )

    name_match = (
        actual_name == expected_name
    )

    expected = {
        "vlan_id": vlan_id,
        "name": expected_name
    }

    actual = {
        "vlan_id": actual_vlan_id,
        "name": actual_name
    }

    # PASS
    if vlan_id_match and name_match:
        return verification_passed(
            target=vlan_id,
            expected=expected,
            actual=actual
        )

    # FAIL
    return verification_failed(
        target=vlan_id,
        expected=expected,
        actual=actual,
        error="VLAN verification failed"
    )
