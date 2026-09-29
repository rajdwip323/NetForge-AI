"""
NETFORGE-AI IP Verification

Phase 5.4:
IP configuration verification workflow.

This module is vendor-independent at the verification layer.
"""

import ipaddress

from verification.verification_engine import (
    verification_passed,
    verification_failed,
    verification_error
)


def verify_ip_state(
    interface,
    expected_ip,
    expected_mask,
    actual_ip,
    actual_mask
):
    """
    Compare expected and actual IP configuration.
    """

    # Validate interface
    if not isinstance(interface, str) or not interface.strip():
        return verification_error(
            target=interface,
            error="Invalid interface"
        )

    # Validate expected IP
    try:
        ipaddress.IPv4Address(expected_ip)
    except (ipaddress.AddressValueError, TypeError):
        return verification_error(
            target=interface,
            error="Invalid expected IP address"
        )

    # Validate expected subnet mask
    try:
        ipaddress.IPv4Network(
            f"0.0.0.0/{expected_mask}"
        )
    except (ipaddress.NetmaskValueError, ValueError, TypeError):
        return verification_error(
            target=interface,
            expected={
                "ip": expected_ip,
                "mask": expected_mask
            },
            error="Invalid expected subnet mask"
        )

    # Validate actual IP
    try:
        ipaddress.IPv4Address(actual_ip)
    except (ipaddress.AddressValueError, TypeError):
        return verification_error(
            target=interface,
            expected={
                "ip": expected_ip,
                "mask": expected_mask
            },
            actual={
                "ip": actual_ip,
                "mask": actual_mask
            },
            error="Invalid actual IP address"
        )

    # Validate actual subnet mask
    try:
        ipaddress.IPv4Network(
            f"0.0.0.0/{actual_mask}"
        )
    except (ipaddress.NetmaskValueError, ValueError, TypeError):
        return verification_error(
            target=interface,
            expected={
                "ip": expected_ip,
                "mask": expected_mask
            },
            actual={
                "ip": actual_ip,
                "mask": actual_mask
            },
            error="Invalid actual subnet mask"
        )

    # Compare expected vs actual
    ip_match = (
        actual_ip == expected_ip
    )

    mask_match = (
        actual_mask == expected_mask
    )

    expected = {
        "ip": expected_ip,
        "mask": expected_mask
    }

    actual = {
        "ip": actual_ip,
        "mask": actual_mask
    }

    # PASS
    if ip_match and mask_match:
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
        error="IP verification failed"
    )
